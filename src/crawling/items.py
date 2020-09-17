from scrapy import Item, Field


class Product(Item):
	"""
	product item definition
	"""
	name = Field()
	search_term = Field()
	price = Field()
	quantity = Field()
	link = Field()
	shop = Field()
	id = Field()
	image_urls = Field()
	# will be filled automatically by the ImagesPipeline
	images = Field()
	# pillow image that will be loaded from custom pipeline
	image = Field()
	shop_ranking = Field()
