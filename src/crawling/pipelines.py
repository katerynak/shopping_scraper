from PIL import Image
from mongoengine.queryset.visitor import Q
import datetime

from data_collections.Product import Product
from data_collections.ProductPrice import ProductPrice
from product_similarity import same_product


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

	def price_to_float(self, price):
		"""
		given the price string returns its float value
		"""
		return float(price.replace(",", "."))

	def update_price(self, item, product):
		"""
		inserts new price instance in the database
		"""
		productPrice = ProductPrice()
		productPrice.product_id = product.id
		productPrice.price = self.price_to_float(item["price"])
		productPrice.shop = item["shop"]

		productPrice.save()

	def process_item(self, item, spider):

		# check if object already exists
		# id_present = True
		if "id" in item.fields:
			if item["shop"] == "coop":
				product = Product.objects((Q(coop_id=item["id"])))
			elif item["shop"] == "ah":
				product = Product.objects((Q(ah_id=item["id"])))
			else:
				print("error1!!!!!!")
				# exit(0)
		else:
			print("error2!!!!!!")
			# exit(0)

		# case 1: product already exists in the db
		if product:
			print("already exists!")
			product = product[0]
			# check if the price is up to date
			last_price = ProductPrice.objects(Q(product_id=product.id) & Q(shop=item["shop"])).order_by('-date')[0]
			if self.price_to_float(item["price"]) != last_price.price:
				# update the price
				print("updating the price..")
				self.update_price(item, product)
				product.last_update = datetime.datetime.utcnow()
				product.save()
		else:
			# check for other shops

			# quick check first
			product = Product.objects((Q(name=item["name"]) & Q(quantity=item["quantity"])))

			if not product:
				# check if the product with slightly different name or quantity format already
				# exists in the db
				if len(Product.objects) > 0:
					for product2 in Product.objects:
						if same_product(product2, item):
							print("already exists, with a slightly different name / quantity!")
							print("already exists, with a slightly different name / quantity!")
							product = product2

			# case 2: product already exists in another shop
			if product:
				print("already exists, inserting new shop info..")

				shop = item["shop"] + "_"
				product[shop+"id"] = item["id"]
				product[shop+"link"] = item["link"]
				product[shop+"image"] = item["image"].tobytes()
				product[shop+"name"] = item["name"]

				if item["search_term"] not in product.search_term:
					product.search_term.append(item["search_term"])

				self.update_price(item, product)

				product.last_update = datetime.datetime.utcnow()
				product.save()

			# case 3: product does not exist in the db
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

				# inserting product price
				self.update_price(item, product)
				product.save()

		return item