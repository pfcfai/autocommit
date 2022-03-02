# -*- coding: utf-8 -*-
"""
Created on Thu May 30 11:01:23 2019

@author: user
"""
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc
import pandas as pd
import cv2
import os
from PIL import Image
import numpy as np
from tqdm import trange
#Sql select 資料庫查詢語法
x=40
engine = create_engine('mysql+pymysql://root:pfcfai@localhost:3306/stockdata_day')
sqllist = 'show tables'
symbollist = pd.read_sql_query(sqllist, engine)
symbollist = symbollist[x:x+40]
#symbollist = []
#symbollist.append("1102")
for i in trange(len(symbollist)):
    stocksymbol = symbollist.iloc[i,0]
    sql = 'select Date,Open,High,Low,Close from `'+stocksymbol+'` order by Date asc'
    df = pd.read_sql_query(sql, engine)
    #長度大於60才執行
    if len(df)>= 60 :
    #選出近60日
        df = df[len(df)-60:]
        #將df產生圖檔
        test = pd.date_range('1900-01-01', periods=len(df['Date']), freq='D')
        df['Date'] = test
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
        df['Date2'] = df['Date'].apply(lambda d: mdates.date2num(d.to_pydatetime()))
        tuples = [tuple(x) for x in df[['Date2','Open','High','Low','Close']].values]
        fig, ax = plt.subplots()
        fig.set_size_inches(20.48/3,20.48/3)#(28.45,28.45)
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        #fig.layout.xaxis.type='category'
        #ax.xaxis.set_major_formatter(FuncFormatter(format_date))
        #plt.xticks(rotation=45)
        #plt.xlabel("Date")
        #plt.ylabel("Price")
        #plt.title("1101")
        plt.xticks([])
        plt.yticks([])
        candlestick_ohlc(ax, tuples, width=.6, colorup='g', alpha =.4)
        fig.savefig("C:\\python_code\\KBarRecognition\\ModelSelect\\Daysample\\"+stocksymbol+".jpg",dpi=300)
        plt.close(fig)
#        fig.canvas.draw()
        #裁切圖片
#        img = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
#        img  = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
#        img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
        img = cv2.imread("C:\\python_code\\KBarRecognition\\ModelSelect\\Daysample\\"+stocksymbol+".jpg")
        x = 263
        y = 257
        w = 1570
        h = 1520
        crop_img = img[y:y+h, x:x+w]
        cv2.imwrite("C:\\python_code\\KBarRecognition\\ModelSelect\\Daysample\\"+stocksymbol+".jpg",crop_img)
        
#        #縮小成60*29
        pic = Image.open("C:\\python_code\\KBarRecognition\\ModelSelect\\Daysample\\"+stocksymbol+".jpg")
#        pic = Image.fromarray(crop_img)
        pic = pic.resize((60, 29))
        pic.save("C:\\python_code\\KBarRecognition\\ModelSelect\\Daysample\\"+stocksymbol+".jpg")
        
        #Model Recognize
        from keras.models import load_model
        
        model = load_model('Recognize_Ver2.h5')
        x_image_test=[]                     #裝圖片的變數
#        img = np.array(pic)
        img =  cv2.imread("C:\\python_code\\KBarRecognition\\ModelSelect\\Daysample\\"+stocksymbol+".jpg")          #使用CV2讀取圖片
        x_image_test.append(img)
        x_image_test=np.asarray(x_image_test) 
        x_image_test = x_image_test.astype('float32') / 255.0
        pp=model.predict(x_image_test)
#        print(pp[0])
        #分類多
        if pp[0][1]==1:
            sql = 'select Date,Open,High,Low,Close from `'+stocksymbol+'` order by Date asc'
            df = pd.read_sql_query(sql, engine)
            #選出近60日
            df = df[len(df)-60:]
            #將df產生圖檔
            test = pd.date_range('1900-01-01', periods=len(df['Date']), freq='D')
            df['Date'] = test
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
            df['Date2'] = df['Date'].apply(lambda d: mdates.date2num(d.to_pydatetime()))
            tuples = [tuple(x) for x in df[['Date2','Open','High','Low','Close']].values]  
            fig, ax = plt.subplots()
            fig.set_size_inches(20.48/3,20.48/3)
            ax.xaxis_date()
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    #        #fig.layout.xaxis.type='category'
    #        #ax.xaxis.set_major_formatter(FuncFormatter(format_date))
    #        #plt.xticks(rotation=45)
    #        #plt.xlabel("Date")
    #        #plt.ylabel("Price")
            plt.title(stocksymbol)
            plt.xticks([])
            plt.yticks([])
            candlestick_ohlc(ax, tuples, width=.6,colordown='g', colorup='r', alpha =.4)
            fig.savefig("C:\\python_code\\KBarRecognition\\ModelSelect\\DayLong\\"+stocksymbol+".jpg",dpi=300)
            plt.close(fig)
        #分類空
        elif pp[0][2]==1:
            sql = 'select Date,Open,High,Low,Close from `'+stocksymbol+'` order by Date asc'
            df = pd.read_sql_query(sql, engine)
            #選出近60日
            df = df[len(df)-60:]
            #將df產生圖檔
            test = pd.date_range('1900-01-01', periods=len(df['Date']), freq='D')
            df['Date'] = test
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
            df['Date2'] = df['Date'].apply(lambda d: mdates.date2num(d.to_pydatetime()))
            tuples = [tuple(x) for x in df[['Date2','Open','High','Low','Close']].values]  
            fig, ax = plt.subplots()
            fig.set_size_inches(20.48/3,20.48/3)
            ax.xaxis_date()
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    #        #fig.layout.xaxis.type='category'
    #        #ax.xaxis.set_major_formatter(FuncFormatter(format_date))
    #        #plt.xticks(rotation=45)
    #        #plt.xlabel("Date")
    #        #plt.ylabel("Price")
            plt.title(stocksymbol)
            plt.xticks([])
            plt.yticks([])
            candlestick_ohlc(ax, tuples, width=.6,colordown='g', colorup='r', alpha =.4)
            fig.savefig("C:\\python_code\\KBarRecognition\\ModelSelect\\DayShort\\"+stocksymbol+".jpg",dpi=300)       
            plt.close(fig)