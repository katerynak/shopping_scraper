import random
import os
import redis
from mongoengine import *

from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.settings import Settings
from scrapy.utils.log import configure_logging

from spiders.ah_spider import AHSpider
from spiders.coop_spider import CoopSpider

from data_collections.Product import Product
from data_collections.ProductPrice import ProductPrice


# TODO : make a pool of user agents to be rotated https://developers.whatismybrowser.com/useragents/explore/operating_system_name/linux/
# https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/
# see other practices from not getting bunned https://docs.scrapy.org/en/latest/topics/practices.html


def set_settings(settings):
	"""
    Settings useful to not get blocked & blacklisted
    :param settings:
    :return:
    """
	settings.set("BOT_NAME", "tutorial")
	settings.set("USER_AGENT",
				 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) snap Chromium/78.0.3904.108 Chrome/78.0.3904.108 Safari/537.36")
	settings.set("ROBOTSTXT_OBEY", False)
	settings.set("CONCURRENT_REQUESTS_PER_DOMAIN", 1)
	settings.set("CONCURRENT_REQUESTS_PER_IP", 1)
	settings.set("DEFAULT_REQUEST_HEADERS", {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
	})
	settings.set("HTTPCACHE_ENABLED", False)
	settings.set("FEED_EXPORT_ENCODING", "utf-8")
	settings.set("LOG_FILE", "log.txt")
	settings.set("LOGENABLED", True)
	settings.set("STATS_ENABLED", True)
	settings.set("AUTOTHROTTLE_TARGET_CONCURRENCY", 1.0)
	settings.set("COOKIES_ENABLED", False)
	settings.set("DOWNLOAD_DELAY", 3)
	settings.set('ITEM_PIPELINES', {'scrapy.pipelines.images.ImagesPipeline': 1,
									'pipelines.LoadImages': 2,
									'pipelines.SaveItems': 3,
									'pipelines.SendToOut': 4
									})
	settings.set('IMAGES_STORE', "images")


# for development purposes only
def clean_database():
	products_to_delete = Product.objects()
	products_to_delete.delete()

	products_to_delete = ProductPrice.objects()
	products_to_delete.delete()


def wait_for_input():
	found_input = False

	while not found_input:
		print("waiting for an input")
		task = redis_connection.blpop([products_input_queue], 0)
		received_queue = task[0].decode("utf-8")
		received_input = task[1].decode("utf-8")
		print("received message from %s" % received_queue)
		# run_spiders(JOB_SPIDERS, settings, received_input)
		found_input = True
	return received_input


if __name__ == "__main__":

	for env_var in ["CRAWLER_OUTPUT_QUEUE", "CRAWLER_PRODUCTS_INPUT_QUEUE",
					"MONGODB_NAME",
					"REDIS_HOST", "REDIS_PORT", "MONGODB_HOST", "MONGODB_PORT"]:
		assert env_var in os.environ, "%s environment variable should be defined." % env_var

	crawler_output_queue = os.environ["CRAWLER_OUTPUT_QUEUE"]
	products_input_queue = os.environ["CRAWLER_PRODUCTS_INPUT_QUEUE"]

	# connecting to redis instance
	print("connecting to redis...")
	redis_connection = redis.Redis(host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"], charset="utf-8")
	print("connected to redis")

	print("creating connection to mongodb")
	connect(os.environ["MONGODB_NAME"], host=os.environ["MONGODB_HOST"], port=int(os.environ["MONGODB_PORT"]))
	print("connection to mongodb created")

	# for debugging purposes
	clean_database()

	# waiting for the user input
	products = [wait_for_input()]
	# spider shop list
	shop_spiders = [AHSpider, CoopSpider]
	settings = Settings()
	set_settings(settings)
	runner = CrawlerRunner(settings=settings)

	# parallel crawling
	for product in products:
		random.shuffle(shop_spiders)
		for shop_spider in shop_spiders:
			l = runner.crawl(shop_spider, product, redis_connection, crawler_output_queue)
	d = runner.join()
	d.addBoth(lambda _: reactor.stop())

	configure_logging()
	reactor.run()
