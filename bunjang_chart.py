from selenium import webdriver
from bs4 import BeautifulSoup
import re
from time import sleep
import numpy as np
import pandas as pd
import chromedriver_autoinstaller

def get_bunjang(search_keyword, db):
    try:
        result = []

        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument("--remote-debugging-port=9222")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        path = '/usr/bin/chromedriver'
        driver = webdriver.Chrome(path, options=options)
        # driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
        driver.implicitly_wait(3)

        temp_list = []
        count = 1

        for page in range(1):

            driver.get('https://m.bunjang.co.kr/search/products?q=' + search_keyword + '&order=' + "date" + '&page=' + str(page))
            sleep(1)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # items = soup.select('#root > div > div > div:nth-child(4) > div > div.sc-lnmtFM.dYMRID')
            items = soup.select('#root > div > div > div:nth-child(4) > div > div.sc-lnmtFM.dYMRID > div')

            name_list, upload_time_list, price_list, link_list, img_link_list, address_list = [], [], [], [], [], []

            for i in items:
                divs = i.find_all("div")
                for div in divs:
                    href_div = div.find_all(attrs={'class': 'sc-jKVCRD bqiLXa'})
                    link_div = div.find_all(attrs={'class': 'sc-LKuAh fuGAmW'})
                    img_div = div.find_all(attrs={'class': 'sc-kaNhvL hCNYZO'})
                    for link in link_div:
                        isAD = div.find_all(attrs={'class':'sc-kxynE fnToiW'})
                        AD = []
                        for ad in isAD:
                            if ad.get_text() == 'AD':
                                AD.append(ad)
                        if len(AD) == 0:
                            for hrefs in href_div:
                                href = hrefs.attrs['href']
                                link_list.append("https://bunjang.co.kr" + href)
                            for imgs in img_div:
                                img_find = imgs.find('img')
                                img = img_find['src']
                                img_link_list.append(img)
                            price_div = div.find_all(attrs={'class': "sc-hzNEM bmEaky"})
                            if len(price_div) == 0:
                                    price_list.append('0')
                            else:
                                for price in price_div:
                                    prices = re.sub(r'[^0-9]', '', price.get_text())
                                    price_list.append(prices)
                            name_div = div.find_all(attrs={'class': "sc-iBEsjs fqRSdX"})
                            for name in name_div:
                                name_list.append(name.get_text())
                            place_div = div.find_all(attrs={'class': "sc-chbbiW ncXbJ"})
                            for place in place_div:
                                address_list.append(place.get_text())
                            time_div = div.find_all(attrs={'class': "sc-cooIXK fHvorz"})
                            for time in time_div:
                                time = time.get_text()
                                if time[1] in '시' or time[2] in '시' or time[1] in '분' or time[2] in '분' or time[1] in '초' or time[2] in '초':
                                    upload_time_list.append('오늘')
                                # elif time[0] in ['1', '2', '3', '4', '5', '6', '7'] and time[1] in '일':
                                #         upload_time_list.append(time)
                                else:
                                    upload_time_list.append(time)

        try:
            doc_ref = db.collection(u'99con').document(u'bunjang_chart').collection(u'' + search_keyword).document(
                u'last_number')
            docs = doc_ref.get()
            dic_number = docs.to_dict()
            bunjang_last_number = dic_number["number"]
            # print(bunjang_last_number)
        except:
            doc_ref = db.collection(u'99con').document(u'bunjang_chart').collection(u'' + search_keyword).document(
                u'last_number')
            doc_ref.set({
                u'number': 0
            })
            docs = doc_ref.get()
            dic_number = docs.to_dict()
            bunjang_last_number = dic_number["number"]
            # print(bunjang_last_number)

        if bunjang_last_number == 0:
            pass
        else:
            index = 0
            doc_ref = db.collection(u'99con').document(u'bunjang_chart').collection(u'' + search_keyword).document(
                u'' + str(bunjang_last_number - 1))
            docs = doc_ref.get()
            dic_row = docs.to_dict()
            latest_link = dic_row["link"]
            # print(latest_link)
            if latest_link in link_list:
                index = link_list.index(latest_link)
                # print(link_list)
                # print(index)
                del name_list[index:]
                del address_list[index:]
                del price_list[index:]
                del link_list[index:]
                del img_link_list[index:]
                del upload_time_list[index:]

        index = 0
        for i in range(len(name_list)-1, -1, -1):
            print(str(index) + "번째 번장 삽입")
            doc_ref = db.collection(u'99con').document(u'bunjang_chart').collection(u'' + search_keyword).document(
                u'' + str(int(bunjang_last_number) + int(index)))
            doc_ref.set({
                u'id': bunjang_last_number + i,
                u'platform': "번개장터",
                u'name': name_list[i],
                u'upload_time': upload_time_list[i],
                u'address': address_list[i],
                u'price': price_list[i],
                u'link': link_list[i],
                u'img_link': img_link_list[i],
                u'out_lier': "low"
            })
            index += 1
        doc_ref = db.collection(u'99con').document(u'bunjang_chart').collection(u'' + search_keyword).document(
            u'last_number')
        doc_ref.set({
            u'number': len(name_list) + bunjang_last_number
        })
        driver.quit()
    except:
        print("bunjang_chart except")
        pass
    
    #     temp_list = price_list
    #     np_temp = np.array(temp_list, dtype=np.int64)
    #     pd_temp = pd.Series(np_temp)
    #     Q3 = pd_temp.quantile(.75)
    #     Q1 = pd_temp.quantile(.25)
    #     Q2 = pd_temp.quantile(.5)
    #     IQR = Q3 - Q1
        
    #     if IQR > Q2:
    #         low_np = list(np_temp[Q1 > np_temp])
    #         high_np = list(np_temp[Q3 < np_temp])
    #     else:
    #         low_np = list(np_temp[Q1-0.2*IQR > np_temp])
    #         high_np = list(np_temp[Q3+0.4*IQR < np_temp])
        
    #     for i in range(len(name_list)):
    #         if upload_time_list[i] not in '오늘':
    #             if (upload_time_list[i][1] != '주') and (upload_time_list[i][1] != '달') and (upload_time_list[i][2] != '달' and (upload_time_list[i][1] != '년')):
    #                 if int(price_list[i]) in low_np:
    #                     pass
    #                 elif int(price_list[i]) in high_np:
    #                     pass
    #                 else:
    #                     result.append([count, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(price_list[i]), str(link_list[i]), img_link_list[i], 'normal'])
    #                     count += 1
    #         else:
    #             if int(price_list[i]) in low_np:
    #                     pass
    #             elif int(price_list[i]) in high_np:
    #                 pass
    #             else:
    #                 result.append([count, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(price_list[i]), str(link_list[i]), img_link_list[i], 'normal'])
    #                 count += 1
    # driver.quit()
    # return result