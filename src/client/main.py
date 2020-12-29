import json
import logging
import os
from typing import Any, Dict, List

import flask
import mongoengine as mongo
import mongoengine.queryset.visitor as mongo_visitor
import redis

import data_collections.Product as Product
import data_collections.ProductPrice as ProductPrice

# Other column settings -> http://bootstrap-table.wenzhixin.net.cn/documentation/#column-options
# Search results table columns.
PRODUCT_COLUMNS = [
  {
    "field": "name", # which is the field's name of data key
    "title": "name", # display as the table header's name
    "sortable": True,
  },
  {
    "field": "price (€)",
    "title": "price (€)",
    "sortable": True,
  },
  {
      "field": "quantity",
      "title": "quantity",
      "sortable": True
  },
  {
    "field": "unit price (€)",
    "title": "unit price (€)",
    "sortable": True,
  },
  {
    "field": "unit measure",
    "title": "unit measure",
    "sortable": True,
  },
    {
    "field": "shop_link",
    "title": "link",
    "sortable": True
    },
    {"field": "image",
     "title": "image",
     }
]

app = flask.Flask(__name__)

# Checking for the environment vars.
for var_name in [
   "CRAWLER_PRODUCTS_INPUT_QUEUE",
   "BROKER_PRODUCTS_OUTPUT_QUEUE",
   "REDIS_HOST",
   "REDIS_PORT",
   "MONGODB_HOST",
   "MONGODB_PORT"
]:
   assert var_name in os.environ, "%s environment variable is missing." % var_name

print("Connecting to redis...")
redis_connection = redis.Redis(
   host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"]
)
print("Connected to redis.")

# Connect to the database.
print("creating connection to mongodb")
mongo.connect(
  os.environ["MONGODB_NAME"],
  host=os.environ["MONGODB_HOST"],
  port=int(os.environ["MONGODB_PORT"]),
)
print("connection to mongodb created")


# Map root address to the search page.
@app.route('/')
def index():
   return flask.render_template('search_page.html')


# Search results page.
@app.route('/search_results/<product_name>')
def search_results(product_name):
   # Send a message for the crawler through redis.
   redis_connection.lpush(
      os.environ["CRAWLER_PRODUCTS_INPUT_QUEUE"], product_name
   )
   # Go to the results page.
   return flask.render_template('search_results.html',
                                data={},
                                columns={},
                                product_name=product_name,
                                title=f"Results for {product_name}")


@app.route('/search', methods=['POST', 'GET'])
def search():
   if flask.request.method == 'POST':
      product = flask.request.form['product']
   else:
      product = flask.request.args.get('product')
   return flask.redirect(flask.url_for('search_results', product_name=product))


@app.route('/results_list2')
def results_list2():
    search_term = flask.request.args.get('jsdata')
    items = _get_search_products(search_term)
    d = {"data": items, "columns": PRODUCT_COLUMNS}
    return json.dumps(d)


def _get_search_products(search_term: str) -> List[Dict[str, Any]]:
    """
    Get product list in a json format, given the input search term.

    :param search_term: product to search
    :return: list of products
    """
    # Search products in the db with the given tag.
    products = Product.Product.objects(
        (mongo_visitor.Q(search_term=search_term))
    )
    # Extract data to display from the results.
    res_list = []
    logging.error("products")
    logging.error(len(products))
    for product in products:
        # Get product price.
        product_prices = ProductPrice.ProductPrice.objects(
            (mongo_visitor.Q(product_id=str(product.id)))
        )
        # Extract price info.
        for price in product_prices:
            item = {}
            # Extract product info.
            item["name"] = str(product.name)
            # item["shop"] = str(price.shop)
            item["price (€)"] = price.price
            item["unit price (€)"] = price.unit_price
            item["unit measure"] = str(price.unit_measure)
            item["quantity"] = str(product.quantity)
            item["shop_link"] = f"<a href=\"{str(price.shop_link)}\">{str(price.shop)}</a>"
            item["image"] = f"<img src=\"{price.image_link}\"  width=\"100\" height=\"100\">"
            res_list.append(item)
    return res_list


if __name__ == '__main__':
   app.debug = True
   # Set to ‘0.0.0.0’ to have server available externally.
   app.run(host='0.0.0.0', port="5000")
