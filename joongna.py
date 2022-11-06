import firebase_admin
from selenium import webdriver
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import re
import numpy as np
import pandas as pd
from time import sleep
from geopy.geocoders import Nominatim
# from firebase_admin import db
# from firebase_admin import credentials
# from firebase_admin import firestore
import chromedriver_autoinstaller
#
#
# cred = credentials.Certificate("../../con-635db-firebase-adminsdk-ki86d-a3e7d8b4ac.json")
# firebase_admin.initialize_app(cred)
#
# db = firestore.client()

def get_joongna(search_keyword, db):
    try:
        result = []


        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument("--remote-debugging-port=9222")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        path = '/usr/bin/chromedriver'
        driver = webdriver.Chrome(path, options=options)
        # driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
        # driver.get('https://web.joongna.com/search?keyword=' +search_keyword)
        driver.implicitly_wait(3)
        sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        items = soup.select('#__next > div > div.container > div > div.ant-col.ant-col-20.css-t77d8m > div.ant-row.listWrap.css-euacx')

        name_list, upload_time_list, price_list, link_list, img_link_list, address_list = [], [], [], [], [], []
        for i in items:
            divs = i.find_all("div")
            for div in divs:
                link_div = div.find_all(attrs={'class': 'css-8rmnao'})
                for link in link_div:
                    href = link.attrs['href']
                    link_list.append('https://web.joongna.com' + href)
                    second_div = link.find_all(attrs={'class': 'css-17j97b9'})
                    for second in second_div:
                        third_div = second.find_all(attrs={'class': 'css-jib2h7'})
                        for third in third_div:
                            imgs = third.find('img')
                            img = imgs['src']
                            img_link_list.append(img)
                        price_div = second.find_all(attrs={'class': 'priceTxt'})
                        for price in price_div:
                            prices = re.sub(r'[^0-9]', '', price.get_text())
                            if len(prices) == 0:
                                price_list.append(0)
                            else:
                                price_list.append(int(prices))
                        title_div = second.find_all(attrs={'class': 'titleTxt'})
                        for title in title_div:
                            name_list.append(title.get_text())
                        time_div = second.find_all(attrs={'class': 'registInfo'})
                        for time in time_div:
                            spans = time.find_all('span')
                            flag = True
                            for span in spans:
                                if len(time) == 1:
                                    tim = span.get_text()
                                    upload_time_list.append(tim)
                                    address_list.append('None')
                                else:
                                    if flag is True:
                                        address = span.get_text()
                                        address_list.append(address)
                                        flag = False
                                    else:
                                        tim = span.get_text()
                                        upload_time_list.append(tim)

        del name_list[24:]
        del address_list[24:]
        del price_list[24:]
        del link_list[24:]
        del img_link_list[24:]
        del upload_time_list[24:]

        try:
            doc_ref = db.collection(u'99con').document(u'joongna').collection(u'' + search_keyword).document(
                u'last_number')
            docs = doc_ref.get()
            dic_number = docs.to_dict()
            joongna_last_number = dic_number["number"]
            # print(joongna_last_number)
        except:
            doc_ref = db.collection(u'99con').document(u'joongna').collection(u'' + search_keyword).document(
                u'last_number')
            doc_ref.set({
                u'number': 0
            })
            docs = doc_ref.get()
            dic_number = docs.to_dict()
            joongna_last_number = dic_number["number"]
            # print(joongna_last_number)

        if joongna_last_number == 0:
            pass
        else:
            index = 0
            doc_ref = db.collection(u'99con').document(u'joongna').collection(u'' + search_keyword).document(
                u'' + str(joongna_last_number - 1))
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
        # if IQR > Q2:
        #     low_np = list(np_temp[Q1 > np_temp])
        #     high_np = list(np_temp[Q3 < np_temp])
        # else:
        #     low_np = list(np_temp[Q1-0.2*IQR > np_temp])
        #     high_np = list(np_temp[Q3+0.4*IQR < np_temp])


        index = 0
        for i in range(len(name_list)-1, -1, -1):
            print(str(index) + "번째 중나 삽입")
            doc_ref = db.collection(u'99con').document(u'joongna').collection(u'' + search_keyword).document(
                u'' + str(int(joongna_last_number) + int(index)))
            doc_ref.set({
                u'id': joongna_last_number + i,
                u'platform': "중고나라",
                u'name': name_list[i],
                u'upload_time': upload_time_list[i],
                u'address': address_list[i],
                u'price': price_list[i],
                u'link': link_list[i],
                u'img_link': img_link_list[i],
                u'out_lier': "low"
            })
            index += 1
        doc_ref = db.collection(u'99con').document(u'joongna').collection(u'' + search_keyword).document(
            u'last_number')
        doc_ref.set({
            u'number': len(name_list) + joongna_last_number
        })

        driver.quit()
    except:
        print("joongna except")
        pass
