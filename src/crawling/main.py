"""
The main loop receiving and sending messages to/from `redis`.
"""
import os

import mongoengine as mongo
import redis
import scrapy.crawler
import scrapy.settings
import scrapy.utils
import scrapy.utils.log
import twisted.internet.reactor

import data_collections.Product as Product
import data_collections.ProductPrice as ProductPrice
import spiders.ah_spider as ah_spider
import spiders.coop_spider as coop_spider

# Environment variables that should be set.
ENVIRONMENT_VARS = [
    "CRAWLER_OUTPUT_QUEUE",
    "CRAWLER_PRODUCTS_INPUT_QUEUE",
    "MONGODB_NAME",
    "REDIS_HOST",
    "REDIS_PORT",
    "MONGODB_HOST",
    "MONGODB_PORT",
]


def set_settings(settings):
    """
    Settings useful to not get blocked & blacklisted.

    :param settings: scrapy settings instance
    :return:
    """
    settings.set("BOT_NAME", "tutorial")
    settings.set(
        "USER_AGENT",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, "
        "like Gecko) snap Chromium/78.0.3904.108 Chrome/78.0.3904.108 "
        "Safari/537.36",
    )
    settings.set("ROBOTSTXT_OBEY", False)
    settings.set("CONCURRENT_REQUESTS_PER_DOMAIN", 1)
    settings.set("CONCURRENT_REQUESTS_PER_IP", 1)
    settings.set(
        "DEFAULT_REQUEST_HEADERS",
        {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
        },
    )
    settings.set("HTTPCACHE_ENABLED", False)
    settings.set("FEED_EXPORT_ENCODING", "utf-8")
    settings.set("LOG_FILE", "log.txt")
    settings.set("LOGENABLED", True)
    settings.set("STATS_ENABLED", True)
    settings.set("AUTOTHROTTLE_TARGET_CONCURRENCY", 1.0)
    settings.set("COOKIES_ENABLED", False)
    settings.set("DOWNLOAD_DELAY", 3)
    settings.set(
        "ITEM_PIPELINES",
        {
            "scrapy.pipelines.images.ImagesPipeline": 1,
            "pipelines.LoadImages": 2,
            "pipelines.ExtractMeasuresQuantities": 3,
            "pipelines.SaveItems": 4,
            "pipelines.SendToOut": 5,
        },
    )
    settings.set("IMAGES_STORE", "images")


def clean_database():
    """
    Delete all the items from the database.

    Function used for debugging.
    """
    # Delete product items.
    products_to_delete = Product.Product.objects
    products_to_delete.delete()
    # Delete product prices items.
    products_to_delete = ProductPrice.ProductPrice.objects
    products_to_delete.delete()


def wait_for_input():
    """
    Loop waiting for the user input.

    Loop waiting for a message with the user input from the `redis` queue.
    When an input is received, exits the loop and returns the received message.

    :return: the received message from the `redis` queue
    """
    # Flag showing whether the input was found.
    found_input = False
    # Loop until receive a message.
    while not found_input:
        print("Waiting for an input.")
        # Check for a new message from the redis queue.
        task = redis_connection.blpop([products_input_queue], 0)
        received_queue = task[0].decode("utf-8")
        received_input = task[1].decode("utf-8")
        print(f"Received message from {received_queue}")
        found_input = True
    return received_input


if __name__ == "__main__":
    # Check if the environment variables are defined.
    for env_var in ENVIRONMENT_VARS:
        assert env_var in os.environ, (
            "%s environment variable should be " "defined." % env_var
        )
    # Save queues names.
    crawler_output_queue = os.environ["CRAWLER_OUTPUT_QUEUE"]
    products_input_queue = os.environ["CRAWLER_PRODUCTS_INPUT_QUEUE"]
    # Connect to redis instance.
    print("connecting to redis...")
    redis_connection = redis.Redis(
        host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"], charset="utf-8"
    )
    print("connected to redis")
    # Connect to the database.
    print("creating connection to mongodb")
    mongo.connect(
        os.environ["MONGODB_NAME"],
        host=os.environ["MONGODB_HOST"],
        port=int(os.environ["MONGODB_PORT"]),
    )
    print("connection to mongodb created")
    # TODO: remove when no more necessary.
    # Debugging: clean the database.
    clean_database()
    while True:
        # Wait for the user input.
        products = [wait_for_input()]
        # Spiders list.
        shop_spiders = [ah_spider.AHSpider, coop_spider.CoopSpider]
        # shop_spiders = [ah_spider.AHSpider]
        # Get scrapy default settings.
        settings = scrapy.settings.Settings()
        # Set custom settings.
        set_settings(settings)
        # Initialize crawler runner.
        runner = scrapy.crawler.CrawlerRunner(settings=settings)
        # Create a crawler for each product to scrape and for each shop to scrape
        # from.
        for product in products:
            for shop_spider in shop_spiders:
                _ = runner.crawl(
                    shop_spider, product, redis_connection, crawler_output_queue
                )
        # Configure scrapy logging.
        scrapy.utils.log.configure_logging()
        # Run scrapers in parallel.
        d = runner.join()
        d.addBoth(lambda _: twisted.internet.reactor.stop())
        twisted.internet.reactor.run()
