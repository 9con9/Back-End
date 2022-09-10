from selenium import webdriver
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import re
import numpy as np

def get_joongna(search_keyword):
    
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
    driver.get('https://web.joongna.com/search?keyword=' + search_keyword + '&page=1')
    driver.implicitly_wait(3)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    items = soup.select('#__next > div > div.container > div > div.ant-col.ant-col-20.css-t77d8m > div.ant-row.listWrap.css-euacx')

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
                        if len(prices) == 0:
                            price_list.append(0)
                        else:
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
                                    
    temp_list = price_list
    np_temp = np.array(temp_list, dtype=np.int64)
    Q3, Q1, Q2 = np.percentile(np_temp, [75, 25, 50])
    IQR = Q3 - Q1
    if IQR > Q2:
        low_np = list(np_temp[Q1 > np_temp])
        high_np = list(np_temp[Q3 < np_temp])
    else:
        low_np = list(np_temp[Q1-0.2*IQR > np_temp])
        high_np = list(np_temp[Q3+0.4*IQR < np_temp])

    for i in range(len(name_list)):
        prices = int(re.sub(r'[^0-9]', '', price_list[i]))
        if prices in low_np:
            result.append([i+1, '중고 나라', name_list[i], upload_time_list[i], str(address_list[i]), int(prices), str(link_list[i]), img_link_list[i], 'low'])
        elif prices in high_np:
            result.append([i+1, '중고 나라', name_list[i], upload_time_list[i], str(address_list[i]), int(prices), str(link_list[i]), img_link_list[i], 'high'])
        else:
            result.append([i+1, '중고 나라', name_list[i], upload_time_list[i], str(address_list[i]), int(prices), str(link_list[i]), img_link_list[i], 'normal'])
    return result