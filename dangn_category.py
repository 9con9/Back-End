import pymysql
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
import chromedriver_autoinstaller
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
    name, address, price, link, img_link, upload_time = [], [], [], [], [], []
    print(end_number)


    for check in categoly:
        if keyword == check:
            end_number = int(15 // len(categoly[keyword]))+1
            break
    else:
        print("카테고리 찾지 못함")

    link_start = 0
    link_end = end_number - 1
    print(link_start)
    print(link_end)


    for key in categoly[keyword]:
        # 셀레니움
        url = "https://www.daangn.com/search/천안 " + key

        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        #driver.find_element_by_xpath("//*[@id=\"result\"]/div[1]/div[2]/span").click()

        driver.implicitly_wait(time_to_wait=5)

        for i in range(2, end_number+1):
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


        for i in range(link_start , link_end):
            driver.get(link[i])
            page = driver.page_source
            soup = BeautifulSoup(page, "html.parser")
            temp_upload_time = driver.find_elements_by_xpath('//*[@id="article-category"]/time')[0].text
            if temp_upload_time[0:2] == "끌올":
                upload_time.append(temp_upload_time[3:])
            else:
                upload_time.append(temp_upload_time)

        link_start = link_end
        link_end += (end_number - 1)

        print("업로드 타임: ", upload_time)
        print("이름들 : ", name)
        print(link_start)
        print(link_end)


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

    # db에 sql
    for i in range(len(name)):
        cursor.execute(sql,
                       (i + 1, '당근 마켓', pattern.sub(r"", name[i]), upload_time[i], address[i], price[i], str(link[i]), img_link[i], 'normal'))

    conn.commit()
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간

# for i in cccc:
#     get_dangn(i)
