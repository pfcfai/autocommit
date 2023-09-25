#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
for y in np.arange(2010, 2023, 1):
    url = f'https://www.cftc.gov/files/dea/history/fut_fin_xls_{str(y)}.zip'
    file = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(file.content))
    z.extractall('rawdata2/')
    z.close()

    files = os.listdir('rawdata2/')
    latest_file = max(map(lambda x: 'rawdata2/' + x, files), key = os.path.getctime)
    newname = f'rawdata2/FinFutYY_{y}{os.path.splitext(latest_file)[1]}'
    try:
        os.rename(latest_file, newname)
        print(f'Done: {newname}')
        continue
    except:
        print(f'{newname} already exists.')
        os.remove(latest_file)
        continue

for y in np.arange(2010, 2023, 1):
    url = f'https://www.cftc.gov/files/dea/history/dea_fut_xls_{str(y)}.zip'
    file = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(file.content))
    z.extractall('rawdata2/')
    z.close()

    files = os.listdir('rawdata2/')
    latest_file = max(map(lambda x: 'rawdata2/' + x, files), key = os.path.getctime)
    latest_file_name = latest_file.split('/')[-1].split('.')[0]
    newname = f'rawdata2/{latest_file_name}_{y}{os.path.splitext(latest_file)[1]}'
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

# In[ ]:

'''
def concatRawdata(folder,CFTC_Contract_Market_Code, prefix, newname):
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


# In[ ]:


def updateCFTC(old_cftc,CFTC_Contract_Market_Code, prefix, outputName):
    old_cftc['Report_Date_as_MM_DD_YYYY'] = pd.to_datetime(old_cftc['Report_Date_as_MM_DD_YYYY'])
    last_date = old_cftc['Report_Date_as_MM_DD_YYYY'].sort_values(ascending = False).iloc[0]
    target_year = (last_date + datetime.timedelta(7)).year
    if prefix == 'FinFutYY':
        url = f'https://www.cftc.gov/files/dea/history/fut_fin_xls_{str(target_year)}.zip'
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
    newDf.to_csv(f'{outputName}', index = False)
    print('saved successfully.')


# In[ ]:


def concatDf(name:str, path_annual:str, path_FinFutYY:str):
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

        cols = ['Report_Date_as_MM_DD_YYYY', 'Open_Interest_All','NonComm_Positions_Long_All','NonComm_Positions_Short_All']
        cftcs_annual_df = pd.read_csv(path_annual)
        df_1 = cftcs_annual_df[cols].set_index('Report_Date_as_MM_DD_YYYY')
        df_1.index = pd.to_datetime(df_1.index)
       
        
        cols = ['Report_Date_as_MM_DD_YYYY','Open_Interest_All','Lev_Money_Positions_Long_All','Lev_Money_Positions_Short_All']
        cftcs_FinFutYY_df = pd.read_csv(path_FinFutYY)
        df_2 = cftcs_FinFutYY_df[cols].set_index('Report_Date_as_MM_DD_YYYY')
        df_2.index = pd.to_datetime(df_2.index)
    
        
        print('close', close.index[0])
        print('annual', df_1.index[0])
        print('FinFutYY', df_2.index[0])
        df = pd.concat([close,df_1,df_2], axis = 1).dropna() 
        df = df.loc[:, ~df.columns.duplicated()]
    
        return df
    


# 由於美元是不同交易所的商品，因此需要另外寫一個條件給他

# In[ ]:


def concatDf_from_apipricedata(name:str,path_annual:str, path_FinFutYY:str):
    dbconn=pymysql.connect(
    host="103.17.9.213",
    database= "pricedata_day",
    user="webmysql@actwebdb2",
    password="AIteam168",
    port=3306,
    charset='utf8',
    )
    
    sql = f'select Date, Close from apipricedata where Symbol="{name}" order by Date desc;'
    
    close = pd.read_sql(sql = sql, con = dbconn).sort_values('Date').reset_index(drop = True)
    close = close.set_index('Date')
    close.index= pd.to_datetime(close.index.map(lambda x: str(int(x))))
    dbconn.close()


    cols = ['Report_Date_as_MM_DD_YYYY', 'Open_Interest_All','NonComm_Positions_Long_All','NonComm_Positions_Short_All']
    cftcs_annual_df = pd.read_csv(path_annual)  
    df_1 = cftcs_annual_df[cols].set_index('Report_Date_as_MM_DD_YYYY')
    df_1.index = pd.to_datetime(df_1.index)
   
       
        
    cols = ['Report_Date_as_MM_DD_YYYY','Open_Interest_All','Lev_Money_Positions_Long_All','Lev_Money_Positions_Short_All']
    cftcs_FinFutYY_df = pd.read_csv(path_FinFutYY)
    df_2 = cftcs_FinFutYY_df[cols].set_index('Report_Date_as_MM_DD_YYYY')
    df_2.index = pd.to_datetime(df_2.index)
    
    print('close', close.index[0])
    print('annual', df_1.index[0])
    print('FinFutYY', df_2.index[0])
    
    
    df = pd.concat([close,df_1,df_2], axis = 1).dropna() 
    df = df.loc[:, ~df.columns.duplicated()]
   
    return df


# 以下跑迴圈，目的是為了讓電腦有FinFuttYY，annual的檔案，方便我們做下一步，此處有包含美元

# In[ ]:
# concatRawdata 只需要做一次 ，因此下面的程式碼註解掉
'''
commodity_list=['NASDAQ','DJ','mini_sp','USD','AUD','BP','NZD','SF','EUD','JPY','CAD','thirtyDAY_FEDERAL_FUNDS','threeMONTH_EURODOLLARS','twoYEAR_US_TREASURY_NOTES','fiveYEAR_US_TREASURY_NOTES','tenYEAR_US_TREASURY_NOTES','US_TREASURY_BONDS','LONG_TERM_US_TREASURY_BONDS']
commodity_UPL=['209742','124603','13874A','098662','232741','096742','112741',
                '092741','099741','097741','090741','045601','132741',
                '042601','044601','043602','020601','020604']      
for s,m in zip(commodity_list,commodity_UPL):
    
    try:
        cftcs_FinFutYY = concatRawdata('rawdata2/', m, 'FinFutYY', s)
        cftcs_annual= concatRawdata('rawdata2/', m, 'annual', s)  
    except Exception as e:
        print(e)
        print("檢查列表是否有錯誤")            

'''

# 以下跑迴圈，把已知的東西帶入之前所定義的函式，得出由dataframe所組成的list，此處沒有包含美元，包含美元的程式碼在最下方，未完成

# In[ ]:


commodity_list=['NASDAQ','DJ','mini_sp','USD','AUD','BP','NZD','SF','EUD','JPY','CAD','thirtyDAY_FEDERAL_FUNDS','threeMONTH_EURODOLLARS','twoYEAR_US_TREASURY_NOTES','fiveYEAR_US_TREASURY_NOTES','tenYEAR_US_TREASURY_NOTES','US_TREASURY_BONDS','LONG_TERM_US_TREASURY_BONDS']
commodity_UPL=['209742','124603','13874A','098662','232741','096742','112741',
                '092741','099741','097741','090741','045601','132741',
                '042601','044601','043602','020601','020604']
commodity_code=['nq','ym','es','dx','ad','bp','nv','sf','ec','jy','cd','ff','ed','tu','fv','ty','us','wn']

commodity_FinFutYY_csv=['cftcs_FinFutYY_NASDAQ.csv','cftcs_FinFutYY_DJ.csv','cftcs_FinFutYY_mini_sp.csv','cftcs_FinFutYY_USD.csv',
                        'cftcs_FinFutYY_AUD.csv','cftcs_FinFutYY_BP.csv','cftcs_FinFutYY_NZD.csv','cftcs_FinFutYY_SF.csv',
                        'cftcs_FinFutYY_EUD.csv','cftcs_FinFutYY_JPY.csv','cftcs_FinFutYY_CAD.csv',
                        'cftcs_FinFutYY_thirtyDAY_FEDERAL_FUNDS.csv','cftcs_FinFutYY_threeMONTH_EURODOLLARS.csv','cftcs_FinFutYY_twoYEAR_US_TREASURY_NOTES.csv','cftcs_FinFutYY_fiveYEAR_US_TREASURY_NOTES.csv'
                        ,'cftcs_FinFutYY_tenYEAR_US_TREASURY_NOTES.csv','cftcs_FinFutYY_US_TREASURY_BONDS.csv','cftcs_FinFutYY_LONG_TERM_US_TREASURY_BONDS.csv']

commodity_annual_csv=['cftcs_annual_NASDAQ.csv','cftcs_annual_DJ.csv','cftcs_annual_mini_sp.csv','cftcs_annual_USD.csv',
                        'cftcs_annual_AUD.csv','cftcs_annual_BP.csv','cftcs_annual_NZD.csv','cftcs_annual_SF.csv',
                        'cftcs_annual_EUD.csv','cftcs_annual_JPY.csv','cftcs_annual_CAD.csv',
                        'cftcs_annual_thirtyDAY_FEDERAL_FUNDS.csv','cftcs_annual_threeMONTH_EURODOLLARS.csv','cftcs_annual_twoYEAR_US_TREASURY_NOTES.csv','cftcs_annual_fiveYEAR_US_TREASURY_NOTES.csv'
                        ,'cftcs_annual_tenYEAR_US_TREASURY_NOTES.csv','cftcs_annual_US_TREASURY_BONDS.csv','cftcs_annual_LONG_TERM_US_TREASURY_BONDS.csv']    
final_list=[]
a=0

for s,m,t,n,g in zip(commodity_list,commodity_UPL,commodity_code,commodity_FinFutYY_csv,commodity_annual_csv):
    if s== "USD":
        try:
            cftcs_FinFutYY = pd.read_csv(n)
            updateCFTC(cftcs_FinFutYY, m, 'FinFutYY',n)
            cftcs_annual = pd.read_csv(g)
            updateCFTC(cftcs_annual, m, 'annual', g)
          
            a= concatDf_from_apipricedata(t, g, n )
            final_list.append(a)
            
        except Exception as e: 
            print(e)
            print("請逐項檢查列表中的元素是否正確")
            
    else:
        try:
            cftcs_FinFutYY = pd.read_csv(n)
            updateCFTC(cftcs_FinFutYY, m, 'FinFutYY',n)
            cftcs_annual = pd.read_csv(g)
            updateCFTC(cftcs_annual, m, 'annual', g)
    
            a= concatDf(t, g, n )
            final_list.append(a)
        except Exception as e: 
            print(e)
            print("請逐項檢查列表中的元素是否正確")
            
print(final_list)


# 以下跑迴圈，並定義函數，並將 final_list 轉成 HighChart 可以讀的 JSON file
# combinelist : [a,b,c] , [d,e,f] => [[a,d],[b,e],[c,f]] , 因 HighChart 的TimeSeries吃這個格式，其中 a,b,c 為 JS Timestamp

# In[ ]:


import datetime
import pytz
timezone = pytz.timezone("Asia/Taipei")

number_of_data=[604,604,604,603,604,604,604,604,604,604,604,602,604,604,602,604,604,604]
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
        
    槓桿基金多方部位=i['Lev_Money_Positions_Long_All'].tolist()
    槓桿基金空方部位=i['Lev_Money_Positions_Short_All'].tolist()
    槓桿基金= [槓桿基金多方部位[w]-槓桿基金空方部位[w] for w in range(0,len(槓桿基金多方部位))]
    投機者多方部位=i["NonComm_Positions_Long_All"].tolist()
    投機者空方部位=i["NonComm_Positions_Short_All"].tolist()
    投機 = [投機者多方部位[z]-投機者空方部位[z] for z in range(0,len(投機者多方部位))]
    
    date_list=年月日[-q:]##date
    close_list=收盤[-q:]## close
    spect_list=投機[-q:]## non commercial
    commercial_list=槓桿基金[-q:]## m-money
    
    dict[j+"_close"]=     combinelist(date_list,close_list)
    dict[j+"_spect"]=     combinelist(date_list,spect_list)
    dict[j+"_commercial"]=combinelist(date_list,commercial_list)
    b=str(dict).replace("'","\"".replace(r"\n",""))
print(b)

with open(("CFTC_test2.json"),"w") as json_file:
    json.dump(dict,json_file)


# In[ ]:
print('==== EOF ====')



