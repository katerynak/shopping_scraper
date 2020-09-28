import datetime
from mongoengine import *


class Product(DynamicDocument):
	name = StringField(required=True, max_length=100)
	search_term = ListField(required=False)
	last_update = DateTimeField(default=datetime.datetime.utcnow)
	quantity = StringField(required=False, max_length=50)
	comparison_quantity = FloatField(required=False)
	comparison_measure = StringField(required=False, max_length=50)
	coop_link = URLField(required=False)
	ah_link = URLField(required=False)
	# shop_ids = ListField(required=False)
	coop_id = IntField(required=False)
	ah_id = IntField(required=False)
	ah_image = BinaryField(required=False)
	coop_image = BinaryField(required=False)
	ah_name = StringField(required=False, max_length=100)
	coop_name = StringField(required=False, max_length=100)
	ah_ranking = IntField(required=False)
	coop_ranking = IntField(required=False)
	# brand = StringField(required=False, max_length=50)
	# ingredients = ListField(required=False)