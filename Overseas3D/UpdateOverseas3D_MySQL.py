#!/usr/bin/env python
# coding: utf-8

# In[2]:


# -*- coding: utf-8 -*-
'''
說明:
1.資料庫連線
2.抓央行台幣匯率 (download csv from website)
3.設定契約、契約名稱、契約規格
4.紀錄要存入資料庫的三個欄位:契約規格(千元)、波動率、OI(千口)
5.依照OI遞減排序並幫 df加上 id
'''
import pymysql
import numpy as np
import time , datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#from mpl_finance import candlestick_ohlc

#from plot_M import draw_K, plot

# dbconnect
dbconn=pymysql.connect(
            host="103.17.9.213",
            database= "pricedata_day",
            user="webmysql@actwebdb2",
            password="AIteam168",
            port=3306,
            charset='utf8',
            )  


# In[3]:


# 抓取央行台幣匯率

import requests
csv_url='https://www.cbc.gov.tw/public/data/OpenData/外匯局/FTDOpenData015.csv'
req = requests.get(csv_url)
url_content = req.content
csv_file = open('NTD.csv', 'wb')
csv_file.write(url_content)
csv_file.close()

df_nt=pd.read_csv('NTD.csv') 
NTD=df_nt['NTD/USD'].iloc[-1]
print(NTD)


# In[11]:



# 設定契約、契約名稱、契約規格
tablenames=['es','nq','ym','ad','bp','cd','ec','jy','sf','zc','zs','zw','gc','si','hg','cl','ty','us']
contractdict={'es':5,'nq':2,'ym':0.5,'ad':10000,'bp':10000*0.625,'cd':10000*10,'ec':10000*1.25,'jy':0.1*1.25,'sf':10000*12.5,'zc':10,'zs':10,'zw':50,'gc':10,'si':1000,'hg':25000,'cl':1000,'ty':1000,'us':1000}
namesdict={'es':'微型S&P','nq':'微型NASDAQ','ym':'小型道瓊','ad':'微型澳幣','bp':'微型英鎊','cd':'加幣','ec':'微型歐元','jy':'微型日圓','sf':'瑞士法郎','zc':'小玉米','zs':'小黃豆','zw':'小麥','gc':'微型黃金','si':'微型白銀','hg':'銅','cl':'輕原油','ty':'T-Bond','us':'T-Note'}

for i in tablenames:
    #i='es'
    #print(i)
    sql='select Date,Close,Open_Int from {} where Date > "20200223" order by Date desc limit 253;'.format(i)
    generator_df = pd.read_sql(sql=sql,  # mysql query
                               con=dbconn)  # size you want to fetch each time  

    generator_df=generator_df.sort_values(by=['Date'],ascending='True').reset_index()

    # Compute the logarithmic returns using the Closing price 
    generator_df['Log_Ret'] = np.log(generator_df['Close'] / generator_df['Close'].shift(1))

    # Compute Volatility using the pandas rolling standard deviation function
    generator_df['ContractValue'] = generator_df['Close'] * contractdict[i]*NTD
    generator_df['Volatility'] = generator_df['Log_Ret'].rolling(window=252).std() * np.sqrt(252)

    #print(generator_df)

    Date=generator_df.iloc[252][1]
    Close=generator_df.iloc[252][2]
    
    # 紀錄要存入資料庫的三個欄位:契約規格(千元)、波動率、OI(千口)
    
    ContractValue=round(generator_df.iloc[252][5]/1000,0)
    Vol=round(generator_df.iloc[252][6],4)
    OI=generator_df.iloc[251][3]/1000
    
    commod_list=[i,namesdict[i],Date,Close,ContractValue,Vol,OI]
    #print(commod_list)

    if i=='es':
        header = ['symbol','mod_name','Date','Close','ContractValue_K','Vol','OI_K']
        df=pd.DataFrame.from_records([commod_list],columns=header)
    else:
        new_row = pd.DataFrame([commod_list], columns=df.columns.tolist() )
        df = df.append(new_row, ignore_index=True)
# 依照OI遞減排序並幫 df加上 id
df=df.sort_values(by='OI_K', ascending=False)
df.reset_index(inplace=True)
df['id']=df.index+1
print(df)
# save dataframe to a csv file
#df.to_csv('df.csv', index=False)
# save dataframe to database
engine2 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/cotdatabase?charset=utf8')
df.to_sql('chart_overseas3D', engine2, if_exists = 'replace',index=False)


# In[ ]:




