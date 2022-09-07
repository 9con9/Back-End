# from distutils.command.upload import upload
# import pymysql
# import requests
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
    result = []
    bunjang = bj.get_bunjang(keyword)
    count = len(bunjang)
    spl = keyword.split()
    list_spl = [k for k in spl]
    naver_keyword_list = list_spl[1:]
    naver_keyword = " ".join(naver_keyword_list)
    print("나 네이버 키워드" ,naver_keyword)
    print(naver_keyword)
    dangn = keyword_dangn(keyword)
    naver = keyword_joongna(naver_keyword)
    bunjang = np.array(bunjang)
    dangn = np.array(dangn)
    naver = np.array(naver)
    all = list(np.concatenate((bunjang, dangn, naver)))
    result.extend(naver, dangn, bunjang, all)
    # remove_db()
    return result




def keyword_joongna(search_keyword):
    # 이모티콘 제거하기
    pattern = re.compile("["
            u"\U00010000-\U0010FFFF"  #BMP characters 이외
                               "]+", flags=re.UNICODE)

    result = []

    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
    driver.implicitly_wait(3)
    driver.get('https://web.joongna.com/search?keyword=' + search_keyword + '&page=1')
    sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    items = soup.select(
        '#__next > div > div.container > div > div.ant-col.ant-col-20.css-t77d8m > div.ant-row.listWrap.css-euacx')

    name_list, upload_time_list, price_list, link_list, img_link_list, address_list = [], [], [], [], [], []

    for i in items:
        divs = i.find_all("div")
        for div in divs:
            link_div = div.find_all(attrs={'class': 'css-8rmnao'})
            for link in link_div:
                href = link.attrs['href']
                link_list.append('https://web.joongna.com' + href)
                second_div = link.find_all(attrs={'class': 'css-17j97b9'})
                for second in second_div:
                    third_div = second.find_all(attrs={'class': 'css-jib2h7'})
                    for third in third_div:
                        imgs = third.find('img')
                        img = imgs['src']
                        img_link_list.append(img)
                    price_div = second.find_all(attrs={'class': 'priceTxt'})
                    for price in price_div:
                        prices = re.sub(r'[^0-9]', '', price.get_text())
                        price_list.append(prices)
                    title_div = second.find_all(attrs={'class': 'titleTxt'})
                    for title in title_div:
                        name_list.append(title.get_text())
                    time_div = second.find_all(attrs={'class': 'registInfo'})
                    for time in time_div:
                        spans = time.find_all('span')
                        flag = True
                        print(time)
                        for span in spans:
                            if len(time) == 1:
                                tim = span.get_text()
                                upload_time_list.append(tim)
                                address_list.append('None')
                            else:
                                if flag is True:
                                    address = span.get_text()
                                    address_list.append(address)
                                    flag = False
                                else:
                                    tim = span.get_text()
                                    upload_time_list.append(tim)

    print(len(name_list), upload_time_list, len(price_list), len(link_list), len(img_link_list), address_list)
    for check in upload_time_list:
        if not ((int(check[0:1]) < 8) and (check[2:3] != "일") or (check[1:2] == "시") or (check[2:3] == "시") or (check[1:2] == "분") or (check[2:3] == "분")):
            index = upload_time_list.index(check)
            del name_list[index:]
            del upload_time_list[index:]
            del price_list[index:]
            del link_list[index:]
            del img_link_list[index:]
            del address_list[index:]
            break;

    print(len(name_list))

    temp_list = price_list
    np_temp = np.array(temp_list, dtype=np.int64)
    Q3, Q1, Q2 = np.percentile(np_temp, [75, 25, 50])
    IQR = Q3 - Q1
    print(Q3, Q1, Q2, IQR)
    if IQR > Q2:
        low_np = list(np_temp[Q1 > np_temp])
        high_np = list(np_temp[Q3 < np_temp])
    else:
        low_np = list(np_temp[Q1 - 0.4 * IQR > np_temp])
        high_np = list(np_temp[Q3 + 0.4 * IQR < np_temp])
    print(Q3 + 1 * IQR, Q1 - 1 * IQR, Q2, IQR)

    for i in range(len(name_list)):
        prices = int(re.sub(r'[^0-9]', '', price_list[i]))
        if prices in low_np:
            result.append([i + 1, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(prices),
                           str(link_list[i]), img_link_list[i], 'low'])
        elif prices in high_np:
            result.append([i + 1, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(prices),
                           str(link_list[i]), img_link_list[i], 'high'])
        else:
            result.append([i + 1, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(prices),
                           str(link_list[i]), img_link_list[i], 'normal'])
    return result

    # temp_upload_time_list = np.array(upload_time_list)
    # index = np.where(not((int(temp_upload_time_list[0:1]) < 8) and (temp_upload_time_list[2:3] != "일") or (temp_upload_time_list[1:2] == "시") or
    #                      (temp_upload_time_list[2:3] == "시") or (temp_upload_time_list[1:2] == "분") or (temp_upload_time_list[2:3] == "분")))
    # print(index)
    # print(index[0])



    # while (int(upload_time[-1][0:1]) < 8) and (upload_time[-1][2:3] != "일") or (upload_time[-1][1:2] == "시") or (upload_time[-1][2:3] == "시"):
    #     if plus_count == 4:
    #         print()
    #         print("나 클릭할고얌")
    #         print()
    #         driver.find_element("xpath", '//*[@id="root"]/div[1]/section/article/button').click()
    #         plus_count = 0
    #     print("나는 일  :" ,upload_time[-1][1:2])
    #     print("나는 숫자 : ",upload_time[-1][0:1])
    #     naver_parsing(start, end, name, address, price, link, img_link, upload_time, driver)
    #     start = end
    #     end += 2
    #     plus_count += 1
    # print("DB들어간다.")
    # # DB 연결하기
    # return set_db("중고 나라", pattern, name, upload_time, address, price, link, img_link, count, keyword)

# def naver_parsing(start, end, name, address, price, link, img_link, upload_time, driver):
#     for i in range(start,end):
#         print(i)
#
#         address.append("None")
#         ## 위치 못가져옴
#         upload_time.append(driver.find_elements("xpath",
#             '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
#         print(driver.find_elements("xpath",
#             '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
#             ## 업로드시간 가져옴
#         name.append(driver.find_elements("xpath", '//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/div/a/span')[0].text)
#         ## 이름 가져옴
#         #upload_time.append(driver.find_elements_by_xpath('// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / div / p')[0].text)
#         ## 업로드시간 가져옴
#         if len(re.sub(r'[^0-9]', '', driver.find_elements("xpath", '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / p')[0].text)) == 0:
#             price.append("0")
#         else:
#             price.append(re.sub(r'[^0-9]', '', driver.find_elements("xpath", '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / div / a / p')[0].text))
#         ## 가격 가져옴
#         link.append(driver.find_elements("xpath", '// *[ @ id = "root"] / div[1] / section / article / div / div[' + str(i) + '] / div / a')[0].get_attribute('href'))
#         ## 해당 주소 가져옴
#         try:
#             img_link.append(driver.find_elements("xpath", '//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/a/div/img')[0].get_attribute("src"))
#             ## 영상 가져옴
#         except:
#             img_link.append(driver.find_elements("xpath", '//*[@id="root"]/div[1]/section/article/div/div[' + str(i) + ']/div/div/a')[0].get_attribute("href"))
#             ## 이미지주소 가져옴


def keyword_dangn(keyword):
    # 이모티콘 제거하기
    pattern = re.compile("["
                         u"\U00010000-\U0010FFFF"  # BMP characters 이외
                         "]+", flags=re.UNICODE)
    url = "https://www.daangn.com/search/" + keyword
    # url = "https://www.daangn.com/search/천안%20아이패드%20에어3"

    # 변수 초기화
    name_list, address_list, price_list, link_list, img_link_list, upload_time_list = [], [], [], [], [], []
    result = []


    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # 셀레니움

    driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
    driver.implicitly_wait(time_to_wait=5)
    driver.get(url)
    arr = []
    for _ in range(8):
        arr.append(driver.find_element('xpath', "//*[@id=\"result\"]/div[1]/div[2]/span"))
    for ele in range(8):
        arr[ele].click()
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
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
                prices = re.sub(r'[^0-9]', '', pr.get_text())
                print(prices)
                if len(prices) == 0:
                    price_list.append(0)
                else:
                    price_list.append(int(prices))

            name_s = art.find_all(attrs={'class': "article-title"})
            for name in name_s:
                name_list.append(name.get_text().strip())

            place_p = art.find_all(attrs={'class': "article-region-name"})
            for place in place_p:
                address_list.append(place.get_text().strip())

    print(len(name_list))
    print(len(price_list))
    print(len(link_list))
    print(len(img_link_list))
    print(len(name_list))
    print(len(address_list))

    count = 0
    index = 0
    while count < 4 and index != len(name_list):
        driver.get(link_list[index])
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        temp_upload_time = driver.find_elements("xpath",'//*[@id="article-category"]/time')[0].text
        temp_upload_time = temp_upload_time.lstrip("끌올 ")
        if not ((int(temp_upload_time[0:1]) < 8) and (temp_upload_time[2:3] != "일") or (temp_upload_time[1:2] == "시") or (temp_upload_time[2:3] == "시")):
            count += 1
            print(temp_upload_time)
        if temp_upload_time[0:2] == "끌올":
            upload_time_list.append(temp_upload_time[3:])
        else:
            upload_time_list.append(temp_upload_time)
        index += 1
        print(index)
        print(temp_upload_time)

    if count == 4:
        del img_link_list[index:]
        del price_list[index:]
        del name_list[index:]
        del address_list[index:]
        del link_list[index:]



    print(len(name_list))
    print(len(price_list))
    print(len(link_list))
    print(len(img_link_list))
    print(len(name_list))
    print(len(address_list))
    print(len(upload_time_list))

    # dangn_parsing(2, 12, name, address, price, link, img_link, upload_time, driver, url)
    # start = 12
    # end = 22
    # while (int(upload_time[-1][0:1]) < 8) and (upload_time[-1][2:3] != "일") or (upload_time[-1][1:2] == "시") or (upload_time[-1][2:3] == "시"):
    #     print()
    #     print(upload_time[-1][1:2])
    #     print(upload_time[-1][0:1])
    #     print()
    #     driver.get(url)
    #     page = driver.page_source
    #     soup = BeautifulSoup(page, "html.parser")
    #     plus = end // 12
    #     print(plus)
    #     for i in range(plus+1):
    #         driver.find_element("xpath", "//*[@id=\"result\"]/div[1]/div[2]/span").click()
    #     dangn_parsing(start, end, name, address, price, link, img_link, upload_time, driver, url)
    #     start = end
    #     end += 10
    #
    # print("DB들어간다.")
    # # DB 연결하기
    temp_list = price_list
    np_temp = np.array(temp_list, dtype=np.int64)
    Q3, Q1, Q2 = np.percentile(np_temp, [75, 25, 50])
    IQR = Q3 - Q1
    if IQR > Q2:
        low_np = list(np_temp[Q1 > np_temp])
        high_np = list(np_temp[Q3 < np_temp])
    else:
        low_np = list(np_temp[Q1 - 0.2 * IQR > np_temp])
        high_np = list(np_temp[Q3 + 0.4 * IQR < np_temp])

    for i in range(len(name_list)):
        if int(price_list[i]) in low_np:
            result.append(
                [i + 1, '당근 마켓', pattern.sub(r"", name_list[i]), upload_time_list[i], address_list[i], price_list[i],
                 str(link_list[i]), img_link_list[i], 'low'])
        elif int(price_list[i]) in high_np:
            result.append(
                [i + 1, '당근 마켓', pattern.sub(r"", name_list[i]), upload_time_list[i], address_list[i], price_list[i],
                 str(link_list[i]), img_link_list[i], 'high'])
        else:
            result.append(
                [i + 1, '당근 마켓', pattern.sub(r"", name_list[i]), upload_time_list[i], address_list[i], price_list[i],
                 str(link_list[i]), img_link_list[i], 'normal'])
    return result






def dangn_parsing(start, end, name, address, price, link, img_link, upload_time, driver, url):
    

    for i in range(start, end):
        print(i)

        name.append(driver.find_elements("xpath", 
            "//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/div/span[1]")[0].text)
        address.append(
            driver.find_elements("xpath", "//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[1]")[
                0].text.strip())
        if len(re.sub(r'[^0-9]', '', driver.find_elements("xpath", "//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[2]")[
                0].text.strip())) == 0:
            price.append('0')
        else:
            price.append(re.sub(r'[^0-9]', '', driver.find_elements("xpath", "//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[2]/p[2]")[
                0].text.strip()))
        link.append(
            driver.find_elements("xpath", "//*[@id='flea-market-wrap']/article[" + str(i) + "]/a")[0].get_attribute(
                'href'))
        img_link.append(
            driver.find_elements("xpath", "//*[@id='flea-market-wrap']/article[" + str(i) + "]/a/div[1]/img")[
                0].get_attribute("src"))
        
    link_start = start - 2
    link_end = end - 2
    for i in range(link_start, link_end):
        print(i)
        driver.get(link[i])
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        temp_upload_time = driver.find_elements("xpath", '//*[@id="article-category"]/time')[0].text
        if temp_upload_time[0:2] == "끌올":
            upload_time.append(temp_upload_time[3:])
        else:
            upload_time.append(temp_upload_time)



def set_db(platform, pattern,name,  upload_time, address, price, link, img_link, count, keyword):
    
    result = []
    # DB 연결하기

    # conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="condb", use_unicode=True)

    # # DB 커서 만들기
    # cursor = conn.cursor(pymysql.cursors.DictCursor)

  #  cursor.execute("TRUNCATE condb.usersells")

    # cursor.execute('SET NAMES utf8mb4')
    # cursor.execute("SET CHARACTER SET utf8mb4")
    # cursor.execute("SET character_set_connection=utf8mb4")
    
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
    # sql = "INSERT INTO condb.chart_usersells VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
            result.append([count + 1, platform, pattern.sub(r"", name[i]), upload_time[i], address[i], price[i], str(link[i]),img_link[i], 'normal', keyword])
        print(str(count) + "번쨰 디비들어간다")
        count += 1
    print(count)
    # conn.commit()
    return result

# def remove_db():
#     print("DB제거 들어간다")
    # conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="condb", use_unicode=True)

    # # DB 커서 만들기
    # cursor = conn.cursor(pymysql.cursors.DictCursor)

    # for i in range(8,30):
    #     cursor.execute('Delete from condb.chart_usersells where upload_time = "' + str(i) + '일 전"')

    # conn.commit()
    # print("DB제거 끝났당")

#keyword_naver('아이폰13', 200)


# keyword_dangn("아이패드 에어4")#, 1)
# print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간