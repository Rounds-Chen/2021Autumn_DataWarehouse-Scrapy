# -*- coding: utf-8 -*-
# Define here the models for your spider middleware
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import time
from collections import defaultdict
from scrapy.exceptions import NotConfigured
import  requests

class RandomProxyMiddleware(object):
    def __init__(self):
        self.stats = defaultdict(int)  # 默认值是0    统计次数
        self.max_failed = 3  # 请求最多不超过35次
        self.ip= "http://117.161.75.82:3128"


    @staticmethod
    def get_proxy():
        ans=requests.get("http://1.15.13.86:5010/get/").json()
        return ans

    def delete_proxy(self,proxy):
        # if requests.get("http://127.0.0.1:5010/count")<10:
        #     time.sleep(300) # sleep 3min
        self.stats[proxy]=0
        requests.get("http://1.15.13.86:5010/delete/?proxy={}".format(proxy[7:]))

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
        if not request.meta.get("proxy") :
            request.meta["proxy"] = self.ip
            # logging.log(logging.WARNING, "{} 没有代理，设置代理ip:{}".format(request.meta['asin'],request.meta["proxy"]))
        # logging.log(logging.WARNING,"{} 已有代理，下一步。。。".format(request.meta['asin']))
        return None

    def process_response(self, request, response, spider):
        cur_proxy = request.meta.get('proxy')
        logging.log(logging.WARNING,"回复状态码: {}".format(response.status))

        items = response.xpath('//div[@id="detailBullets_feature_div"]')
        if response.status !=200 :
            self.stats[cur_proxy] += 1
            logging.log(logging.WARNING,"代理ip {}，第{}次出现错误状态码{}".format(cur_proxy, self.stats[cur_proxy],response.status))
            if self.stats[cur_proxy] >= self.max_failed:  # 当前ip失败超过5次
                logging.log(logging.WARNING,"代理 {}可能被封了".format(cur_proxy))
                if self.ip==cur_proxy:
                    self.ip="http://"+self.get_proxy()['proxy']
                    logging.log(logging.WARNING,'新ip',self.ip)
                request.meta['proxy']=self.ip
                self.delete_proxy(cur_proxy)
            return request

        # if items==[]:
        #     logging.log(logging.WARNING,'{} 需要重新爬取'.format(request.meta['asin']))
        #     return request
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


