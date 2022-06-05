import pymysql
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import chromedriver_autoinstaller
import numpy as np

start = time.time()  # 시작 시간 저장
def get_dangn(keyword):
    # 이모티콘 제거하기
    pattern = re.compile("["
                         u"\U00010000-\U0010FFFF"  # BMP characters 이외
                         "]+", flags=re.UNICODE)

    url = "https://www.daangn.com/search/" + keyword
    # url = "https://www.daangn.com/search/천안%20아이패드%20에어3"

    # 변수 초기화
    name, address, price, link, img_link, upload_time = [], [], [], [], [], []

    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    options.add_argument("headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # 셀레니움

    driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
    driver.implicitly_wait(time_to_wait=5)
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    driver.find_element_by_xpath("//*[@id=\"result\"]/div[1]/div[2]/span").click()
    driver.find_element_by_xpath("//*[@id=\"result\"]/div[1]/div[2]/span").click()
    driver.implicitly_wait(time_to_wait=5)

    for i in range(2, 13):
        print(i)

        name.append(
            driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/div/span[1]")[
                0].text)
        address.append(
            driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[1]")[
                0].text.strip())
        
        if len(re.sub(r'[^0-9]', '', driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[2]")[
                0].text.strip())) == 0:
            price.append('0')
        else:
            price.append(re.sub(r'[^0-9]', '', driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[2]")[
                0].text.strip()))
            
        link.append(
            driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a")[0].get_attribute(
                'href'))
        img_link.append(
            driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[1]/img")[
                0].get_attribute("src"))

    for i in range(len(name)):
        driver.get(link[i])
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        temp_upload_time = driver.find_elements_by_xpath('//*[@id="article-category"]/time')[0].text
        if temp_upload_time[0:2] == "끌올":
            upload_time.append(temp_upload_time[3:])
        else:
            upload_time.append(temp_upload_time)

    print(upload_time)
    # DB 연결하기

    conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="condb", use_unicode=True)

    # DB 커서 만들기
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("TRUNCATE condb.daagun")

    cursor.execute('SET NAMES utf8mb4')
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")

    # sql 문
    sql = "INSERT INTO condb.daagun VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    temp_list = price
    np_temp = np.array(temp_list, dtype=np.int64)
    Q3, Q1, Q2 = np.percentile(np_temp, [80, 20, 50])
    IQR = Q3 - Q1
    if IQR > Q2:
        low_np = list(np_temp[Q1 > np_temp])
        high_np = list(np_temp[Q3 < np_temp])
    else:
        low_np = list(np_temp[Q1-0.2*IQR > np_temp])
        high_np = list(np_temp[Q3+0.4*IQR < np_temp])

    # db에 sql
    for i in range(len(name)):
        if int(price[i]) in low_np:
            cursor.execute(sql,(i + 1, '당근 마켓', pattern.sub(r"", name[i]), upload_time[i], address[i], price[i], str(link[i]),img_link[i], 'low'))
        elif int(price[i]) in high_np:
            cursor.execute(sql,(i + 1, '당근 마켓', pattern.sub(r"", name[i]), upload_time[i], address[i], price[i], str(link[i]),img_link[i], 'high'))
        else:
            cursor.execute(sql,(i + 1, '당근 마켓', pattern.sub(r"", name[i]), upload_time[i], address[i], price[i], str(link[i]),img_link[i], 'normal'))

    conn.commit()
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간s