import scrapy
import ast

from items import Product


class CoopSpider(scrapy.Spider):
	name = "coopSpider"
	search_term = None
	shop_search_url = "https://www.coop.nl/zoeken"

	def __init__(self, search_term):
		self.search_term = search_term

	def start_requests(self):
		"""
		starts the first request to the supermarket website
		:return:
		"""
		params = {
			'SearchTerm': self.search_term
		}
		yield scrapy.FormRequest(url=self.shop_search_url, formdata=params, callback=self.parse, method="GET")

	def save_page(self, response):
		"""
		saves the response to file
		:param response:
		:return:
		"""
		filename = 'dowloaded.html'
		with open(filename, 'wb') as f:
			f.write(response.body)

	def parse(self, response):
		"""
		extracts the products' information from the result page
		:param response:
		:return:
		"""
		# self.save_page(response)
		names = response.xpath("//h2[starts-with(@class, 'productTitle')]/a/text()").getall()
		images = response.xpath("//picture[@class='img']/img/@data-srcset").getall()
		prices = response.xpath("//ins[@class='price']//text()").getall()
		# assuming each price is composed of euros and eurocents
		prices = [prices[i] + prices[i+1] for i in range(0, len(prices), 2)]
		quantities = response.xpath("//div[starts-with(@class, 'productDescription')]/div/div/text()").getall()
		product_links = response.xpath("//a[@class='img']/@href").getall()
		id = response.xpath("//article[contains(@class, 'listItem')]/@data-product").getall()
		ids = []
		for id_item in id:
			id_item = ast.literal_eval(id_item)
			id_item = id_item["id"]
			ids.append(id_item)

		for i in range(len(names)):
			product = Product()
			product["search_term"] = self.search_term
			product["name"] = names[i]
			product["price"] = prices[i]
			product["quantity"] = quantities[i]
			product["link"] = product_links[i]
			product["shop"] = "coop"
			product["id"] = ids[i]
			product["image_urls"] = [images[i].split(",")[1][:-3]]
			yield product

		next_page_active = response.xpath("//a[@rel='next']/../@class").get()
		if "inactive" not in next_page_active:
			next_page = response.xpath("//a[@rel='next']/@href").get()
			yield scrapy.FormRequest(url=next_page, callback=self.parse, method="GET")

