# -*- coding: utf-8 -*-

import scrapy
from autohomecar.items import SeriesItem


class CarSpider(scrapy.Spider):
    name = 'car_spider'
    #allowed_domains = ['autohome.com.cn']
    #start_urls = ['http://www.autohome.com.cn/grade/carhtml/A.html']
    start_urls = ['http://www.autohome.com.cn/grade/carhtml/%s.html' % chr(ord('A') + i) for i in range(26)]

    def parse(self, response):
        ids = response.xpath('body/dl//ul//li/@id')
        for id in ids:
            url = 'https://www.autohome.com.cn/' + id.extract()[1:] + '/#pvareaid=3311672'
            yield scrapy.Request(url=url, callback=self.parse_next_page, dont_filter=True)

    def parse_next_page(self, response):
        for id in response.xpath('//dd//a[@class="name"]/@href').extract():
            url = 'https://www.autohome.com.cn' + id
            yield scrapy.Request(url=url, callback=self.parse_config_page, dont_filter=True)

    def parse_config_page(self, response):
        print('正在爬取车辆配置页面...')
        item = SeriesItem()
        try:
            item['car_title_name'] = ''.join(response.xpath('//div[@class="athm-sub-nav__car__name"]/a//text()').extract()).strip()
            item['car_name'] = response.xpath('//div[@class="information-tit"]/h2/text()').extract_first()
            item['price_one'] = ''.join(response.xpath('//a[@id="cityDealerPrice"]//text()').extract()).strip()
            item['price_two'] = ''.join(response.xpath('//dl[@class="information-other"]/dd/div[@class="con"]//text()').extract()[:3]).strip()

            item['level'] = response.xpath('//div[@class="param-list"]/div[1]/p/text()').extract_first()  # 级别
            item['displacement'] = response.xpath('//div[@class="param-list"]/div[2]/p/text()').extract_first()
            item['max_power'] = response.xpath('//div[@class="param-list"]/div[3]/p/text()').extract_first()
            item['max_torque'] = response.xpath('//div[@class="param-list"]/div[4]/p/text()').extract_first()
            item['speed_box'] = response.xpath('//div[@class="param-list"]/div[5]/p/text()').extract_first()
            item['oil'] = response.xpath('//div[@class="param-list"]/div[6]/p/text()').extract_first()
            item['standard'] = response.xpath('//div[@class="param-list"]/div[7]/p/text()').extract_first()  # 环保标准
            yield item
        except:
            pass

