from PIL import Image
from mongoengine.queryset.visitor import Q
import datetime

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
		id_present = True
		if "id" in item.fields:
			if item["shop"] == "coop":
				product = Product.objects((Q(coop_id=item["id"])))
			elif item["shop"] == "ah":
				product = Product.objects((Q(ah_id=item["id"])))
		if product:
			# the product from the shop was already inserted in the database
			print("already exists!")
		else:
			# check for the products from other shop with the same name and quantity
			id_present = False
			product = Product.objects((Q(name=item["name"]) & Q(quantity=item["quantity"])))

		# TODO: additional check based on name and/or image similarity + price updates

		if product:
			print("already exists, checking for missing fields..")
			modified = False
			if not id_present:
				print("adding new shop reference for an existing object")
				shop = item["shop"] + "_"
				product[shop+"id"] = item["id"]
				product[shop+"link"] = item["link"]
				product[shop+"image"] = item["image"].tobytes()
				modified = True

			# we are assuming that products with same ids cannot have names or quantities changed in time
			# so we don't check name and quantity fields for now

			if item["search_term"] not in product.search_term:
				product.search_term.append(item["search_term"])
				modified = True

			if modified:
				print("object modified")
				product.last_update = datetime.datetime.utcnow()

		else:
			print("inserting new object..")
			product = Product()
			product.name = item["name"]
			shop = item["shop"] + "_"
			product[shop + "id"] = item["id"]
			product[shop + "link"] = item["link"]
			product[shop + "image"] = item["image"].tobytes()

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