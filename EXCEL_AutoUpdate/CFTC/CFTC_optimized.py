#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import requests
import io
import os
import zipfile
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns
import datetime


# 以下下載CFTC檔案

# In[ ]:

'''
for y in np.arange(2010, 2022, 1):
    url = f'https://www.cftc.gov/files/dea/history/fut_disagg_xls_{str(y)}.zip'
    file = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(file.content))
    z.extractall('rawdata/')
    z.close()

    files = os.listdir('rawdata/')
    latest_file = max(map(lambda x: 'rawdata/' + x, files), key = os.path.getctime)
    newname = f'rawdata/f_year_{y}{os.path.splitext(latest_file)[1]}'
    try:
        os.rename(latest_file, newname)
        print(f'Done: {newname}')
        continue
    except:
        print(f'{newname} already exists.')
        os.remove(latest_file)
        continue

for y in np.arange(2010, 2022, 1):
    url = f'https://www.cftc.gov/files/dea/history/dea_fut_xls_{str(y)}.zip'
    file = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(file.content))
    z.extractall('rawdata/')
    z.close()

    files = os.listdir('rawdata/')
    latest_file = max(map(lambda x: 'rawdata/' + x, files), key = os.path.getctime)
    latest_file_name = latest_file.split('/')[-1].split('.')[0]
    newname = f'rawdata/{latest_file_name}_{y}{os.path.splitext(latest_file)[1]}'
    try:
        os.rename(latest_file, newname)
        print(f'Done: {newname}')
        continue
    except:
        print(f'{newname} already exists.')
        os.remove(latest_file)
        continue


# 以下定義函數:
# concatRawdata : 將各年度同商品檔案資料合併 ,存成 cftcs_{prefix}_{newname}.csv
# updateCFTC    : 更新最近一次的CFTC 檔案資料 到 dataframe
# concatDf      : 將 價格、投機部位、管理部位 各別由 三個dataframe 整併成一個 dataframe

# In[2]:

'''
def concatRawdata(folder, CFTC_Contract_Market_Code, prefix, newname):
    output = []
    for name in os.listdir(folder):
        if prefix in name:
            temp = pd.read_excel(folder + name)
            temp = temp[temp['CFTC_Contract_Market_Code'] == CFTC_Contract_Market_Code]
            output.append(temp)
            print(name)
    output = pd.concat(output, axis = 0).sort_values('Report_Date_as_MM_DD_YYYY').reset_index(drop = True)
    output = output[~output['Report_Date_as_MM_DD_YYYY'].duplicated(keep='first')]
    output.to_csv(f'/home/targets/autocommit/EXCEL_AutoUpdate/CFTC/cftcs_{prefix}_{newname}.csv', index = False)
    return output


# In[3]:


def updateCFTC(old_cftc, CFTC_Contract_Market_Code, prefix, outputName):
    old_cftc['Report_Date_as_MM_DD_YYYY'] = pd.to_datetime(old_cftc['Report_Date_as_MM_DD_YYYY'])
    last_date = old_cftc['Report_Date_as_MM_DD_YYYY'].sort_values(ascending = False).iloc[0]
    target_year = (last_date + datetime.timedelta(7)).year
    if prefix == 'f_year':
        url = f'https://www.cftc.gov/files/dea/history/fut_disagg_xls_{str(target_year)}.zip'
    elif prefix == 'annual':
        url = f'https://www.cftc.gov/files/dea/history/dea_fut_xls_{str(target_year)}.zip'
    else:
        print('wrong prefix!!')
        return
    file = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(file.content))
    z.extractall('')
    z.close()

    df = pd.read_excel(f'{prefix}.xls')
    newDf = df[df['CFTC_Contract_Market_Code'] == CFTC_Contract_Market_Code].sort_values('Report_Date_as_MM_DD_YYYY', ascending = False)
    newDf['Report_Date_as_MM_DD_YYYY'] = pd.to_datetime(newDf['Report_Date_as_MM_DD_YYYY'])
    newDf = pd.concat([old_cftc, newDf[newDf['Report_Date_as_MM_DD_YYYY'] > last_date]], axis = 0, ignore_index = True).sort_values('Report_Date_as_MM_DD_YYYY')
    print(f'{outputName}')
    print('newest report date: {}'.format(newDf['Report_Date_as_MM_DD_YYYY'].iloc[-1]))
    newDf = newDf[~newDf['Report_Date_as_MM_DD_YYYY'].duplicated(keep='first')]
    # newDf.to_csv(f'{outputName}', index = False) #231116
    newDf.to_csv(f'/home/targets/autocommit/EXCEL_AutoUpdate/CFTC/{outputName}', index = False)
    print('saved successfully.')


# In[4]:


def concatDf(name:str, path_annual:str, path_f_year:str):
        dbconn=pymysql.connect(
            host="103.17.9.213",
            database= "pricedata_day",
            user="webmysql@actwebdb2",
            password="AIteam168",
            port=3306,
            charset='utf8',
            )
        sql = f'select Date, Close from {name} order by Date desc;'
        close = pd.read_sql(sql = sql, con = dbconn).sort_values('Date').reset_index(drop = True)
        close = close.set_index('Date')
        close.index= pd.to_datetime(close.index.map(lambda x: str(int(x))))
        dbconn.close()

        cols = ['Report_Date_as_MM_DD_YYYY', 'Open_Interest_All', 'NonComm_Positions_Long_All', 'NonComm_Positions_Short_All', 'Comm_Positions_Long_All', 'Comm_Positions_Short_All',                 'NonRept_Positions_Long_All', 'NonRept_Positions_Short_All']

        cftcs_annual_df = pd.read_csv(path_annual)
        df_1 = cftcs_annual_df[cols].set_index('Report_Date_as_MM_DD_YYYY')
        df_1.index = pd.to_datetime(df_1.index)
        cols = ['Report_Date_as_MM_DD_YYYY', 'Open_Interest_All',
                'Prod_Merc_Positions_Long_ALL', 'Prod_Merc_Positions_Short_ALL',
                'Swap_Positions_Long_All', 'Swap__Positions_Short_All',
                'M_Money_Positions_Long_ALL', 'M_Money_Positions_Short_ALL',
                'Other_Rept_Positions_Long_ALL', 'Other_Rept_Positions_Short_ALL']

        cftcs_f_year_df = pd.read_csv(path_f_year)
        df_2 = cftcs_f_year_df[cols].set_index('Report_Date_as_MM_DD_YYYY')
        df_2.index = pd.to_datetime(df_2.index)
        
        print('close', close.index[-1])
        print('annual', df_1.index[-1])
        print('f_year', df_2.index[-1])
        df = pd.concat([close, df_1, df_2], axis = 1).dropna()
        df = df.loc[:, ~df.columns.duplicated()]

        return df


# In[5]:

'''
執行步驟分開做:
    第一步 : concatRawdata 只需要做一次 ，因此下面的第一個cell 部分程式碼被註解掉
    第二步 : 同時執行更新與合併 ，結果存成 final_list 是 list of dataframes
'''

# In[7]:


commodity_list=["gold","palladium","platinum","silver","copper","light_crude_oil","gasoline","hot_fuel","natural_gas","corn","soybean_oil","soybean","wheat","soybean_flour"]
# commodity_UPL : CFTC_Contract_Market_Code
commodity_UPL=['088691','075651','076651','084691','085692','067651','111659','022651','023651','002602','007601','005602','001602','026603']
commodity_code=["gc","pa","pl","si","hg","cl","rb","ho","ng","zc","bo","zs","zw","sm"]
commodity_f_year_csv=['cftcs_f_year_gold.csv','cftcs_f_year_palladium.csv','cftcs_f_year_platinum.csv','cftcs_f_year_silver.csv','cftcs_f_year_copper.csv','cftcs_f_year_light_crude_oil.csv','cftcs_f_year_gasoline.csv','cftcs_f_year_hot_fuel.csv','cftcs_f_year_natural_gas.csv','cftcs_f_year_corn.csv','cftcs_f_year_soybean_oil.csv','cftcs_f_year_soybean.csv','cftcs_f_year_wheat.csv','cftcs_f_year_soybean_flour.csv']
commodity_annual_csv=['cftcs_annual_gold.csv','cftcs_annual_palladium.csv','cftcs_annual_platinum.csv','cftcs_annual_silver.csv','cftcs_annual_copper.csv','cftcs_annual_light_crude_oil.csv','cftcs_annual_gasoline.csv','cftcs_annual_hot_fuel.csv','cftcs_annual_natural_gas.csv','cftcs_annual_corn.csv','cftcs_annual_soybean_oil.csv','cftcs_annual_soybean.csv','cftcs_annual_wheat.csv','cftcs_annual_soybean_flour.csv']
cftcs_f_year=0
cftcs_annual=0
final_list=[]
a=0

# concatRawdata 只需要做一次 ，因此下面的程式碼註解掉
'''
for s,m,t,n,g in zip(commodity_list,commodity_UPL,commodity_code,commodity_f_year_csv,commodity_annual_csv):
    cftcs_f_year = concatRawdata('rawdata/', m, 'f_year', s)
    cftcs_annual= concatRawdata('rawdata/', m, 'annual', s)

'''


# In[8]:


folder_path='/home/targets/autocommit/EXCEL_AutoUpdate/CFTC/'
for s,m,t,n,g in zip(commodity_list,commodity_UPL,commodity_code,commodity_f_year_csv,commodity_annual_csv):
    # n_path = os.path.join(folder_path, n)
    # cftcs_f_year = pd.read_csv(n_path)
    cftcs_f_year = pd.read_csv(n)
    updateCFTC(cftcs_f_year, m, 'f_year',n)
    # g_path = os.path.join(folder_path, g)
    # cftcs_annual = pd.read_csv(g_path)
    cftcs_annual = pd.read_csv(g)
    updateCFTC(cftcs_annual, m, 'annual', g)

    a= concatDf(t, g, n )
    final_list.append(a)
    
print(final_list)


# 定義函數，並將 final_list 轉成 HighChart 可以讀的 JSON file
# combinelist : [a,b,c] , [d,e,f] => [[a,d],[b,e],[c,f]] , 因 HighChart 的TimeSeries吃這個格式，其中 a,b,c 為 JS Timestamp
# 
# 

# In[9]:


import datetime
import pytz
timezone = pytz.timezone("Asia/Taipei")

number_of_data=[630,629,630,626,630,409,452,468,276,630,630,630,424,630]
年月日=[]
import json
dict={}
dict1={}
dict2={}

def combinelist(list_x,list_y):
    res_list = []
    for (item1, item2) in zip(list_x,list_y):
        innerlist=[item1,item2]
        res_list.append(innerlist)
    return res_list

for i,q,j in zip(final_list,number_of_data,commodity_list):
    with_index=i.reset_index()
    日期=with_index["index"].tolist()
    for 準確日期 in 日期:
        #準確日期=準確日期.strftime("%Y-%m-%d")
        dtzone=timezone.localize(準確日期)
        tstamp = dtzone.timestamp()
        jststamp=int(round(tstamp))*1000+3600000*8 # highchart需要*1000 and 微調資料 +8小時
        年月日.append(jststamp)
        收盤=i["Close"].tolist()
        
    基金管理多方部位=i["M_Money_Positions_Long_ALL"].tolist()
    基金管理空方部位=i["M_Money_Positions_Short_ALL"].tolist()
    基金= [基金管理多方部位[w]-基金管理空方部位[w] for w in range(0,len(基金管理多方部位))]
    投機者多方部位=i["NonComm_Positions_Long_All"].tolist()
    投機者空方部位=i["NonComm_Positions_Short_All"].tolist()
    投機 = [投機者多方部位[z]-投機者空方部位[z] for z in range(0,len(投機者多方部位))]
    
    date_list=年月日[-q:]##date
    close_list=收盤[-q:]## close
    spect_list=投機[-q:]## non commercial
    commercial_list=基金[-q:]## m-money
    
    dict[j+"_close"]=     combinelist(date_list,close_list)
    dict[j+"_spect"]=     combinelist(date_list,spect_list)
    dict[j+"_commercial"]=combinelist(date_list,commercial_list)
    b=str(dict).replace("'","\"".replace(r"\n",""))
print(b)

with open(("/home/targets/autocommit/EXCEL_AutoUpdate/CFTC/CFTC_test.json"),"w") as json_file:
    json.dump(dict,json_file)

print('==== EOF ====')




