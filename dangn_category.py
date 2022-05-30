import pymysql
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import chromedriver_autoinstaller


categoly = {"디지털기기": ["스마트폰","태블릿", "스마트워치", "케이스", "케이블", "충전기", "이어폰", "프로젝터", "프린터", "pc", "데스크탑", "노트북", "카메라", "스피커", "티비", "냉장고"]
               , "가구/인테리어": ["소품", "꽃", "수공예품",  "침실가구",  "거실가구",  "침구"]
               , "유아용품": ["남아의류", "여아의류", "유아교육", "인형", "출산", "유아용품"]
               , "스포츠/레저": ["골프", "캠핑", "낚시", "축구", "자전거", "스케이트", "킥보드", "테니스", "등산", "헬스", "요가", "야구", "볼링", "배드민턴", "탁구", "농구", "당구"]
               , "의류" : ["패딩", "코트", "맨투맨", "후드티", "티셔츠", "블라우스", "셔츠", "바지", "청바지", "반바지", "치마", "원피스", "가디건", "니트", "자켓", "정장", "조끼", "트레이닝"]
               , "도서/티켓/문구": ["도서", "문구", "기프티콘", "쿠폰", "상품권", "티켓"]
               , "악기": ["도서", "문구", "기프티콘", "쿠폰", "상품권", "티켓"]
               , "반려동물" : ["강아지", "고양이", "사료", "강아지 간식", "고양이 간식", "강아지 용품", "고양이 용품"]
               , "미용": ["스킨케어", "로션", "메이크업", "향수", "네일아트", "미용", "다이어트", "화장품"]
               , "콘솔게임": ["플레이스테이션", "XBOX", "게임CD", "닌텐도 스위치", "wii"]
            }



def get_dangn(keyword):
    # 이모티콘 제거하기
    pattern = re.compile("["
                         u"\U00010000-\U0010FFFF"  # BMP characters 이외
                         "]+", flags=re.UNICODE)
    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    options.add_argument("headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
    driver.implicitly_wait(time_to_wait=5)

    # 변수 초기화
    end_number = 0
    name, address, price, link, img_link = [], [], [], [], []

    for check in categoly:
        if keyword == check:
            end_number = int(50 // len(categoly[keyword]))
            break
    else:
        print("카테고리 찾지 못함")

    for key in categoly[keyword]:
        # 셀레니움
        url = "https://www.daangn.com/search/" + key

        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        driver.find_element_by_xpath("//*[@id=\"result\"]/div[1]/div[2]/span").click()

        driver.implicitly_wait(time_to_wait=5)

        for i in range(2, end_number+1):
            print(i)

            name.append(
                driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/div/span[1]")[
                    0].text)
            address.append(
                driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[1]")[
                    0].text.strip())
            price.append(driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[2]")[
                             0].text.strip())
            link.append(
                driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a")[0].get_attribute(
                    'href'))
            img_link.append(
                driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[1]/img")[
                    0].get_attribute("src"))

    # DB 연결하기
    conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="condb", use_unicode=True)

    # DB 커서 만들기
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("TRUNCATE condb.usersells")

    cursor.execute('SET NAMES utf8mb4')
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")

    # sql 문
    sql = "INSERT INTO condb.UserSells VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"

    # db에 sql
    for i in range(len(name)):
        cursor.execute(sql,
                       (i + 1, '당근 마켓', pattern.sub(r"", name[i]), "null", address[i], price[i], str(link[i]), img_link[i]))

    conn.commit()
