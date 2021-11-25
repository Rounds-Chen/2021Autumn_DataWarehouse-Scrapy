import scrapy
import logging

# class EtlItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     id=scrapy.Field()
#     title=scrapy.Field()
#     format=scrapy.Field()
#     edition=scrapy.Field()
#     people=scrapy.Field()
#     role=scrapy.Field()
#     rate=scrapy.Field()
#     basic_info=scrapy.Field()
#     # release_date=scrapy.Field()
#     #
#     # release_year=scrapy.Field()
#     # x_ray=scrapy.Field()
#     # director=scrapy.Field()
#     # actor=scrapy.Field()
#     # gener=scrapy.Field()


class Item_2(scrapy.Item):
    id=scrapy.Field()
    basic_info=scrapy.Field()




class Demo(scrapy.Spider):
    name="Demo"
    allowed_domains=['amazon.com']



    def close(self, reason):
        with open("null_asin.txt",'w') as f:
            f.write('\n'.join(self.null_asin)) # 写入错误信息
        f.close()
        print('写入错误信息！！！！！')
        # with open("error_503.txt",'w') as w:
        #     w.write('\n'.join(self.error_503_id))

    def start_requests(self):
        baseUrl='https://www.amazon.com/dp/'
        # self.error_404_id=[]
        # self.error_503_id=[]
        self.null_asin=[]

        with open(r'ETL/data/loss_asin.txt') as f:
            for line in f:
                url=baseUrl+line
                yield scrapy.Request(url,meta={'asin':line.strip()},
                                     callback=self.parse_basic_info,
                                     headers={'Accept':'application/json, text/javascript, */*; q=0.01',
                                              'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'})

    # 获取basic info
    def parse_basic_info(self,response):
        item=Item_2()
        item['id']=response.meta['asin']
        try:
            # 基本信息栏
            infos = dict()
            items = response.xpath('//div[@id="detailBullets_feature_div"]')[1] \
                .xpath('.//ul[@class="a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"]//li')
            if items==[]:
                self.null_asin.append(items['id']) # 记录空asin
            else:
                for i in items:
                    key, value = i.xpath('.//span[@class="a-text-bold"]/text()').extract_first(), i.xpath(
                        './/span[2]/text()').extract_first()
                    key = key.split('\n')[0]
                    infos[key] = value
                item['basic_info'] = str(infos)

        except:
            pass

        return item


    def parse(self, response, **kwargs):
        # if response.status==200:
        #     self.error_404_id.append(response.meta['asin'])
        # elif response.status==503:
        #     self.error_503_id.append(response.meta['asin'])

        # if response.xpath('//div[@class="av-page-desktop avu-retail-page"]')!=[]:
        #     return self.parse_retail_page(response)
        # else:
        return self.parse_dvd(response)

    # def parse_dvd(self, response):
    #     item=EtlItem()
    #     item['id']=response.meta['asin']
    #
    #     try:
    #         item['title']=response.xpath('//*[@id="productTitle"]/text()').extract_first().strip() # 电影名称
    #         item['edition']=response.xpath('//div[@class="top-level selected-row"]//td[@class="a-text-left dp-edition-col"]' # 电影版本
    #                                        '//span[@class="a-size-small a-color-base"]/text()').extract_first()
    #         item['release_date']=response.xpath('//div[@class="top-level selected-row"]//td[@class="a-text-left dp-edition-col"]'
    #                                             '//span[@class="a-size-small a-color-base"]/text()').extract()[1]
    #         item['format']=response.xpath('//div[@class="top-level selected-row"]//td[@class="dp-title-col"]' # 电影格式
    #                                        '//span[@class="a-size-small a-color-base"]/text()').extract_first()
    #
    #         #['Molly Ringwald', 'Anthony Michael Hall', 'John Hughes']
    #         item['people']= response.xpath('//div[@id="bylineInfo"]//a[@class="a-link-normal"]/text()').extract() # 电影人员
    #         # ['(Actor), ', '(Actor), ', '(Director, Writer)', 'Rated: ', 'Format: ']
    #         item['role']=response.xpath('//div[@id="bylineInfo"]//span[@class="a-color-secondary"]/text()').extract()[:len(item['people'])] # 人员角色
    #         # PG
    #         item['rate']=response.xpath('//div[@id="bylineInfo"]//span[@class="a-size-small"]/text()').extract_first() # 电影分级
    #
    #         # 基本信息栏
    #         infos=dict()
    #         items=response.xpath('//div[@id="detailBullets_feature_div"]')[1]\
    #             .xpath('.//ul[@class="a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"]//li')
    #         for i in items:
    #             key,value=i.xpath('.//span[@class="a-text-bold"]/text()').extract_first(),i.xpath('.//span[2]/text()').extract_first()
    #             key=key.split('\n')[0]
    #             infos[key]=value
    #         item['basic_info']=str(infos)
    #
    #         # logging.warning(infos)
    #
    #     except:
    #         pass

        # return item

    # def parse_retail_page(self, response):
    #     item = EtlItem()
    #     item['id'] = response.meta['asin']
    #
    #     try:
    #         item['title']=response.xpath('//h1[@data-automation-id="title"]/text()').extract_first()
    #         item['format']='Prime Vedio'
    #
    #         item['release_year']= response.xpath('//span[@data-automation-id="release-year-badge"]/text()').extract_first()
    #         item['x_ray']=response.xpath('//span[@data-automation-id="x-ray-badge"]/text()').extract_first()
    #         item['rate']=response.xpath('//span[@data-automation-id="rating-badge"]/span/text()').extract_first()
    #
    #         items=response.xpath('//div[@data-automation-id="meta-info"]//dl')
    #         item['director']=items[0].xpath('.//a/text()').extract_first()
    #         item['actor']=items[1].xpath('.//a/text()').extract() #  ['Diane Keaton', 'Mandy Moore', 'Gabriel Macht']
    #         item['gener']=items[2].xpath('.//a/text()').extract() #  ['Comedy', 'Drama']
    #     except:
    #         pass
    #
    #     return item





