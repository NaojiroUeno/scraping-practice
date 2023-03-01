#coding: shiftjis

import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
browser = webdriver.Chrome(options=options)

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
header = {
    'User-Agent': user_agent
}

def split_location(locate):
    address = re.sub( '[^0-9-]', '', locate)
    locate = locate.replace(address, '')
    pre = re.match(r'(...??[都道府県])' , locate)
    locate = locate.replace(pre[0], '')

    return pre[0], locate, address


HEADER = ['店舗名', '電話番号', 'メールアドレス', '都道府県', '市町村', '番地', '建物名', 'URL', 'SSL']
df = pd.DataFrame(columns=HEADER)

driver = webdriver.Chrome('./chromedriver')
base_url = "https://r.gnavi.co.jp/area/jp/rs/"
driver.get(base_url)
num = 1
count_record = 0
flag = False

while True:
    cur_url = driver.current_url
    driver.get(cur_url)
    elem_urls = [elem.get_attribute('href') for elem in driver.find_elements(By.CLASS_NAME, 'style_titleLink__oiHVJ')]

    for elem in elem_urls:
        count_record += 1
        driver.get(elem)

        name = driver.find_element(By.ID, 'info-name').text

        phone_number = driver.find_element(By.CLASS_NAME, 'number').text

        locate = driver.find_element(By.CLASS_NAME, 'region').text
        prefucture, city, address = split_location(locate)

        if driver.find_elements(By.CLASS_NAME, 'locality'):
            building = driver.find_element(By.CLASS_NAME, 'locality').text
        else:
            building = ""

        if driver.find_elements(By.XPATH, '//a[text()="お店のホームページ"]'):
            shop_url = driver.find_element(By.XPATH, '//a[text()="お店のホームページ"]').get_attribute('href')
            # print(shop_url)
        elif driver.find_elements(By.CLASS_NAME, 'sv-of'):
            shop_url = driver.find_element(By.CLASS_NAME, 'sv-of').get_attribute('href')
            # print(driver.find_element(By.CLASS_NAME, 'sv-of'))
        else:
            shop_url = ""

        if 'https' in shop_url:
            ssl = "TRUE"
        else:
            ssl = "FALSE"

        if driver.find_elements(By.XPATH, '//a[text()="お店に直接メールする"]'):
            mail = driver.find_element(By.XPATH, '//a[text()="お店に直接メールする"]').get_attribute('href')
            mail = mail.replace('mailto:', '')
        else:
            mail = ""

        row = [[name, phone_number, mail, prefucture, city, address, building, shop_url, ssl]]
        df_append = pd.DataFrame(data=row, columns=HEADER)
        df = pd.concat([df, df_append], axis=0)


        if count_record == 50:
            flag = True
            break

        # print(name, shop_url)

    if flag : 
        break
    else:
        driver.get(cur_url)
        a_item = driver.find_element(By.CLASS_NAME, 'style_nextIcon__M_Me_')
        a_item.click()
        time.sleep(3)

df.to_csv('1-2.csv', index=False, encoding="shift-jis", errors='ignore')