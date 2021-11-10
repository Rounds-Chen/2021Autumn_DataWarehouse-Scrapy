import scrapy

class EtlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id=scrapy.Field()
    title=scrapy.Field()
    format=scrapy.Field()
    edition=scrapy.Field()
    people=scrapy.Field()
    role=scrapy.Field()
    rate=scrapy.Field()
    basic_info=scrapy.Field()



class Demo(scrapy.Spider):
    name="Demo"
    allowed_domains=['amazon.com']



    def close(self, reason):
        with open("error.txt",'w') as f:
            f.write('\n'.join(self.error_id)) # 写入错误信息

    def start_requests(self):
        baseUrl='https://www.amazon.com/dp/'
        self.error_id=[]
        with open(r'ETL/data/asin_test.txt') as f:
            for line in f:
                url=baseUrl+line
                yield scrapy.Request(url,meta={'asin':line},
                                     callback=self.parse,
                                     headers={'Accept':'application/json, text/javascript, */*; q=0.01',
                                              'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'})

    def parse(self, response, **kwargs):
        item=EtlItem()
        item['id']=response.meta['asin']

        if response.status==404:
            self.error_id.append('错误页面：' + (response.meta['asin']))

        try:
            item['title']=response.xpath('//*[@id="productTitle"]/text()').extract_first().strip() # 电影名称
            item['edition']=response.xpath('//div[@class="top-level selected-row"]//td[@class="a-text-left dp-edition-col"]' # 电影版本
                                           '//span[@class="a-size-small a-color-base"]/text()').extract_first()

            item['format']=response.xpath('//div[@class="top-level selected-row"]//td[@class="dp-title-col"]' # 电影格式
                                           '//span[@class="a-size-small a-color-base"]/text()').extract_first()

            #['Molly Ringwald', 'Anthony Michael Hall', 'John Hughes']
            item['people']= response.xpath('//div[@id="bylineInfo"]//a[@class="a-link-normal"]/text()').extract() # 电影人员
            # ['(Actor), ', '(Actor), ', '(Director, Writer)', 'Rated: ', 'Format: ']
            item['role']=response.xpath('//div[@id="bylineInfo"]//span[@class="a-color-secondary"]/text()').extract()[:-2] # 人员角色
            # PG
            item['rate']=response.xpath('//div[@id="bylineInfo"]//span[@class="a-size-small"]/text()').extract_first() # 电影分级

            # 基本信息栏
            infos=dict()
            items=response.xpath('//div[@id="detailBullets_feature_div"]')[1]\
                .xpath('.//ul[@class="a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"]//li')
            for i in items:
                key,value=i.xpath('.//span[@class="a-text-bold"]/text()').extract_first(),i.xpath('.//span[2]/text()').extract_first()
                key=key.split('\n')[0]
                infos[key]=value
            item['basic_info']=infos

        except:
            pass



        return item