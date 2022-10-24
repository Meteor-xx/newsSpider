import scrapy
from scrapy import Request
import json

# NBA https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fnba&excludeBy=tags&excludeValues=&size=11&from=300
# Tennis https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fsports%2Ftennis&excludeBy=tags&excludeValues=&size=11&from=10
# MLB https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fmlb&excludeBy=tags&excludeValues=&size=11&from=30
# Soccer https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fsoccer&excludeBy=tags&excludeValues=&size=11&from=10
# NHL https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fnhl&excludeBy=tags&excludeValues=&size=11&from=10
# Conflicts https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fconflicts&excludeBy=tags&excludeValues=&size=11&from=10
# Disasters https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fdisasters&excludeBy=tags&excludeValues=&size=11&from=10
# fires https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fdisasters%2Ffires&excludeBy=tags&excludeValues=&size=11&from=10
# earthquake https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fdisasters%2Fearthquakes&excludeBy=tags&excludeValues=&size=11&from=20
# floods https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fdisasters%2Ffloods&excludeBy=tags&excludeValues=&size=11&from=10
from newsSpider.items import NewsSeeds


class FoxnewsSpider(scrapy.Spider):
    name = 'FoxNewsSeeds'
    allowed_domains = ['www.foxnews.com']
    start_urls = ['https://www.foxnews.com/']
    categorys = [
        [["Sports"],
         [["NBA", "api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fnba&excludeBy=tags&excludeValues=&size=20&from="],
          # page 不足["Tennis", "api/article-search?searchBy=tags&values=fox-news%2Fsports%2Ftennis&excludeBy=tags&excludeValues=&size=100&from="],
          ["MLB", "api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fmlb&excludeBy=tags&excludeValues=&size=20&from="],
          ["Soccer", "api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fsoccer&excludeBy=tags&excludeValues=&size=20&from="],
          ["NHL", "api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fnhl&excludeBy=tags&excludeValues=&size=20&from="]
          ]],
        [["Disasters"],
         [
          ["Total", "api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fdisasters&excludeBy=tags&excludeValues=&size=20&from="]
         # 细分类page不足
         # [["Fires", "api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fdisasters%2Ffires&excludeBy=tags&excludeValues=&size=100&from="],
         #  ["Earthquake", "api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fdisasters%2Fearthquakes&excludeBy=tags&excludeValues=&size=100&from="],
         #  ["Floods", "api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fdisasters%2Ffloods&excludeBy=tags&excludeValues=&size=100&from="]
          ]],
        [["Conflicts"],
         [["Total", "api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fconflicts&excludeBy=tags&excludeValues=&size=20&from="]
          ]]
    ]
    next_cate = False  # 切换类别
    next_api_index = False  # 切换api_url
    cate_num = 0  # 类别
    cate_api_index = 1  # 类内index
    nums = 0  # 当前爬取数量
    Seeds = ""

    def start_requests(self):

        url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1] + str(self.nums)
        print("*****Start crawl: {}".format(url))
        yield Request(url=url, callback=self.parse)

    def parse(self, response):
        seed = response.xpath("//body/p/text()").extract()[0][1:-1]
        if self.nums != 5000:
            self.nums += 20
            seed = seed + ','  # 便于拼接
            self.Seeds = self.Seeds + seed
            next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1] + str(self.nums)
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
                next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1] + str(0)
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
                next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index][1] + str(0)
                yield scrapy.Request(url=next_url, callback=self.parse)

