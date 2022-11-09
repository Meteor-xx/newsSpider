import glob
import json
import os

import scrapy
from scrapy import Request

from newsSpider.items import EconomictimeItem


def check_list_end_correct(strings):
    strings = "".join(strings).strip().replace('&nbsp', ' ').replace('\xa0', ' ').replace('\n', '').replace('​', '')
    return strings


class EconomictimeSpider(scrapy.Spider):
    name = 'Economictime'
    allowed_domains = ['economictimes.indiatimes.com']
    start_urls = ['https://economictimes.indiatimes.com']
    file = glob.glob("./newsSpider/news_seeds/Economic*")
    lines = open(file[0], encoding="utf-8").readlines()
    datas = [json.loads(l) for l in lines]
    pages = []  # page: 0:title 1:url 2:description 3:time 4:page_category 5: Economictime_*_News
    for cate in datas[:]:
        for page in cate:
            try:
                page_item = [page['title'][0], page['url'][0], page['description'][0], page['time'][0], "PL"]
                pages.append(page_item)
            except Exception as e:
                continue

    def start_requests(self):
        for id, page in enumerate(self.pages):
            if id <= 10:
                self.pages[id].append("Economictime_" + page[4] + "_" + str(id) + "_News")
                url = self.start_urls[0] + page[1]
                print("*****Start crawl: {}".format(url))
                yield Request(url=url, callback=self.parse, meta={"DocumentID": self.pages[id][5], "Page": page})

    def parse(self, response):
        article = response.xpath(".//article")
        article_body = response.xpath(".//div[@class='artText']")
        text_body = article.xpath(".//figure[@class='artImg'] |"
                                  ".//div[@class='artText']/text() |"
                                  ".//div[@class='artText']/a/text() |"
                                  ".//div[@class='artText']/strong/a/text() |"
                                  ".//div[@class='artText']/strong/text() |"
                                  ".//div[@class='artText']/div/figure")
        img_body = []
        img_num = 0
        text = []
        for section in text_body:
            if len(section.xpath("./img")) > 0:  # 如果是图片
                img_id = response.meta['DocumentID'] + "_" + str(img_num)
                img_body.append([section, img_id])  # 加入img_body
                img_num += 1
                text.append("<IMG " + img_id + ">")
                print("<IMG " + img_id + ">")
                continue
            text.append(section.extract())
        text = check_list_end_correct(text)
        imgs = []
        for img in img_body:
            img_url = img[0].xpath("./img/@src | ./img/@data-original").extract()
            if len(img_url) > 1:
                img_url = img_url[1]
            else:
                img_url = img_url[0]
            img_caption = img[0].xpath("./figcaption/text() | ./img/@title").extract()
            img_caption = check_list_end_correct(img_caption)  # img_caption[0]表示不要摄影师描述
            imgs.append({"caption": img_caption, "id": img[1], "src": img_url})

        item = EconomictimeItem()
        item['title'] = response.meta['Page'][0]
        item['body'] = text
        item['page_url'] = self.start_urls[0] + response.meta['Page'][1]
        item['page_id'] = response.meta['DocumentID']
        item['imgs'] = imgs
        yield item

