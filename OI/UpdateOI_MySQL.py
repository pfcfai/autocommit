#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-
'''
說明: 將stockfuturedata_day 擷取 最新一天的OI 資料 放到 cotdatabase 做成API url
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
            database= "stockfuturedata_day",
            user="webmysql@actwebdb2",
            password="AIteam168",
            port=3306,
            charset='utf8',
            )  
dbconn2=pymysql.connect(
            host="103.17.9.213",
            database= "cotdatabase",
            user="webmysql@actwebdb2",
            password="AIteam168",
            port=3306,
            charset='utf8',
            ) 


# In[2]:


# today
from datetime import datetime
now = datetime.now() # current date and time
year = now.strftime("%Y")
month = now.strftime("%m")
day = now.strftime("%d")
today=year+month+day
print(now)
print(today)


# In[4]:


# yesterday
import datetime
yday=datetime.date.today() - datetime.timedelta(days=1)
queryday=yday.strftime("%Y%m%d")


# In[5]:


# Determine which Contract
def  third_wen(y,m):                                                #   此函數需參數 年 及 月
    day=21-(datetime.date(y,m,1).weekday()+4)%7         #   weekday函數 禮拜一為0;禮拜日為6
    return datetime.date(y,m,day)                               
print(third_wen(int(year),int(month)))                                     # 會 print 出 2016-5-18 為五月份第三個禮拜三


residual=third_wen(int(year),int(month))-datetime.date.today()      # 今天持有201605 契約的時間價值

if third_wen(int(year),int(month))>datetime.date.today():
    Contract=year+month
else:
    Contract=year+format(int(month)+1, '02d')
print(Contract)


# In[30]:


# Define upper and lower stike-boundaries
import math
sql='select Twseclose from chart_optionoi where Date="{}" and Type="買權" ;'.format(queryday)
generator_df = pd.read_sql(sql=sql,  # mysql query
                           con=dbconn2)  # size you want to fetch each time  
print(generator_df)
lower=math.floor(generator_df.iloc[0][0]/100-9)*100
upper=math.floor(generator_df.iloc[0][0]/100+9)*100
print(lower,upper)


# In[50]:


# sql insert
sql='select Date, Type, Contract, Strike, Openinterest, id from optiontable where Date="{}" and Contract="{}" and strike>{} and strike<{} and Timesession="一般"  ;'.format(queryday,Contract,lower,upper)
generator_df = pd.read_sql(sql=sql,  # mysql query
                           con=dbconn)  # size you want to fetch each time  
print(generator_df)
df = pd.DataFrame(generator_df, columns=['Date', 'Type', 'Contract', 'Strike', 'Openinterest','id'])
print(df.dtypes)

from sqlalchemy.types import NVARCHAR, Float, Integer
dtypedict = {
'Date': NVARCHAR(length=255),
'Type': NVARCHAR(length=255),
'Contract': NVARCHAR(length=255),
'Strike': Integer(),
'Openinterest': Integer(),
'id': Integer()
}
print(df.dtypes)
engine2 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/cotdatabase?charset=utf8')
df.to_sql('dailytxooi', engine2, if_exists = 'replace',index=False, dtype=dtypedict)


# In[ ]:




