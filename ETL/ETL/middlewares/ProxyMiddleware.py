# -*- coding: utf-8 -*-
# Define here the models for your spider middleware
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random
from scrapy import signals



# 创建一个中间件     ip代理池
from collections import defaultdict
from scrapy.exceptions import NotConfigured

import re
from time import sleep

# from util.webRequest import WebRequest
import  requests

class ProxyFetcher(object):
    @staticmethod
    def freeProxy13(max_page=5):
        """
        http://www.89ip.cn/index.html
        89免费代理
        :param max_page:
        :return:
        """
        base_url = 'http://www.89ip.cn/index_{}.html'
        for page in range(1, max_page + 1):
            url = base_url.format(page)
            r = requests.get(url, timeout=10)
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
                r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

class RandomProxyMiddleware(object):

    def __init__(self):
        # 第三步 初始化配置和变量
        # 在settings中写一个 PROXIES 列表配置
        # 从settings中把代理读进来（把环境变量读进来）
        self.proxies = []
        p=ProxyFetcher().freeProxy13()
        for _ in p:
            self.proxies.append(_)

        self.stats = defaultdict(int)  # 默认值是0    统计次数
        self.max_failed = 3  # 请求最多不超过3次


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
        # 第四步 为每个request对象随机分配一个ip代理
        # 让这个请求使用代理                       初始url不使用代理ip
        if self.proxies and not request.meta.get("proxy") and request.url not in spider.start_urls:
            request.meta["proxy"] = random.choice(self.proxies)

    def process_response(self, request, response, spider):
        # 第五步： 请求成功
        cur_proxy = request.meta.get('proxy')
        # 判断是否被对方禁封
        if response.status > 400:
            # 给相应的ip失败次数 +1
            self.stats[cur_proxy] += 1
            print("当前ip{}，第{}次出现错误状态码".format(cur_proxy, self.stats[cur_proxy]))
        # 当某个ip的失败次数累计到一定数量
        if self.stats[cur_proxy] >= self.max_failed:  # 当前ip失败超过3次
            print("当前状态码是{}，代理{}可能被封了".format(response.status, cur_proxy))
            # 可以认为该ip被对方封了，从代理池中删除这个ip
            self.remove_proxy(cur_proxy)
            del request.meta['proxy']
            # 将这个请求重新给调度器，重新下载
            return request

        # 状态码正常的时候，正常返回
        return response

    def process_exception(self, request, exception, spider):
        # 第五步：请求失败
        cur_proxy = request.meta.get('proxy')   # 取出当前代理
        from twisted.internet.error import ConnectionRefusedError, TimeoutError
        # 如果本次请求使用了代理，并且网络请求报错，认为这个ip出了问题
        if cur_proxy and isinstance(exception, (ConnectionRefusedError, TimeoutError)):
            print("当前的{}和当前的{}".format(exception, cur_proxy))
            self.remove_proxy(cur_proxy)
            del request.meta['proxy']
            # 重新下载这个请求
            return request

    def remove_proxy(self, proxy):
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            print("从代理列表中删除{}".format(proxy))