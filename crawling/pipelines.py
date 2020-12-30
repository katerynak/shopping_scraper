"""
Classes of all the item processing pipelines.
"""

import copy
import datetime

import mongoengine.queryset.visitor as mongo_visitor
import PIL.Image as Image

import data_collections.Product as Product
import data_collections.ProductPrice as ProductPrice
import data_processing.product_similarity as product_sim


class LoadImages(object):
    """
    Load images in memory.
    """

    def process_item(self, item, spider):
        """
        Load the image and update the product correspondent field.

        :param item: item crawled from spider
        :param spider: spider who crawled the item
        :return: product item for the next pipeline
        """
        # Load the directory name where images are stored.
        images_dir = spider.settings.get("IMAGES_STORE")
        # Append a slash if needed.
        if images_dir[-1] != "/":
            images_dir = images_dir + "/"
        # Read the image from file.
        image = Image.open(images_dir + item["images"][0]["path"])
        # Update the item field.
        item["image"] = image
        return item


class ValidateItems(object):
    """
    Checks if an item is a valid item.
    """

    def process_item(self, item, spider):
        """
        Check if all the item fields are as expected.

        :param item: item crawled from spider
        :param spider: spider who crawled the item
        :return: product item for the next pipeline
        """
        raise NotImplementedError


class ExtractMeasuresQuantities(object):
    """
    Extract measures and converts quantities for the comparison.
    """

    def process_item(self, item, spider):
        """
        Extract and normalize measure, quantity and price.

        Extract measure, quantity and price fields, get their correspondent
        normalized values, that should be used to compare the item to other items.

        :param item: item crawled from spider
        :param spider: spider who crawled the item
        :return: product item for the next pipeline
        """
        # Extract measure from the quantity field.
        measure = product_sim.find_measure(item["quantity"])
        # Extract quantity from the quantity field.
        quantity = product_sim.find_quantity(item["quantity"], measure)
        # Obtain the normalized values of measure and quantity fields.
        (
            item["comparison_quantity"],
            item["comparison_measure"],
        ) = product_sim.convert_measure(quantity, measure)
        # Convert string price to float.
        item["price"] = price_to_float(item["price"])
        # Calculate the unit price.
        if item["comparison_measure"] != "":
            item["unit_price"] = item["price"] / item["comparison_quantity"]
            # Round unit price to 2 decimals, convert unit price in grams to
            # kilograms.
            if item["comparison_measure"] == "g":
                item["comparison_measure"] = "kg"
                item["unit_price"] = round(item["unit_price"]*1000, 2)
            else:
                item["unit_price"] = round(item["unit_price"], 2)
        else:
            item["unit_price"] = 0.
            item["comparison_measure"] = "No measure found"
        return item


def price_to_float(price):
    """
    Convert the price string to float.

    :param price: input price string
    :return: price float
    """
    return float(price.replace(",", "."))


class SaveItems(object):
    """
    Save items to the database if not already exist.
    """

    def update_price(self, item, product):
        """
        Inserts new price instance into the database.

        :param item: item crawled from spider
        :param product: product instance inserted into the database
        """
        productPrice = ProductPrice.ProductPrice()
        productPrice.product_id = product.id
        productPrice.price = item["price"]
        productPrice.shop = item["shop"]
        productPrice.shop_link = item["link"]
        productPrice.image_link = item["image_urls"][0]
        productPrice.unit_price = item["unit_price"]
        productPrice.unit_measure = item["comparison_measure"]
        productPrice.search_term = item["search_term"]
        productPrice.save()

    def process_item(self, item, spider):
        """
        Update the database with item info.

        Pack the item info as product and product price database instances,
        insert if not already exist, or update if needed.

        :param item: item crawled from spider
        :param spider: spider who crawled the item
        :return: product item and shop name for the next pipeline
        """
        # Check if the product already exists.
        if "id" in item.fields:
            if item["shop"] == "coop":
                product = Product.Product.objects(
                    (mongo_visitor.Q(coop_id=item["id"]))
                )
            elif item["shop"] == "ah":
                product = Product.Product.objects(
                    (mongo_visitor.Q(ah_id=item["id"]))
                )
        # Case 1: product already exists in the db.
        if product:
            print("Already exists!")
            product = product[0]
            # Check if the price is up to date.
            last_price = ProductPrice.ProductPrice.objects(
                (
                    mongo_visitor.Q(product_id=product.id)
                    & mongo_visitor.Q(shop=item["shop"])
                )
            ).order_by("-date")[0]
            if item["price"] != last_price.price:
                # Update the price.
                product.last_update = datetime.datetime.utcnow()
                product.save()
                print("Updating the price..")
                self.update_price(item, product)
            if item["shop_ranking"] != product[item["shop"] + "_" + "ranking"]:
                print("Updating the shop ranking..")
                product[item["shop"] + "_" + "ranking"] = item["shop_ranking"]
                product.last_update = datetime.datetime.utcnow()
                product.save()
        else:
            # Check for other shops.
            #
            # Quick check first.
            product = Product.Product.objects(
                (
                    mongo_visitor.Q(name=item["name"])
                    & mongo_visitor.Q(quantity=item["quantity"])
                )
            )
            if not product:
                # Check if the product with slightly different name or quantity format already
                # exists in the db.
                if len(Product.Product.objects) > 0:
                    for product2 in Product.Product.objects:
                        if product_sim.same_product(product2, item):
                            print(
                                "already exists, with a slightly different name / quantity!"
                            )
                            product = product2
            else:
                product = product[0]
            # Case 2: product already exists in another shop.
            if product:
                print("already exists, inserting new shop info..")
                shop = item["shop"] + "_"
                product[shop + "id"] = item["id"]
                product[shop + "link"] = item["link"]
                product[shop + "image"] = item["image"].tobytes()
                product[shop + "name"] = item["name"]
                product[shop + "ranking"] = item["shop_ranking"]
                if item["search_term"] not in product.search_term:
                    product.search_term.append(item["search_term"])
                product.last_update = datetime.datetime.utcnow()
                product.save()
                # Insert new price instance.
                self.update_price(item, product)
            # Case 3: product does not exist in the db.
            else:
                print("inserting new object..")
                product = Product.Product()
                product.name = item["name"]
                shop = item["shop"] + "_"
                product[shop] = shop
                product["link"] = item["link"]
                product[shop + "id"] = item["id"]
                product[shop + "link"] = item["link"]
                product[shop + "image"] = item["image"].tobytes()
                product[shop + "ranking"] = item["shop_ranking"]
                product.search_term = [item["search_term"]]
                product.quantity = item["quantity"]
                product.comparison_quantity = item["comparison_quantity"]
                product.comparison_measure = item["comparison_measure"]
                # Inserting product price.
                product.save()
                # Insert new price instance.
                self.update_price(item, product)
        return {"product": copy.deepcopy(product), "shop": item["shop"]}


class SendToOut(object):
    """
    Pushes the scraped data id to the `redis` queue.
    """

    def process_item(self, item, spider):
        """
        Process the received item.

        Pack some of the item's info and send them to the `redis` queue.

        :param item: a dictionary containing "product" and "shop" fields, where
            "product" is the product instance inserted into the database, and
            "shop" is a string with the shop name
        :param spider: spider who crawled the item
        :return: product item for the next pipeline
        """
        product = item["product"]
        # Pack selected info for the broker.
        out_dict = {}
        out_dict["product_id"] = str(product.id)
        out_dict["search_term"] = product.search_term
        out_dict["shop"] = item["shop"]
        out_dict["name"] = product.name
        # Send the item to the `redis` queue.
        spider.redis_connection.lpush(spider.output_queue, str(out_dict))
        # Return the product item for the next pipeline.
        return product
