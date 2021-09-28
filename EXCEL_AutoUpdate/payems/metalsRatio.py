#!/usr/bin/env python
# coding: utf-8

# In[3]:


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


# In[5]:


# 金銀比  
sql='select t1.timestamp , t1.Close/t2.Close as ratio from pricedata_day.gc as t1 inner join pricedata_day.si as t2 on t1.timestamp=t2.timestamp order by timestamp desc;'
generator_df = pd.read_sql(sql=sql,     # mysql query
                               con=dbconn)  # size you want to fetch each time (we choose 2-years data) 
#print(generator_df)

# re-arrange desc to asc
generator_df=generator_df.sort_values(by=['timestamp'],ascending=True)
generator_df.reset_index(drop=True, inplace=True)
#print(generator_df)
dict=generator_df.values.tolist()
print(dict)

import json
with open('/home/spark/autocommit/EXCEL_AutoUpdate/payems/gc_si_ratio.json', 'w') as json_file:
    json.dump(dict, json_file)


# In[6]:


# 鉑金比
sql='select t1.timestamp , t2.Close/t1.Close as ratio from pricedata_day.gc as t1 inner join pricedata_day.pl as t2 on t1.timestamp=t2.timestamp order by timestamp desc;'
generator_df = pd.read_sql(sql=sql,     # mysql query
                               con=dbconn)  # size you want to fetch each time (we choose 2-years data) 
#print(generator_df)

# re-arrange desc to asc
generator_df=generator_df.sort_values(by=['timestamp'],ascending=True)
generator_df.reset_index(drop=True, inplace=True)
#print(generator_df)
dict=generator_df.values.tolist()
print(dict)

import json
with open('/home/spark/autocommit/EXCEL_AutoUpdate/payems/pl_gc_ratio.json', 'w') as json_file:
    json.dump(dict, json_file)


# In[7]:


# 鉑鈀比
sql='select t1.timestamp , t2.Close/t1.Close as ratio from pricedata_day.pa as t1 inner join pricedata_day.pl as t2 on t1.timestamp=t2.timestamp order by timestamp desc;'
generator_df = pd.read_sql(sql=sql,     # mysql query
                               con=dbconn)  # size you want to fetch each time (we choose 2-years data) 
#print(generator_df)

# re-arrange desc to asc
generator_df=generator_df.sort_values(by=['timestamp'],ascending=True)
generator_df.reset_index(drop=True, inplace=True)
#print(generator_df)
dict=generator_df.values.tolist()
print(dict)

import json
with open('/home/spark/autocommit/EXCEL_AutoUpdate/payems/pl_pa_ratio.json', 'w') as json_file:
    json.dump(dict, json_file)


# In[16]:


# 銅金比
sql='select t1.timestamp , t2.Close/t1.Close as ratio from pricedata_day.gc as t1 inner join pricedata_day.hg as t2 on t1.timestamp=t2.timestamp order by timestamp desc;'
generator_df = pd.read_sql(sql=sql,     # mysql query
                               con=dbconn)  # size you want to fetch each time (we choose 2-years data) 
#print(generator_df)

# re-arrange desc to asc
generator_df=generator_df.sort_values(by=['timestamp'],ascending=True)
generator_df.reset_index(drop=True, inplace=True)
#print(generator_df)

generator_df['pct_yoy'] = generator_df['ratio'].pct_change(252)
generator_df=generator_df.dropna()
del generator_df['ratio']
#print(generator_df)

dict=generator_df.values.tolist()
print(dict)

import json
with open('/home/spark/autocommit/EXCEL_AutoUpdate/payems/hg_gc_yoy.json', 'w') as json_file:
    json.dump(dict, json_file)

