from PIL import Image
from mongoengine.queryset.visitor import Q

from data_collections.Product import Product
from data_collections.ProductPrice import ProductPrice


class SendToOut(object):
	"""
	Pushes the scraped data to redis queue
	"""

	def process_item(self, item, spider):

		spider.redis_connection.lpush(spider.output_queue, str(dict(item)))
		return item


class LoadImages(object):
	"""
	Loads images in memory to store them in redis
	"""

	def process_item(self, item, spider):
		images_dir = spider.settings.get("IMAGES_STORE")
		if images_dir[-1] != "/":
			images_dir = images_dir + "/"
		im = Image.open(images_dir + item["images"][0]["path"])
		item["image"] = im

		return item


class ValidateItems(object):
	"""
	Checks if an item is a valid item
	"""

	def process_item(self, item, spider):

		# to be implemented
		return item


class SaveItems(object):
	"""
	Saves items to the database if not already exist
	"""

	def process_item(self, item, spider):
		# check if object already exists
		if "id" in item.fields:
			if item["shop"] == "coop":
				product = Product.objects((Q(coop_id=item["id"])))
			elif item["shop"] == "ah":
				product = Product.objects((Q(coop_id=item["id"])))

		# TODO: additional check based on name and/or image similarity + price updates

		if product:
			print("already exists!")
			print(product[0])
		else:
			print("inserting new object..")
			product = Product()
			product.name = item["name"]

			if item["shop"] == "coop":
				product.coop_id = item["id"]
				product.coop_link = item["link"]
				product.coop_image = item["images"]
			elif item["shop"] == "ah":
				product.ah_id = item["id"]
				product.ah_link = item["link"]
				product.ah_image = item["images"]

			product.search_term = [item["search_term"]]
			product.quantity = item["quantity"]
			product.save()

			# inserting product price
			productPrice = ProductPrice()
			productPrice.product_id = product.id
			productPrice.price = float(item["price"].replace(",", "."))
			productPrice.shop = item["shop"]

			productPrice.save()

		return item