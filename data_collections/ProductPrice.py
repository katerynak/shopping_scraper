import datetime

import mongoengine as mongo


class ProductPrice(mongo.DynamicDocument):
    """
    Definition of product price schema.
    """
    product_id = mongo.ObjectIdField(primary_key=False)
    search_term = mongo.StringField(required=True)
    price = mongo.FloatField(required=True)
    date = mongo.DateTimeField(default=datetime.datetime.utcnow)
    shop = mongo.StringField(required=True, max_length=50)
    shop_link = mongo.URLField(required=False)
    image_link = mongo.URLField(required=False)
    unit_price = mongo.FloatField(required=False)
    unit_measure = mongo.StringField(required=False, max_length=50)
