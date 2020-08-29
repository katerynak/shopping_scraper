from scrapy import Item, Field


class Product(Item):
	"""
	product item definition, images field will be filled automatically by
	the ImagesPipeline
	"""
	name = Field()
	search_term = Field()
	price = Field()
	quantity = Field()
	link = Field()
	shop = Field()
	id = Field()
	image_urls = Field()
	images = Field()
