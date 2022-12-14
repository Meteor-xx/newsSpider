# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NewsItem(scrapy.Item):
    source = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    page_url = scrapy.Field()
    page_id = scrapy.Field()
    imgs = scrapy.Field()


class NewsSeeds(scrapy.Item):
    seeds = scrapy.Field()
    category = scrapy.Field()