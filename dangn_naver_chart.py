from bs4 import BeautifulSoup
import re
from selenium import webdriver
import time
from time import sleep
import bunjang_chart as bj
import numpy as np
import pandas as pd

start = time.time()  # 시작 시간 저장
def get_data(keyword):
    result = []
    
    bunjang = bj.get_bunjang(keyword)
    
    spl = keyword.split()
    list_spl = [k for k in spl]
    naver_keyword_list = list_spl[1:]
    naver_keyword = " ".join(naver_keyword_list)
    naver = keyword_joongna(naver_keyword)
    
    dangn = keyword_dangn(keyword)
    
    bunjang = np.array(bunjang)
    dangn = np.array(dangn)
    naver = np.array(naver)
    all = list(np.concatenate((bunjang, dangn, naver)))
    result.extend([naver, dangn, bunjang, all])
    
    return result

def keyword_joongna(search_keyword):

    result = []

    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--remote-debugging-port=9222") 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    path = '/usr/bin/chromedriver'
    driver = webdriver.Chrome(path, options=options)
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
                        for span in spans:
                            if len(time) == 1:
                                tim = span.get_text()
                                if tim[1] in '시' or tim[2] in '시' or tim[1] in '분' or tim[2] in '분' or \
                                        tim[1] in '초' or tim[2] in '초':
                                    upload_time_list.append('오늘')
                                else:
                                    upload_time_list.append(tim)
                                address_list.append('None')
                            else:
                                if flag is True:
                                    address = span.get_text()
                                    address_list.append(address)
                                    flag = False
                                else:
                                    tim = span.get_text()
                                    if tim[1] in '시' or tim[2] in '시' or tim[1] in '분' or tim[2] in '분' or \
                                            tim[1] in '초' or tim[2] in '초':
                                        upload_time_list.append('오늘')
                                    else:
                                        upload_time_list.append(tim)

    for check in upload_time_list:
        if check == "오늘":
            pass
        elif not ((int(check[0:1]) < 8) and (check[2:3] != "일") or (check[1:2] == "시") or (check[2:3] == "시") or (check[1:2] == "분") or (check[2:3] == "분")):
            index = upload_time_list.index(check)
            del name_list[index:]
            del upload_time_list[index:]
            del price_list[index:]
            del link_list[index:]
            del img_link_list[index:]
            del address_list[index:]
            break

    temp_list = price_list
    np_temp = np.array(temp_list, dtype=np.int64)
    pd_temp = pd.Series(np_temp)
    Q3 = pd_temp.quantile(.75)
    Q1 = pd_temp.quantile(.25)
    Q2 = pd_temp.quantile(.5)
    IQR = Q3 - Q1
    
    if IQR > Q2:
        low_np = list(np_temp[Q1 > np_temp])
        high_np = list(np_temp[Q3 < np_temp])
    else:
        low_np = list(np_temp[Q1 - 0.2 * IQR > np_temp])
        high_np = list(np_temp[Q3 + 0.4 * IQR < np_temp])

    for i in range(len(name_list)):
        prices = int(re.sub(r'[^0-9]', '', price_list[i]))
        if prices in low_np:
            result.append([i + 1, '중고 나라', name_list[i], upload_time_list[i], str(address_list[i]), int(prices),
                           str(link_list[i]), img_link_list[i], 'low'])
        elif prices in high_np:
            result.append([i + 1, '중고 나라', name_list[i], upload_time_list[i], str(address_list[i]), int(prices),
                           str(link_list[i]), img_link_list[i], 'high'])
        else:
            result.append([i + 1, '중고 나라', name_list[i], upload_time_list[i], str(address_list[i]), int(prices),
                           str(link_list[i]), img_link_list[i], 'normal'])
    return result

def keyword_dangn(keyword):
    
    result = []
    
    # 이모티콘 제거하기
    pattern = re.compile("["
                         u"\U00010000-\U0010FFFF"  # BMP characters 이외
                         "]+", flags=re.UNICODE)
    url = "https://www.daangn.com/search/" + keyword

    # 변수 초기화
    name_list, address_list, price_list, link_list, img_link_list, upload_time_list = [], [], [], [], [], []

    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--remote-debugging-port=9222") 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # 셀레니움

    path = '/usr/bin/chromedriver'
    driver = webdriver.Chrome(path, options=options)
    driver.implicitly_wait(time_to_wait=5)
    driver.get(url)
    for _ in range(8):
        driver.find_element('xpath', "//*[@id=\"result\"]/div[1]/div[2]/span").click()
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
        if temp_upload_time[0:2] == "끌올":
            if temp_upload_time[1] in '시' or temp_upload_time[2] in '시' or temp_upload_time[1] in '분' \
                    or temp_upload_time[2] in '분' or temp_upload_time[1] in '초' or temp_upload_time[2] in '초':
                upload_time_list.append('오늘')
            else:
                upload_time_list.append(temp_upload_time)
        else:
            if temp_upload_time[1] in '시' or temp_upload_time[2] in '시' or temp_upload_time[1] in '분' \
                    or temp_upload_time[2] in '분' or temp_upload_time[1] in '초' or temp_upload_time[2] in '초':
                upload_time_list.append('오늘')
            else:
                upload_time_list.append(temp_upload_time)
        index += 1

    if count == 4:
        del img_link_list[index:]
        del price_list[index:]
        del name_list[index:]
        del address_list[index:]
        del link_list[index:]

    index = 0
    
    while index != len(upload_time_list):
        if upload_time_list[index] == "오늘":
            index += 1
        elif ((upload_time_list[index][1:2] == "달") or (upload_time_list[index][2:3] == "달")):
            del name_list[index]
            del price_list[index]
            del address_list[index]
            del img_link_list[index]
            del link_list[index]
            del upload_time_list[index]
        elif not ((int(upload_time_list[index][0:1]) < 8) and (upload_time_list[index][2:3] != "일") or (upload_time_list[index][1:2] == "시") or (
                upload_time_list[index][2:3] == "시")):
            del name_list[index]
            del price_list[index]
            del address_list[index]
            del img_link_list[index]
            del link_list[index]
            del upload_time_list[index]
        else:
            index += 1
            
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