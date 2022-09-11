from selenium import webdriver
from bs4 import BeautifulSoup
import re
from time import sleep
import numpy as np
import pandas as pd

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
    driver.implicitly_wait(3)
    
    temp_list = []
    count = 1
    
    for page in range(1, 3):
            
        driver.get('https://m.bunjang.co.kr/search/products?q=' + search_keyword + '&order=' + "date" + '&page=' + str(page))
        sleep(1)
        
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
                            time = time.get_text()
                            if time[1] in '시' or time[2] in '시' or time[1] in '분' or time[2] in '분' or time[1] in '초' or time[2] in '초':
                                upload_time_list.append('오늘')
                            else:
                                upload_time_list.append(time)
                                
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
            low_np = list(np_temp[Q1-0.2*IQR > np_temp])
            high_np = list(np_temp[Q3+0.4*IQR < np_temp])
        
        for i in range(len(name_list)):
            if upload_time_list[i] not in '오늘':
                if (upload_time_list[i][1] != '주') and (upload_time_list[i][1] != '달') and (upload_time_list[i][2] != '달' and (upload_time_list[i][1] != '년')):
                    if int(price_list[i]) in low_np:
                        pass
                    elif int(price_list[i]) in high_np:
                        pass
                    else:
                        result.append([count, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(price_list[i]), str(link_list[i]), img_link_list[i], 'normal'])
                        count += 1
            else:
                if int(price_list[i]) in low_np:
                        pass
                elif int(price_list[i]) in high_np:
                    pass
                else:
                    result.append([count, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(price_list[i]), str(link_list[i]), img_link_list[i], 'normal'])
                    count += 1
    driver.quit()
    return result