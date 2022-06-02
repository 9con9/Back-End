import pymysql
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import chromedriver_autoinstaller
import time
from time import sleep

start = time.time()  # 시작 시간 저장
def get_data(keyword):
    spl = keyword.split()
    list_spl = [k for k in spl]
    naver_keyword_list = list_spl[1:]
    naver_keyword = " ".join(naver_keyword_list)
    print(naver_keyword)
    count = 0
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

    naver_parsing(2, 12, name, address, price, link, img_link, upload_time, driver)
    start = 12
    end = 15
    plus_count = 0
    while (int(upload_time[-1][0:1]) < 8) and (upload_time[-1][2:3] != "일") or (upload_time[-1][1:2] == "시") or (upload_time[-1][2:3] == "시"):
        if plus_count == 5:
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
    set_db("중고 나라", pattern, name, upload_time, address, price, link, img_link, count)

def naver_parsing(start, end, name, address, price, link, img_link, upload_time, driver):
    for i in range(start,end):
        print(i)
        temp = driver.find_elements_by_xpath(
            '//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/div/a/div/p[1]')[0].text

        if temp[-1] not in "전":
            address.append(temp)
            print(temp)\
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
        #upload_time.append(driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
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

    driver = webdriver.Chrome(chromedriver_autoinstaller.install())#, options=options)
    driver.implicitly_wait(time_to_wait=5)
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
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

        dangn_parsing(start, end, name, address, price, link, img_link, upload_time, driver, url)
        start = end
        end += 10


    print("DB들어간다.")
    # DB 연결하기
    return set_db("당근 마켓", pattern,name,  upload_time, address, price, link, img_link, count)






def dangn_parsing(start, end, name, address, price, link, img_link, upload_time, driver, url):
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    plus = end // 12
    print(plus)
    for i in range(plus+1):
        driver.find_element_by_xpath("//*[@id=\"result\"]/div[1]/div[2]/span").click()


    for i in range(start, end):
        print(i)

        name.append(driver.find_elements_by_xpath(
            "//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/div/span[1]")[0].text)
        address.append(
            driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[1]")[
                0].text.strip())
        price.append(
            driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[2]")[
                0].text.strip())
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



def set_db(platform, pattern,name,  upload_time, address, price, link, img_link, count):
    # DB 연결하기

    conn = pymysql.connect(host="127.0.0.1", user="root", password="1234", db="condb", use_unicode=True)

    # DB 커서 만들기
    cursor = conn.cursor(pymysql.cursors.DictCursor)

  #  cursor.execute("TRUNCATE condb.usersells")

    cursor.execute('SET NAMES utf8mb4')
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")



    # sql 문
    sql = "INSERT INTO condb.chart_usersells VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
    print(count)
    # db에 sql
    for i in range(len(name)):
        cursor.execute(sql,
                       (count + 1, platform, pattern.sub(r"", name[i]), upload_time[i], address[i], price[i], str(link[i]),
                        img_link[i]))
        print(str(count) + "번쨰 디비들어간다")
        count += 1
    print(count)
    conn.commit()
    return count

def remove_db():
    print("DB제거 들어간다")
    conn = pymysql.connect(host="127.0.0.1", user="root", password="1234", db="condb", use_unicode=True)

    # DB 커서 만들기
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    for i in range(8,30):
        cursor.execute('Delete from condb.chart_usersells where upload_time = "' + str(i) + '일 전"')

    conn.commit()
    print("DB제거 끝났당")



get_data("천안 아이패드 에어")
print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간