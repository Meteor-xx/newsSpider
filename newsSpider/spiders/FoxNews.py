import glob
import json

import scrapy
from scrapy import Request


def check_list_end_correct(strings):
    new_strings = []

    for string in strings:
        # string = string.strip()
        # if string[-1] not in [".","?","!","\"","。","！","”","？"]:
        #
        #     if string.split(" ")[0].lower() in ["what","where","when","how","which","will","do","does","is","are","were","was"]:
        #         string += "?"
        #     else:
        #         string += "."
        new_strings.append(string)

    return new_strings


class FoxnewsSpider(scrapy.Spider):
    name = 'FoxNews'
    allowed_domains = ['foxnews.com']
    start_urls = ['http://foxnews.com/']
    files = glob.glob("./news_seeds/Fox*")
    pages = []  # page: 0:title 1:url 2:description 3:publicationDate 4: Fox_*_News
    for file_name in files:
        lines = open(file_name, encoding="utf-8").readlines()
        datas = [json.loads(l) for l in lines]
        for cate in datas[:]:
            for page in cate:
                page_item = [page['title'], page['url'], page['description'], page['publicationDate']]
                pages.append(page_item)

    def start_requests(self):
        for id, page in enumerate(self.pages[0:1]):
            self.pages[id].append("Fox_" + str(id) + "_News")
            url = self.start_urls[0] + page[1]
            print("*****Start crawl: {}".format(url))
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        body = response.xpath(".//div[@class='article-body']/p/text() "
                              "| .//div[@class='article-body']/p/a/text()").extract()
        print("*"*100)
        body = "".join(check_list_end_correct(body)).split()
        print(body)
        print("*" * 100)
        pass

