import glob
import json
import os

import scrapy
from scrapy import Request

from newsSpider.items import FoxNewsItem


def check_list_end_correct(strings):
    strings = "".join(strings).strip().replace('&nbsp', ' ').replace('\xa0', ' ').replace('\n', '')
    return strings


class FoxnewsSpider(scrapy.Spider):
    name = 'FoxNews'
    allowed_domains = ['foxnews.com']
    start_urls = ['http://foxnews.com/']
    files = glob.glob("./newsSpider/news_seeds/Fox*")
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
            yield Request(url=url, callback=self.parse, meta={"DocumentID": self.pages[id][4], "Page": page})

    def parse(self, response):
        article_body = response.xpath(".//div[@class='article-body']")

        text_body = article_body.xpath("./p/text() | ./p/a/text()").extract()
        text_body = check_list_end_correct(text_body)
        img_body = article_body.xpath(".//div[@baseimage] | .//div[@imageorig]")
        imgs = []
        for index, img in enumerate(img_body):
            img_url = img.xpath("@imageorig | @baseimage").extract()
            img_caption = img.xpath(".//div[@class='caption']/p/text()"
                                    " | .//div[@class='caption']/p/span/text()").extract()
            img_caption = check_list_end_correct(img_caption[0])  # img_caption[0]表示不要摄影师描述
            # imgs[x]: caption DocumentID src
            imgs.append({"caption": img_caption, "id": response.meta['DocumentID'] + "_" + str(index), "src": img_url[0]})
        item = FoxNewsItem()
        item['title'] = response.meta['Page'][0]
        item['body'] = text_body
        item['page_url'] = self.start_urls[0] + response.meta['Page'][1]
        item['page_id'] = response.meta['DocumentID']
        item['imgs'] = imgs
        yield item

