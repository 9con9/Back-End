from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
from time import sleep
import bunjang_chart as bj
import numpy as np
import pandas as pd
import chromedriver_autoinstaller

start = time.time()  # 시작 시간 저장
def get_data(keyword):
    result = []
    
    bunjang = bj.get_bunjang(keyword)
    
    spl = keyword.split()
    list_spl = [k for k in spl]
    naver_keyword_list = list_spl[1:]
    naver_keyword = " ".join(naver_keyword_list)
    # naver = keyword_joongna(naver_keyword)
    
    # dangn = keyword_dangn(keyword)
    
    # bunjang = np.array(bunjang)
    # dangn = np.array(dangn)
    # naver = np.array(naver)
    # all = list(np.concatenate((bunjang, dangn, naver)))
    # result.extend([naver, dangn, bunjang, all])
    
    return result

def keyword_joongna(search_keyword, db):
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
        driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
        driver.implicitly_wait(3)
        driver.get('https://web.joongna.com/search?keyword=' + search_keyword + '&page=1')
        sleep(1)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        items = soup.select(
            '#__next > div > div.container > div > div.ant-col.ant-col-20.css-t77d8m > div.ant-row.listWrap.css-euacx')

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
                            price_list.append(prices)
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
                                    if tim[1] in '시' or tim[2] in '시' or tim[1] in '분' or tim[2] in '분' or \
                                            tim[1] in '초' or tim[2] in '초':
                                        upload_time_list.append('오늘')
                                    else:
                                        upload_time_list.append(tim)
                                    address_list.append('None')
                                else:
                                    if flag is True:
                                        address = span.get_text()
                                        address_list.append(address)
                                        flag = False
                                    else:
                                        tim = span.get_text()
                                        if tim[1] in '시' or tim[2] in '시' or tim[1] in '분' or tim[2] in '분' or \
                                                tim[1] in '초' or tim[2] in '초':
                                            upload_time_list.append('오늘')
                                        else:
                                            upload_time_list.append(tim)

        for check in upload_time_list:
            if check == "오늘":
                pass
            elif not ((int(check[0:1]) < 8) and (check[2:3] != "일") or (check[1:2] == "시") or (check[2:3] == "시") or (check[1:2] == "분") or (check[2:3] == "분")):
                index = upload_time_list.index(check)
                del name_list[index:]
                del upload_time_list[index:]
                del price_list[index:]
                del link_list[index:]
                del img_link_list[index:]
                del address_list[index:]
                break

        try:
            doc_ref = db.collection(u'99con').document(u'joongna_chart').collection(u'' + search_keyword).document(
                u'last_number')
            docs = doc_ref.get()
            dic_number = docs.to_dict()
            bunjang_last_number = dic_number["number"]
            # print(bunjang_last_number)
        except:
            doc_ref = db.collection(u'99con').document(u'joongna_chart').collection(u'' + search_keyword).document(
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
            doc_ref = db.collection(u'99con').document(u'joongna_chart').collection(u'' + search_keyword).document(
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

        index = 0
        for i in range(len(name_list)-1, -1, -1):
            print(str(index) + "번째 중나 삽입")
            doc_ref = db.collection(u'99con').document(u'joongna_chart').collection(u'' + search_keyword).document(
                u'' + str(int(bunjang_last_number) + int(index)))
            doc_ref.set({
                u'id': bunjang_last_number + i,
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
        doc_ref = db.collection(u'99con').document(u'joongna_chart').collection(u'' + search_keyword).document(
            u'last_number')
        doc_ref.set({
            u'number': len(name_list) + bunjang_last_number
        })
        driver.quit()
    except:
        print("joongna_chart except")
        pass


def keyword_dangn(keyword, db):
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
        driver.implicitly_wait(time_to_wait=5)
        driver.get(url)
        for _ in range(8):
            driver.find_element('xpath', "//*[@id=\"result\"]/div[1]/div[2]/span").click()
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

        count = 0
        index = 0
        while count < 4 and index != len(name_list):
            driver.get(link_list[index])
            page = driver.page_source
            soup = BeautifulSoup(page, "html.parser")
            temp_upload_time = driver.find_elements("xpath",'//*[@id="article-category"]/time')[0].text
            temp_upload_time = temp_upload_time.lstrip("끌올 ")
            if not ((int(temp_upload_time[0:1]) < 8) and (temp_upload_time[2:3] != "일") or (temp_upload_time[1:2] == "시") or (temp_upload_time[2:3] == "시")):
                count += 1
            if temp_upload_time[0:2] == "끌올":
                if temp_upload_time[1] in '시' or temp_upload_time[2] in '시' or temp_upload_time[1] in '분' \
                        or temp_upload_time[2] in '분' or temp_upload_time[1] in '초' or temp_upload_time[2] in '초':
                    upload_time_list.append('오늘')
                else:
                    upload_time_list.append(temp_upload_time)
            else:
                if temp_upload_time[1] in '시' or temp_upload_time[2] in '시' or temp_upload_time[1] in '분' \
                        or temp_upload_time[2] in '분' or temp_upload_time[1] in '초' or temp_upload_time[2] in '초':
                    upload_time_list.append('오늘')
                else:
                    upload_time_list.append(temp_upload_time)
            index += 1

        if count == 4:
            del img_link_list[index:]
            del price_list[index:]
            del name_list[index:]
            del address_list[index:]
            del link_list[index:]

        index = 0

        while index != len(upload_time_list):
            if upload_time_list[index] == "오늘":
                index += 1
            elif ((upload_time_list[index][1:2] == "달") or (upload_time_list[index][2:3] == "달")):
                del name_list[index]
                del price_list[index]
                del address_list[index]
                del img_link_list[index]
                del link_list[index]
                del upload_time_list[index]
            elif not ((int(upload_time_list[index][0:1]) < 8) and (upload_time_list[index][2:3] != "일") or (upload_time_list[index][1:2] == "시") or (
                    upload_time_list[index][2:3] == "시")):
                del name_list[index]
                del price_list[index]
                del address_list[index]
                del img_link_list[index]
                del link_list[index]
                del upload_time_list[index]
            else:
                index += 1

        try:
            doc_ref = db.collection(u'99con').document(u'dangn_chart').collection(u'' + keyword).document(
                u'last_number')
            docs = doc_ref.get()
            dic_number = docs.to_dict()
            bunjang_last_number = dic_number["number"]
            # print(bunjang_last_number)
        except:
            doc_ref = db.collection(u'99con').document(u'dangn_chart').collection(u'' + keyword).document(
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
            doc_ref = db.collection(u'99con').document(u'dangn_chart').collection(u'' + keyword).document(
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

        index = 0
        for i in range(len(name_list)-1, -1, -1):
            print(str(index) + "번째 당근 삽입")
            doc_ref = db.collection(u'99con').document(u'dangn_chart').collection(u'' + keyword).document(
                u'' + str(int(bunjang_last_number) + int(index)))
            doc_ref.set({
                u'id': bunjang_last_number + i,
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
        doc_ref = db.collection(u'99con').document(u'dangn_chart').collection(u'' + keyword).document(
            u'last_number')
        doc_ref.set({
            u'number': len(name_list) + bunjang_last_number
        })
        driver.quit()
    except:
        print("dangn_chart except")
        pass
