from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import numpy as np
import pandas as pd
from time import sleep

start = time.time()  # 시작 시간 저장

cccc = ["디지털기기", "가구/인테리어", "유아용품", "스포츠/레저", "의류", "도서/티켓/문구", "반려동물", "미용", "콘솔게임"]
categoly = {"디지털기기": ["스마트폰","태블릿", "스마트워치", "충전기", "이어폰", "프로젝터", "컴퓨터", "노트북", "카메라", "티비", "케이블", "pc", "공유기", "셋톱박스", "아이패드"]
               , "가구/인테리어": ["소품","가구", "침구", "인테리어", "책상"]
               , "유아용품": ["아동복", "유아", "인형", "출산", "유아용품"]
               , "스포츠/레저": ["골프", "자전거", "킥보드", "테니스", "헬스", "야구", "볼링", "배드민턴", "탁구", "농구", "당구", "등산", "트램펄린", "운동기구", "아령"]
               , "의류": ["패딩", "코트", "맨투맨", "후드티", "셔츠", "바지", "치마", "원피스", "가디건", "니트", "블라우스", "양말", "슬렉스",  "통바지", "청바지"]
               , "도서/티켓/문구": ["도서", "문구", "기프티콘", "쿠폰", "상품권", "티켓"]
               , "반려동물": ["사료", "강아지 간식", "고양이 간식", "강아지 용품", "고양이 용품"]
               , "미용": ["스킨로션", "메이크업", "향수", "네일아트", "컨실러"]
               , "콘솔게임": ["플스", "XBOX", "ps5", "닌텐도 스위치", "wii"]
            }



def get_dangn(keyword):
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
    options.add_argument("--remote-debugging-port=9222") 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    path = '/usr/bin/chromedriver'
    driver = webdriver.Chrome(path, options=options)
    driver.implicitly_wait(time_to_wait=5)

    # 변수 초기화
    end_number = 0
    name_list, address_list, price_list, link_list, img_link_list, upload_time_list = [], [], [], [], [], []

    for check in categoly:
        if keyword == check:
            end_number = int(15 // len(categoly[keyword]))+1
            break
    else:
        print("카테고리 찾지 못함")

    link_start = 0
    link_end = end_number - 1


    for key in categoly[keyword]:
        # 셀레니움
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
        del img_link_list[(link_end+1):]
        del price_list[(link_end+1):]
        del name_list[(link_end+1):]
        del address_list[(link_end+1):]
        del link_list[(link_end+1):]

        for i in range(link_start , link_end+1):
            driver.get(link_list[i])
            page = driver.page_source
            soup = BeautifulSoup(page, "html.parser")
            temp_upload_time = driver.find_elements('xpath','//*[@id="article-category"]/time')[0].text
            if temp_upload_time[0:2] == "끌올":
                upload_time_list.append(temp_upload_time[3:])
            else:
                upload_time_list.append(temp_upload_time)


    temp_list = price_list
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
        low_np = list(np_temp[Q1-0.2*IQR > np_temp])
        high_np = list(np_temp[Q3+0.4*IQR < np_temp])
        
    for i in range(len(name_list)):
        if prices in low_np:
             result.append([i + 1, '당근 마켓', pattern.sub(r"", name_list[i]), upload_time_list[i], address_list[i], price_list[i], str(link_list[i]), img_link_list[i], 'low'])
        elif prices in high_np:
             result.append([i + 1, '당근 마켓', pattern.sub(r"", name_list[i]), upload_time_list[i], address_list[i], price_list[i], str(link_list[i]), img_link_list[i], 'high'])
        else:
            result.append([i + 1, '당근 마켓', pattern.sub(r"", name_list[i]), upload_time_list[i], address_list[i], price_list[i], str(link_list[i]), img_link_list[i], 'normal'])
    driver.quit()    
    return result