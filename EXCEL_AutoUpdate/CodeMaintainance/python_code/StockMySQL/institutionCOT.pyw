# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 13:55:22 2019

@author: user
== bug notes ==
排程周一到週五，若遇假日無資料會跳bug
因此如果有bug，隔天沒問題的話，可以不需理會
"""


import pandas as pd
from sqlalchemy import create_engine
import pymysql
import numpy as np
import time
import datetime
from line_notify import error_msg

try:
    #response = urllib2.urlopen("http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=20190410&type=ALL")
    #
    #html_doc = response.read()
    todaydate = time.strftime("%Y%m%d",time.localtime())

    
    #ca_path = 'C:\\Users\\user\\Desktop\\MYSQL\\BaltimoreCyberTrustRoot.crt.pem'
    #ssl={'ssl': {'ssl-ca': 'C:\\Users\\user\\Desktop\\MYSQL\\BaltimoreCyberTrustRoot.crt.pem'}}
    year = int(todaydate[:4])-1911
    month = todaydate[4:6]
    day = todaydate[6:]
    
    # url="https://www.twse.com.tw/fund/T86?response=csv&date="+todaydate+"&selectType=ALLBUT0999" 2023/03/19 證交所網頁改版
    url="https://www.twse.com.tw/pcversion/fund/T86?response=csv&date="+todaydate+"&selectType=ALLBUT0999"
    url2="https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?l=zh-tw&o=csv&se=EW&t=D&d="+str(year)+"/"+month+"/"+str(day)+"&s=0,asc"
    timestampvalue = int(time.mktime(datetime.datetime.strptime(todaydate, "%Y%m%d").timetuple())*1000)
    
    
    #股票價格資料
    stockurl="http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date="+todaydate+"&type=ALLBUT0999"
    stockurl2="https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&o=csv&d="+str(year)+"/"+month+"/"+str(day)+"&s=0,asc,0"
    stocktwcsv=pd.read_csv(stockurl,encoding='ANSI',header=None,names = list(range(0,16))) 
    stocktwocsv=pd.read_csv(stockurl2,encoding='ANSI',header=None,names = list(range(0,16))) 
    
    
    #股票價格櫃買資料
    stocktwolen = stocktwocsv[stocktwocsv[0].str.len() ==4]
    def rep2(n):
        return (n.str.extract(r'(\d{4})',expand=False))
    stocktwofilt = stocktwolen.iloc[:,0].str.extract(r'(\d{4})').dropna()
    stocktwoindex=list(stocktwofilt.index)
    stocktwocsv2=stocktwocsv.iloc[stocktwoindex][:]
    #股票價格上市資料
    stockfiltstart = stocktwcsv[0]== '="0050"'
    stockstartindex =stocktwcsv[stockfiltstart][0].index.values[0]
    
    stockcsv2 = stocktwcsv.iloc[stockstartindex:,:9]
    stockcsv2.iloc[:,0] = stockcsv2.iloc[:,0].str.extract(r'(\d+[A-Z]?)')
    
    stockdatalist =pd.concat([stocktwocsv2.iloc[:,:2],stockcsv2.iloc[:,:2]],axis=0).reset_index(drop=True)
    
    
    
    #data=pd.read_csv(url,encoding='big5')
    twcsv=pd.read_csv(url,encoding='ANSI',header=None,names = list(range(0,19))).sort_values(by=0,ascending=True).reset_index(drop=True)
    twocsv=pd.read_csv(url2,encoding='ANSI',header=None,names = list(range(0,24))) 
    
    #上市資料
    filtstart = twcsv[0]== 'ETF證券代號第六碼為K、M、S、C者，表示該ETF以外幣交易。'
    endindex =twcsv[filtstart][0].index.values[0]
    csv2 = twcsv.iloc[1:endindex,:19]
    csv2['日期'] = todaydate
    csv2.iloc[:,0] = csv2.iloc[:,0].str.extract(r'(\d+[A-Z]?)')
    finalcsv = pd.concat([csv2.iloc[:,19:20],csv2.iloc[:,:19]],axis = 1)
    #finalcsv.columns = ['日期','股票代號','股票名稱','外陸資買進股數(不含外資自營商)','外陸資賣出股數(不含外資自營商)','外陸資買賣超股數(不含外資自營商)','外資自營商買進股數','外資自營商賣出股數','外資自營商買賣超股數','投信買進股數','投信賣出股數','投信買賣超股數','自營商買賣超股數','自營商買進股數(自行買賣)','自營商賣出股數(自行買賣)','自營商買賣超股數(自行買賣)','自營商買進股數(避險)','自營商賣出股數(避險)','自營商買賣超股數(避險)','三大法人買賣超股數']
    finalcsv.columns =['日期','股票代號','股票名稱','外陸資買進股數不含外資自營商','外陸資賣出股數不含外資自營商','外陸資買賣超股數不含外資自營商','外資自營商買進股數','外資自營商賣出股數','外資自營商買賣超股數','投信買進股數','投信賣出股數','投信買賣超股數','自營商買賣超股數','自營商買進股數自行買賣','自營商賣出股數自行買賣','自營商買賣超股數自行買賣','自營商買進股數避險','自營商賣出股數避險','自營商買賣超股數避險','三大法人買賣超股數']
        
    #finalcsv['timestamp'] = timestampvalue
    #上櫃資料
    twolen = twocsv[twocsv[0].str.len() ==4]
    twofilt = twolen.iloc[:,0].str.extract(r'(\d{4})').dropna()
    twoindex=list(twofilt.index)
    twocsv2=twocsv.iloc[twoindex][:]
    twocsv2['日期'] = todaydate
    twofinalcsv = pd.concat([twocsv2.iloc[:,24:25],twocsv2.iloc[:,:8],twocsv2.iloc[:,11:14],twocsv2.iloc[:,22:23],twocsv2.iloc[:,14:20],twocsv2.iloc[:,23:24]],axis = 1)
    twofinalcsv.columns = ['日期','股票代號','股票名稱','外陸資買進股數不含外資自營商','外陸資賣出股數不含外資自營商','外陸資買賣超股數不含外資自營商','外資自營商買進股數','外資自營商賣出股數','外資自營商買賣超股數','投信買進股數','投信賣出股數','投信買賣超股數','自營商買賣超股數','自營商買進股數自行買賣','自營商賣出股數自行買賣','自營商買賣超股數自行買賣','自營商買進股數避險','自營商賣出股數避險','自營商買賣超股數避險','三大法人買賣超股數']
    
    #twofinalcsv['timestamp'] = timestampvalue
    
    totalcsv = pd.concat([finalcsv,twofinalcsv],axis=0).reset_index(drop=True)
    
    stockdatalist.columns =['股票代號','股票名稱']
    stockdatalistdic = stockdatalist.set_index('股票代號').to_dict()['股票名稱']
    
    countlist = pd.concat([totalcsv.iloc[:,1:3],stockdatalist],axis=0)
    countlistsss =countlist['股票代號'].value_counts().reset_index().drop_duplicates()
    countfilt = countlistsss['股票代號']==1
    finalcountlist = countlistsss[countfilt]
    
    finalcountlist.columns=['股票代號','次數']
    finalcountlist['股票名稱'] = finalcountlist['股票代號'].map(stockdatalistdic)
    finalcountlist['日期'] = todaydate
    finalSQLcount = pd.concat([finalcountlist.iloc[:,3],finalcountlist.iloc[:,0],finalcountlist.iloc[:,2]],axis=1)
    finalSQLcount['1'],finalSQLcount['2'],finalSQLcount['17'],finalSQLcount['3'],finalSQLcount['4'],finalSQLcount['5'],finalSQLcount['6'],finalSQLcount['7'],finalSQLcount['8'],finalSQLcount['9'],finalSQLcount['10'],finalSQLcount['11'],finalSQLcount['12'],finalSQLcount['13'],finalSQLcount['14'],finalSQLcount['15'],finalSQLcount['16'] = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    finalSQLcount.columns = ['日期','股票代號','股票名稱','外陸資買進股數不含外資自營商','外陸資賣出股數不含外資自營商','外陸資買賣超股數不含外資自營商','外資自營商買進股數','外資自營商賣出股數','外資自營商買賣超股數','投信買進股數','投信賣出股數','投信買賣超股數','自營商買賣超股數','自營商買進股數自行買賣','自營商賣出股數自行買賣','自營商買賣超股數自行買賣','自營商買進股數避險','自營商賣出股數避險','自營商買賣超股數避險','三大法人買賣超股數']
    
    for QQQ in range(3,20):
        totalcsv.iloc[:,QQQ] = totalcsv.iloc[:,QQQ].str.replace(',','')
    engine2 = create_engine('mysql+pymysql://root:pfcfai@localhost:3306/stockdata_day')
    totalcsv.to_sql('stockcotdata', engine2, if_exists = 'append',index=False)
    engine2 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/stockdata_day?charset=utf8')
    totalcsv.to_sql('stockcotdata', engine2, if_exists = 'append',index=False)
        
    #無三大法人交易
    engine2 = create_engine('mysql+pymysql://root:pfcfai@localhost:3306/stockdata_day')
    finalSQLcount.to_sql('stockcotdata', engine2, if_exists = 'append',index=False)
    engine2 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/stockdata_day?charset=utf8')
    finalSQLcount.to_sql('stockcotdata', engine2, if_exists = 'append',index=False)
except:
    error_msg()
