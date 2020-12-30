import datetime

import mongoengine as mongo


class Product(mongo.DynamicDocument):
    """
    Definition of product schema.
    """
    name = mongo.StringField(required=True, max_length=100)
    search_term = mongo.ListField(required=False)
    last_update = mongo.DateTimeField(default=datetime.datetime.utcnow)
    quantity = mongo.StringField(required=False, max_length=50)
    comparison_quantity = mongo.FloatField(required=False)
    comparison_measure = mongo.StringField(required=False, max_length=50)
    shop = mongo.StringField(required=False, max_length=50)
    coop_link = mongo.URLField(required=False)
    ah_link = mongo.URLField(required=False)
    # shop_ids =  ListField(required=False)
    coop_id = mongo.IntField(required=False)
    ah_id = mongo.StringField(required=False)
    ah_image = mongo.BinaryField(required=False)
    coop_image = mongo.BinaryField(required=False)
    ah_name = mongo.StringField(required=False, max_length=100)
    coop_name = mongo.StringField(required=False, max_length=100)
    ah_ranking = mongo.IntField(required=False)
    coop_ranking = mongo.IntField(required=False)

