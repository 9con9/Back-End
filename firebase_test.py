# -*- coding: utf-8 -*-
from multiprocessing import Pool

import pandas as pd
import numpy as np
import threading
import dangn
import joongna
import bunjang
import bunjang_chart
import dangn_naver_chart
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
        
class Bun_chart():
    def __init__(self, _input, keyword):
        self.db = _input
        self.keyword = keyword
        self.state = threading.Thread(target=bunjang_chart.get_bunjang, args=(self.keyword, self.db,))

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

class dan_chart():
    def __init__(self, _input, keyword):
        self.db = _input
        self.keyword = keyword
        self.state = threading.Thread(target=dangn_naver_chart.keyword_dangn, args=(self.keyword, self.db,))

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

class joo_chart():
    def __init__(self, _input, keyword):
        self.db = _input
        self.keyword = keyword
        self.state = threading.Thread(target=dangn_naver_chart.keyword_joongna, args=(self.keyword, self.db,))

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
    
def parsing_chart(keyword, db):
    
    spl = keyword.split()
    list_spl = [k for k in spl]
    joongna_keyword_temp = list_spl[1:]
    joongna_keyword = " ".join(joongna_keyword_temp)
    
    a_class = Bun_chart(db, keyword)
    b_class = dan_chart(db, keyword)
    c_class = joo_chart(db, joongna_keyword)

    a_class.do_start()
    b_class.do_start()
    c_class.do_start()

    a_class.stop()
    b_class.stop()
    c_class.stop()




def get_bunjang(keyword, db):
    global result
    try:
        doc_ref = db.collection(u'99con').document(u'bunjang').collection(u'' + keyword).document(
            u'last_number')
        docs = doc_ref.get()
        dic_number = docs.to_dict()
        bunjang_last_number = dic_number["number"]
        print(bunjang_last_number)
        result = []
    except:
        return None
    for i in range(bunjang_last_number-1, bunjang_last_number-25, -1):
        try:
            print("번장 슈웃~")
            doc_ref = db.collection(u'99con').document(u'bunjang').collection(u'' + keyword).document(
                u'' + str(i))
            docs = doc_ref.get()
            dic_row = docs.to_dict()
            result.append(
                [dic_row["id"], dic_row["platform"], pattern.sub(r"", dic_row["name"]), dic_row["upload_time"], dic_row["address"], dic_row["price"],
                                   str(dic_row["link"]), dic_row["img_link"]])
        except:
            pass

    # print(result)


def get_dangn(keyword, db):
    global result
    try:
        doc_ref = db.collection(u'99con').document(u'dangn').collection(u'' + keyword).document(
            u'last_number')
        docs = doc_ref.get()
        dic_number = docs.to_dict()
        dangn_last_number = dic_number["number"]
        print(dangn_last_number)
        result = []
    except:
        return None
    for i in range(dangn_last_number-1, dangn_last_number-19, -1):
        try:
            print("당근 슈웃~")
            doc_ref = db.collection(u'99con').document(u'dangn').collection(u'' + keyword).document(
                u'' + str(i))
            docs = doc_ref.get()
            dic_row = docs.to_dict()
            result.append(
                [dic_row["id"], dic_row["platform"], pattern.sub(r"", dic_row["name"]), dic_row["upload_time"], dic_row["address"], dic_row["price"],
                                   str(dic_row["link"]), dic_row["img_link"]])
        except:
            pass
    # print(result)


def get_joongna(keyword, db):
    global result
    try:
        doc_ref = db.collection(u'99con').document(u'joongna').collection(u'' + keyword).document(
            u'last_number')
        docs = doc_ref.get()
        dic_number = docs.to_dict()
        joongna_last_number = dic_number["number"]
        print(joongna_last_number)
        result = []
    except:
        return None
    for i in range(joongna_last_number-1, joongna_last_number-25, -1):
        try:
            print("중나 슈웃~")
            doc_ref = db.collection(u'99con').document(u'joongna').collection(u'' + keyword).document(
                u'' + str(i))
            docs = doc_ref.get()
            dic_row = docs.to_dict()
            result.append(
                [dic_row["id"], dic_row["platform"], pattern.sub(r"", dic_row["name"]), dic_row["upload_time"], dic_row["address"], dic_row["price"],
                                   str(dic_row["link"]), dic_row["img_link"]])
        except:
            pass
    # print(result)

def get_bunjang_chart(keyword, db):
    global result
    try:
        doc_ref = db.collection(u'99con').document(u'bunjang_chart').collection(u'' + keyword).document(
            u'last_number')
        docs = doc_ref.get()
        dic_number = docs.to_dict()
        bunjang_last_number = dic_number["number"]
        print(bunjang_last_number)
        result = []
    except:
        return None
    for i in range(bunjang_last_number-1, bunjang_last_number-25, -1):
        try:
            print("번장 슈웃~")
            doc_ref = db.collection(u'99con').document(u'bunjang_chart').collection(u'' + keyword).document(
                u'' + str(i))
            docs = doc_ref.get()
            dic_row = docs.to_dict()
            result.append(
                [dic_row["id"], dic_row["platform"], pattern.sub(r"", dic_row["name"]), dic_row["upload_time"], dic_row["address"], dic_row["price"],
                                   str(dic_row["link"]), dic_row["img_link"]])
        except:
            pass
    # print(result)


def get_dangn_chart(keyword, db):
    global result
    try:
        doc_ref = db.collection(u'99con').document(u'dangn_chart').collection(u'' + keyword).document(
            u'last_number')
        docs = doc_ref.get()
        dic_number = docs.to_dict()
        dangn_last_number = dic_number["number"]
        print(dangn_last_number)
        result = []
    except:
        return None
    for i in range(dangn_last_number-1, dangn_last_number-19, -1):
        try:
            print("당근 슈웃~")
            doc_ref = db.collection(u'99con').document(u'dangn_chart').collection(u'' + keyword).document(
                u'' + str(i))
            docs = doc_ref.get()
            dic_row = docs.to_dict()
            result.append(
                [dic_row["id"], dic_row["platform"], pattern.sub(r"", dic_row["name"]), dic_row["upload_time"], dic_row["address"], dic_row["price"],
                                   str(dic_row["link"]), dic_row["img_link"]])
        except:
            pass

    # print(result)


def get_joongna_chart(keyword, db):
    global result
    try:
        doc_ref = db.collection(u'99con').document(u'joongna_chart').collection(u'' + keyword).document(
            u'last_number')
        docs = doc_ref.get()
        dic_number = docs.to_dict()
        joongna_last_number = dic_number["number"]
        print(joongna_last_number)
        result = []
    except:
        return None
    for i in range(joongna_last_number-1, joongna_last_number-25, -1):
        try:
            print("중나 슈웃~")
            doc_ref = db.collection(u'99con').document(u'joongna_chart').collection(u'' + keyword).document(
                u'' + str(i))
            docs = doc_ref.get()
            dic_row = docs.to_dict()
            result.append(
                [dic_row["id"], dic_row["platform"], pattern.sub(r"", dic_row["name"]), dic_row["upload_time"], dic_row["address"], dic_row["price"],
                                   str(dic_row["link"]), dic_row["img_link"]])
        except:
            pass


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

def get_chart_data(keyword, db):
    global result
    
    spl = keyword.split()
    list_spl = [k for k in spl]
    joongna_keyword_temp = list_spl[1:]
    joongna_keyword = " ".join(joongna_keyword_temp)
    
    n = 0

    t1 = threading.Thread(target=get_joongna_chart, args=(joongna_keyword, db,))
    t2 = threading.Thread(target=get_bunjang_chart, args=(keyword, db,))
    t3 = threading.Thread(target=get_dangn_chart, args=(keyword, db,))

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

    # col = ["id", "platform", "name", "upload_time", "address", "price", "link", "img_link", "iqr"]
    # df = pd.DataFrame(result, columns=col)
    # df = df[["price", "iqr"]]
    return result

def del_iqr_time(all):
    
    all_df = pd.DataFrame(all)
    low_index = all_df[all_df[8].str.contains('low')].index
    high_index = all_df[all_df[8].str.contains('high')].index
    normal_df = all_df.drop(low_index)
    normal_df = normal_df.drop(high_index)
    
    year_index = normal_df[normal_df[3].str.contains('년')].index
    month_index = normal_df[normal_df[3].str.contains('달')].index
    week_index = normal_df[normal_df[3].str.contains('주')].index
    normal_df = normal_df.drop(year_index)
    normal_df = normal_df.drop(month_index)
    normal_df = normal_df.drop(week_index)
    
    result = normal_df.values.tolist()
    
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
    # print(result)
    print()
    print("time :", time.time() - start)
    return all

def shut_chart(keyword,db):
    global result
    try:
        default_app = get_app()
    except ValueError:
        default_app = initialize_app()
    start = time.time()  # 시작 시간 저장
    # keyword = "서울 아이패드 에어4"

    parsing_chart(keyword, db)
    all = get_chart_data(keyword, db)
    try:
        all = del_iqr_time(all)
    except:
        print("del_iqr except")
    # print(result)
    print()
    print("time :", time.time() - start)
    return all