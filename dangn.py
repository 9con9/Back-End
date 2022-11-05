from bs4 import BeautifulSoup
import re
from selenium import webdriver
import numpy as np
import pandas as pd
import chromedriver_autoinstaller


def get_dangn(keyword, db):
    try:
        result = []
        # 이모티콘 제거하기
        pattern = re.compile("["
                             u"\U00010000-\U0010FFFF"  # BMP characters 이외
                             "]+", flags=re.UNICODE)

        url = "https://www.daangn.com/search/" + keyword


        # 변수 초기화
        name_list, address_list, price_list, link_list, img_link_list, upload_time_list = [], [], [], [], [], []

        # 옵션 생성
        options = webdriver.ChromeOptions()
        # 창 숨기는 옵션 추가
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument("--remote-debugging-port=9222")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])


        # 셀레니움
        path = '/usr/bin/chromedriver'
        driver = webdriver.Chrome(path, options=options)
        driver.get(url)
        driver.implicitly_wait(time_to_wait=5)
        driver.find_element("xpath", "//*[@id=\"result\"]/div[1]/div[2]/span").click()
        driver.find_element("xpath", "//*[@id=\"result\"]/div[1]/div[2]/span").click()
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")

        driver.implicitly_wait(time_to_wait=5)

        items = soup.select("#flea-market-wrap")

        for i in items:
            articles = i.find_all("article")
            for art in articles:
                link_art = art.find_all(attrs={'class': 'flea-market-article-link'})
                for link in link_art:
                    href = link.attrs["href"]
                    link_list.append("https://www.daangn.com/" + href)

                    imgs = link.find('img')
                    img = imgs['src']

                    img_link_list.append(img)

                price_p = art.find_all(attrs={'class': "article-price"})
                for pr in price_p:
                    if "만원" in pr.get_text():
                        prices = re.sub(r'[^0-9]', '', pr.get_text())
                        prices = str(prices) + "0000"
                    else:
                        prices = re.sub(r'[^0-9]', '', pr.get_text())
                    if len(prices) == 0:
                        price_list.append(0)
                    else:
                        price_list.append(int(prices))

                name_s = art.find_all(attrs={'class': "article-title"})
                for name in name_s:
                    name_list.append(name.get_text().strip())

                place_p = art.find_all(attrs={'class': "article-region-name"})
                for place in place_p:
                    address_list.append(place.get_text().strip())
        try:
            doc_ref = db.collection(u'99con').document(u'dangn').collection(u'' + keyword).document(
                u'last_number')
            docs = doc_ref.get()
            dic_number = docs.to_dict()
            dangn_last_number = dic_number["number"]
            # print(dangn_last_number)
        except:
            doc_ref = db.collection(u'99con').document(u'dangn').collection(u'' + keyword).document(
                u'last_number')
            doc_ref.set({
                u'number': 0
            })
            docs = doc_ref.get()
            dic_number = docs.to_dict()
            dangn_last_number = dic_number["number"]
            # print(dangn_last_number)

        if dangn_last_number == 0:
            pass
        else:
            index = 0
            doc_ref = db.collection(u'99con').document(u'dangn').collection(u'' + keyword).document(u'' + str(dangn_last_number-1))
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

        for i in range(len(name_list)):
            driver.get(link_list[i])
            page = driver.page_source
            soup = BeautifulSoup(page, "html.parser")
            temp_upload_time = driver.find_elements("xpath",'//*[@id="article-category"]/time')[0].text
            if temp_upload_time[0:2] == "끌올":
                upload_time_list.append(temp_upload_time[3:])
            else:
                upload_time_list.append(temp_upload_time)

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
        #     low_np = list(np_temp[Q1 - 0.2 * IQR > np_temp])
        #     high_np = list(np_temp[Q3 + 0.4 * IQR < np_temp])


        index = 0
        for i in range(len(name_list)-1,-1,-1):
            print(str(index) + "번째 당근 삽입")
            doc_ref = db.collection(u'99con').document(u'dangn').collection(u'' + keyword).document(u'' + str(int(dangn_last_number) + int(index)))
            doc_ref.set({
                u'id': dangn_last_number + i,
                u'platform': "당근마켓",
                u'name': name_list[i],
                u'upload_time': upload_time_list[i],
                u'address': address_list[i],
                u'price': price_list[i],
                u'link': link_list[i],
                u'img_link': img_link_list[i],
                u'out_lier': "low"
            })
            index += 1
        doc_ref = db.collection(u'99con').document(u'dangn').collection(u'' + keyword).document(
            u'last_number')
        doc_ref.set({
            u'number' : len(name_list) + dangn_last_number
        })
        driver.quit()
    except:
        print("당근 except남 ㅅㄱ")
        pass

