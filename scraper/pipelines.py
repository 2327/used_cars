# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from dbapi.dbtools import Base_Updater


class CarsScraperPipeline(object):

    def __init__(self):
        self.updater = Base_Updater()

    def open_spider(self, spider):
        self.updater.start_updating()

    def process_item(self, item, spider):
        print(item.values())
        self.updater.update(item)
        return item

    def close_spider(self, spider):
        print('close_spider() method run...')
        self.updater.end_updating()

    # DEBUG
    # def process_item(self, item, spider):
    #     print(item)
    #     return item
    #
    # def close_spider(self, spider):
    #     print('Closing...')