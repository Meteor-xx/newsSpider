import json
from typing import List, Dict
from newsSpider.test import read_cal_files


def div_into_cate(_pages: List) -> Dict:
    page_in_cate = {"Conflicts": [], "Sports": [], "Disasters": []}
    for page in _pages:
        page_id = page['page_id'][4:-1]
        cate = page_id[:page_id.find("_")]
        page_in_cate[cate].append(page)
    return page_in_cate


def page_with_4to8_img(_pages: List) -> List:
    pages = []
    for page in _pages:
        if len(page['imgs']) <= 8:
            pages.append(page)
    return pages


def save_txt(_page: Dict):
    page_id = _page["page_id"]
    file_name = "../news/" + page_id + ".txt"
    file_text = _page["body"]
    file = open(file_name, "a", encoding="utf-8")
    file.write(file_text)
    file.flush()
    file.close()
    print(file_name, " saved")


def choose_page(_file_path: str):
    lines = open(_file_path, encoding="utf-8").readlines()
    datas = [json.loads(l) for l in lines]
    pages_in_cate = div_into_cate(datas)
    pages_in_cate["Conflicts"] = page_with_4to8_img(pages_in_cate["Conflicts"])
    pages_in_cate["Sports"] = page_with_4to8_img(pages_in_cate["Sports"])
    pages_in_cate["Disasters"] = page_with_4to8_img(pages_in_cate["Disasters"])

    for page in pages_in_cate["Sports"][74:84]:
        # print(index,page["page_id"])
        save_txt(page)
    # for index, cate in enumerate(pages_in_cate):
    #     print("*" * 50)
    #     print(cate, " :")
    #     for page in pages_in_cate[cate][20:40]:
    #         save_txt(page)
    #     print("*" * 50)


if __name__ == '__main__':
    json_file = "../news/FoxNews_4imgs_200words_cleaned.json"
    choose_page(json_file)
