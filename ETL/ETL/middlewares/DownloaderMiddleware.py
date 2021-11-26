import logging

from scrapy import signals


class DownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        super(DownloaderMiddleware, self).__init__()
        self.cur_asin=""
        self.cur_times=0

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        try:
            items = response.xpath('//div[@id="detailBullets_feature_div"]')
            if self.cur_times<=3 and items == []:
                logging.log(logging.WARNING,"asin "+request.meta['asin']+" re-req...")
                self.cur_times+=1
                self.cur_asin=request.meta['asin']
                return request
            else:
                self.cur_times=0
                self.cur_asin=""
        except:
            self.cur_times = 0
            self.cur_asin = ""
            logging.log(logging.WARNING,"DownloaderMiddleware Error!!!")
            return request

        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
