import scrapy
from scrapy import Request
import json

# NBA https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fnba&excludeBy=tags&excludeValues=&size=11&from=300
# Tennis https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fsports%2Ftennis&excludeBy=tags&excludeValues=&size=11&from=10
# MLB https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fmlb&excludeBy=tags&excludeValues=&size=11&from=30
# Disasters https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fdisasters&excludeBy=tags&excludeValues=&size=11&from=10
# Conflicts https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fconflicts&excludeBy=tags&excludeValues=&size=11&from=10
from newsSpider.items import NewsSeeds


class FoxnewsSpider(scrapy.Spider):
    name = 'FoxNewsSeeds'
    allowed_domains = ['www.foxnews.com']
    start_urls = ['https://www.foxnews.com/']
    categorys = [
        [["Sports"],
         ["api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fnba&excludeBy=tags&excludeValues=&size=10&from=",
        "api/article-search?searchBy=tags&values=fox-news%2Fsports%2Ftennis&excludeBy=tags&excludeValues=&size=10&from=",
        "api/article-search?searchBy=tags&values=fox-news%2Fsports%2Fmlb&excludeBy=tags&excludeValues=&size=10&from="
          ]],
        [["Disasters"],
         ["api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fdisasters&excludeBy=tags&excludeValues=&size=10&from="
          ]],
        [["Conflicts"],
         ["api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fconflicts&excludeBy=tags&excludeValues=&size=10&from="
          ]]
    ]
    next_cate = False  # 切换类别
    next_api_index = False  # 切换api_url
    cate_num = 1  # 类别
    cate_api_index = 0  # 类内index
    nums = 0  # 当前爬取数量
    Seeds = ""

    def start_requests(self):

        url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index] + str(self.nums)
        print("*****Start crawl: {}".format(url))
        yield Request(url=url, callback=self.parse)

    def parse(self, response):
        seed = response.xpath("//body/p/text()").extract()[0][1:-1]
        if self.nums != 1000:
            self.nums += 10
            seed = seed + ','  # 便于拼接
            self.Seeds = self.Seeds + seed
            next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index] + str(self.nums)
            yield scrapy.Request(url=next_url, callback=self.parse)
        else:
            self.Seeds = self.Seeds + seed
            item = NewsSeeds()
            item["seeds"] = "[" + self.Seeds + "]\r\n"
            item["category"] = self.categorys[self.cate_num][0][0]  # 当前类别名
            self.next_api_index = True  # 切换api
            yield item
        if self.next_api_index:  # 切换分类下api
            self.next_api_index = False
            if self.cate_api_index < (len(self.categorys[self.cate_num][1]) - 1):  # 需要切换api并且判断是否是该分类下最后一个api
                self.cate_api_index += 1
                self.nums = 0
                self.Seeds = ""
                next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index] + str(0)
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
                next_url = self.start_urls[0] + self.categorys[self.cate_num][1][self.cate_api_index] + str(0)
                yield scrapy.Request(url=next_url, callback=self.parse)

