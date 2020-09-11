import datetime
from mongoengine import *


class Product(DynamicDocument):
	name = StringField(required=True, max_length=100)
	search_term = ListField(required=False)
	last_update = DateTimeField(default=datetime.datetime.utcnow)
	quantity = StringField(required=False, max_length=50)
	coop_link = URLField(required=False)
	ah_link = URLField(required=False)
	# shop_ids = ListField(required=False)
	coop_id = IntField(required=False)
	ah_id = IntField(required=False)
	ah_image = BinaryField(required=False)
	coop_image = BinaryField(required=False)
	# brand = StringField(required=False, max_length=50)
	# ingredients = ListField(required=False)