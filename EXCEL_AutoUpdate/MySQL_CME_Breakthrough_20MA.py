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


df_ori = pd.read_csv('/home/spark/autocommit/EXCEL_AutoUpdate/CME.csv',encoding='BIG5') # define query tables
tablelist=df_ori['mod_id'].tolist()
modnamelist=df_ori['mod_name'].tolist()


# In[3]:


print(df_ori['mod_id'].tolist())
print(df_ori['mod_name'].tolist())


# In[5]:


# make a list of statistic description 

def stat(df_from_dict):
    positive_count=df_from_dict[df_from_dict['result%']>=0].describe()['result'].iloc[0]
    positive_avg  =round(df_from_dict[df_from_dict['result%']>=0].describe()['result%'].iloc[1],2)
    positive_max  =round(df_from_dict[df_from_dict['result%']>=0].describe()['result%'].iloc[7],2)
    negative_count=df_from_dict[df_from_dict['result%']<0].describe()['result'].iloc[0]
    negative_avg  =round(df_from_dict[df_from_dict['result%']<0].describe()['result%'].iloc[1],2)
    negative_min  =round(df_from_dict[df_from_dict['result%']<0].describe()['result%'].iloc[3],2)
    positive_win  =round(positive_count/(positive_count+negative_count)*100,2)
    negative_win  =round(negative_count/(positive_count+negative_count)*100,2)
    positive_maxpt=round(df_from_dict[df_from_dict['result']>=0].describe()['result'].iloc[7],2)
    negative_maxpt=round(df_from_dict[df_from_dict['result']<0].describe()['result'].iloc[3],2)
    commod_list=[modnamelist[i],positive_count,positive_avg,positive_max,negative_count,negative_avg,negative_min,positive_win,negative_win,positive_maxpt,negative_maxpt]

    return commod_list


breakthrough_up=[]
breakthrough_dn=[]

for i in range(len(tablelist)):
    
    # 取得 需要的 df by mod
    
    sql='select Date,Open,High,Low,Close from {} order by Date desc limit 504;'.format(tablelist[i])
    generator_df = pd.read_sql(sql=sql,     # mysql query
                               con=dbconn)  # size you want to fetch each time (we choose 2-years data)  
    # re-arrange desc to asc
    generator_df=generator_df.sort_values(by=['Date'],ascending=True)
    generator_df.reset_index(drop=True, inplace=True)
    generator_df["20MA"]=generator_df["Close"].rolling(window=20).mean()
    generator_df["filter"]=generator_df['Close']>generator_df['20MA']
    generator_df["pct"]=generator_df['Close'].pct_change()*100
    # print(generator_df)
    

    # 篩選 符合條件 之資訊
    
    new_df=generator_df
    up_dict=[] # 篩選 符合 向上穿越的條件
    dn_dict=[] # 篩選 符合 向下穿越的條件
    
    for j in range(1,len(new_df['filter'])-1):
        updict={}
        dndict={}
        if new_df['filter'][j]==True and new_df['filter'][j-1]==False:

            updict['Date']=new_df['Date'][j]
            updict['con%']=new_df['pct'][j]
            updict['result%']=new_df['pct'][j+1]
            updict['result']=new_df['pct'][j+1]*new_df['Close'][j]/100

            up_dict.append(updict)
            
        elif new_df['filter'][j]==False and new_df['filter'][j-1]==True:
            
            dndict['Date']=new_df['Date'][j]
            dndict['con%']=new_df['pct'][j]
            dndict['result%']=new_df['pct'][j+1]
            dndict['result']=new_df['pct'][j+1]*new_df['Close'][j]/100

            dn_dict.append(dndict)

    df_from_updict = pd.DataFrame(up_dict, columns=['Date', 'con%', 'result%', 'result'])
    df_from_dndict = pd.DataFrame(dn_dict, columns=['Date', 'con%', 'result%', 'result'])
    # print(df_from_dict)
    
    breakthrough_up.append(stat(df_from_updict))
    breakthrough_dn.append(stat(df_from_dndict))

print(breakthrough_up)
print(breakthrough_dn)


# In[6]:


import json
mydict={}
mydict['breakthrough_long']=breakthrough_up
mydict['breakthrough_short']=breakthrough_dn

with open('/home/spark/autocommit/EXCEL_AutoUpdate/CME_breakthrough20MA.json', 'w') as json_file:
    json.dump(mydict, json_file)



import json

with open('.json', 'w') as json_file:
    json.dump(dict, json_file)

