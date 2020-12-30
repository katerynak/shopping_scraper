import logging

import scrapy

from items import Product


class AHSpider(scrapy.Spider):
    name = "ahSpider"
    search_term = None
    shop_search_url = "https://www.ah.nl/zoeken"
    shop_url = "https://www.ah.nl"

    def __init__(self, search_term, redis_connection, output_queue):
        self.search_term = search_term
        self.redis_connection = redis_connection
        self.output_queue = output_queue

    def start_requests(self):
        """
        starts the first request to the supermarket website
        :return:
        """
        params = {
            "query": self.search_term,
            "page": "50",  # assuming the result can have a maximum of 50 pages
        }
        yield scrapy.FormRequest(
            url=self.shop_search_url, formdata=params, method="GET", callback=self.parse
        )

    def save_page(self, response):
        """
        saves the response to file
        :param response:
        :return:
        """
        filename = "dowloaded.html"
        with open(filename, "wb") as f:
            f.write(response.body)

    def parse(self, response):
        """
        extracts the products' information from the result page
        :param response:
        :return:
        """
        # self.save_page(response)
        names = response.xpath(
            "//strong[@data-testhook='product-title']/span/text()"
        ).getall()
        images = response.xpath(
            "//img[starts-with(@class, 'lazy-image_')]/@src"
        ).getall()
        prices = response.xpath(
            "//div[contains(@class, 'price-amount_highlight')]//text()"
        ).getall()
        # assuming each price is composed of euros and eurocents
        prices = [
            prices[i] + prices[i + 1] + prices[i + 2] for i in range(0, len(prices), 3)
        ]
        quantities = response.xpath(
            "//span[@data-testhook='product-unit-size']/text()"
        ).getall()
        product_links = response.xpath(
            "//a[starts-with(@class, 'link_root')]/@href"
        ).getall()
        product_links = [
            self.shop_url + product_links[i] for i in range(0, len(product_links), 2)
        ]
        for i in range(len(names)):
            product = Product()
            product["search_term"] = self.search_term
            product["name"] = names[i]
            product["price"] = prices[i]
            product["quantity"] = quantities[i]
            product["link"] = product_links[i]
            product["shop_ranking"] = i
            product["shop"] = "ah"
            elements = product["link"].split("/")
            for el in elements:
                if "wi" in el:
                    product["id"] = el[2:]
            product["image_urls"] = [images[i]]

            yield product
