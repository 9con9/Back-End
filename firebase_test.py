import threading
import firebase_admin
import dangn
import joongna
import bunjang
from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import firestore
import time
import re
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
    return result



def get_data(keyword, db):
    result_dangn = get_dangn(keyword, db)
    result_bunjang = get_bunjang(keyword, db)
    result_joongna = get_joongna(keyword, db)
    result = result_dangn + result_joongna + result_bunjang
    return result


if __name__ == "__main__":
    start = time.time()  # 시작 시간 저장
    keyword = "수원 아이패드 에어4"
    cred = credentials.Certificate("../../con-635db-firebase-adminsdk-ki86d-a3e7d8b4ac.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    parsing(keyword, db)
    # result = get_data(keyword, db)
    # print(result)
    print()
    print("time :", time.time() - start)