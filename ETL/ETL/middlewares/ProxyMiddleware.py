# -*- coding: utf-8 -*-
# Define here the models for your spider middleware
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
from collections import defaultdict
from scrapy.exceptions import NotConfigured
import  requests

class RandomProxyMiddleware(object):
    def __init__(self):
        self.stats = defaultdict(int)  # 默认值是0    统计次数
        self.max_failed = 5  # 请求最多不超过35次

    @staticmethod
    def get_proxy():
        return requests.get("http://127.0.0.1:5010/get/").json()

    @staticmethod
    def delete_proxy(proxy):
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

    @classmethod
    def from_cralwer(cls, crawler):
        # 第一步 创建中间件对象
        # 首先获取配置 HTTPPROXY_ENABLED 看看是否启用代理，
        if not crawler.settings.getbool("HTTPPROXY_ENABLED"):  # 如果没有启用代理
            raise NotConfigured
        # auth_encoding = crawler.settings.get("HTTPPROXY_AUTH_ENCODING")  # 读取配置，这里暂时不用
        # 第二步
        return cls(crawler.settings)  # cls（）实际调用的是 init()函数，如果init接受参数，cls就需要参数

    def process_request(self, request, spider):
        if not request.meta.get("proxy") and request.url not in spider.start_urls:
            request.meta["proxy"] = self.get_proxy().get("proxy")

    def process_response(self, request, response, spider):
        cur_proxy = request.meta.get('proxy')
        if response.status > 400:
            self.stats[cur_proxy] += 1
            logging.log(logging.WARNING,"当前ip{}，第{}次出现错误状态码".format(cur_proxy, self.stats[cur_proxy]))
        if self.stats[cur_proxy] >= self.max_failed:  # 当前ip失败超过3次
            logging.log(logging.WARNING,"当前状态码是{}，代理{}可能被封了".format(response.status, cur_proxy))
            self.delete_proxy(cur_proxy)
            del request.meta['proxy']
            return request

        return response

    def process_exception(self, request, exception, spider):
        # 第五步：请求失败
        cur_proxy = request.meta.get('proxy')   # 取出当前代理
        from twisted.internet.error import ConnectionRefusedError, TimeoutError
        # 如果本次请求使用了代理，并且网络请求报错，认为这个ip出了问题
        if cur_proxy and isinstance(exception, (ConnectionRefusedError, TimeoutError)):
            logging.log(logging.WARNING,"当前的{}和当前的{}".format(exception, cur_proxy))
            self.delete_proxy(cur_proxy)
            del request.meta['proxy']
            # 重新下载这个请求
            return request


