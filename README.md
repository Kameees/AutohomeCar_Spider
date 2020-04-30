# autohomecar
> 本文爬取的汽车之家数据只供个人学习使用。
> 采用selenium+scrapy的方式爬取。
> 本项目Github地址为：[AutohomeCar_Spider](https://github.com/Kameees/AutohomeCar_Spider)

# 事前准备

推荐在Anaconda创建虚拟环境进行。请确保事先安装好Scrapy、PyMongo、Selenium库以及相应的浏览器驱动。

我用的是Firefox，所以安装geckodriver。

# 爬取思路

- 在车型大全页面获取各汽车品牌型号名称和详情页面链接。
- 获取具体车型的详情页面链接。
- 使用Selenium爬取汽车之家汽车详情页面。

# 爬取分析

打开汽车之家车型大全页面(https://www.autohome.com.cn/car/#pvareaid=3311275)，能看到此页面包含了所有品牌的汽车数据。

打开开发者工具，切换到XHR过滤器下拉网页可以看到Ajax请求，这些请求就是获取车型大全HTML的Ajax请求。

![autohomecar2.png](https://kameee.top/upload/2020/04/autohomecar-2-4bb8a0b7b8ed48a8933563497cab79b3.png)

https://www.autohome.com.cn/grade/carhtml/A.html
可知汽车大全全部请求链接为A.html到Z.html。

可直接通过requests获取。

通过分析可知第二个页面是品牌下同一车辆型号不同款式的汽车列表。

地址为：https://www.autohome.com.cn/ + (汽车id) + /#levelsource=000000000_0&pvareaid=3311672

所以我们需要爬取汽车id构建下一个页面的id。

在第二个页面使用Selenium爬取车辆具体配置页面的链接。

然后在车辆具体配置页面，爬取我们所需要的车辆配置数据。

![autohomecar1.png](https://kameee.top/upload/2020/04/autohomecar-1-7b1bf36814594593818202f214d77583.png)

```python
car_title_name： 汽车品牌
car_name： 汽车型号
price_one： 厂商指导价
price_two： 经销商指导价
level： 级别
standard： 环保标准
max_power： 最大功率
max_torque： 最大扭矩
speed_box： 变速箱
oil： 工信部综合油耗(L/100km)
displacement： 排量
```

# 开始爬取

使用Scrapy。

创建autohomecar项目。

`scrapy startproject autohomecar`

进入项目新建spider。

`scrapy genspider car_spider autohome.com.cn`

修改item,设置需要爬取的数据参数。

代码如下：

```python
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SeriesItem(scrapy.Item):
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
```

修改spider文件夹car_spider编写爬取规则。

```
parse(): 爬取汽车id方法
parse_next_page(): 在汽车型号页面获取具体车辆款式的链接方法
parse_config_page(): 爬取不同款式车辆配置方法
```

代码如下：

```python
# -*- coding: utf-8 -*-

import scrapy
from autohomecar.items import SeriesItem


class CarSpider(scrapy.Spider):
    name = 'car_spider'
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
```

# 数据存储

将爬取的数据存入JSON和保存为CSV文件。具体代码实现在pipelines中。(也可保存至MongoDB)

```
JsonPipeline():存入JSON文件
CsvPipeline():存入CSV文件
```

代码如下：

```python
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
```
# 下载中间件Middlewares设置

设置scrapy对接selenium

```python
# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import random
from autohomecar.settings import USER_AGENT as ua_list


class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        # 从ua_list中随机选择一个User-Agent
        user_agent = random.choice(ua_list)
        # 给请求添加头信息
        request.headers['User-Agent'] = user_agent
        # 可以添加代理ip，方式如下
        # request.meta['proxy'] = "..."
        print(request.headers['User-Agent'])


# selenium对接scrapy部分
class SeleniumMiddleware(object):
    def process_request(self, request, spider):
        firefox_options = Options()
        firefox_options.add_argument('--headless')
        self.driver = webdriver.Firefox(firefox_options=firefox_options)
        self.driver.get(request.url)
        time.sleep(2)

        html = self.driver.page_source
        self.driver.quit()

        response = scrapy.http.HtmlResponse(url=request.url, body=html, request=request, encoding='utf-8')
        return response
```

# 启用设置,修改settings

启用pipelines和middlewares。

```python
# -*- coding: utf-8 -*-

# Scrapy settings for autohomecar project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'autohomecar'

SPIDER_MODULES = ['autohomecar.spiders']
NEWSPIDER_MODULE = 'autohomecar.spiders'

#LOG_LEVEL = 'WARN'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'autohomecar.middlewares.AutohomecarSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    #'autohomecar.middlewares.UserAgentMiddleware': 543,
    'autohomecar.middlewares.SeleniumMiddleware': 500,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'autohomecar.pipelines.JsonPipeline': 300,
    #'autohomecar.pipelines.MongoPipeline': 301,
    'autohomecar.pipelines.CsvPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
#MONGO_URI = 'localhost'
#MONGO_DATABASE = "car_data"  # 库名
```

# 运行scrapy项目

`scrapy crawl car_spider`

运行一段时间后可查看爬取的数据。

![autohomecar3.png](https://kameee.top/upload/2020/04/autohomecar-3-ff31cd1db332441b88a58157d839b1e7.png)
