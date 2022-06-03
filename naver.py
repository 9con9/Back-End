import pymysql
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import chromedriver_autoinstaller
import numpy as np


start = time.time()  # 시작 시간 저장
def get_naver(keyword):
    # 이모티콘 제거하기
    pattern = re.compile("["
            u"\U00010000-\U0010FFFF"  #BMP characters 이외
                               "]+", flags=re.UNICODE)

    # 변수 초기화
    name, upload_time, price, link, img_link, address = [], [], [], [], [], []

    url = "https://m.joongna.com/search-list/product?searchword=" + keyword

    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    options.add_argument("headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # 셀레니움

    driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)

    driver.implicitly_wait(time_to_wait=5)
    # 중고나라 접속
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    driver.find_element_by_xpath('//*[@id="root"]/div[1]/section/article/button').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="root"]/div[1]/section/article/button').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="root"]/div[1]/section/article/button').click()

    for i in range(2,12):
        print(i)
        temp = driver.find_elements_by_xpath(
            '//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/div/a/div/p[1]')[0].text

        if temp[-1] not in "전":
            address.append(temp)
            print(temp)
            ## 위치 가져옴

            upload_time.append(driver.find_elements_by_xpath(
                '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p[2]')[0].text)
            print(driver.find_elements_by_xpath(
                '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p[2]')[0].text)
            ## 업로드시간 가져옴
        else:
            address.append("None")
            ## 위치 못가져옴
            upload_time.append(driver.find_elements_by_xpath(
                '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
            print(driver.find_elements_by_xpath(
                '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
            ## 업로드시간 가져옴
        name.append(driver.find_elements_by_xpath('//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/div/a/span')[0].text)
        ## 이름 가져옴
        upload_time.append(driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
        ## 업로드시간 가져옴
        # price.append(driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / p')[0].text)
        
        
        if len(re.sub(r'[^0-9]', '', driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / p')[0].text)) == 0:
            price.append('0')
        else:
            price.append(re.sub(r'[^0-9]', '', driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / p')[0].text))
        
        ## 가격 가져옴
        link.append(driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / a')[0].get_attribute('href'))
        ## 해당 주소 가져옴
        try:
            img_link.append(driver.find_elements_by_xpath('//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/a/div/img')[0].get_attribute("src"))
            ## 영상 가져옴
        except:
            img_link.append(driver.find_elements_by_xpath('//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/div/a')[0].get_attribute("href"))
            ## 이미지주소 가져옴

    # DB 연결하기
    conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="condb", use_unicode=True)


    # DB 커서 만들기
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute('SET NAMES utf8mb4')
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")
    
    cursor.execute("TRUNCATE condb.naver_usersells")

    # sql 문
    sql = "INSERT INTO condb.naver_usersells VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
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
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간