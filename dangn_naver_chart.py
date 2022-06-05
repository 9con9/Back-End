from distutils.command.upload import upload
import pymysql
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import chromedriver_autoinstaller
import time
from time import sleep
import bunjang_chart as bj
import numpy as np

start = time.time()  # 시작 시간 저장
def get_data(keyword):
    count = bj.get_bunjang(keyword)-1
    count = 0
    spl = keyword.split()
    list_spl = [k for k in spl]
    naver_keyword_list = list_spl[1:]
    naver_keyword = " ".join(naver_keyword_list)
    print("나 네이버 키워드" ,naver_keyword)
    print(naver_keyword)
    count = keyword_dangn(keyword, count)
    keyword_naver(naver_keyword, count)
    remove_db()






def keyword_naver(keyword, count):
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
    print("나 클릭할고얌")

    naver_parsing(2, 12, name, address, price, link, img_link, upload_time, driver)
    start = 12
    end = 15
    plus_count = 0
    while (int(upload_time[-1][0:1]) < 8) and (upload_time[-1][2:3] != "일") or (upload_time[-1][1:2] == "시") or (upload_time[-1][2:3] == "시"):
        if plus_count == 4:
            print()
            print("나 클릭할고얌")
            print()
            driver.find_element_by_xpath('//*[@id="root"]/div[1]/section/article/button').click()
            plus_count = 0
        print("나는 일  :" ,upload_time[-1][1:2])
        print("나는 숫자 : ",upload_time[-1][0:1])
        naver_parsing(start, end, name, address, price, link, img_link, upload_time, driver)
        start = end
        end += 2
        plus_count += 1
    print("DB들어간다.")
    # DB 연결하기
    set_db("중고 나라", pattern, name, upload_time, address, price, link, img_link, count, keyword)

def naver_parsing(start, end, name, address, price, link, img_link, upload_time, driver):
    for i in range(start,end):
        print(i)
        
        address.append("None")
        ## 위치 못가져옴
        upload_time.append(driver.find_elements_by_xpath(
            '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
        print(driver.find_elements_by_xpath(
            '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
            ## 업로드시간 가져옴
        name.append(driver.find_elements_by_xpath('//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/div/a/span')[0].text)
        ## 이름 가져옴
        #upload_time.append(driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
        ## 업로드시간 가져옴
        if len(re.sub(r'[^0-9]', '', driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / p')[0].text)) == 0:
            price.append("0")
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


def keyword_dangn(keyword, count):
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
    driver.implicitly_wait(time_to_wait=5)
    driver.find_element_by_xpath("//*[@id=\"result\"]/div[1]/div[2]/span").click()
    driver.find_element_by_xpath("//*[@id=\"result\"]/div[1]/div[2]/span").click()

    driver.implicitly_wait(time_to_wait=5)

    dangn_parsing(2, 12, name, address, price, link, img_link, upload_time, driver, url)
    start = 12
    end = 22
    while (int(upload_time[-1][0:1]) < 8) and (upload_time[-1][2:3] != "일") or (upload_time[-1][1:2] == "시") or (upload_time[-1][2:3] == "시"):
        print()
        print(upload_time[-1][1:2])
        print(upload_time[-1][0:1])
        print()
        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        plus = end // 12
        print(plus)
        for i in range(plus+1):
            driver.find_element_by_xpath("//*[@id=\"result\"]/div[1]/div[2]/span").click()
        dangn_parsing(start, end, name, address, price, link, img_link, upload_time, driver, url)
        start = end
        end += 10

    print("DB들어간다.")
    # DB 연결하기
    return set_db("당근 마켓", pattern,name,  upload_time, address, price, link, img_link, count, keyword)






def dangn_parsing(start, end, name, address, price, link, img_link, upload_time, driver, url):
    

    for i in range(start, end):
        print(i)

        name.append(driver.find_elements_by_xpath(
            "//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/div/span[1]")[0].text)
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
        
    link_start = start - 2
    link_end = end - 2
    for i in range(link_start, link_end):
        print(i)
        driver.get(link[i])
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        temp_upload_time = driver.find_elements_by_xpath('//*[@id="article-category"]/time')[0].text
        if temp_upload_time[0:2] == "끌올":
            upload_time.append(temp_upload_time[3:])
        else:
            upload_time.append(temp_upload_time)



def set_db(platform, pattern,name,  upload_time, address, price, link, img_link, count, keyword):
    # DB 연결하기

    conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="condb", use_unicode=True)

    # DB 커서 만들기
    cursor = conn.cursor(pymysql.cursors.DictCursor)

  #  cursor.execute("TRUNCATE condb.usersells")

    cursor.execute('SET NAMES utf8mb4')
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")
    
    print("나는 시간")
    print(upload_time[-1][1:3])
    print(upload_time[-1][2:4])
    print("업로드타임 수정 들어간다")
    for i in range(len(upload_time)):
        if upload_time[i][1] in "시" or upload_time[i][2] in "시" or upload_time[i][1] in "분" or upload_time[i][2] in "분" or upload_time[i][1] in "초" or upload_time[i][2] in "초":
             upload_time[i] = "오늘"
    print("업로드타임 수정 끝났다")
        
    
    temp_list = price
    print(price)
    np_temp = np.array(temp_list, dtype=np.int64)
    Q3, Q1, Q2 = np.percentile(np_temp, [80, 20, 50])
    IQR = Q3 - Q1
    if IQR > Q2:
        low_np = list(np_temp[Q1 > np_temp])
        high_np = list(np_temp[Q3 < np_temp])
    else:
        low_np = list(np_temp[Q1-0.2*IQR > np_temp])
        high_np = list(np_temp[Q3+0.4*IQR < np_temp])

    # sql 문
    sql = "INSERT INTO condb.chart_usersells VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    print(count)
    # db에 sql
    for i in range(len(name)):
        if int(price[i]) in low_np:
            # cursor.execute(sql,(count + 1, platform, pattern.sub(r"", name[i]), upload_time[i], address[i], price[i], str(link[i]),img_link[i], 'low'))
            pass
        elif int(price[i]) in high_np:
            # cursor.execute(sql,(count + 1, platform, pattern.sub(r"", name[i]), upload_time[i], address[i], price[i], str(link[i]),img_link[i], 'high'))
            pass
        else:
            cursor.execute(sql,(count + 1, platform, pattern.sub(r"", name[i]), upload_time[i], address[i], price[i], str(link[i]),img_link[i], 'normal', keyword))
        print(str(count) + "번쨰 디비들어간다")
        count += 1
    print(count)
    conn.commit()
    return count

def remove_db():
    print("DB제거 들어간다")
    conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="condb", use_unicode=True)

    # DB 커서 만들기
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    for i in range(8,30):
        cursor.execute('Delete from condb.chart_usersells where upload_time = "' + str(i) + '일 전"')

    conn.commit()
    print("DB제거 끝났당")

#keyword_naver('아이폰13', 200)
print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간