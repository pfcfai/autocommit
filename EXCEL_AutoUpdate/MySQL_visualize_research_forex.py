#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-
import pymysql
import numpy as np
import time , datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#from mpl_finance import candlestick_ohlc
from tqdm import trange

# dbconnect
dbconn=pymysql.connect(
            host="103.17.9.213",
            database= "pricedata_day",
            user="webmysql@actwebdb2",
            password="AIteam168",
            port=3306,
            charset='utf8',
            )  


# In[6]:

tb=['ym','es','nq','twse','ec','jy','bp','cd','sf','ad','cl','ng','rb','ho','gc','si','hg','pl','pa','zs','zw','zc']
for i in range(len(tb)):
    
    name=['道瓊','標普500','那斯達克','台灣加權','歐元','日圓','英鎊','加幣','瑞郎','澳幣','輕原油','天然氣','無鉛汽油','熱燃油','金','銀','銅','鉑','鈀','黃豆','小麥','玉米']
    sql='select timestamp , Close from {} order by timestamp desc ;'.format(tb[i])
    generator_df = pd.read_sql(sql=sql,     # mysql query
                                   con=dbconn)  # size you want to fetch each time (we choose 2-years data) 
    #print(generator_df)

    # re-arrange desc to asc
    generator_df=generator_df.sort_values(by=['timestamp'],ascending=True)
    generator_df.reset_index(drop=True, inplace=True)
    #print(generator_df)
    dict=generator_df.values.tolist()
print('==daily seperate==')
print(dict)

    import json
    with open('/home/spark/autocommit/EXCEL_AutoUpdate/{}.json'.format(name[i]), 'w') as json_file:
        json.dump(dict, json_file)




