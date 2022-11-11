# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os.path
import re

from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline

from newsSpider.items import NewsSeeds, NewsItem


class NewsspiderPipeline:
    def process_item(self, item, spider):
        return item


class NewsPipeline(object):
    def __init__(self):
        self.file = ""

    def process_item(self, item, spider):
        if isinstance(item, NewsItem):
            line = json.dumps(dict(item), ensure_ascii=False) + "\n"
            file_url = "./news/" + item["source"] + ".json"
            self.file = open(file_url, "a", encoding="utf-8")
            self.file.write(line)
            self.file.flush()
            self.file.close()
            return item  # 若pipeline较多，则需要return item，否则下一个pipeline接收到的为None


class NewsSeedsPipeline(object):
    def __init__(self):
        self.file = ""

    def process_item(self, item, spider):
        if isinstance(item, NewsSeeds):
            file_url = "./newsSpider/news_seeds/" + item["category"] + ".json"  # 更改时修改前缀
            self.file = open(file_url, "a", encoding="utf-8")
            self.file.write(item['seeds'])
            self.file.flush()
            self.file.close()
            return item


class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        # 下载图片，如果传过来的是集合需要循环下载
        # meta里面的数据是从spider获取，然后通过meta传递给下面方法：file_path
        if isinstance(item, NewsItem):
            imgs = item["imgs"]
            for img in imgs:
                yield Request(url=img['src'], meta={'name': img['id']})

    # def item_completed(self, results, item, info):
    #     # 是一个元组，第一个元素是布尔值表示是否成功
    #     if not results[0][0]:
    #         print("下载失败:"+item)
    #     return item

    # 重命名，若不重写这函数，图片名为哈希，就是一串乱七八糟的名字
    def file_path(self, request, response=None, info=None):
        # 接收上面meta传递过来的图片名称
        name = request.meta['name']
        # 提取url 图像后缀
        image_name = request.url.split('.')[-1]

        if ".gif" in request.url:
            image_name = "gif"
        elif ".png" in request.url:
            image_name = "png"
        elif ".jpg" in request.url:
            image_name = "jpg"

        if image_name not in ["jpg", "png", "gif"]:
            image_name = "jpg"
        # 清洗Windows系统的文件夹非法字符，避免无法创建目录
        folder_strip = re.sub(r'[？\\*|“<>:/]', '', str(name))
        # 分文件夹存储的关键：{0}对应着name；{1}对应着image_guid
        filename = u'{0}.{1}'.format(folder_strip, image_name)
        return filename
