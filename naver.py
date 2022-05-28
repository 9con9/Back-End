import pymysql
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import chromedriver_autoinstaller

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

    for i in range(2,30):
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
        price.append(driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / p')[0].text)
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
    conn = pymysql.connect(host="127.0.0.1", user="root", password="1234", db="condb", use_unicode=True)

    # DB 커서 만들기
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute('SET NAMES utf8mb4')
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")
    
    cursor.execute("TRUNCATE condb.naver_usersells")

    # sql 문
    sql = "INSERT INTO condb.naver_usersells VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"

    # db에 sql
    for i in range(len(name)):
       cursor.execute(sql, (i+1, '중고 나라', pattern.sub(r"",name[i]), upload_time[i], str(address[i]), price[i], str(link[i]), img_link[i]))

    conn.commit()
