import glob
import json
import os

import scrapy
from scrapy import Request

from newsSpider.items import NewsItem


def check_list_end_correct(strings):
    strings = "".join(strings).strip().replace('&nbsp', ' ').replace('\xa0', ' ').replace('\n', '').replace('​', '')
    strings = strings.replace('&quot;', '"').replace("&#39;", "'")
    return strings


class VOANewsSpider(scrapy.Spider):
    name = 'VOANews'
    allowed_domains = ['www.voanews.com']
    start_urls = ['https://www.voanews.com']
    file = glob.glob("./newsSpider/news_seeds/VOA*")
    lines = open(file[0], encoding="utf-8").readlines()
    datas = [json.loads(l) for l in lines]
    pages = []  # page: 0:title 1:url 2:description 3:time 4:page_category 5: VOA_*_News
    for cate in datas[:]:
        for page in cate:
            try:
                page_item = [page['title'][0], page['url'][0], page['description'][0], page['time'][0], "Meet"]
                pages.append(page_item)
            except Exception as e:
                continue

    def start_requests(self):
        for id, page in enumerate(self.pages):
            self.pages[id].append("VOA_" + page[4] + "_" + str(id) + "_News")
            url = self.start_urls[0] + page[1]
            print("*****Start crawl: {}".format(url))
            yield Request(url=url, callback=self.parse, meta={"DocumentID": self.pages[id][5], "Page": page})

    def parse(self, response):
        article_head = response.xpath(".//div[@class='hdr-container']")
        article_body = response.xpath(".//div[@class='body-container']")
        img_body = []
        img_num = 0
        text = []
        cover_img = article_head.xpath(".//div[@class='cover-media']")
        if len(cover_img) > 0:
            img_id = response.meta['DocumentID'] + "_" + str(img_num)
            img_body.append([cover_img.xpath("./figure"), img_id])  # 加入img_body
            img_num += 1
            text.append("<IMG " + img_id + ">")

        text_body = article_body.xpath(
                                       ".//div[@class='wsw']/span/text() |"
                                       ".//div[@class='wsw']/p/text() |"
                                       ".//div[@class='wsw']/p/strong/text() |"
                                       ".//div[@class='wsw']/p/a/text() |"
                                       ".//div[@class='wsw']/p/em/text() |"
                                       ".//div[@class='wsw']/strong/text() |"
                                       ".//div[@class='wsw']/div/figure"
        )

        for section in text_body:
            if len(section.xpath(".//img")) > 0:  # 如果是图片
                img_id = response.meta['DocumentID'] + "_" + str(img_num)
                img_body.append([section, img_id])  # 加入img_body
                img_num += 1
                text.append("<IMG " + img_id + ">")
                continue
            text.append(section.extract())
        text = check_list_end_correct(text)
        imgs = []
        for img in img_body:
            img_url = img[0].xpath(".//img/@src").extract()
            img_caption = img[0].xpath("./figcaption//span/text()").extract()
            img_caption = check_list_end_correct(img_caption)
            imgs.append({"caption": img_caption, "id": img[1], "src": img_url[0]})

        item = NewsItem()
        item['source'] = "VOA_" + response.meta['Page'][4] + "_News"
        item['title'] = check_list_end_correct(response.meta['Page'][0])
        item['body'] = text
        item['page_url'] = self.start_urls[0] + response.meta['Page'][1]
        item['page_id'] = response.meta['DocumentID']
        item['imgs'] = imgs
        yield item

