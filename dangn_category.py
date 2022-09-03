# import pymysql
# import requests
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
    result = []
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
    name_list, address_list, price_list, link_list, img_link_list, upload_time_list = [], [], [], [], [], []
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
                    prices = re.sub(r'[^0-9]', '', pr.get_text().strip())
                    print(prices)
                    price_list.append(prices)

                name_s = art.find_all(attrs={'class': "article-title"})
                for name in name_s:
                    name_list.append(name.get_text().strip())

                place_p = art.find_all(attrs={'class': "article-region-name"})
                for place in place_p:
                    address_list.append(place.get_text().strip())

        # for i in range(2, end_number+1):
        #     print(i)
        #
        #     name.append(
        #         driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/div/span[1]")[
        #             0].text)
        #     address.append(
        #         driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[1]")[
        #             0].text.strip())
        #     if len(re.sub(r'[^0-9]', '', driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[2]")[
        #         0].text.strip())) == 0:
        #         price.append('0')
        #     else:
        #         price.append(re.sub(r'[^0-9]', '', driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[2]")[
        #         0].text.strip()))
        #     link.append(
        #         driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a")[0].get_attribute(
        #             'href'))
        #     img_link.append(
        #         driver.find_elements_by_xpath("//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[1]/img")[
        #             0].get_attribute("src"))


        for i in range(link_start , link_end):
            driver.get(link_list[i])
            page = driver.page_source
            soup = BeautifulSoup(page, "html.parser")
            temp_upload_time = driver.find_elements_by_xpath('//*[@id="article-category"]/time')[0].text
            if temp_upload_time[0:2] == "끌올":
                upload_time_list.append(temp_upload_time[3:])
            else:
                upload_time_list.append(temp_upload_time)

        link_start = link_end
        link_end += (end_number - 1)

        print("업로드 타임: ", upload_time_list)
        print("이름들 : ", name_list)
        print(link_start)
        print(link_end)



    for i in range(len(name)):
        result.append([i + 1, '당근 마켓', pattern.sub(r"", name[i]), upload_time_list[i], address_list[i], price_list[i], str(link[i]), img_link_list[i], 'normal'])


    # print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
    print(result)


get_dangn("디지털기기")