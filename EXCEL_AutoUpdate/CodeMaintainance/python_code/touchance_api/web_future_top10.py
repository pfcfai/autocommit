# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 15:28:34 2020

@author: user
"""
import sys
import time
from tcoreapi_mq import * 
import tcoreapi_mq
import threading
import datetime
import pandas as pd
from sqlalchemy import create_engine

#讀取期貨保證金表格
future_table = pd.read_html("https://www.taifex.com.tw/cht/5/stockMarginingDetail")
#aa = time.strftime('%H:%M:%S', time.localtime())
future_table = future_table[0]
# future_table.columns=future_table.iloc[0,:]
# future_table = future_table.drop([0]).reset_index(drop=True)
future_table = future_table[['股票期貨英文代碼','股票期貨標的證券代號','股票期貨中文簡稱','原始保證金適用比例']]
future_table['目前價格'] = 0
future_table['漲跌'] = 0
future_table['漲跌幅'] = 0
future_table['震幅'] = 0
future_table['原始保證金'] = 0
future_table['成交量'] = 0
future_table['時間'] = 0
future_table['id'] = 0
future_table['id'] = [i for i in range(len(future_table.股票期貨英文代碼))]
#future_table['test'] = 0
future_table.columns = ['future_code','stock_code','stock_name','money_percent','price','change','change_p','highlow_p','origin_money','volume','time','id']
future_table.money_percent = future_table.money_percent.str.rstrip('%').astype('float') / 100

temp_time = 0
g_TradeZMQ = None
g_QuoteZMQ = None
g_TradeSession = ""
g_QuoteSession = ""

oTime = datetime.datetime.strptime('08:43','%H:%M').time()
cTime = datetime.datetime.strptime('13:46','%H:%M').time()

#判斷合約月份
now = datetime.datetime.now()
m = now.month
y = now.year
d = now.day
first_weekday = datetime.date(year=y, month=m, day=1).weekday()+1
multi = 2 if 3-first_weekday >=0 else 3
settle_day = 3 - first_weekday + 7*multi +1
plus = 1 if d > settle_day else 0

contract = f'{y}{m+plus:02}'

#實時行情回補
def OnRealTimeQuote(symbol):
    if len(symbol['TradingPrice'])>0:
        global future_table
        global temp_time
        global cTime
        future_symbol = symbol['Symbol'].split('.')[3]
        price = float(symbol['TradingPrice'])
        try:
            future_table.loc[future_table.future_code==future_symbol,'price']=float(symbol['TradingPrice'])
            future_table.loc[future_table.future_code==future_symbol,'change']=float(symbol['Change'])
            future_table.loc[future_table.future_code==future_symbol,'change_p']=round(float(symbol['Change'])/float(symbol['YClosedPrice'])*100,2)
            future_table.loc[future_table.future_code==future_symbol,'highlow_p']=round((float(symbol['HighPrice'])-float(symbol['LowPrice']))/float(symbol['YClosedPrice'])*100,2)
        except ValueError:
            print(f'股票 :{symbol["SecurityName"]} 成交量 :{symbol["TradeVolume"]}')
            g_QuoteZMQ.UnsubQuote(g_QuoteSession, symbol["Symbol"])
        future_table.loc[future_table.future_code==future_symbol,'volume']=int(symbol['TradeVolume'])
#        if len(symbol['TradingPrice'])>1:
        if future_table.loc[future_table.future_code==future_symbol,'stock_name'].iloc[0].find('小型')>-1:
            shares = 100
        else:
            shares = 2000
        future_table.loc[future_table.future_code==future_symbol,'origin_money']=int(future_table['money_percent'][future_table.future_code==future_symbol].iloc[0]*price*shares)
        future_table.loc[future_table.future_code==future_symbol,'time']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    
    now = int(time.time())
    if now % 11 == 0 and now != temp_time:
        temp_time = now
        future_table = future_table.sort_values(by='volume', ascending=False)
        print(f'here is :{future_table.head(10)}')
        engine = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/webaiuse')
        future_table.to_sql('stockf_realtime',engine,if_exists='replace',index=False)
        
    # current_time = datetime.datetime.now().time()
    # if current_time > cTime:
    #     logout()
    #     print("EXIT")
    #     sys.exit()
        

#行情消息接收
def quote_sub_th(obj,sub_port,filter = ""):
    global message
    socket_sub = obj.context.socket(zmq.SUB)
    #socket_sub.RCVTIMEO=7000   #ZMQ超時設定
    socket_sub.connect("tcp://127.0.0.1:%s" % sub_port)
    socket_sub.setsockopt_string(zmq.SUBSCRIBE,filter)
    while(True):
        message = (socket_sub.recv()[:-1]).decode("utf-8")
        index =  re.search(":",message).span()[1]  # filter
        message = message[index:]
        message = json.loads(message)
        if(message["DataType"]=="REALTIME" and message["Quote"]["Symbol"].count('TC.F.TWF')>0):
            OnRealTimeQuote(message["Quote"])


def logout():
    print("Logout")
    g_QuoteZMQ.Logout(g_QuoteSession)
    
#建立連線
g_QuoteZMQ = QuoteAPI("ZMQ","8076c9867a372d2a9a814ae710c256e2")
q_data = g_QuoteZMQ.Connect("51237")
print(q_data)

if q_data["Success"] != "OK":
    print("[quote]connection failed")


g_QuoteSession = q_data["SessionKey"]

#建立一個行情線程
t2 = threading.Thread(target = quote_sub_th,args=(g_QuoteZMQ,q_data["SubPort"],))
t2.start()

#訂閱所有股期報價
for i in range(len(future_table.future_code)):
# for i in range(10):
    s = future_table.future_code[i]
    quoteSymbol = f"TC.F.TWF.{s}.{contract}"
    g_QuoteZMQ.SubQuote(g_QuoteSession, quoteSymbol)

