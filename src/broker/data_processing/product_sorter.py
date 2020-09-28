from data_collections.Product import Product
from data_collections.ProductPrice import ProductPrice
from data_processing.product_similarity import match_measures

from mongoengine.queryset.visitor import Q
from enum import Enum


class ProductSorter:

	def __init__(self, searchTerm):
		self.searchTerm = searchTerm
		self.best = None

	class Alternatives(Enum):
		ALT1 = "alternative1"
		ALT2 = "alternative2"

	# TODO: add comparison taking into account both price and shop ranking,
	#    one way to do it can be taking n products with the best prices and to order them by ranking
	def compare(self, product_id, shop):
		"""
		comparison based on unit price for now, if new product is more convenient then another returns true
		"""
		# retrieve the product in the database
		product = Product.objects(Q(id=product_id))[0]
		productPrice = ProductPrice.objects((Q(product_id=product_id) & Q(shop=shop))).order_by('-date')[0]

		if self.best is None:
			self.best = {}
			self.best_price = {}
			self.best[self.Alternatives.ALT1] = product
			self.best_price[self.Alternatives.ALT1] = productPrice
		else:
			alt = self.Alternatives.ALT1
			matching_measures = match_measures(self.best[alt].quantity, product.quantity)
			if matching_measures is None:
				alt = self.Alternatives.ALT2
				if alt not in self.best:
					self.best[alt] = product
					self.best_price[alt] = productPrice
					return
				else:
					matching_measures = match_measures(self.best[alt].quantity, product.quantity)

			if matching_measures is None:
				print("error")
				print(self.best[alt].quantity)
				print(product.quantity)
			else:
				best_q, product_q, best_m, product_m = matching_measures
				best_unit_price = self.best_price[alt].price / best_q
				product_unit_price = productPrice.price / product_q
				if product_unit_price < best_unit_price:
					self.best[alt] = product
					self.best_price[alt] = productPrice
					print("new best found!")
					print(self.best[alt].name)
					print(self.best_price[alt].price)
					print(self.best_price[alt].shop)
					print(self.best[alt].quantity)
					print("----------------------")
					return True

		return False
