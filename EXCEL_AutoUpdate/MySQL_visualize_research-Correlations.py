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


# In[2]:


# tablenames=['es','nq','ym','ad','bp','cd','ec','jy','sf','zc','zs','zw','gc','si','cl','ty','us']
dfname=['df1','df2','df3','df4','df5','df6','df7','df8','df9','df10','df11','df12','df13','df14','df15','df16','df17']
for i in range(17):
    tb=['ym','nq','es','ec','jy','bp','cd','sf','ad','ty','gc','si','hg','cl','zs','zw','zc']
    sql='select Date,timestamp,Close from {} order by timestamp desc limit 21;'.format(tb[i])
    dfname[i] = pd.read_sql(sql=sql, con=dbconn) 
    dfname[i]=dfname[i].sort_values(by=['timestamp'],ascending=True)
    dfname[i].reset_index(drop=True, inplace=True)
    dfname[i]['pct_{}'.format(tb[i])]=dfname[i]['Close'].pct_change()
    #dfname[i]=dfname[i].set_index('Date').drop(['Close'], axis=1).drop(['timestamp'], axis=1)
    dfname[i]=dfname[i].set_index('timestamp').drop(['Close'], axis=1).drop(['Date'], axis=1)
    #print(dfname[i])


temp = pd.DataFrame()

temp = pd.concat([dfname[0],dfname[1],dfname[2],dfname[3],dfname[4],dfname[5],dfname[6],dfname[7],dfname[8],dfname[9],dfname[10],dfname[11],dfname[12],dfname[13],dfname[14],dfname[15],dfname[16]],join="inner",axis=1)
#temp2 = pd.concat([dfname[3],dfname[4],dfname[5],dfname[6],dfname[7],dfname[8]],join="inner",axis=1)
print(temp)



# In[3]:


#plt.scatter(dfname[0]['pct_gc'],dfname[1]['pct_si'])
#plt.show()
#corr=dfname[0]['pct_gc'].corr(dfname[1]['pct_si'])
#print('correlation:',corr)
corr_mtx=temp.corr()

print(corr_mtx)


# In[4]:


mylist=[]
for m in range(17):
    for n in range(17):
        innerlist=[]
        innerlist.append(m)
        innerlist.append(n)
        innerlist.append(round(corr_mtx.iloc[m][n],2))
        mylist.append(innerlist)
        #print(mylist)
        
import json
with open('corr_dailyupdate.json', 'w') as json_file:
    json.dump(mylist, json_file)
       
from datetime import datetime
print(datetime.today().strftime('%Y-%m-%d') )
today=datetime.today().strftime('%Y-%m-%d')
print('updated {}'.format(today))






