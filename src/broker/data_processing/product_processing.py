from data_collections.Product import Product
from data_collections.ProductPrice import ProductPrice

from mongoengine.queryset.visitor import Q


def process_product(product_data):
	"""
	processes product data coming from crawler, updates the dataset if needed
	:param product_data:
	:return:
	"""
	# debugging purpose only
	# products_to_delete = Product.objects()
	# products_to_delete.delete()

	# products_to_delete = ProductPrice.objects()
	# products_to_delete.delete()

	#TODO: data validation

	# check if object already exists
	if "id" in product_data:
		if product_data["shop"] == "coop":
			product = Product.objects((Q(coop_id=product_data["id"])))
		elif product_data["shop"] == "ah":
			product = Product.objects((Q(coop_id=product_data["id"])))

	#TODO: additional check based on name and/or image similarity + price updates

	if product:
		print("already exists!")
		print(product[0])
	else:
		print("inserting new object..")
		product = Product()
		product.name = product_data["name"]

		if product_data["shop"] == "coop":
			product.coop_id = product_data["id"]
			product.coop_link = product_data["link"]
			product.coop_image = product_data["image"]
		elif product_data["shop"] == "ah":
			product.ah_id = product_data["id"]
			product.ah_link = product_data["link"]
			product.ah_image = product_data["image"]

		product.search_term = [product_data["search_term"]]
		product.quantity = product_data["quantity"]
		product.save()

		# inserting product price
		productPrice = ProductPrice()
		productPrice.product_id = product.id
		productPrice.price = float(product_data["price"].replace(",", "."))
		productPrice.shop = product_data["shop"]

		productPrice.save()
