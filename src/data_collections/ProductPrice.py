import datetime

import mongoengine as mongo


class ProductPrice(mongo.DynamicDocument):
    """
    Definition of product price schema.
    """

    product_id = mongo.ObjectIdField(primary_key=False)
    price = mongo.FloatField(required=True)
    date = mongo.DateTimeField(default=datetime.datetime.utcnow)
    shop = mongo.StringField(required=True, max_length=50)
    unit_price = mongo.FloatField(required=False)
