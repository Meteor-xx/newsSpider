import glob
import json
import os.path
import shutil
import sys
from typing import List
import utils

def page_collection(_filename: str) -> List:
    lines = open(_filename,
                 encoding="utf-8").readlines()
    datas = [json.loads(l) for l in lines]
    page_4img_200text = 0
    page_3img_200text = 0
    page_2img_200text = 0
    pages_2img_200text = []
    pages_4img_200text = []
    pages_3img_200text = []
    for page in datas:
        page_img_num = len(page['imgs'])
        page_text_num = len(page['body'].split())
        if page_img_num >= 4 and page_text_num >= 200:
            page_4img_200text += 1
            pages_4img_200text.append(page)
        if page_img_num >= 3 and page_text_num >= 200:
            page_3img_200text += 1
            pages_3img_200text.append(page)
        if page_img_num >= 2 and page_text_num >= 200:
            page_2img_200text += 1
            pages_2img_200text.append(page)
    return pages_4img_200text


def mv_pages(_pages: List, _dst_file: str):
    files = open(_dst_file, "a", encoding="utf-8")
    for line in _pages:
        line = json.dumps(line, ensure_ascii=False) + "\n"
        files.write(line)
        files.flush()


def copy_file(_srcfile: str, _dstpath: str):  # 复制函数
    # srcfile 需要复制、移动的文件
    # dstpath 目的地址
    _srcfile = glob.glob(_srcfile)
    if not os.path.isfile(_srcfile[0]):
        print("%s not exist!" % _srcfile)
    else:
        fpath, fname = os.path.split(_srcfile[0])  # 分离文件名和路径
        if not os.path.exists(_dstpath):
            os.makedirs(_dstpath)  # 创建路径
        shutil.copy(_srcfile[0], _dstpath + fname)  # 复制文件


def mv_imgs(_pages: List, _start_path: str, _dst_path: str):  # 拿到需要转移图片的page list

    for index, page in enumerate(_pages):
        print("\r", end="")
        print("Moving imgs: {}% ".format(index/len(_pages) * 100), end="")
        sys.stdout.flush()
        imgs = page['imgs']
        if len(imgs) != 0:
            for img in imgs:
                img_id = img['id']
                srcfile = _start_path + img_id + "*"
                copy_file(srcfile, _dst_path)


def read_files():
    print(os.path.abspath("."))
    files = glob.glob("./news_seeds/FoxNewsSeeds_Sports*")
    pages = []  # page: 0:title 1:url 2:description 3:publicationDate 4: Fox_*_News
    for file_name in files:
        print(file_name[file_name.find("_", 20) + 1:file_name.find(".", 10)])
        lines = open(file_name, encoding="utf-8").readlines()
        datas = [json.loads(l) for l in lines]
        for cate in datas[:]:
            for page in cate:
                page_item = [page['title'], page['url'], page['description'], page['publicationDate']]
                pages.append(page_item)
    print(len(pages))


def read_cal_files(_file: str):
    lines = open(_file, encoding="utf-8").readlines()
    datas = [json.loads(l) for l in lines]
    page_num = len(datas)
    total_img_num = 0
    min_img_page = ""
    max_img_page = ""
    min_img_num = len(datas[0]['imgs'])
    max_img_num = len(datas[0]['imgs'])
    total_text_num = 0
    min_text_page = ""
    max_text_page = ""
    min_text_num = len(datas[0]['body'].split())
    max_text_num = len(datas[0]['body'].split())
    page_4img_200text = 0
    page_3img_200text = 0
    page_2img_200text = 0
    for page in datas:
        page_img_num = len(page['imgs'])
        page_text_num = len(page['body'].split())
        total_img_num = total_img_num + page_img_num
        total_text_num = total_text_num + page_text_num
        if page_text_num <= min_text_num:
            min_text_page = page['page_url']
            min_text_num = page_text_num
        if page_text_num >= max_text_num:
            max_text_page = page['page_url']
            max_text_num = page_text_num
        if page_img_num <= min_img_num:
            min_img_page = page['page_url']
            min_img_num = page_img_num
        if page_img_num >= max_img_num:
            max_img_page = page['page_url']
            max_img_num = page_img_num
        if page_img_num >= 4 and page_text_num >=200:
            page_4img_200text += 1
        if page_img_num >= 3 and page_text_num >=200:
            page_3img_200text += 1
        if page_img_num >= 2 and page_text_num >=200:
            page_2img_200text += 1
    avg_img_num = total_img_num / page_num
    avg_text_num = total_text_num / page_num
    print("*" * 100)
    print("Total page num: ", page_num)
    print("*" * 10)
    print("Image:")
    print("Avg image num: ", avg_img_num)
    print("Max image num: ", max_img_num)
    print("Max image page: ", max_img_page)
    print("Min image num: ", min_img_num)
    print("Min image page: ", min_img_page)
    print("*" * 10)
    print("Text:")
    print("Avg Text num: ", avg_text_num)
    print("Max Text num: ", max_text_num)
    print("Max Text page: ", max_text_page)
    print("Min Text num: ", min_text_num)
    print("Min Text page: ", min_text_page)
    print("*" * 10)
    print("Page with over 2 imgs and 200 words: ", page_2img_200text)
    print("Page with over 3 imgs and 200 words: ", page_3img_200text)
    print("Page with over 4 imgs and 200 words: ", page_4img_200text)
    print("*" * 100)


def confirm_img(_id: str) -> bool:
    dir_path = "../VOA_Meet_Media/"
    img_path = dir_path + _id + "*"
    img_exist = False
    img_file = glob.glob(img_path)
    if len(img_file) != 0:
        img_exist = True
    return img_exist


def clean_pages(_pages: List) -> List:
    pages_cleaned = []
    pages_del = []
    print("***Start cleaning***")
    for index, page in enumerate(_pages):  # read in page and rectify page with image downloaded
        if index % 100 == 0:
            print(index / 10, end="")
        if index % 10 == 0:
            print("*", end="")
        print("\r", end="")
        print("Cleaning pages: {}% ".format(index / len(_pages) * 100), end="")
        imgs = page['imgs']
        page_del = False  # 是否删除page
        for img in imgs:
            img_exist = confirm_img(img['id'])
            if not img_exist:
                page_del = True
                pages_del.append(page)
                break
        if not page_del:
            pages_cleaned.append(page)
    print("\n")
    return pages_cleaned


# 清洗page函数
# 确保page携带的image都存在
def clean(_file: str):
    # "/media/meteor/MySSD/LEGION-GTX3080-Linux/workspace/newsSpider/news/FoxNews_4imgs_200words.json"
    pages = page_collection(_file)
    print("Get ", len(pages), " pages")
    cleaned_pages = clean_pages(pages)
    print("Cleaned ", len(cleaned_pages), " pages")
    des_json = "../news/VOA_Meet_4imgs_200words_cleaned.json"
    mv_pages(cleaned_pages, des_json)
    mv_imgs(cleaned_pages, "/media/meteor/MySSD/LEGION-GTX3080-Linux/workspace/newsSpider/VOA_Meet_Media/",
            "/media/meteor/MySSD/LEGION-GTX3080-Linux/workspace/newsSpider/VOA_Meet_4imgs_200words/")
    print("\nPages saved: ", des_json)


def read_seed(_file: str):
    file = open(_file, encoding="utf-8")
    lines = file.readlines()
    # clean_seed(line)
    Conflict_num = 0
    Disaster_num = 0
    Sports_num = 0
    for l in lines:
        data = json.loads(l)
        id = data['imgs'][0]['id']
        if id.find("Fox_Sports") >= 0:
            Sports_num += 1
            continue
        if id.find("Fox_Disasters") >= 0:
            Disaster_num += 1
            continue
        if id.find("Fox_Conflicts") >= 0:
            Conflict_num += 1
            continue

    print("Conflict num:", Conflict_num)
    print("Disasters num:", Disaster_num)
    print("Sports num:", Sports_num)


def clean_seed(_data: str):
    _data = json.loads(_data)
    near_time = utils.time_format(_data[0]['time'][0])
    far_time = utils.time_format(_data[0]['time'][0])
    for page in _data:
        page_time = page['time']
        page_time = utils.time_format(page_time[0])
        if page_time > near_time:
            near_time = page_time
        if page_time < far_time:
            far_time = page_time
    print(near_time, far_time)


if __name__ == '__main__':
    # start_path = "../newsmedia/"
    # dst_path = "../FoxNews_4imgs_200words/"
    page_json = "/media/meteor/MySSD/LEGION-GTX3080-Linux/workspace/newsSpider/news/FoxNews_4imgs_200words_cleaned.json"
    # pages = page_collection(page_json)
    # mv_imgs(pages, start_path, dst_path)
    read_seed(page_json)
