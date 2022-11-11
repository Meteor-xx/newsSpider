import scrapy
from scrapy import Request
import json

from newsSpider.items import NewsSeeds


def check_list_end_correct(strings):
    strings = "".join(strings)\
        .strip().replace('&nbsp', ' ').replace('\xa0', ' ').replace('\n', '').replace('​', '').replace('\u201c', '')
    return strings


class VOASeedsSpider(scrapy.Spider):
    name = 'VOASeeds'
    allowed_domains = ['www.voanews.com']
    start_urls = ['https://www.voanews.com/']
    categorys = [
        [["VOAPolitic"],
         [["Meet", "s?k=president%20meeting&tab=news&pi=", "&r=any&pp=50"]
          ]]
    ]
    next_cate = False  # 切换类别
    next_api_index = False  # 切换api_url
    cate_num = 0  # 类别
    cate_api_index = 0  # 类内index
    nums = 1  # 当前爬取数量
    Seeds = ""

    def start_requests(self):

        url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1] + str(self.nums) +\
              self.categorys[self.cate_num][1][self.cate_api_index][2]
        print("*****Start crawl: {}".format(url))
        yield Request(url=url, callback=self.parse)

    def parse(self, response):
        sections = response.xpath(
            ".//div[@class='media-block__content media-block__content--h media-block__content--h-xs']"
        )
        json_seeds = ""
        for section in sections:
            time = section.xpath("./span/text()").extract()
            url = section.xpath("./a/@href").extract()
            title = section.xpath("./a/h4/text()").extract()
            description = section.xpath("./a/p/text() | ./a/p/strong/text()").extract()
            seed = {
                'time': time,
                'url': url,
                'title': title,
                'description': ''.join(description)
            }
            json_seed = json.dumps(seed)
            json_seeds = json_seeds + check_list_end_correct(json_seed) + ','
        if self.nums != 200:
            self.nums += 1
            self.Seeds = self.Seeds + json_seeds
            next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1] + str(self.nums)\
                       + self.categorys[self.cate_num][1][self.cate_api_index][2]
            yield scrapy.Request(url=next_url, callback=self.parse)
        else:
            self.Seeds = self.Seeds + json_seeds[:-1]
            item = NewsSeeds()
            item["seeds"] = "[" + self.Seeds + "]\r\n"
            item["category"] = self.categorys[self.cate_num][0][0] + "_" +\
                               self.categorys[self.cate_num][1][self.cate_api_index][0]  # 当前类别名
            self.next_api_index = True  # 切换api
            yield item
        if self.next_api_index:  # 切换分类下api
            self.next_api_index = False
            if self.cate_api_index < (len(self.categorys[self.cate_num][1]) - 1):  # 需要切换api并且判断是否是该分类下最后一个api
                self.cate_api_index += 1
                self.nums = 0
                self.Seeds = ""
                next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1]\
                           + str(self.nums) + self.categorys[self.cate_num][1][self.cate_api_index][2]
                yield scrapy.Request(url=next_url, callback=self.parse)
            else:  # 当前是该分类下最后一个api，需要切换类别
                self.next_cate = True
        if self.next_cate:  # 切换分类
            self.next_cate = False
            if self.cate_num < (len(self.categorys) - 1):  # 判断是否是最后一个分类
                self.cate_num += 1
                self.nums = 0
                self.Seeds = ""
                self.cate_api_index = 0
                next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1]\
                           + str(self.nums) + self.categorys[self.cate_num][1][self.cate_api_index][2]
                yield scrapy.Request(url=next_url, callback=self.parse)

