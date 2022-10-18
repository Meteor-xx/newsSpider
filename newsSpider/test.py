import glob
import json

def read_cal_files():
    lines = open("/media/meteor/MySSD/LEGION-GTX3080-Linux/workspace/newsSpider/news/FoxNews.json", encoding="utf-8").readlines()
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
    for page in datas:
        page_img_num = len(page['imgs'])
        page_text_num = len(page['body'].split())
        total_img_num = total_img_num + page_img_num
        total_text_num = total_text_num + page_text_num
        if page_text_num < min_text_num:
            min_text_page = page['page_url']
            min_text_num = page_text_num
        if page_text_num > max_text_num:
            max_text_page = page['page_url']
            max_text_num = page_text_num
        if page_img_num < min_img_num:
            min_img_page = page['page_url']
            min_img_num = page_img_num
        if page_img_num > max_img_num:
            max_img_page = page['page_url']
            max_img_num = page_img_num
        if page_img_num >= 4 and page_text_num >=200:
            page_4img_200text += 1
        if page_img_num >= 3 and page_text_num >=200:
            page_3img_200text += 1
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
    print("Page with over 3 imgs and 200 words: ", page_3img_200text)
    print("Page with over 4 imgs and 200 words: ", page_4img_200text)
    print("*" * 100)


if __name__ == '__main__':
    read_cal_files()
    # lines = open("./news_seeds/FoxNewsSeeds_Sports.json", encoding="utf-8").readlines()
    # datas = [json.loads(l) for l in lines]
    # for cate in datas[:]:
    #     for page in cate:
    #         print(page['url'])

    # files = glob.glob("./news_seeds/Fox*")
    # pages = []
    # for file_name in files:
    #     lines = open(file_name, encoding="utf-8").readlines()
    #     datas = [json.loads(l) for l in lines]
    #     for cate in datas[:]:
    #         for page in cate:
    #             page_item = [page['title'], page['url'], page['description'], page['publicationDate']]
    #             pages.append(page_item)
    #
    # for i, page in enumerate(pages):
    #     print(i, page[0])
