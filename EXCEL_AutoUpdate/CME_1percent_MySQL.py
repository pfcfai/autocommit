#!/usr/bin/python3.8
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


# In[3]:


def df_add_diff(df):    
    twcsv=df    
    diff=[]
    diff_in_per=[]
    for i in range(len(twcsv['Close'])):    
        if i==0:
            diff.append(0)
            diff_in_per.append(0)
        else:
            diff.append(round(twcsv['Close'][i]-twcsv['Close'][i-1],4))
            diff_in_per.append(round((twcsv['Close'][i]/twcsv['Close'][i-1]-1)*100,2))
            
    twcsv['diff']=diff
    twcsv['diff%']=diff_in_per
    
    return twcsv

for i in trange(len(df_ori),dynamic_ncols=True): # for each table
    
    tablename=df_ori.iloc[i][0] # querytable
    mod_name=df_ori.iloc[i][1]  # name of the commodity
    
    sql='select Date,Open,High,Low,Close from {} order by Date desc limit 504;'.format(tablename)
    generator_df = pd.read_sql(sql=sql,     # mysql query
                               con=dbconn)  # size you want to fetch each time (we choose 2-years data)  

    # re-arrange desc to asc
    generator_df=generator_df.sort_values(by=['Date'],ascending=True)
    generator_df.reset_index(drop=True, inplace=True)

    # add two columns and def filter (condition: 1% < diff% <2%)
    new_df=df_add_diff(generator_df) 
    new_df['filter']=df_add_diff(generator_df)['diff%'].between(1,2)
    
    my_dict=[]
    # record info. after the day meets condition
    for j in range(len(new_df['filter'])-1):
        mydict={}
        if new_df['filter'][j]==True:
            
            mydict['Date']=new_df['Date'][j]
            mydict['con_p']=new_df['diff%'][j]
            mydict['diff']=new_df['diff'][j+1]
            mydict['diff_p']=new_df['diff%'][j+1]
            mydict['id']=j
            my_dict.append(mydict)
    
    df_from_dict = pd.DataFrame(my_dict, columns=['Date', 'con_p', 'diff','diff_p','id'])
    
    engine2 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/webaiuse?charset=utf8')
    df_from_dict.to_sql('cme_'+str(1)+'percent_'+tablename, engine2, if_exists = 'replace',index=False)
    # to check statistic desc.
    # print(df_from_dict[df_from_dict['diff%']<0].describe()) 

    # make a list of statistic description 
    positive_count=df_from_dict[df_from_dict['diff_p']>=0].describe()['diff_p'].iloc[0]
    positive_avg  =round(df_from_dict[df_from_dict['diff_p']>=0].describe()['diff_p'].iloc[1],2)
    positive_max  =df_from_dict[df_from_dict['diff_p']>=0].describe()['diff_p'].iloc[7]
    negative_count=df_from_dict[df_from_dict['diff_p']<0].describe()['diff_p'].iloc[0]
    negative_avg  =round(df_from_dict[df_from_dict['diff_p']<0].describe()['diff_p'].iloc[1],2)
    negative_min  =df_from_dict[df_from_dict['diff_p']<0].describe()['diff_p'].iloc[3]
    positive_win  =round(positive_count/(positive_count+negative_count)*100,4)
    negative_win  =round(negative_count/(positive_count+negative_count)*100,4)
    positive_maxpt=round(df_from_dict[df_from_dict['diff']>=0].describe()['diff'].iloc[7],2)
    negative_maxpt=round(df_from_dict[df_from_dict['diff']<0].describe()['diff'].iloc[3],2)
    commod_list=[i+1,mod_name,positive_count,positive_avg,positive_max,negative_count,negative_avg,negative_min,positive_win,negative_win,positive_maxpt,negative_maxpt]
    
    # append lists to dataframe
    if i==0:
        header = ['id','mod_name','p_count','p_avg','p_max','n_count','n_avg','n_min','p_win','n_win','p_maxpt','n_maxpt']
        df=pd.DataFrame.from_records([commod_list],columns=header)
    else:
        new_row = pd.DataFrame([commod_list], columns=df.columns.tolist() )
        df = df.append(new_row, ignore_index=True)
print(df)


# In[4]:


# save to database (local and cloud)
#engine2 = create_engine('mysql+pymysql://root:root@localhost:3306/finance')
#df.to_sql('cme_'+str(1)+'percent', engine2, if_exists = 'replace',index=False)
engine2 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/webaiuse?charset=utf8')
df.to_sql('cme_'+str(1)+'percent', engine2, if_exists = 'replace',index=False)


# In[5]:


'''
dbsettings=["root","root","finance","cmetest"]

def df_to_mysql(dbsettings,dataFrame):
    
    sqlEngine = create_engine('mysql+pymysql://{}:{}@127.0.0.1/{}'.format(dbsettings[0],dbsettings[1],dbsettings[2]), pool_recycle=3600)
    dbConnection = sqlEngine.connect()

    try:
        frame = dataFrame.to_sql(dbsettings[3], dbConnection ,if_exists='replace',index=False);
    except ValueError as vx:
        print(vx)
    except Exception as ex:
        print(ex)
    else:
        print("Table %s created successfully." % dbsettings[3]);
    finally:
        dbConnection.close()

df_to_mysql(dbsettings,df)
'''


# In[ ]:




