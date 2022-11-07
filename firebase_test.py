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
    location_list = ['서울', '종로', '중구', '용산', '성동', '광진', '동대문', '중랑', '성북', '강북', '도봉', '노원', '은평', '서대문', '마포', '양천',
                     '강서', '구로', '금천', '영등포', '동작', '관악', '서초', '강남', '송파', '강동', '경기', '수원', '고양', '용인', '성남', '부천',
                     '화성', '안산', '남양주', '안양', '평택', '시흥', '파주', '의정부', '김포', '광주', '광명', '군포', '하남', '오산', '양주', '이천',
                     '구리', '안성', '포천', '의왕', '양평', '여주', '동두천', '가평', '과천', '연천', '대구', '중구', '동구', '서구', '남구', '북구',
                     '수성', '달서', '달성', '광주', '동구', '서구', '남구', '북구', '광산', '울산', '중구', '남구', '동구', '북구', '울주', '충북',
                     '충청', '충청북도', '청주', '충주', '제천', '보은', '옥천', '영동', '증평', '진천', '괴산', '음성', '단양', '전라북도', '전북', '전주',
                     '군산', '익산', '정읍', '남원', '김제', '완주', '진안', '무주', '장수', '임실', '순창', '고창', '부안', '경상북도', '경북', '포항',
                     '경주', '김천', '안동', '구미', '영주', '영천', '상주', '문경', '경산', '군위', '의성', '청송', '영양', '영덕', '청도', '고령',
                     '성주', '칠곡', '예천', '봉화', '울진', '울릉', '제주', '서귀포시', '부산', '중구', '서구', '동구', '영도', '부산진', '동래', '해운대',
                     '사하', '금정', '강서', '연제', '수영', '사상', '기장', '인천', '중구', '동구', '미추홀', '연수', '남동', '부평', '계양', '서구',
                     '강화', '옹진', '대전', '동구', '중구', '서구', '유성', '대덕', '세종', '강원', '춘천', '원주', '강릉', '동해', '태백', '속초',
                     '삼척', '홍천', '횡성', '영월', '평창', '정선', '철원', '화천', '양구', '인제', '고성', '양양', '충남', '충청남도', '천안', '공주',
                     '보령', '아산', '서산', '논산', '계룡', '당진', '금산', '부여', '서천', '청양', '홍성', '예산', '태안', '전남', '전라남도', '목포',
                     '여수', '순천', '나주', '광양', '담양', '곡성', '구례', '고흥', '보성', '화순', '장흥', '강진', '해남', '영암', '무안', '함평',
                     '영광', '장성', '완도', '진도', '신안', '경남', '경상남도', '창원', '진주', '통영', '사천', '김해', '밀양', '거제', '양산', '의령',
                     '함안', '창녕', '고성', '남해', '하동', '산청', '함양', '거창', '합천']
    spl = keyword.split()
    list_spl = [k for k in spl]
    temp = list_spl[0:1]
    temp2 = list_spl[1:]
    location_string = " ".join(temp)
    keyword_string = " ".join(temp2)
    if location_string in location_list:
        joongna_keyword = keyword_string
    else:
        joongna_keyword = keyword
    a_class = Bun(db, keyword)
    b_class = dan(db, keyword)
    c_class = joo(db, joongna_keyword)


    a_class.do_start()
    b_class.do_start()
    c_class.do_start()

    a_class.stop()
    b_class.stop()
    c_class.stop()
    
def parsing_chart(keyword, db):
    location_list = ['서울', '종로', '중구', '용산', '성동', '광진', '동대문', '중랑', '성북', '강북', '도봉', '노원', '은평', '서대문', '마포', '양천',
                     '강서', '구로', '금천', '영등포', '동작', '관악', '서초', '강남', '송파', '강동', '경기', '수원', '고양', '용인', '성남', '부천',
                     '화성', '안산', '남양주', '안양', '평택', '시흥', '파주', '의정부', '김포', '광주', '광명', '군포', '하남', '오산', '양주', '이천',
                     '구리', '안성', '포천', '의왕', '양평', '여주', '동두천', '가평', '과천', '연천', '대구', '중구', '동구', '서구', '남구', '북구',
                     '수성', '달서', '달성', '광주', '동구', '서구', '남구', '북구', '광산', '울산', '중구', '남구', '동구', '북구', '울주', '충북',
                     '충청', '충청북도', '청주', '충주', '제천', '보은', '옥천', '영동', '증평', '진천', '괴산', '음성', '단양', '전라북도', '전북', '전주',
                     '군산', '익산', '정읍', '남원', '김제', '완주', '진안', '무주', '장수', '임실', '순창', '고창', '부안', '경상북도', '경북', '포항',
                     '경주', '김천', '안동', '구미', '영주', '영천', '상주', '문경', '경산', '군위', '의성', '청송', '영양', '영덕', '청도', '고령',
                     '성주', '칠곡', '예천', '봉화', '울진', '울릉', '제주', '서귀포시', '부산', '중구', '서구', '동구', '영도', '부산진', '동래', '해운대',
                     '사하', '금정', '강서', '연제', '수영', '사상', '기장', '인천', '중구', '동구', '미추홀', '연수', '남동', '부평', '계양', '서구',
                     '강화', '옹진', '대전', '동구', '중구', '서구', '유성', '대덕', '세종', '강원', '춘천', '원주', '강릉', '동해', '태백', '속초',
                     '삼척', '홍천', '횡성', '영월', '평창', '정선', '철원', '화천', '양구', '인제', '고성', '양양', '충남', '충청남도', '천안', '공주',
                     '보령', '아산', '서산', '논산', '계룡', '당진', '금산', '부여', '서천', '청양', '홍성', '예산', '태안', '전남', '전라남도', '목포',
                     '여수', '순천', '나주', '광양', '담양', '곡성', '구례', '고흥', '보성', '화순', '장흥', '강진', '해남', '영암', '무안', '함평',
                     '영광', '장성', '완도', '진도', '신안', '경남', '경상남도', '창원', '진주', '통영', '사천', '김해', '밀양', '거제', '양산', '의령',
                     '함안', '창녕', '고성', '남해', '하동', '산청', '함양', '거창', '합천']
    spl = keyword.split()
    list_spl = [k for k in spl]
    temp = list_spl[0:1]
    temp2 = list_spl[1:]
    location_string = " ".join(temp)
    keyword_string = " ".join(temp2)
    if location_string in location_list:
        joongna_keyword = keyword_string
    else:
        joongna_keyword = keyword
    
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
    try:
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
    except:
        print("iqr except")
        return None

def del_iqr_time(all):
    try:
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
    except:
        print("del_iqr_time except")
        return None

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