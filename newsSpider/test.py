import glob
import json

if __name__ == '__main__':
    # lines = open("./news_seeds/FoxNewsSeeds_Sports.json", encoding="utf-8").readlines()
    # datas = [json.loads(l) for l in lines]
    # for cate in datas[:]:
    #     for page in cate:
    #         print(page['url'])
    files = glob.glob("./news_seeds/Fox*")
    pages = []
    for file_name in files:
        lines = open(file_name, encoding="utf-8").readlines()
        datas = [json.loads(l) for l in lines]
        for cate in datas[:]:
            for page in cate:
                page_item = [page['title'], page['url'], page['description'], page['publicationDate']]
                pages.append(page_item)

    for i, page in enumerate(pages):
        print(i, page[0])
