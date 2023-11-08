import time
from tcoreapi_mq import * 
import tcoreapi_mq
import threading
import pandas as pd
import datetime
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
from get_uid import uid_api
import os
cwd = os.getcwd()
def cal_contract():                            #計算當月期貨合約
    global now
    now = datetime.datetime.now()
    m = now.month
    y = now.year
    d = now.day
    first_weekday = datetime.date(year=y, month=m, day=1).weekday()+1
    multi = 2 if 3-first_weekday >=0 else 3
    settle_day = 3 - first_weekday + 7*multi +1
    plus = 1 if d > settle_day else 0
    if m+plus>12 :
        y=y+1
        m=1
        plus=0
    contract = f'{y}{m+plus:02}'
    return contract
 
def get_history(future_code,g_QuoteZMQ,start,end):                             #抓當日分K
    global frames
    for i in range(start,end):
        
        symbol = future_code['股票期貨英文代碼'].iloc[i]
        code = future_code['股票期貨標的證券代號'].iloc[i]
        print(f'end :{end} code :{code}')
        contract = cal_contract() 
        quoteSymbol = f"TC.F.TWF.{symbol}.{contract}"
        print(quoteSymbol)
        data_type = "1K"
        date = now.strftime("%Y%m%d")
        StrTim = f'{date}00'
        EndTim = f'{date}10'
        SubHis = g_QuoteZMQ.SubHistory(g_QuoteSession,quoteSymbol,data_type,StrTim,EndTim)     #訂閱歷史資料

        temp = []      
        for i in range(0,300,50):
            QryInd = f"{i}"                                                     #一次只能取50筆，透過QryInd紀錄最後一筆
            time.sleep(3)          
        
            HisData = g_QuoteZMQ.GetHistory(g_QuoteSession,quoteSymbol,data_type,StrTim,EndTim,QryInd)  #請求歷史報價
            data = pd.DataFrame(HisData['HisData'])
            temp.append(data)
            
        frames.append([code,pd.concat([i for i in temp],axis=0)])
def base64_to_url(volume_sort,start,end):
    for i in range(start,end):
        _dict = volume_sort[i][1]
        img_base64 = _dict['base64']
        img_url = img_upload(img_base64)
        volume_sort[i][1].update({'url': img_url})                             #img base64編碼上傳，回傳圖片網址
        print(f'end :{end} symbol :{_dict["future_name"]}')
# ##############################################連線=========================================        
g_QuoteZMQ = QuoteAPI("ZMQ","8076c9867a372d2a9a814ae710c256e2")
q_data = g_QuoteZMQ.Connect("51237")
print(q_data)

if q_data["Success"] != "OK":
    print("[quote]connection failed")

g_QuoteSession = q_data["SessionKey"]
# ############################################抓資料=========================================
#資料週期
future_table = pd.read_html("https://www.taifex.com.tw/cht/5/stockMarginingDetail")[0]       #抓股期詳細資料
r = requests.get('https://deeptrade.pfcf.com.tw/pfcf/stockf/volumetop10')                    #抓top10資料 
stock_api = pd.DataFrame(r.json()) 
stock_api['preclose'] = stock_api['price'] - stock_api['change']
future_code = future_table[future_table['股票期貨標的證券代號'].isin(stock_api.stock_code)]    #篩選top10英文代號

frames = []
threads =[]
s = time.time()
for j in range(0,10):                                                                        #收報價多執行緒
    threads.append(threading.Thread(target = get_history,args=(future_code,g_QuoteZMQ,0+j,1+j,)))
    threads[j].start()

for thread in threads:                                                                       #等待所有執行緒都完成
    thread.join()
e = time.time()
time_cost = e - s
print(f'收報價花費{time_cost:.0f}秒')
# ##############################################畫圖=========================================
volume_sort = []
for frame in frames:
    code = frame[0]                                                                      #抓各項數據
    preclose = stock_api.loc[stock_api.stock_code==code,'preclose']
    future_name = stock_api.loc[stock_api.stock_code==code,'stock_name'].iloc[0]
    future_chg = stock_api.loc[stock_api.stock_code==code,'change_p'].iloc[0]
    origin_money = stock_api.loc[stock_api.stock_code==code,'origin_money'].iloc[0]
    volume = stock_api.loc[stock_api.stock_code==code,'volume'].iloc[0]
    price = stock_api.loc[stock_api.stock_code==code,'price'].iloc[0]
    
    draw_text1 = f"{code} {future_name}({'+' if future_chg>0 else ''}{future_chg}%)"     #圖片文字
    close = frame[1].loc[:,'Close'].reset_index(drop=True)
    close = pd.concat([preclose,close],axis = 0).reset_index(drop=True).astype(float)    #收盤價
    price_min = close.min()
    price_max = close.max()
    index = pd.date_range('29/6/2021 08:45:00', periods=301, freq='T')                   #做早盤時間index
    data = pd.Series(np.nan, index=index)
    data[:len(close)] = close                                                            #合併close與index
   
    wave=abs(price_max-price_min)/5
    price_max+=wave 
    price_min+=-wave/2                                                                   #圖片下上預留空間
    
    fig, ax = plt.subplots()
    plt.gcf().set_size_inches(16,13.5)                                                   #新增畫布
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))                   #設定x軸時間格式
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())                              #設定時間刻度
    
    plt.ylim((price_min, price_max))                                                     #X軸與Y軸範圍
    plt.xlim((data.index[0],data.index[-1]))
    
    color = 'red' if future_chg>0 else 'green'
    plt.plot(data, linestyle='-',color=color, lw=5)                                      #收盤價畫線
    
    plt.axhline(preclose.iloc[0], color='black', lw=2, linestyle='-')                    #畫昨收水平線
    plt.xticks(fontsize=50)                                                              #座標軸字體大小
    plt.yticks(fontsize=50)
    
    plt.gca().spines['top'].set_visible(False)  
    plt.gca().spines['right'].set_visible(False)                                         #上、右框線消除
    ax.yaxis.set_major_locator(MaxNLocator(5))                                           #y軸刻度最大數量
    plt.subplots_adjust(top = 0.85, bottom = 0.15, right = 0.97, left = 0.1, hspace = 0, wspace = 0)
    
    save_file = BytesIO()                                                                #將圖片存入內存，再讀取後編碼成base64
    plt.savefig(save_file, format='PNG',transparent = True) #,bbox_inches='tight'
    save_file.seek(0) 
    img_base64 = base64.b64encode(save_file.read())
    
    soy = 'soy_red' if future_chg>0 else 'soy_gray' if future_chg==0 else 'soy_green'
    imageA = Image.open(rf'{cwd}/{soy}.jpg') #讀取底圖
    imageA = imageA.convert('RGBA')                                                      #轉成RGBA通道(A是透明度)
    widthA , heightA = imageA.size
    imageB = Image.open(BytesIO(base64.b64decode(img_base64)))
    imageB = imageB.convert('RGBA')
    widthB , heightB = imageB.size
    newWidthB = int(widthA/1.3)                                                          #縮小圖片
    newHeightB = int(heightB/widthB*newWidthB)
    imageB_resize = imageB.resize((newWidthB, newHeightB))
    
    resultPicture = Image.new('RGBA', imageA.size, (0, 0, 0, 0))                         #新增空白圖片
    resultPicture.paste(imageA,(0,0))                                                    #貼上底圖
    right_bottom = (180, 200)                                                            #設置折線圖位置
    resultPicture.paste(imageB_resize, right_bottom, imageB_resize)                      #貼上折線圖
    
    Drawimg = ImageDraw.Draw(resultPicture)                                              #文字物件
    Myfont = ImageFont.truetype('C:/Windows/Fonts/MSJHBD.TTC', 170)                      #文字字體
    (x, y) = (50, 195) 
    color  = 'rgb(255, 255, 255)' 
    Drawimg.text((x, y), draw_text1, fill=color, font=Myfont)                            #貼上文字
    # resultPicture.show()
    save_file = BytesIO()                                                                #將圖片存入內存，再讀取後編碼成base64
    resultPicture.save(save_file, 'PNG')
    save_file_base64 = base64.b64encode(save_file.getvalue()).decode('utf8')
        
    imf = {}
    imf.update({                                                                         #存成字典
            'code':code,
            'future_name':future_name,
            'future_chg':future_chg,
            'volume':volume,
            'origin_money':origin_money,
            'price':price,
            'base64':save_file_base64,
            })
    volume_sort.append([volume,imf])
#volume_sort.sort(reverse=True)
volume_sort.sort(key=lambda x: x[0], reverse=True)

threads2 =[]
s = time.time()
for j in range(0,10):                                                                   #base64編碼上傳雲端多執行緒
    threads2.append(threading.Thread(target = base64_to_url,args=(volume_sort,0+j,1+j,)))
    time.sleep(2)
    threads2[j].start()

for thread in threads2:
    thread.join()
e = time.time()
time_cost = e - s
print(f'上傳圖片花費{time_cost:.0f}秒')
##############################################傳line=========================================
from linebot import LineBotApi
from linebot.models import TextSendMessage,ButtonsTemplate,CarouselTemplate,CarouselColumn
from linebot.models import TemplateSendMessage,URITemplateAction,MessageTemplateAction
from linebot.models import ImageCarouselTemplate,ImageCarouselColumn,PostbackTemplateAction
from linebot.models import ImagemapSendMessage,BaseSize,URIImagemapAction,ImagemapArea,MessageImagemapAction

# warning = '以上資訊僅供參考，交易保證金會依盤中股價變動而有所不同。'
container = []
for i in range(10):
    data = volume_sort[i][1]
    load = CarouselColumn(
                    thumbnail_image_url = data['url'],
                    title = f'股期成交量NO.{i+1}   {data["future_name"]}',
                    text=f'成交量 :{data["volume"]:,.0f}口\n保證金 : ${data["origin_money"]} (會浮動)\n股票交割款 : ${data["price"]*2000:,.0f} (兩張)',
                    actions=[
                    URITemplateAction(
                        label='股期眉角',
                        uri='https://www.pfcf.com.tw/eventweb/top10/'
                        ),
                    MessageTemplateAction(
                        label='統一期貨各分公司資訊',
                        text='統一期貨各分公司資訊'
                        )
                    ]
                )
    container.append(load)
Carousel_template = TemplateSendMessage(
        alt_text='今日股期成交量TOP10',
        template=CarouselTemplate(
        columns=container
    )
)



line_bot_api = LineBotApi('z5B76MyolY5J2gNOtfJ1EYe3XiDq1A2HhaAWZb3OGQmyBY06+CKXH3wOgxrNfaaw3HLilXnZAOnL9Yn07OYroG4Kb0yChFyP1GY+C5iJ+KgIGCVjWGf2YmlK/MCG17KjZzylXjhlROryduUo1DX+sQdB04t89/1O/w1cDnyilFU=')
# line_bot_api.push_message('U919bd66a7cb241d3792cb3987161dfe1',Carousel_template)
#line_bot_api.push_message('U00fd958fbc230fea1e9114d2be1e2f04',Carousel_template)

member_list=list(uid_api('股期'))
for i in range (0,len(member_list),150):
    line_bot_api.multicast(member_list[i:i+149],Carousel_template)
    #print(member_list[i:i+149])
#member_list=list(pd.read_csv(f"{cwd}/intracompany_list.CSV",encoding="ANSI").UID)
#line_bot_api.multicast(member_list,Carousel_template)
# test = TextSendMessage(text='以上資訊僅供參考，交易保證金會依盤中股價變動而有所不同。')
# line_bot_api.push_message('U919bd66a7cb241d3792cb3987161dfe1',test)