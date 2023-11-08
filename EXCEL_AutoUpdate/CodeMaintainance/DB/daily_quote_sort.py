# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 11:25:31 2019

@author: user
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 18:25:34 2019

@author: user
"""

import pandas as pd
import pymysql
import os
import re
import csv
import time
from sqlalchemy import create_engine
import numpy as np
import datetime

#ca_path = 'C:\\Users\\user\\Desktop\\MYSQL\\BaltimoreCyberTrustRoot.crt.pem'
#ssl={'ssl': {'ssl-ca': 'C:\\Users\\user\\Desktop\\MYSQL\\BaltimoreCyberTrustRoot.crt.pem'}}
# 存到mysql
def save_mysql(file, db):
    # engine2 = create_engine('mysql+pymysql://root:pfcfai@localhost:3306/calculate?charset=utf8')
    # file.to_sql(db, engine2, if_exists='replace', index=False)
    engine2 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/calculate?charset=utf8')
    file.to_sql(db, engine2, if_exists='replace', index=False)

engine = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/pricedata_day?charset=utf8')
# create_engine('mysql+pymysql://root:pfcfai@localhost:3306/pricedata_day?charset=utf8')
sql = '''
      show tables ;
      '''
df = pd.read_sql(sql, engine)
dic = {'ad': '澳幣', 'bo': '黃豆油', 'bp': '英鎊', 'cd': '加幣', 'cl': '輕原油', 'cn':'富時中國A50',
       'ec': '歐元', 'ed': '歐美元', 'es': '小s&p', 'ff': '30天利率', 'fv': '美五年債',
       'gc': '黃金', 'hg': '銅', 'jy': '日幣', 'lc': '活牛', 'lh': '瘦豬', 'ng': '天然氣',
       'nq': '小那斯達克', 'nv': '紐幣', 'pa': '鈀金', 'pl': '白金', 'sf': '瑞郎',
       'si': '白銀', 'sm': '黃豆粉', 'tu': '美二年債', 'twse': '加權指數', 'txf': '台指期',
       'ty': '美十年債', 'us': '美長債', 'wn': '美超長債', 'ym': '小道瓊', 'zc': '玉米',
       'zs': '黃豆','zw':'小麥','ho':'熱燃油','rb':'汽油'}

ch_name = pd.DataFrame.from_dict(dic, orient='index', columns=['ch_name'])
table = pd.DataFrame(columns=['symbol_eg', 'pct'])
for symbol in df.iloc[:, 0]:
    if symbol == 'totalpricedata' or symbol == 'apipricedata' or symbol =='Sortdic' or symbol == 'apipricedata2' :
        continue
    sql = '''
      select * from %s ORDER BY date desc limit 2 ;
      ''' % (symbol)
    quote_table = pd.read_sql(sql, engine)

    quote_table.index = [symbol, symbol]
    print(quote_table)
    quote = quote_table['Close'].to_frame()
    quote['pct'] = quote.Close.pct_change(-1) * 100
    quote['pct'] = quote['pct'].round(2)
    quote['diff'] = quote.Close.diff(-1)
    quote['close'] = quote_table.Close
    quote = quote.dropna().reset_index().drop(['Close'], axis=1)
    quote.columns = ['symbol_eg', 'pct', 'diff','close']
    table = pd.concat([table, quote], axis=0,sort=True)

date = int(quote_table['Date'].iloc[0])

table = table.sort_values(by='pct', ascending=False).round(4).reset_index(drop=True)
table.index = table.symbol_eg
table['symbol'] = ch_name
table = table.reset_index(drop=True)
#table = table[['symbol', 'pct', 'diff','close']].reset_index(drop=True)

##取前幾大
top_5 = table.nlargest(7, 'pct')
last_5 = table.nsmallest(7, 'pct')
result = pd.concat([top_5, last_5], axis=0).sort_values(by='pct', ascending=False)
result['id'] = list(range(len(result)))
result = result[['symbol','symbol_eg', 'pct','close','id']]

save_mysql(result, 'quotesort')

#
#
#分類行情

metals =['黃金','銅','鈀金','白金','白銀']
equity_Index=['小s&p','小那斯達克','台指期','小道瓊']
energy =['輕原油','天然氣','熱燃油','汽油']
agricultural =['黃豆油','黃豆粉','玉米','黃豆','小麥','活牛','瘦豬',]
fx =['澳幣','英鎊','加幣','歐元','日幣','紐幣','瑞郎']
interest_rates =['歐美元','美五年債','美二年債','美十年債','美長債','美超長債','30天利率',]

categories = {'metals':metals,
              'equityindex':equity_Index,
              'energy':energy,
              'agricultural':agricultural,
              'fx':fx,
              'interestrates':interest_rates}
for category in categories:
    temp = table[table.symbol.isin(categories[category])] #.nlargest(3,'pct')
    temp = temp.iloc[(-temp.pct.abs()).argsort()] #.iloc[:3,:]
    temp['id'] = list(range(len(temp)))
    save_mysql(temp,category)




## 時間轉時間戳
#def to_timestamp(x):
#    timestamp = time.mktime(datetime.datetime.strptime(x, "%Y%m%d").timetuple())
#    return timestamp
#    
#df['timestamp'] = Date.apply(to_timestamp)*1000


# 讀資料庫
# engine = create_engine('mysql+pymysql://miles:Aa12345678@192.168.204.40:3306/calculate')
#
# sql = '''
#  select * from `fx` order by pct desc ;
#  '''
# check_table = pd.read_sql(sql,engine)