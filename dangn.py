# import pymysql
# import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import chromedriver_autoinstaller
import numpy as np

start = time.time()  # 시작 시간 저장


def get_dangn(keyword):
    result = []
    # 이모티콘 제거하기
    pattern = re.compile("["
                         u"\U00010000-\U0010FFFF"  # BMP characters 이외
                         "]+", flags=re.UNICODE)

    url = "https://www.daangn.com/search/" + keyword
    # url = "https://www.daangn.com/search/천안%20아이패드%20에어3"

    # 변수 초기화
    name_list, address_list, price_list, link_list, img_link_list, upload_time_list = [], [], [], [], [], []

    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    options.add_argument("headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # 셀레니움

    driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
    driver.implicitly_wait(time_to_wait=5)
    driver.get(url)
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
                prices = re.sub(r'[^0-9]', '', pr.get_text())
                print(prices)
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

    # start = time.time()  # 시작 시간 저장
    # for link in link_list:
    #     driver.get(link)
    #     page = driver.page_source
    #     soup = BeautifulSoup(page, "html.parser")
    #     upload = soup.select_one("#article-category > time").text.strip()
    #     upload_time_list.append(upload)
    # print("time :", time.time() - start)

    start = time.time()  # 시작 시간 저장
    for i in range(len(name_list)):
        driver.get(link_list[i])
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        temp_upload_time = driver.find_elements("xpath",'//*[@id="article-category"]/time')[0].text
        if temp_upload_time[0:2] == "끌올":
            upload_time_list.append(temp_upload_time[3:])
        else:
            upload_time_list.append(temp_upload_time)
        print(temp_upload_time)
    print("time :", time.time() - start)

    temp_list = price_list
    np_temp = np.array(temp_list, dtype=np.int64)
    Q3, Q1, Q2 = np.percentile(np_temp, [75, 25, 50])
    IQR = Q3 - Q1
    if IQR > Q2:
        low_np = list(np_temp[Q1 > np_temp])
        high_np = list(np_temp[Q3 < np_temp])
    else:
        low_np = list(np_temp[Q1 - 0.2 * IQR > np_temp])
        high_np = list(np_temp[Q3 + 0.4 * IQR < np_temp])

    for i in range(len(name_list)):
        if int(price_list[i]) in low_np:
            result.append([i + 1, '당근 마켓', pattern.sub(r"", name_list[i]), upload_time_list[i], address_list[i], price_list[i],
                           str(link_list[i]), img_link_list[i], 'low'])
        elif int(price_list[i]) in high_np:
            result.append([i + 1, '당근 마켓', pattern.sub(r"", name_list[i]), upload_time_list[i], address_list[i], price_list[i],
                           str(link_list[i]), img_link_list[i], 'high'])
        else:
            result.append([i + 1, '당근 마켓', pattern.sub(r"", name_list[i]), upload_time_list[i], address_list[i], price_list[i],
                           str(link_list[i]), img_link_list[i], 'normal'])
            #result.append([i + 1, '당근 마켓', pattern.sub(r"", name[i]), upload_time_list[i], address_list[i], price_list[i],
                          # str(link[i]), img_link_list[i], 'normal'])
    return result
    # conn.commit()
    print("time :", time.time() - start)