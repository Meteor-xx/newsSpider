# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from itemadapter import ItemAdapter
from newsSpider.items import  NewsSeeds


class NewsspiderPipeline:
    def process_item(self, item, spider):
        return item


class NewsSeedsPipeline(object):
    def __init__(self):
        self.file = ""

    def process_item(self, item, spider):
        if isinstance(item, NewsSeeds):
            file_url = "./news_seeds/FoxNewsSeeds_" + item["category"] + ".json"
            self.file = open(file_url, "a", encoding="utf-8")
            self.file.write(item['seeds'])
            self.file.flush()
            return item
