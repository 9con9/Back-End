from bs4 import BeautifulSoup
from selenium import webdriver
import chromedriver_autoinstaller
import re

category = {
    "디지털기기": [600],
    "가구/인테리어": [810],
    "유아용품": [500],
    "스포츠/레저": [700],
    "의류": [310, 320, 405],
    "도서/티켓/문구": [900],
    "반려동물": [980],
    "미용": [410],
    "콘솔게임": [600600]
}

def get_bunjang(search_keyword):
    
    result = []
    
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(chromedriver_autoinstaller.install(), options=options)
    driver.implicitly_wait(3)
    
    name_list, upload_time_list, price_list, link_list, img_link_list, address_list = [], [], [], [], [], []
    
    for key in category[search_keyword]:
        driver.get('https://m.bunjang.co.kr/categories/' + str(key) + '?page=1' + "&req_ref=popular_category")
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        items = soup.select('#root > div > div > div:nth-child(4) > div > div:nth-child(4) > div')
        for i in items:
            divs = i.find_all('div')
            for div in divs:
                link_div = div.find_all(attrs={'class' : 'sc-LKuAh hjcqIZ'})
                for link in link_div:
                    isAD = div.find_all(attrs={'class': 'sc-gmeYpB fxEeIU'})
                    AD = []
                    for ad in isAD:
                        if ad.get_text() == 'AD':
                            AD.append(ad)
                    if len(AD) == 0:
                        href = link.attrs['href']
                        link_list.append('https://bunjang.co.kr' + href)

                        imgs = link.find('img')
                        img = imgs['src']
                        
                        img_link_list.append(img)
                        
                        price_div = div.find_all(attrs={'class': 'sc-kxynE kwIxAx'})
                        
                        if len(price_div) == 0:
                            price_list.append('0')
                        else:
                            for price in price_div:
                                price_list.append(price.get_text())
                        
                        name_div = div.find_all(attrs={'class': 'sc-chbbiW hmkmpv'})
                        for name in name_div:
                            name_list.append(name.get_text())
                            
                        place_div = div.find_all(attrs={'class': 'sc-cooIXK cHmIok'})
                        for place in place_div:
                            address_list.append(place.get_text())
                            
                        time_div = div.find_all(attrs={'class': 'sc-gmeYpB fxEeIU'})
                        for time in time_div:
                            upload_time_list.append(time.get_text())

    for i in range(len(name_list)):
        prices = re.sub(r'[^0-9]', '', price_list[i])
        result.append([i+1, '번개 장터', name_list[i], upload_time_list[i], str(address_list[i]), int(prices), str(link_list[i]), img_link_list[i], 'normal'])

    return result