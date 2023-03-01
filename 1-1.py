#coding: shiftjis

import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import time


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

base_url = "https://r.gnavi.co.jp/area/jp/rs/?p="
num = 1
count_record = 0
flag = False

while True:
    time.sleep(3)
    page_url = base_url + str(num)
    response = requests.get(page_url, headers=header)
    response.encoding = response.apparent_encoding
    
    beautifulsoup = BeautifulSoup(response.text, 'html.parser')
    elems = beautifulsoup.select('a.style_titleLink__oiHVJ')
    
    for elem in elems:
        count_record += 1
        url = elem.get('href')
            # print(url)
        res = requests.get(url)
        res.encoding = response.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')

        name = soup.find('p', id='info-name').text

        phone_number = soup.find('span', class_='number').text

        locate = soup.find('span', class_='region').text
        prefucture, city, address = split_location(locate)

        if soup.find('span', class_='locality'):
            building = soup.find('span', class_='locality').text
        else:
            building = ""
        
        row = [[name, phone_number,"", prefucture, city, address, building, " ", " "]]
        df_append = pd.DataFrame(data=row, columns=HEADER)

        df = pd.concat([df, df_append], axis=0)

        if count_record == 50:
            flag = True
            break
        
    if flag : 
        break
    else: 
        num += 1

df.to_csv('1-1.csv', index=False, encoding="shift-jis", errors='ignore')