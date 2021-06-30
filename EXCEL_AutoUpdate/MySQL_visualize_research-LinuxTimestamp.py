#!/usr/bin/env python
# coding: utf-8

# In[8]:


# -*- coding: utf-8 -*-
import pymysql
import numpy as np
import time , datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tqdm import trange

# dbconnect
dbconn=pymysql.connect(
            host="103.17.9.213",
            database= "calculate",
            user="webmysql@actwebdb2",
            password="AIteam168",
            port=3306,
            charset='utf8',
            )  


# In[33]:


dfname=['df1','df2','df3','df4','df5','df6','df7']
dictname=['d1','d2','d3','d4','d5','d6','d7']
tb=['quotesort','fx','metals','interestrates','equityindex','energy','agricultural']
for i in range(len(tb)):
    sql='select * from {} order by pct desc ;'.format(tb[i])
    dfname[i] = pd.read_sql(sql=sql, con=dbconn) 
    dictname[i]={}

    if i==0:
        dictname[i]["symbol"]=dfname[i]['symbol'].values.tolist()
        dictname[i]["symbol_eg"]=dfname[i]['symbol_eg'].values.tolist()
        dictname[i]["pct"]=dfname[i]['pct'].values.tolist()
    else:
        dictname[i]["symbol"]=dfname[i]['symbol'].values.tolist()
        dictname[i]["symbol_eg"]=dfname[i]['symbol_eg'].values.tolist()
        dictname[i]["pct"]=dfname[i]['pct'].values.tolist()
        dictname[i]["close"]=dfname[i]['close'].values.tolist()
    print(dictname[i])


# In[34]:


#取得 linuxtimestamp now , and transform it to datetime str
import datetime
import time
lt=time.time()
timestamp = datetime.datetime.fromtimestamp(lt)
print(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
print(datetime.datetime.now())
print('current epoch time:',time.time())


# In[36]:


finaldict={}
finaldict["sort"]=dictname[0]
finaldict["quote"]={}
finaldict["quote"]["fx"]=dictname[1]
finaldict["quote"]["metals"]=dictname[2]
finaldict["quote"]["interestrates"]=dictname[3]
finaldict["quote"]["equityindex"]=dictname[4]
finaldict["quote"]["energy"]=dictname[5]
finaldict["quote"]["agricultural"]=dictname[6]
finaldict["updateTimestamp"]=time.time()
print(finaldict)

import json
with open('/home/spark/autocommit/EXCEL_AutoUpdate/timestamp_test.json', 'w') as json_file:
    json.dump(finaldict, json_file)

print('updated')


