# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SeriesItem(scrapy.Item):
    #collection = 'car_series'
    car_title_name = scrapy.Field()
    car_name = scrapy.Field()   # 汽车型号
    price_one = scrapy.Field()  # 厂商指导价
    price_two = scrapy.Field()  # 经销商指导价
    level = scrapy.Field()  # 级别
    standard = scrapy.Field()  # 环保标准
    max_power = scrapy.Field()  # 最大功率
    max_torque = scrapy.Field() # 最大扭矩
    speed_box = scrapy.Field()  # 变速箱
    oil = scrapy.Field()    # 工信部综合油耗(L/100km)
    displacement = scrapy.Field()   # 排量
