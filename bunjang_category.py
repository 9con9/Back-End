import firebase_admin
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import numpy as np
import pandas as pd
import re
import chromedriver_autoinstaller

category = {
    "디지털기기": [600],
    "가구/인테리어": [810],
    "유아용품": [500],
    "스포츠/레저": [700],
    "의류": [310, 320, 405],
    "도서/티켓/문구": [900],
    "반려동물": [980],
    "미용": [410],
    "콘솔게임": [600600]
}


def get_bunjang(search_keyword, db):
    result = []

    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument("--remote-debugging-port=9222") //
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    path = '/usr/bin/chromedriver'
    driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
    driver.implicitly_wait(3)

    name_list, upload_time_list, price_list, link_list, img_link_list, address_list = [], [], [], [], [], []

    for key in category[search_keyword]:
        driver.get('https://m.bunjang.co.kr/categories/' + str(key) + '?page=1' + "&req_ref=popular_category")
        sleep(1)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        items = soup.select('#root > div > div > div:nth-child(4) > div > div:nth-child(4) > div')

        for i in items:
            divs = i.find_all("div")
            for div in divs:
                href_div = div.find_all(attrs={'class': 'sc-dEoRIm iizKix'})
                link_div = div.find_all(attrs={'class': 'sc-dEoRIm iizKix'})
                img_div = div.find_all(attrs={'class': 'sc-jtggT eSpfym'})
                for link in link_div:
                    isAD = div.find_all(attrs={'class': 'sc-gmeYpB eQzNrP'})
                    AD = []
                    for ad in isAD:
                        if ad.get_text() == 'AD':
                            AD.append(ad)
                    if len(AD) == 0:
                        for hrefs in href_div:
                            href = hrefs.attrs['href']
                            link_list.append("https://bunjang.co.kr" + href)
                        for imgs in img_div:
                            img_find = imgs.find('img')
                            img = img_find['src']
                            img_link_list.append(img)
                        price_div = div.find_all(attrs={'class': "sc-kaNhvL moVyh"})
                        if len(price_div) == 0:
                            price_list.append('0')
                        else:
                            for price in price_div:
                                prices = re.sub(r'[^0-9]', '', price.get_text())
                                price_list.append(prices)
                        name_div = div.find_all(attrs={'class': "sc-jKVCRD gwleiO"})
                        for name in name_div:
                            name_list.append(name.get_text())
                        place_div = div.find_all(attrs={'class': "sc-LKuAh YRCiR"})
                        for place in place_div:
                            address_list.append(place.get_text())
                        time_div = div.find_all(attrs={'class': "sc-hzNEM jOnwQC"})
                        for time in time_div:
                            upload_time_list.append(time.get_text())
    del name_list[24:]
    del address_list[24:]
    del price_list[24:]
    del link_list[24:]
    del img_link_list[24:]
    del upload_time_list[24:]
    if search_keyword == "가구/인테리어":
        search_keyword = "가구인테리어"
    elif search_keyword == "도서/티켓/문구":
        search_keyword = "도서티켓문구"
    elif search_keyword == "스포츠/레저":
        search_keyword = "스포츠레저"
    try:
        doc_ref = db.collection(u'99con').document(u'bunjang_category').collection(u'' + search_keyword).document(
            u'last_number')
        docs = doc_ref.get()
        dic_number = docs.to_dict()
        bunjang_last_number = dic_number["number"]
        # print(bunjang_last_number)
    except:
        doc_ref = db.collection(u'99con').document(u'bunjang_category').collection(u'' + search_keyword).document(
            u'last_number')
        doc_ref.set({
            u'number': 0
        })
        docs = doc_ref.get()
        dic_number = docs.to_dict()
        bunjang_last_number = dic_number["number"]
        # print(bunjang_last_number)

    if bunjang_last_number == 0:
        pass
    else:
        index = 0
        doc_ref = db.collection(u'99con').document(u'bunjang_category').collection(u'' + search_keyword).document(
            u'' + str(bunjang_last_number - 1))
        docs = doc_ref.get()
        dic_row = docs.to_dict()
        latest_link = dic_row["link"]
        # print(latest_link)
        if latest_link in link_list:
            index = link_list.index(latest_link)
            # print(link_list)
            # print(index)
            del name_list[index:]
            del address_list[index:]
            del price_list[index:]
            del link_list[index:]
            del img_link_list[index:]
            del upload_time_list[index:]

    # temp_list = price_list
    # np_temp = np.array(temp_list, dtype=np.int64)
    # pd_temp = pd.Series(np_temp)
    # Q3 = pd_temp.quantile(.75)
    # Q1 = pd_temp.quantile(.25)
    # Q2 = pd_temp.quantile(.5)
    # IQR = Q3 - Q1
    #
    # if IQR > Q2:
    #     low_np = list(np_temp[Q1 > np_temp])
    #     high_np = list(np_temp[Q3 < np_temp])
    # else:
    #     low_np = list(np_temp[Q1-0.2*IQR > np_temp])
    #     high_np = list(np_temp[Q3+0.4*IQR < np_temp])

    print(bunjang_last_number)
    index = 0
    for i in range(len(name_list) - 1, -1, -1):
        print(str(index) + "번째 번장 삽입")
        doc_ref = db.collection(u'99con').document(u'bunjang_category').collection(u'' + search_keyword).document(
            u'' + str(int(bunjang_last_number) + int(index)))
        doc_ref.set({
            u'id': bunjang_last_number + i,
            u'platform': "번개장터",
            u'name': name_list[i],
            u'upload_time': upload_time_list[i],
            u'address': address_list[i],
            u'price': price_list[i],
            u'link': link_list[i],
            u'img_link': img_link_list[i]
        })
        index += 1
    doc_ref = db.collection(u'99con').document(u'bunjang_category').collection(u'' + search_keyword).document(
        u'last_number')
    doc_ref.set({
        u'number': len(name_list) + bunjang_last_number
    })
    driver.quit()
# from firebase_admin import db
# from firebase_admin import credentials
# from firebase_admin import firestore
# cred = credentials.Certificate("../../test-3ab4e-firebase-adminsdk-pof1a-0c12bc8c6c.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()
# get_bunjang("디지털기기", db)
