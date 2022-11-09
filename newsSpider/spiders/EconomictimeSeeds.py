import scrapy
from scrapy import Request
import json

from newsSpider.items import NewsSeeds


def parse_res(response):
    json_res = ""
    res = response.xpath(".//div[@class='contentD']")
    for page in res:
        title = page.xpath(".//h2/text()").extract()
        description = page.xpath(".//div[@class='syn']/text()").extract()
        time = page.xpath(".//time/text()").extract()
        url = page.xpath(".//a/@href").extract()
        page_json = {
            'title': title,
            'description': description,
            'time': time,
            'url': url
        }
        json_res += json.dumps(page_json) + ','

    return json_res


class EconomictimeSpider(scrapy.Spider):
    name = 'EconomictimeSeeds'
    allowed_domains = ['economictimes.indiatimes.com']
    start_urls = ['https://economictimes.indiatimes.com/']
    categorys = [
        [["Product_launch"],
         [["PL", "lazyload_topicmore.cms?query=product%20launch&type=article&curpg=", "&pageno="],
          ]],
    ]
    next_cate = False  # 切换类别
    next_api_index = False  # 切换api_url
    cate_num = 0  # 类别
    cate_api_index = 0  # 类内index
    nums = 0  # 当前爬取数量
    Seeds = ""

    def start_requests(self):

        url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1] + str(self.nums) \
              + self.categorys[self.cate_num][1][self.cate_api_index][2] + str(self.nums)
        print("*****Start crawl: {}".format(url))
        yield Request(url=url, callback=self.parse)

    def parse(self, response):
        seed = parse_res(response)
        print(seed)
        if self.nums != 200:
            self.nums += 1
            self.Seeds = self.Seeds + seed
            next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1] + str(self.nums)\
                       + self.categorys[self.cate_num][1][self.cate_api_index][2] + str(self.nums)
            yield scrapy.Request(url=next_url, callback=self.parse)
        else:
            self.Seeds = self.Seeds + seed
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
                next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1] +\
                           str(self.nums) + self.categorys[self.cate_num][1][self.cate_api_index][2] + str(self.nums)
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
                next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1] + \
                           str(self.nums) + self.categorys[self.cate_num][1][self.cate_api_index][2] + str(self.nums)
                yield scrapy.Request(url=next_url, callback=self.parse)


