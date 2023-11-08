#!/usr/bin/env python
# coding: utf-8

import time
from tcoreapi_mq import * 
import tcoreapi_mq
import threading
import pandas as pd
# import datetime
from datetime import datetime, timedelta
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm  
import numpy as np
from io import BytesIO
import base64
from imgupload import img_upload
import matplotlib.image as mpimg
from PIL import Image,ImageDraw,ImageFont
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import DateFormatter, DayLocator
import os
import time
from tcoreapi_mq import * 
import tcoreapi_mq
import threading

from linebot import LineBotApi
from linebot.models import TextSendMessage,ButtonsTemplate,CarouselTemplate,CarouselColumn
from linebot.models import TemplateSendMessage,URITemplateAction,MessageTemplateAction
from linebot.models import ImageCarouselTemplate,ImageCarouselColumn,PostbackTemplateAction
from linebot.models import ImagemapSendMessage,BaseSize,URIImagemapAction,ImagemapArea,MessageImagemapAction

from sqlalchemy import create_engine
import pymysql
from get_uid import uid_api

class get_history_draw():
    cwd = os.getcwd()
    now = datetime.now()
    draw_flag = 0
    check = []

        
    def connect(self):
        self.g_QuoteZMQ = QuoteAPI("ZMQ","8076c9867a372d2a9a814ae710c256e2")
        self.q_data = self.g_QuoteZMQ.Connect("51237")
        print(self.q_data)        
        if self.q_data["Success"] != "OK":
            print("[quote]connection failed")         
        self.g_QuoteSession = self.q_data["SessionKey"]       
            
    def get_history(self,symbol,datatype,days):
        
        dt1 = datetime.now()

        quoteSymbol = f"{symbol}"
        data_type = datatype
        end_date = self.now.strftime("%Y%m%d")
        #days = 7 if datatype == "1K" else 240*5 if datatype == "DK" else ""
        days=days
        start_date = (self.now - timedelta(days=days)).strftime("%Y%m%d")
        StrTim = f'{start_date}00'
        EndTim = f'{end_date}23'
        SubHis = self.g_QuoteZMQ.SubHistory(self.g_QuoteSession,quoteSymbol,data_type,StrTim,EndTim)     #訂閱歷史資料
        temp = []
        time.sleep(3)
        strQryIndex = 0
        while(True):
            HisData = self.g_QuoteZMQ.GetHistory(self.g_QuoteSession,quoteSymbol,data_type,StrTim,EndTim,strQryIndex)  #請求歷史報價
            time.sleep(0.1)
            data = pd.DataFrame(HisData['HisData'])
            temp.append(data)
            if len(data) == 0:
                break
            strQryIndex = data.QryIndex.iloc[-1]
            #print(strQryIndex)
        dt2 = datetime.now()
        tdelta = dt2 - dt1 
        print(f'it costs {tdelta} secs')
        return(temp,strQryIndex)
    
    def test_df(self,df): # 用來檢查 原始資料 轉換 data_format 有否 str to float 問題
        engine1 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/strategy?charset=utf8')
        df.to_sql('testdf', engine1, if_exists = 'replace',index=False)
    def to_db(self,df):
        
        engine2 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/strategy?charset=utf8')
       
        df.to_sql('realtime', engine2, if_exists = 'append',index=False)
       

    def to_db2(self,df):

        engine3 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/strategy?charset=utf8')
        df.to_sql('linepush', engine3, if_exists = 'append',index=False)

    def fr_db(self,symbol_code):
        # 抓取資料
        engine4 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/strategy?charset=utf8')
        sql =f'SELECT * FROM strategy.realtime where date(timenow) = CURDATE() and symbol_code not in ("{symbol_code}") order by timenow desc limit 28;'
        # note : limit 筆數為總商品比數-1 ex, 29-1 = 28
        df = pd.read_sql(sql,engine4)
        print(f'資料庫回傳{df.head()}')
        return df

    def timecheck(self):
        # 抓取資料 一定要有一筆 不然會報錯
        engine5 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/strategy?charset=utf8')
        sql ='SELECT timenow FROM strategy.linepush order by timenow desc limit 1;'
        # note : limit 筆數為總商品比數-1 ex, 29-1 = 28
        df = pd.read_sql(sql,engine5)
        print(f'last record time :{df.head()}')
        from datetime import datetime
        dt=datetime.now()
        dt1 = datetime(2022,6,29,00,00,00,00000) 
        dt2 = datetime(2022,6,29,1,00) 
        tdelta = dt - df.iloc[0][0]
        tdelta2 = dt2 - dt1 

        print(f'since last record time: {tdelta}') # check time.diff from last record
        print(f'critical time: {tdelta2}') # use this to cool down
        if tdelta > tdelta2:
            tc=True
        else:
            tc=False
        return tc

    def recordcheck(self,symbol_code,timenow):
        # 抓取資料 美股收盤開始起算 當天
        engine6 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/strategy?charset=utf8')
        if timenow.hour>6:
            sql ="SELECT * FROM strategy.linepush where timenow > concat(CURDATE(),' 06:00:00')  ;"
        else:
            sql ="SELECT * FROM strategy.linepush where timenow > concat(CURDATE(),' 00:00:00')  ;"
        df = pd.read_sql(sql,engine6)
        lt=[]
        for i in range(df.shape[0]):
            lt.append(df.iloc[i][7])
        print(f'今天已經發送過的商品: {lt}')
        # 直接轉換 symbol_code 在 lt 內的個數，並回傳做後續是否發訊的判斷
        counts = dict()
        for i in lt:
            counts[i] = counts.get(i, 0) + 1
        print(counts)

        if symbol_code in lt:
            rc=counts[symbol_code] 
        else:
            rc=0
        print(f'rc:{rc}')
        return rc

    def contractcheck(self,symbol_code):
        # 抓取資料
        print('here is contractcheck')
        engine8 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/pricedata_day?charset=utf8')
        if symbol_code not in ('DXM','MYM','MES','MHI','SSI','CN','TWN','IN','MNQ','FITX','FITE'):
            sql =f"SELECT Date,Volume,Contract FROM pricedata_day.apipricedata where Symbol='{symbol_code}' order by Date desc limit 5;"
            df = pd.read_sql(sql,engine8)
            print(df)

            if df.iloc[0][2]==df.iloc[1][2]:
                cc=True
            else:
                cc=False
        elif symbol_code in ('DXM','MYM','MES'):
            if symbol_code =='DXM':symbol_code ='DAX'
            elif symbol_code =='MYM':symbol_code ='YM'
            else:symbol_code ='ES'

            sql =sql =f"SELECT Date,Volume,Contract FROM pricedata_day.apipricedata where Symbol='{symbol_code}' order by Date desc limit 5;"
            df = pd.read_sql(sql,engine8)
            print(df)
            if df.iloc[0][2]==df.iloc[1][2]:
                cc=True
            else:
                cc=False
        else:
            cc=True


        return cc

    def data_format(self,data):
        symbol_data = pd.concat([i for i in data],axis=0)
  
        symbol_data['hour'] = (symbol_data.Time.astype(int)//10000).astype(str).str.zfill(2)
        symbol_data['minute'] = (symbol_data.Time.astype(int)%10000//100).astype(str).str.zfill(2)
        symbol_data['Date2'] = symbol_data.Date + symbol_data.hour + symbol_data.minute
        symbol_data['Date2'] = pd.to_datetime(symbol_data['Date2'], format='%Y%m%d%H%M')
        symbol_data = symbol_data.set_index('Date2')
        
        symbol_data = symbol_data.drop(columns=['OI']) # temp if str to float problem => kill
        symbol_data = symbol_data.resample('60T').last()[:-1].dropna().astype(float)
        # symbol_data = symbol_data.resample('60T').last()[:-1].dropna().astype(int) #220601 refresh

        draw_data = symbol_data.dropna()
        origin_index = draw_data.index
        last_time = origin_index[-1] + timedelta(hours=1)
        add_space = pd.date_range(last_time, periods=10, freq='H')
        
        origin_index = origin_index.append(add_space).to_frame()
        origin_index['format'] = origin_index.index.month.astype(str) +'/' +origin_index.index.day.astype(str)
        origin_index = origin_index.set_index('format')
        origin_index = origin_index.index
        
        
        now = datetime.now()
        m = now.month
        d = now.day
        weekday = datetime.today().isoweekday()
        weekend = [f'{m}/{d-weekday}',f'{m}/{d-weekday-1}']
        date_labels = origin_index[~origin_index.isin(weekend)].drop_duplicates()[1:]
        
        date_index = []
        for i in range(1,len(origin_index)):
            if  origin_index[i] != origin_index[i-1] and origin_index[i] not in weekend:
                date_index.append(i)
        # temp_index = symbol_data.index[:len(draw_data)]
        # draw_data.index = temp_index
        draw_data = draw_data['Close']
        last_time = draw_data.index[-1] + timedelta(hours=1)
        add_space = pd.date_range(last_time, periods=10, freq='H')
        add_space = pd.DataFrame(np.zeros([10,1]),index = add_space,columns=['Close']).replace(0,np.NaN)
        draw_data = draw_data.append(add_space.Close)
        draw_data = draw_data.reset_index(drop=True)
        return([draw_data,date_index,date_labels])

    def text_format(self,Fontsize,str_x,str_y,color,draw_text,Drawimg): #圖片文字控制 因為實在太多
        Myfont = ImageFont.truetype('C:/Windows/Fonts/MSJHBD.TTC', Fontsize)       
        Drawimg.text((str_x, str_y), draw_text, fill=color, font=Myfont) 
            
    def draw(self,date_index,date_labels,draw_data,draw_text,gcf_x,gcf_y,resize,img_x,img_y,str_x,str_y,dot_size,color,pctNegtive,symbol_code,switch_code):
        # self.check.append([draw_text,origin_index,draw_data])
        close = draw_data.reset_index(drop=True)
        
        price_min = close.min()
        price_max = close.max()
                                                                #合併close與index
        data = draw_data
        
        wave=abs(price_max-price_min)/5
        price_max+=wave 
        price_min+=-wave/2                                                                   #圖片下上預留空間

        fig, ax = plt.subplots()
        # plt.gcf().set_size_inches(16,13.5)                                                   #新增畫布
        plt.gcf().set_size_inches(gcf_x,gcf_y) 
        
        plt.ylim((price_min, price_max))                                                     #X軸與Y軸範圍
        plt.xlim((data.index[0],data.index[-1]))
        
        # color = 'red' if 1>0 else 'green'
        plt.plot(data, linestyle='-',color=color, lw=5)                                      #收盤價畫線
        plt.scatter(data.index[-11],data.iloc[-11], marker='o', c=color ,s = dot_size)
        
        plt.xticks(fontsize=50)                                                              #座標軸字體大小
        plt.yticks(fontsize=50)
        
        ax.set_xticks(date_index)
        ax.set_xticklabels(date_labels)

        ax.yaxis.set_major_locator(MaxNLocator(5))                                           #y軸刻度最大數量
        plt.gca().spines['top'].set_visible(False)  
        plt.gca().spines['right'].set_visible(False)                                         #上、右框線消除
        
        plt.subplots_adjust(top = 0.85, bottom = 0.15, right = 0.97, left = 0.1, hspace = 0, wspace = 0)
        plt.tight_layout()
        save_file = BytesIO()                                                                #將圖片存入內存，再讀取後編碼成base64
        plt.savefig(save_file, format='PNG',transparent = True) #,bbox_inches='tight'
        save_file.seek(0) 
        img_base64 = base64.b64encode(save_file.read())
            
        # imageA 是底圖(大)  imageB 是上面一層塗(小圖)
        #soy = 'quote_red_v1' if color=='red' else 'quote_green_v1'
        if switch_code==1 :
            soy = 'quote_red' if color=='red' else 'quote_green'
        else:
            soy = 'quote_red2' if color=='red' else 'quote_green2'
        
        # soy = 'quote_square' # 測試用
        imageA = Image.open(rf'{self.cwd}\{soy}.png') #讀取底圖
        imageA = imageA.convert('RGBA')                                                      #轉成RGBA通道(A是透明度)
        widthA , heightA = imageA.size
        imageB = Image.open(BytesIO(base64.b64decode(img_base64)))
        imageB = imageB.convert('RGBA')
        widthB , heightB = imageB.size
        newWidthB = int(widthA/resize)                                                          #縮小圖片
        newHeightB = int(heightB/widthB*newWidthB)
        imageB_resize = imageB.resize((newWidthB, newHeightB))
        print(f'圖的大小: {imageB_resize.size}') # 我想知道 小圖最後的大小
        
        resultPicture = Image.new('RGBA', imageA.size, (0, 0, 0, 0))                         #新增空白圖片
        resultPicture.paste(imageA,(0,0))                                                    #貼上底圖

        img_x, img_y = 50,134
        right_bottom = (img_x, img_y)                                                        #設置折線圖位置
        resultPicture.paste(imageB_resize, right_bottom, imageB_resize)                      #貼上折線圖
        # resultPicture.show()                                                               # 印出貼圖

        Drawimg = ImageDraw.Draw(resultPicture)
        # 處理文字物件
        # def text_format(self,Fontsize,str_x,str_y,color,draw_text,Drawimg): #圖片文字控制 因為實在太多
        # 標題
        if len(draw_text) < 25:
            self.text_format(55,50,73,'rgb(255, 255, 255)',draw_text,Drawimg)
        else:
            self.text_format(45,25,80,'rgb(255, 255, 255)',draw_text,Drawimg)

        # 次標
        # self.text_format(55,50,700,'rgb(0, 0, 128)','主要變動商品報價',Drawimg)
        
        # 內文 加入資料庫 排序3筆
        time.sleep(60) # 為了抓到 後面才塞入資料庫的資料
        realstate=self.fr_db(symbol_code)
        realstate = realstate.sort_values(by=['pct_value'], ascending=pctNegtive) # False -> pct > 0 
        # realstate = realstate.sort_values(by=['pct_value'], ascending=False) # False -> pct > 0 
        print(f'排序後:{realstate}')
        print('# 製作參考商品')
        target=[]
        for i in range(3):
            if len(realstate['normalname'].iloc[i])>5:
                a=realstate['normalname'].iloc[i]
            else:
                a=realstate['normalname'].iloc[i]+" "*4*(6-len(realstate['normalname'].iloc[i]))
            # b=realstate['currency'].iloc[i]
            # c=realstate['margin'].iloc[i]
            if realstate['normalname'].iloc[i] in ("瑞法郎","歐元","加幣","澳幣","高級銅"):
                d=str(round(realstate['recent_close'].iloc[i],4))
            elif realstate['normalname'].iloc[i] == "英磅":
                a="英鎊"+" "*4*(6-len(realstate['normalname'].iloc[i]))
                d=str(round(realstate['recent_close'].iloc[i],4))
            elif realstate['normalname'].iloc[i] =="大台指期貨":
                a="台指期"+" "*4*(6-len(realstate['normalname'].iloc[i]))
                d=str(round(realstate['recent_close'].iloc[i],0))
            elif realstate['normalname'].iloc[i] =="微型S":
                a="微型標普"+" "*4*(6-len(realstate['normalname'].iloc[i]))
                d=str(round(realstate['recent_close'].iloc[i],2))
            else:
                d=str(round(realstate['recent_close'].iloc[i],2))
            e=realstate['change'].iloc[i]
            f=realstate['pct_per'].iloc[i]
            print(a,d,e,f)
            mystr=f'{a}  {d}   {e}   ({f}%) '
            target.append(mystr)
        # mynote='1.保證金資訊請參考圖片連結\n2.漲跌與報酬均以現價/昨收為基準'
        draw_text=f'{target[0]}\n{target[1]}\n{target[2]}'
        self.text_format(30,50,785,'rgb(255, 255, 255)',draw_text,Drawimg) 
        # 底註
        # self.text_format(25,50,950,'rgb(205, 38, 38)',mynote,Drawimg)
        # resultPicture.show() # 測試印出，封測註解掉

        print('resultPicture.show (測試印出，封測註解掉)')
        save_file = BytesIO()                                                                #將圖片存入內存，再讀取後編碼成base64
        resultPicture.save(save_file, 'PNG')
        save_file_base64 = base64.b64encode(save_file.getvalue()).decode('utf8')
        img_url = img_upload(save_file_base64)
        return(img_url)
    
    def customer_list(self,customer_data):
        cus_list=[]
        for i in range(customer_data.shape[0]):
            UID=customer_data['UID'].iloc[i]
            cus_list.append(UID)
        print(f'cus_list:{cus_list}')
        return cus_list

    def line_push(self,img_url,cover_rate,customer_data,switch_code):
        imagemap_message = ImagemapSendMessage(
        base_url=f'{img_url}',
        alt_text=f'價格有較大波動，現價已較昨收盤價波動超過{round(cover_rate,2)}個保證金，請留意交易風險！',
        base_size=BaseSize(height=1040, width=1040),
        actions=[
            URIImagemapAction(
                link_uri='https://appurl.io/5_wRYUkem7', 
                # https://example.com/ 先拿掉 -> https://www.pfcf.com.tw/info/detail/1677
                area=ImagemapArea(
                    x=0, y=0, width=1040, height=1040
                )
            )
            ]
        )
        
        line_bot_api = LineBotApi('z5B76MyolY5J2gNOtfJ1EYe3XiDq1A2HhaAWZb3OGQmyBY06+CKXH3wOgxrNfaaw3HLilXnZAOnL9Yn07OYroG4Kb0yChFyP1GY+C5iJ+KgIGCVjWGf2YmlK/MCG17KjZzylXjhlROryduUo1DX+sQdB04t89/1O/w1cDnyilFU=')
        #line_bot_api.push_message('U919bd66a7cb241d3792cb3987161dfe1',imagemap_message) # yao lin
        #line_bot_api.push_message('U00fd958fbc230fea1e9114d2be1e2f04',imagemap_message) # jun
        member_list=list(uid_api('行情'))
        member_list2=list(uid_api('物料行情'))
        if switch_code==1:
            for i in range (0,len(member_list),150):
                line_bot_api.multicast(member_list[i:i+149],imagemap_message)
        else:
            for i in range (0,len(member_list2),150):
                line_bot_api.multicast(member_list2[i:i+149],imagemap_message)
        # 測試用
        # cus_list=self.customer_list(customer_data)
        # for i in cus_list:
        #    line_bot_api.push_message(i,imagemap_message) # laurent tang # alioth lu
        
        # member_list=list(pd.read_csv(f"{self.cwd}/intracompany_list.CSV",encoding="ANSI").UID)
        # line_bot_api.multicast(member_list,imagemap_message)
    
    
    def back_test(self,symbol,datatype,days,close_time):
        temp,strQryIndex=self.get_history(symbol,datatype,days)
        symbol_data = pd.concat([i for i in temp],axis=0)

        # 總共有 昨收,現價,變動值,報酬率,畫圖用的df
        last_close=symbol_data["Close"][symbol_data["Time"]==close_time].astype(float).iloc[-1]
        recent_close=symbol_data["Close"][symbol_data["QryIndex"]==strQryIndex].astype(float).iloc[0]
        change=recent_close-last_close
        pct=(recent_close/last_close-1)*100
        print(last_close,recent_close,pct)

        return (pct,change,last_close,temp,recent_close)
    
    def future_money(self,symbol_code):
        engine7 = create_engine('mysql+pymysql://webmysql@actwebdb2:AIteam168@103.17.9.213:3306/strategy')
        sql =f'SELECT margin FROM strategy.margin where shortname="{symbol_code}";'
        sql2 =f'SELECT normalname FROM strategy.margin where shortname="{symbol_code}";'
        df = pd.read_sql(sql,engine7)
        df2 = pd.read_sql(sql2,engine7)
        margin=df.astype(float).iloc[0][0]
        normalname=df2.astype(str).iloc[0][0]
        #print(type(df.astype(float).iloc[0][0]))
        return (margin,normalname)

    def file_settings(self):
        quoteSymbol = pd.read_csv('symbol_code.csv',encoding='Utf-8')
        customer = pd.read_csv('customer.csv',encoding='Utf-8')
        pushSymbol = pd.read_csv('symbol_push.csv',encoding='Utf-8')
        return quoteSymbol,customer, pushSymbol
    
    def main(self,symbol,datatype,days,close_time,point,currency,symbol_code,customer_data,pushlist,switch_code):
        self.connect() #連線
        # 回測 => 存資料庫
        pct,change,last_close,data,recent_close=self.back_test(symbol,datatype,days,close_time)
        pct_value=pct
        pct_per=str(round(pct,2)) if pct < 0 else '+'+str(round(pct,2))
        change= str(round(change,4)) if change < 0 else '+'+str(round(change,4))
        
        margin,normalname=self.future_money(symbol_code)
        timenow=datetime.now()
        normalname = normalname[:-2] if len(normalname)>6 else normalname # 為了解決標題太長 無法與宜均圖相容
        realtimelst=[(timenow,normalname,recent_close,change,pct_per,currency,margin,symbol_code,pct_value)]
        header = ['timenow', 'normalname', 'recent_close', 'change','pct_per','currency','margin','symbol_code','pct_value']
        realtimedf = pd.DataFrame.from_records(realtimelst,columns=header)
        print(f'存入資料庫即時資料:{realtimedf}')
        self.to_db(realtimedf)
        #後續運算
        mydata=pd.concat([i for i in data],axis=0)

        cover_rate=(1-0.75) # 重要假設 是控制整個警示的因子 (1-剩餘本金率) default (1-0.75)
        upperbound=round(((margin*cover_rate)/point)/last_close*100,2)
        lowerbound=-1*upperbound

        print(f'pct_per,margin,normalname,upperbound: {pct_per},{margin},{normalname},{upperbound}')
        # print(f'從TC抓回的rawdata: {mydata}')
        
        if (pct > upperbound or pct < lowerbound):
            catchdata=self.get_history(symbol, datatype, 7)
            draw_data,date_index,date_labels=self.data_format(catchdata[0])
            if normalname in ("瑞法郎","歐元","加幣","澳幣","高級銅"):
                draw_text=f'{normalname} {round(recent_close,4)} {change}({pct_per}%)'
            elif normalname =="英磅":
                draw_text=f'英鎊 {round(recent_close,4)} {change}({pct_per}%)'
            elif normalname =="大台指期貨":
                draw_text=f'台指期 {round(recent_close,0)} {change}({pct_per}%)'
            elif normalname =="微型S":
                draw_text=f'微型標普 {round(recent_close,4)} {change}({pct_per}%)'
            else:
                draw_text=f'{normalname} {round(recent_close,2)} {change}({pct_per}%)'
            pctNegtive=True if pct<0 else False #回傳參考資訊時 需要排序
            # 其他參數
            resize = 1.3
            dot_size = 300
            gcf_x = 20
            gcf_y = 13
            color = 'red' if pct > 0 else 'green'
            img_x = 80
            img_y = 129
            str_x = 50
            str_y = 5
            url=self.draw(date_index,date_labels,draw_data,draw_text,gcf_x,gcf_y,resize,img_x,img_y,str_x,str_y,dot_size,color,pctNegtive,symbol_code,switch_code)
            #print(url)
            
            # 檢查是否發過圖卡
            rc=self.recordcheck(symbol_code,timenow)
            print(f'recordcheck:{rc}')
            cc=self.contractcheck(symbol_code)
            print(f'contractcheck:{cc}')
            #cc=True
            tc=gnd.timecheck()
            print(tc)
            if tc is True:
                
                if cc is True:
    
                    if rc ==0 : # 未曾發過
                        print(f'發送圖卡存入資料庫:{realtimedf}')
                        self.to_db2(realtimedf)
                        if symbol_code in pushlist: #在設定名單才push
                            self.line_push(url,cover_rate,customer_data,switch_code) # 傳送
    
                    else:
                        cover_rate=(1-0.35) # 重要假設 是控制整個警示的因子 (1-剩餘本金率) default (1-0.35)
                        upperbound=round(((margin*cover_rate)/point)/last_close*100,2)
                        lowerbound=-1*upperbound
                        if (pct > upperbound or pct < lowerbound):
                            if rc >1:
                                print('今日已發出，且達第二次門檻，將不再發圖卡')
                            else:   
                                print(f'第二次發送圖卡:{realtimedf}')
                                self.to_db2(realtimedf)
                                self.line_push(url,cover_rate,customer_data,switch_code) # 傳送
                        else:
                            print('今日已發出，且未達第二次門檻，不發圖卡')
                else:
                    print('合約換約，可能導致契約價差過大的計算問題，故不發訊')
            else:
                print('time is not yet due , pass!')
                time.sleep(60)


while True:
    try:
        gnd=get_history_draw()
        tc=gnd.timecheck()
        print(tc)
        # if tc is True:    
        t_list=[]
        csv_data,customer_data,pushSymbol = gnd.file_settings() # return quoteSymbol,customer, pushSymbol
        print(customer_data)
        ps=pushSymbol #設定要push的商品是那些
        pushlist=[ps['code'].iloc[k] for k in range(ps.shape[0])]
        print(f'預計會推播的商品有{pushlist}')
        print('# 進入主程序')
        for i in range(36):
            symbol=csv_data['quote_code'].iloc[i]
            symbol_code=csv_data['code'].iloc[i]
            switch_code=csv_data['symbol'].iloc[i]
            
            close_time=csv_data['close_time'].astype(str).iloc[i]
            point=csv_data['point'].iloc[i] #切換整數時的點值 如 NQ 12000.0 * 2
            currency=csv_data['currency'].iloc[i] #切換整數時的點值 如 NQ 12000.0 * 2
            datatype="1K"
            days=3
            print(f'step1 - 商品檔輸入參數:{switch_code},{symbol},{datatype},{days},{close_time},{point}')
            t_list.append(threading.Thread(target=gnd.main, args=(symbol,datatype,days,close_time,point,currency,symbol_code,customer_data,pushlist,switch_code)))  # 建立執行緒
            t_list[i].start()  # 執行
            time.sleep(5)        
            print('子程序間隔5秒鐘')
        print("# 主程序休息1分鐘")
        time.sleep(60) # 避免主程序快速進入第二次迴圈 0621
    #else:
    #        print('time is not yet due , pass!')
    #        time.sleep(60)
    except Exception as e:
        print(e)
 