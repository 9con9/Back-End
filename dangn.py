import pymysql
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import chromedriver_autoinstaller



def get_dangn(keyword):
    # 이모티콘 제거하기
    pattern = re.compile("["
                         u"\U00010000-\U0010FFFF"  # BMP characters 이외
                         "]+", flags=re.UNICODE)

    url = "https://www.daangn.com/search/" + keyword
    # url = "https://www.daangn.com/search/천안%20아이패드%20에어3"

    # 변수 초기화
    name, address, price, link, img_link = [], [], [], [], []

    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    options.add_argument("headless")

    # 셀레니움

    driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
    driver.implicitly_wait(time_to_wait=5)
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    driver.find_element_by_xpath("//*[@id=\"result\"]/div[1]/div[2]/span").click()
    driver.find_element_by_xpath("//*[@id=\"result\"]/div[1]/div[2]/span").click()
    driver.implicitly_wait(time_to_wait=5)


    for i in range(2, 31):
        print(i)

        name.append(driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/div/span[1]")[0].text)
        address.append(driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[1]")[0].text.strip())
        price.append(driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[2]")[0].text.strip())
        link.append(driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a")[0].get_attribute('href'))
        img_link.append(driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[1]/img")[0].get_attribute("src"))

    # DB 연결하기

    conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="condb", use_unicode=True)

    # DB 커서 만들기
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("TRUNCATE condb.usersells")
    
    cursor.execute('SET NAMES utf8mb4')
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")
    

    # sql 문
    sql = "INSERT INTO condb.UserSells VALUES(%s, %s, %s, %s, %s, %s, %s)"

    # db에 sql
    for i in range(len(name)):
        cursor.execute(sql,
                       (i + 1, '당근 마켓', pattern.sub(r"", name[i]), address[i], price[i], str(link[i]), img_link[i]))


    conn.commit()

