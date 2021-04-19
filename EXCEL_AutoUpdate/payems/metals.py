#!/usr/bin/env python
# coding: utf-8

# In[13]:


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


# In[15]:


tablenames=["gc","si","hg","pl","pa"]
for i in tablenames:
    
    sql='select timestamp , Close from {} order by timestamp desc limit 504;'.format(i)
    generator_df = pd.read_sql(sql=sql,     # mysql query
                                   con=dbconn)  # size you want to fetch each time (we choose 2-years data) 
    print(generator_df)

    # re-arrange desc to asc
    generator_df=generator_df.sort_values(by=['timestamp'],ascending=True)
    generator_df.reset_index(drop=True, inplace=True)
    print(generator_df)
    dict=generator_df.values.tolist()
    print(dict)

    import json
    with open('/home/spark/autocommit/EXCEL_AutoUpdate/payems/{}.json'.format(i), 'w') as json_file:
        json.dump(dict, json_file)


