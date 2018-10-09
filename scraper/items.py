# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CarsScraperItem(scrapy.Item):
    brand = scrapy.Field()
    model = scrapy.Field()
    year = scrapy.Field()
    kmage = scrapy.Field()
    price = scrapy.Field()
    engine = scrapy.Field()
    gearbox = scrapy.Field()



