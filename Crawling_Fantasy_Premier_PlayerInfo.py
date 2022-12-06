# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 23:43:13 2022

@author: Michael
"""
# =============================================================
import numpy as np
from urllib.request import urlopen
from bs4 import BeautifulSoup

from selenium import webdriver 
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import random
from pandas import Series

import unicodedata
import urllib.parse
import requests

import matplotlib.pyplot as plt
# =============================================================

# 스크롤
def scroll():
    try:        
        # 페이지 내 스크롤 높이 받아오기
        last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            # 임의의 페이지 로딩 시간 설정
            # PC환경에 따라 로딩시간 최적화를 통해 scraping 시간 단축 가능
            pause_time = random.uniform(1, 2)
            # 페이지 최하단까지 스크롤
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            # 페이지 로딩 대기
            time.sleep(pause_time)
            # 무한 스크롤 동작을 위해 살짝 위로 스크롤(i.e., 페이지를 위로 올렸다가 내리는 제스쳐)
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight-50)")
            time.sleep(pause_time)
            # 페이지 내 스크롤 높이 새롭게 받아오기
            new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
            # 스크롤을 완료한 경우(더이상 페이지 높이 변화가 없는 경우)
            if new_page_height == last_page_height:
                print("스크롤 완료")
                break
                
            # 스크롤 완료하지 않은 경우, 최하단까지 스크롤
            else:
                last_page_height = new_page_height
            
    except Exception as e:
        print("에러 발생: ", e)

# Fantasy Premier League 선수 정보(이름/overview weblink) 크롤링
url = 'https://www.premierleague.com/players'
html = urlopen(url)
soup = BeautifulSoup(html, 'html.parser')
soup
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(url)
driver.find_element("xpath","//*[@class='_2hTJ5th4dIYlveipSEMYHH BfdVlAo_cgSVjDUegen0F js-accept-all-close']").click()
time.sleep(2)
scroll()
soup = bs(driver.page_source, 'html.parser')

table = soup.select_one('table')
tbody = table.select_one('a').text
df = table.select('table > tbody > tr > td > a')
outlist = []
namelist = []
for i in df:
    print('https:'+i.attrs['href'])
    print(i.text)
    namelist.append(i.text)
    outlist.append('{}{}'.format('https:',i.get('href')))
    
outlist = list(map(lambda x : x.replace('overview','stats'), outlist))
# 선수 이름, stat으로 연결되는 홈페이지 데이터프레임화    
fantasyDic = {'PlayerName' : namelist,
              'stat_homepage' : outlist}
fantasyDic = pd.DataFrame(fantasyDic)

fantasyDic.to_csv('fantasyPremier.csv', encoding = 'utf-8', index = False)



# =============================================================

df1 = pd.read_csv('fantasyPremier.csv', encoding = 'utf-8')
df1.columns

# é, ï와 같은 글자 변환
normalized = list(df1['stat_homepage'].map(lambda x : unicodedata.normalize('NFD',x))) # Normal Form Decomposition
test = []
for i in normalized :
    print(i)
    new = u"".join([c for c in i if not unicodedata.combining(c)])
    test.append(new)
df1['stat_homepage'] = test # 덮어쓰기

# 위의 방법으로 변환되지 않았던 글자 직접 변환
df1['stat_homepage'] = df1['stat_homepage'].str.replace('Ø','o')
df1['stat_homepage'] = df1['stat_homepage'].str.replace('ø','o')
df1['stat_homepage'] = df1['stat_homepage'].str.replace('ß','b')

# 정보 데이터프레임화
for j in df1['stat_homepage'][:1]:
    url = j
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    #print(soup.find('span', {'class' : 'stat'}).text)
    columnsList = []
    valueList = []
    for i in range(len(soup.find_all('div',{'class': 'normalStat'}))):
        headerStat = soup.find_all('div',{'class' : 'normalStat'})[i].text.strip().split('\n')[0].strip()
        normalStat = soup.find_all('div',{'class' : 'normalStat'})[i].text.strip().split('\n')[1].strip()
        #columnsList.append(headerStat)
        print(headerStat, ' : ', normalStat)
        print(' --------------- ')
        columnsList.append(headerStat)
        valueList.append(normalStat)
    print(len(columnsList))
    print(len(valueList))
    df2 = pd.DataFrame(data = [valueList], columns = columnsList)
    

for j in df1['stat_homepage'][1:]:
    url = j; print('url: ',url)
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    #print(soup.find('span', {'class' : 'stat'}).text)
    columnsList = []
    valueList = []
    for i in range(len(soup.find_all('div',{'class': 'normalStat'}))):
        headerStat = soup.find_all('div',{'class' : 'normalStat'})[i].text.strip().split('\n')[0].strip()
        normalStat = soup.find_all('div',{'class' : 'normalStat'})[i].text.strip().split('\n')[1].strip()
        #columnsList.append(headerStat)
        #print(headerStat, ' : ', normalStat)
        #print(' --------------- ')
        columnsList.append(headerStat)
        valueList.append(normalStat)
    #print(len(columnsList))
    #print(len(valueList))
    print('---------- : ',j)
    df3 = pd.DataFrame(data = [valueList], columns = columnsList)
    df2 = pd.concat([df2, df3], join = 'outer')


# 데이터 합치기 : 
df2 = df2.reset_index().drop('index', axis = 1)
# df2.info()
# df2.replace(',','')
# df2.applymap(lambda x : str(x).replace(',',''))
player_stat_table = pd.concat([df1,df2], axis = 1)
player_stat_table = player_stat_table.fillna(0)
#player_stat_table['Goals'] = player_stat_table['Goals'].astype(float).sort_values(ascending = False)

stat_only_table = player_stat_table.drop('stat_homepage', axis = 1)
stat_only_table = stat_only_table.applymap(lambda x : str(x).replace(',',''))
stat_only_table = stat_only_table.applymap(lambda x : str(x).replace('%',''))
stat_only_table.iloc[:,1:] = stat_only_table.iloc[:,1:].astype(float)
stat_only_table.to_csv('playerinfo.csv', encoding = 'utf-8')

stat_only_table.columns
x = stat_only_table.sort_values('Goals',ascending = False)
plt.xticks(rotation = 45)
plt.bar(x.iloc[:20,0],x.iloc[:20,1])

sorted_top = stat_only_table.sort_values(['Goals','Shots'], ascending = False)
