# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import csv
from pymongo import MongoClient


class JsonPipeline(object):
    def open_spider(self, spider):
        self.file = open('cars.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        context = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(context)

    def close_spider(self, spider):
        self.file.close()


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongo_uri=crawler.settings.get('MONGO_URI'),
                   mongo_db=crawler.settings.get('MONGO_DATABASE'))

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
            self.db.insert(dict(item))
            return item

    def close_spider(self, spider):
        self.client.close()


class CsvPipeline(object):

    def open_spider(self, spider):
        self.file = open('car.csv', 'w', newline='', encoding='utf-8-sig')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['品牌', '汽车型号', '厂商指导价', '经销商指导价', '级别', '排量', '最大功率', '最大扭矩', '变速箱', '工信部综合油耗(L/100km)', '环保标准'])

    def process_item(self, item, spider):
        self.writer.writerow([item['car_title_name'], item['car_name'], item['price_one'], item['price_two'], item['level'], item['displacement'], item['max_power'], item['max_torque'], item['speed_box'], item['oil'], item['standard']])
        return item

    def close_spider(self, spider):
        self.file.close()