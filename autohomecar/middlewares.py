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


'''
selenium对接scrapy部分
'''

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