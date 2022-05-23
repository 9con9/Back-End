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

    # 셀레니움
    driver = webdriver.Chrome(chromedriver_autoinstaller.install())
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
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="root"]/div[1]/section/article/button').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="root"]/div[1]/section/article/button').click()
    time.sleep(1)

    for i in range(2,10):
        print(i)
        try:
            address.append(driver.find_elements_by_xpath('//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/div/a/div/p[2]')[0].text)
        except:
            address.append("None")
        name.append(driver.find_elements_by_xpath('//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/div/a/span')[0].text)
        upload_time.append(driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
        price.append(driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / p')[0].text)
        link.append(driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / a')[0].get_attribute('href'))
        try:
            img_link.append(driver.find_elements_by_xpath('//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/a/div/img')[0].get_attribute("src"))
        except:
            img_link.append(driver.find_elements_by_xpath('//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/div/a')[0].get_attribute("href"))

    # DB 연결하기
    conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="condb", use_unicode=True)

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