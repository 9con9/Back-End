from selenium import webdriver
from bs4 import BeautifulSoup
import pymysql
import chromedriver_autoinstaller
import re
import numpy as np

def get_bunjang(search_keyword):

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
    driver.implicitly_wait(3)
    driver.get('https://m.bunjang.co.kr/search/products?q=' + search_keyword + '&order=' + "score" + '&page=1')

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    items = soup.select('#root > div > div > div:nth-of-type(4) > div > div.sc-bbkauy.ckBMEw > div')

    name_list, upload_time_list, price_list, link_list, img_link_list, address_list = [], [], [], [], [], []
    
    for i in items:
        divs = i.find_all("div")
        for div in divs:
            link_div = div.find_all(attrs={'class': 'sc-chbbiW dlCCUH'})
            for link in link_div:
                isAD = div.find_all(attrs={'class':'sc-jXQZqI fwwrJI'})
                AD = []
                for ad in isAD:
                    if ad.get_text() == 'AD':
                        AD.append(ad)
                if len(AD) == 0:
                    href = link.attrs['href']
                    
                    link_list.append("https://bunjang.co.kr" + href)
                    
                    imgs = link.find('img')
                    img = imgs['src']

                    img_link_list.append(img)

                    price_div = div.find_all(attrs={'class': "sc-gmeYpB iBMbn"})
                    if len(price_div) == 0:
                            price_list.append('0')
                    else:
                        for price in price_div:
                            prices = re.sub(r'[^0-9]', '', price.get_text())
                            price_list.append(prices)
                    name_div = div.find_all(attrs={'class': "sc-fcdeBU iVCsji"})
                    for name in name_div:
                        name_list.append(name.get_text())
                    place_div = div.find_all(attrs={'class': "sc-kZmsYB eylVEY"})
                    for place in place_div:
                        address_list.append(place.get_text())
                    time_div = div.find_all(attrs={'class': "sc-iSDuPN iJqnGY"})
                    for time in time_div:
                        upload_time_list.append(time.get_text())

    conn = pymysql.connect(host="127.0.0.1", user="root", password="", db="condb", use_unicode=True)

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("TRUNCATE condb.bunjang_usersells")
    
    cursor.execute('SET NAMES utf8mb4')
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")

    sql = "INSERT INTO condb.bunjang_usersells VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    temp_list = price_list
    np_temp = np.array(temp_list, dtype=np.int64)
    Q3, Q1, Q2 = np.percentile(np_temp, [80, 20, 50])
    IQR = Q3 - Q1
    print(Q3, Q1, Q2, IQR)
    if IQR > Q2:
        low_np = list(np_temp[Q1 > np_temp])
        high_np = list(np_temp[Q3 < np_temp])
    else:
        low_np = list(np_temp[Q1-0.2*IQR > np_temp])
        high_np = list(np_temp[Q3+0.4*IQR < np_temp])
    print(Q3+0.4*IQR, Q1-0.2*IQR, Q2, IQR)

    for i in range(len(name_list)):
        prices = int(re.sub(r'[^0-9]', '', price_list[i]))
        if prices in low_np:
            cursor.execute(sql, (i+1, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(prices), str(link_list[i]), img_link_list[i], 'low'))
        elif prices in high_np:
            cursor.execute(sql, (i+1, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(prices), str(link_list[i]), img_link_list[i], 'high'))
        else:
            cursor.execute(sql, (i+1, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(prices), str(link_list[i]), img_link_list[i], 'normal'))

    conn.commit()