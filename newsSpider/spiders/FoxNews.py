import glob
import json
import os

import scrapy
from scrapy import Request

from newsSpider.items import NewsItem


def check_list_end_correct(strings):
    strings = "".join(strings).strip().replace('&nbsp', ' ').replace('\xa0', ' ').replace('\n', '')
    return strings


class FoxnewsSpider(scrapy.Spider):
    name = 'FoxNews'
    allowed_domains = ['foxnews.com']
    start_urls = ['http://foxnews.com/']
    files = glob.glob("./newsSpider/news_seeds/Fox*")
    pages = []  # page: 0:title 1:url 2:description 3:publicationDate 4:page_category 5: Fox_*_News
    for file_name in files:
        lines = open(file_name, encoding="utf-8").readlines()
        page_category = file_name[file_name.find("_", 20) + 1:file_name.find(".", 20)]
        datas = [json.loads(l) for l in lines]
        for cate in datas[:]:
            for page in cate:
                page_item = [page['title'], page['url'], page['description'], page['publicationDate'], page_category]
                pages.append(page_item)

    def start_requests(self):
        for id, page in enumerate(self.pages):
            self.pages[id].append("Fox_" + page[4] + "_" + str(id) + "_News")
            url = self.start_urls[0] + page[1]
            print("*****Start crawl: {}".format(url))
            yield Request(url=url, callback=self.parse, meta={"DocumentID": self.pages[id][5], "Page": page})


    def parse(self, response):
        article_body = response.xpath(".//div[@class='article-body']")
        text_body = article_body.xpath("./p/text() | ./p/a/text() | .//div[@baseimage] | .//div[@imageorig]")
        img_body = []
        img_num = 0
        text = []
        for section in text_body:
            if len(section.xpath("@baseimage | @imageorig")) > 0:  # 如果是图片
                img_id = response.meta['DocumentID'] + "_" + str(img_num)
                img_body.append([section, img_id])  # 加入img_body
                img_num += 1
                text.append("<IMG " + img_id + ">")
                continue
            text.append(section.extract())
        text = check_list_end_correct(text)
        imgs = []
        for img in img_body:
            img_url = img[0].xpath("@imageorig | @baseimage").extract()
            img_caption = img[0].xpath(".//div[@class='caption']/p/text()"
                                       " | .//div[@class='caption']/p/span/text()").extract()
            img_caption = check_list_end_correct(img_caption[0])  # img_caption[0]表示不要摄影师描述
            # imgs[x]: caption DocumentID src
            imgs.append({"caption": img_caption, "id": img[1], "src": img_url[0]})

        item = NewsItem()
        item['source'] = "FoxNews_" + response.meta['Page'][4] + "_News"
        item['title'] = response.meta['Page'][0]
        item['body'] = text
        item['page_url'] = self.start_urls[0] + response.meta['Page'][1]
        item['page_id'] = response.meta['DocumentID']
        item['imgs'] = imgs
        yield item

