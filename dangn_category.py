import firebase_admin
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import numpy as np
import pandas as pd
from time import sleep
from multiprocessing import Pool

start = time.time()  # 시작 시간 저장

cccc = ["디지털기기", "가구/인테리어", "유아용품", "스포츠/레저", "의류", "도서/티켓/문구", "반려동물", "미용", "콘솔게임"]
categoly = {"디지털기기": ["아이폰", "스마트워치","에어팟", "컴퓨터", "노트북", "티비", "아이패드"]
               , "가구/인테리어": ["소품","가구", "침구", "인테리어", "책상"]
               , "유아용품": ["아동복", "유아", "인형", "출산", "유아용품"]
               , "스포츠/레저": ["골프", "자전거", "테니스", "배드민턴", "탁구", "등산"]
               , "의류": ["패딩","의류", "바지", "니트", "슬렉스"]
               , "도서/티켓/문구": ["도서", "문구", "기프티콘", "상품권"]
               , "반려동물": ["사료", "강아지 용품", "고양이 용품"]
               , "미용": ["스킨로션", "메이크업", "향수"]
               , "콘솔게임": [ "XBOX", "ps5", "닌텐도 스위치"]
            }



def get_dangn(keyword, db):
    result = []
    # 이모티콘 제거하기
    pattern = re.compile("["
                         u"\U00010000-\U0010FFFF"  # BMP characters 이외
                         "]+", flags=re.UNICODE)
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

    path = '../../chromedriver'
    driver = webdriver.Chrome(path, options=options)
    driver.implicitly_wait(time_to_wait=5)


    # 변수 초기화
    end_number = 0
    name_list, address_list, price_list, link_list, img_link_list, upload_time_list = [], [], [], [], [], []

    for check in categoly:
        if keyword == check:
            end_number = int(8 // len(categoly[keyword]))+1
            break
    else:
        print("카테고리 찾지 못함")

    link_start = 0
    link_end = end_number - 1
    up_number = end_number
    up_count = link_end


    for key in categoly[keyword]:
        # 셀레니움
        print(key)
        url = "https://www.daangn.com/search/" + key

        driver.get(url)
        driver.implicitly_wait(time_to_wait=5)
        sleep(1)
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")

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
        del img_link_list[(up_count+1):]
        del price_list[(up_count+1):]
        del name_list[(up_count+1):]
        del address_list[(up_count+1):]
        del link_list[(up_count+1):]
        up_count += up_number

        for i in range(link_start , link_end+1):
            driver.get(link_list[i])
            page = driver.page_source
            soup = BeautifulSoup(page, "html.parser")
            temp_upload_time = driver.find_elements('xpath','//*[@id="article-category"]/time')[0].text
            if temp_upload_time[0:2] == "끌올":
                upload_time_list.append(temp_upload_time[3:])
            else:
                upload_time_list.append(temp_upload_time)
        print(name_list)
    if keyword == "가구/인테리어":
        keyword = "가구인테리어"
    elif keyword == "도서/티켓/문구":
        keyword = "도서티켓문구"
    elif keyword == "스포츠/레저":
        keyword = "스포츠레저"

    dangn_last_number = 0
    index = 0
    print(keyword)
    for i in range(len(name_list) - 1, -1, -1):
        print(str(index) + "번째 당근 삽입")
        doc_ref = db.collection(u'99con').document(u'dangn_category').collection(u'' + keyword).document(
            u'' + str(i))
        doc_ref.set({
            u'id': i,
            u'platform': "당근마켓",
            u'name': name_list[i],
            u'upload_time': upload_time_list[i],
            u'address': address_list[i],
            u'price': price_list[i],
            u'link': link_list[i],
            u'img_link': img_link_list[i]
        })
        index += 1
    driver.quit()