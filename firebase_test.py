# -*- coding: utf-8 -*-
from multiprocessing import Pool

import pandas as pd
import numpy as np
import threading
import dangn
import joongna
import bunjang
import time
import re
from firebase_admin import initialize_app, delete_app, get_app
# 이모티콘 제거하기
pattern = re.compile("["
                     u"\U00010000-\U0010FFFF"  # BMP characters 이외
                     "]+", flags=re.UNICODE)


class Bun():
    def __init__(self, _input, keyword):
        self.db = _input
        self.keyword = keyword
        self.state = threading.Thread(target=bunjang.get_bunjang, args=(self.keyword, self.db,))

    def do_start(self):
        self.state.start()

    def stop(self):
        self.state.join()
        print(self.state)


class dan():
    def __init__(self, _input, keyword):
        self.db = _input
        self.keyword = keyword
        self.state = threading.Thread(target=dangn.get_dangn, args=(self.keyword, self.db,))

    def do_start(self):
        self.state.start()

    def stop(self):
        self.state.join()


class joo():
    def __init__(self, _input, keyword):
        self.db = _input
        self.keyword = keyword
        self.state = threading.Thread(target=joongna.get_joongna, args=(self.keyword, self.db,))

    def do_start(self):
        self.state.start()

    def stop(self):
        self.state.join()

#
def parsing(keyword, db):
    a_class = Bun(db, keyword)
    b_class = dan(db, keyword)
    c_class = joo(db, keyword)

    a_class.do_start()
    b_class.do_start()
    c_class.do_start()

    a_class.stop()
    b_class.stop()
    c_class.stop()




def get_bunjang(keyword, db):
    global result
    doc_ref = db.collection(u'99con').document(u'bunjang').collection(u'' + keyword).document(
        u'last_number')
    docs = doc_ref.get()
    dic_number = docs.to_dict()
    bunjang_last_number = dic_number["number"]
    print(bunjang_last_number)
    result = []
    for i in range(bunjang_last_number-1, bunjang_last_number-25, -1):
        print("번장 슈웃~")
        doc_ref = db.collection(u'99con').document(u'bunjang').collection(u'' + keyword).document(
            u'' + str(i))
        docs = doc_ref.get()
        dic_row = docs.to_dict()
        result.append(
            [dic_row["id"], dic_row["platform"], pattern.sub(r"", dic_row["name"]), dic_row["upload_time"], dic_row["address"], dic_row["price"],
                               str(dic_row["link"]), dic_row["img_link"]])
    # print(result)
    return result

def get_dangn(keyword, db):
    global result
    doc_ref = db.collection(u'99con').document(u'dangn').collection(u'' + keyword).document(
        u'last_number')
    docs = doc_ref.get()
    dic_number = docs.to_dict()
    dangn_last_number = dic_number["number"]
    print(dangn_last_number)
    result = []
    for i in range(dangn_last_number-1, dangn_last_number-19, -1):
        print("당근 슈웃~")
        doc_ref = db.collection(u'99con').document(u'dangn').collection(u'' + keyword).document(
            u'' + str(i))
        docs = doc_ref.get()
        dic_row = docs.to_dict()
        result.append(
            [dic_row["id"], dic_row["platform"], pattern.sub(r"", dic_row["name"]), dic_row["upload_time"], dic_row["address"], dic_row["price"],
                               str(dic_row["link"]), dic_row["img_link"]])
    # print(result)
    return result

def get_joongna(keyword, db):
    global result
    doc_ref = db.collection(u'99con').document(u'joongna').collection(u'' + keyword).document(
        u'last_number')
    docs = doc_ref.get()
    dic_number = docs.to_dict()
    joongna_last_number = dic_number["number"]
    print(joongna_last_number)
    result = []
    for i in range(joongna_last_number-1, joongna_last_number-25, -1):
        print("중나 슈웃~")
        doc_ref = db.collection(u'99con').document(u'joongna').collection(u'' + keyword).document(
            u'' + str(i))
        docs = doc_ref.get()
        dic_row = docs.to_dict()
        result.append(
            [dic_row["id"], dic_row["platform"], pattern.sub(r"", dic_row["name"]), dic_row["upload_time"], dic_row["address"], dic_row["price"],
                               str(dic_row["link"]), dic_row["img_link"]])
    # print(result)



# def get_data(keyword, db):
#     result_dangn = get_dangn(keyword, db)
#     result_bunjang = get_bunjang(keyword, db)
#     result_joongna = get_joongna(keyword, db)
#     result = result_dangn + result_joongna + result_bunjang
#     return result


def get_data(keyword, db):
    global result
    n = 0

    t1 = threading.Thread(target=get_joongna, args=(keyword, db,))
    t2 = threading.Thread(target=get_bunjang, args=(keyword, db,))
    t3 = threading.Thread(target=get_dangn, args=(keyword, db,))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
    result = iqr()
    return result

def iqr():
    global result
    pd.set_option('display.max_rows', None)
    col = ["id", "platform", "name", "upload_time", "address", "price", "link", "img_link"]

    df = pd.DataFrame(result, columns=col)

    temp_list = list(df["price"])
    np_temp = np.array(temp_list, dtype=np.int64)
    pd_temp = pd.Series(np_temp)
    Q3 = pd_temp.quantile(.75)
    Q1 = pd_temp.quantile(.25)
    Q2 = pd_temp.quantile(.5)
    IQR = Q3 - Q1
    if IQR > Q2:
        low_np = list(np_temp[Q1 > np_temp])
        high_np = list(np_temp[Q3 < np_temp])
    else:
        low_np = list(np_temp[Q1 - 0.2 * IQR > np_temp])
        high_np = list(np_temp[Q3 + 0.4 * IQR < np_temp])

    for i in range(len(result)):
        if int(result[i][5]) in low_np:
            result[i].append("low")
        elif int(result[i][5]) in high_np:
            result[i].append('high')
        else:
            result[i].append('normal')

    col = ["id", "platform", "name", "upload_time", "address", "price", "link", "img_link", "iqr"]
    df = pd.DataFrame(result, columns=col)
    df = df[["price", "iqr"]]
    return result

# if __name__ == "__main__":
def shut(keyword,db):
    global result
    try:
        default_app = get_app()
    except ValueError:
        default_app = initialize_app()
    start = time.time()  # 시작 시간 저장
    # keyword = "서울 아이패드 에어4"

    parsing(keyword, db)
    all = get_data(keyword, db)
    print(result)
    print()
    print("time :", time.time() - start)
    return all