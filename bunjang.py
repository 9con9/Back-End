from selenium import webdriver
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import re
import numpy as np

def get_bunjang(search_keyword):
    
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
    driver.get('https://m.bunjang.co.kr/search/products?q=' + search_keyword + '&order=' + "score" + '&page=1')
    driver.implicitly_wait(3)

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
            result.append([i+1, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(prices), str(link_list[i]), img_link_list[i], 'low'])
        elif prices in high_np:
            result.append([i+1, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(prices), str(link_list[i]), img_link_list[i], 'high'])
        else:
            result.append([i+1, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(prices), str(link_list[i]), img_link_list[i], 'normal'])
    return result