"""
Common definition for all scrapers of the item class with fields to scrape from
websites.
"""

import scrapy


class Product(scrapy.Item):
    """
    Product item definition.
    """

    # Search term given as input to a scraper.
    search_term = scrapy.Field()
    # Fields scraped from a website.
    name = scrapy.Field()
    price = scrapy.Field()
    quantity = scrapy.Field()
    link = scrapy.Field()
    shop = scrapy.Field()
    id = scrapy.Field()
    image_urls = scrapy.Field()
    # Fields filled by a scraper after analyzing some info from a website.
    shop_ranking = scrapy.Field()
    comparison_quantity = scrapy.Field()
    comparison_measure = scrapy.Field()
    unit_price = scrapy.Field()
    # Will be filled automatically by the ImagesPipeline.
    images = scrapy.Field()
    # Pillow image that will be loaded from custom pipeline.
    image = scrapy.Field()
