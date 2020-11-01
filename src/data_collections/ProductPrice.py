from mongoengine import *
import datetime


class ProductPrice(DynamicDocument):
	product_id = ObjectIdField(primary_key=False)
	price = FloatField(required=True)
	date = DateTimeField(default=datetime.datetime.utcnow)
	shop = StringField(required=True, max_length=50)
	unit_price = FloatField(required=False)