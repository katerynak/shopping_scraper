from PIL import Image
from mongoengine.queryset.visitor import Q
import datetime
from copy import deepcopy

from data_collections.Product import Product
from data_collections.ProductPrice import ProductPrice
import product_similarity


class SendToOut(object):
	"""
	Pushes the scraped data id to redis queue
	"""

	def process_item(self, product_dict, spider):
		product = product_dict["product"]
		out_dict = {}
		out_dict["product_id"] = str(product.id)
		out_dict["search_term"] = product.search_term
		out_dict["shop"] = product_dict["shop"]
		out_dict["name"] = product.name
		spider.redis_connection.lpush(spider.output_queue, str(out_dict))
		return product


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


class ExtractMeasuresQuantities(object):
	"""
	Extracts measures and converts quantities in order to be able to compare the item to others
	"""

	def process_item(self, item, spider):
		measure = product_similarity.find_measure(item["quantity"])
		quantity = product_similarity.find_quantity(item["quantity"], measure)
		item["comparison_quantity"], item["comparison_measure"] = \
			product_similarity.convert_measure(quantity, measure)
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
		if "id" in item.fields:
			if item["shop"] == "coop":
				product = Product.objects((Q(coop_id=item["id"])))
			elif item["shop"] == "ah":
				product = Product.objects((Q(ah_id=item["id"])))

		# case 1: product already exists in the db
		if product:
			print("already exists!")
			product = product[0]
			# check if the price is up to date
			last_price = ProductPrice.objects((Q(product_id=product.id) & Q(shop=item["shop"]))).order_by('-date')[0]
			if self.price_to_float(item["price"]) != last_price.price:
				# update the price
				product.last_update = datetime.datetime.utcnow()
				product.save()
				print("updating the price..")
				self.update_price(item, product)
			if item["shop_ranking"] != product[item["shop"]+"_"+"ranking"]:
				print("updating the shop ranking..")
				product[item["shop"] + "_" + "ranking"] = item["shop_ranking"]
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
						if product_similarity.same_product(product2, item):
							print("already exists, with a slightly different name / quantity!")
							product = product2
			else:
				product = product[0]
			# case 2: product already exists in another shop
			if product:

				print("already exists, inserting new shop info..")

				shop = item["shop"] + "_"
				product[shop + "id"] = item["id"]
				product[shop + "link"] = item["link"]
				product[shop + "image"] = item["image"].tobytes()
				product[shop + "name"] = item["name"]

				product[shop + "ranking"] = item["shop_ranking"]

				if item["search_term"] not in product.search_term:
					product.search_term.append(item["search_term"])

				product.last_update = datetime.datetime.utcnow()
				product.save()

				self.update_price(item, product)

			# case 3: product does not exist in the db
			else:
				print("inserting new object..")
				product = Product()
				product.name = item["name"]
				shop = item["shop"] + "_"
				product[shop + "id"] = item["id"]
				product[shop + "link"] = item["link"]
				product[shop + "image"] = item["image"].tobytes()

				product[shop + "ranking"] = item["shop_ranking"]

				product.search_term = [item["search_term"]]
				product.quantity = item["quantity"]

				product.comparison_quantity = item["comparison_quantity"]
				product.comparison_measure = item["comparison_measure"]

				# inserting product price
				product.save()
				self.update_price(item, product)

		return {"product": deepcopy(product),  "shop": item["shop"]}
