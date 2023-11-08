# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 13:30:04 2019

@author: studentA
"""
import pandas as pd
import requests
import datetime
from datetime import timedelta
import re

#====================================================================================
#台指                                                           
def quote_txf(func):  #CALL                                         #          _, ,_ 
    url='http://www.taifex.com.tw/cht/3/futDailyMarketExcel'        #        （ ‘д‘）
    txf=pd.read_html(url)[2]                                        #         ⊂彡☆))Д´）
    data_time = pd.read_html(url)[1].iloc[0,0] 
    
    temp= r"\d{4}/\d{2}/\d{2}"  
    data_time=re.search(temp,data_time)[0].split()[0]
    
    today=datetime.datetime.today().strftime('%Y/%m/%d')    
    if today ==  data_time:                                           
        txf=txf.rename(columns=txf.iloc[0]).drop(txf.index[0]).reset_index(drop=True)#   
        txf_quote=pd.DataFrame(txf[['開盤價','最高價','最低價','最後成交價','*一般交易時段成交量','*未沖銷契約量']].iloc[0,:]).T
        txf_quote.columns=['o','h','l','c','v','oi']    
        return(txf_quote.T.iloc[:,0]) 
    else:
        func('台指期更新日期不對')

#====================================================================================
#Fred
def quote_Fred_eco(locate=''):       #CALL
    symbols=pd.read_csv('Fred_EcoCode.CSV') 
    today=datetime.datetime.today().strftime('%Y-%m-%d')
    
    for i in symbols.index:
        symbol,freq=symbols.iloc[i,:]
        url='https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=748&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id='+symbol+'&scale=left&cosd=1900-01-01&coed='+today+'&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq='+freq+'&fam=avg&fgst=lin&fgsnd=2009-06-01&line_index=1&transformation=lin&vintage_date=2019-03-26&revision_date=2019-03-26&nd=2002-04-01'
        data=pd.read_csv(url) 
        data.to_csv(locate+symbol+'.csv',index=False)
#quote_Fred_eco('.\\data_download\\')     #範例
#====================================================================================   
#stock ai
def quote_StockAi_eco(locate=''):    #CALL  
    symbols=pd.read_csv('StockAi_EcoCode.CSV').iloc[:,0]
    key='FRtQFgW1Ti'
    start='0001-01-01'    #盤古開天
    today=datetime.datetime.today().strftime('%Y-%m-%d')
    for symbol in symbols:
        url='https://stock-ai.com/ddl?s='+symbol+'&r='+key+'&d1='+start+'&d2='+today
        data=pd.read_csv(url)
        data = data.rename(columns={'Date':'DATE','Value':symbol})
        data.to_csv(locate+symbol+'.csv',index=False)
#quote_StockAi_eco('.\\data_download\\')    範例
#====================================================================================
#CME
def rep(n):
    return (n.str.replace(',','').str.extract(r'(\d*\.\d*|\d*)',expand=False))
def month_to_num(month):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if months.index(month)+1<10:
        return ('0'+str(months.index(month)+ 1))
    else:
        return (str(months.index(month)+ 1))
def rep2(n):
    return (n.str.replace(',','').str.extract(r"('\d*)",expand=False))
def rep3(n):
    return (n.str.extract(r"(\d+)",expand=False))    
def split_save(n,code):
#    return (int(n[:2])/32 + int(n[2:])/4)
    if code =='FV':
        return ((n.str[:2].fillna(0).astype(int)/32) +(n.str[2:].fillna(0).replace("0","0").replace("2","1").replace("5","2").replace("7","3").astype(int)/128))
    elif code =='TU':
        return ((n.str[:2].fillna(0).astype(int)/32) + (n.str[2:].fillna(0).astype(int)/256))
    elif code =='TY':
        return ((n.str[:2].fillna(0).astype(int)/32) + (n.str[2:].fillna(0).astype(int)/320))    
    elif code =='US' or code =='WN':
        return ((n.str[:].fillna(0).astype(int)/32))
    elif code =='ZC' or code =='ZS' or code =='ZW':
        return ((n.str[:].fillna(0).astype(int)/8))
    else:
        pass
def quote_CME():
    yesterday=(datetime.datetime.today()-timedelta(1)).strftime('%m/%d/%Y')
    code_list=pd.read_csv('CME_SymbolCode.csv',index_col='symbol').astype(str).T.to_dict('records')[0]
    quote={}
    for code in code_list:    
        url='https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/'+code_list[code]+'/FUT?strategy=DEFAULT&tradeDate='+yesterday+'&pageSize=50&_=1553243269621'
        #package =requests.get(url) 
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}
        package=requests.get(url=url,headers=headers)  
        data=package.json()
        #compare
        #compare 會遇到 資料空缺無法抓取報錯就中斷問題，往上拉高一層
        if data['empty']==True:
            print(f'the day is off:{code}')        
        else:
            
            temp= r"[0-3]?[0-9] [a-zA-Z]+ \d{4}"  
            updated=re.search(temp,data['updateTime'])[0].split()
            updated[1]=month_to_num(updated[1])
            update_str=updated[1]+'/'+updated[0]+'/'+updated[2]
            temp= r"[0-3]?[0-9]/[0-3]?[0-9]/\d{4}"  
            yesterday_str=re.search(temp,yesterday)[0]
            if yesterday_str==update_str:     #昨天資料有更新就↓
                #if data['empty']==False:

                if code =='FV' or code=='TU' or code=='TY' or code=='WN' or code=='US' or code=='ZC' or code=='ZS' or code=='ZW' :

                    frame=pd.DataFrame(data['settlements']).set_index('month')
                    frame=frame[['open','high','low','settle','volume','openInterest']]
                    frame=frame[(frame['open']!='')&(frame['open']!='-')]
                    framesep = frame.apply(rep2).apply(rep3).fillna(0)
                    frameconvert = framesep.apply(split_save,args=(code,),axis=1)
                    frame2=frame.apply(rep).astype(float)
                    frame2= (frame2 + frameconvert)
                    frame2['sum']=frame2['volume']+frame2['openInterest']
                    frame2['num']= range(1, len(frame2) + 1)
                    frame3=frame2.sort_values(by=['sum'],ascending=False)
                    frame4=frame3.iloc[:2,:].sort_values(by=['num'])
                    
                    back=list(frame4.index)[-1]
                    near=list(frame4.index)[0]
        
                    if frame4.volume.idxmax()==frame4.openInterest.idxmax()==back:
                        cme_quote=pd.DataFrame(frame4.loc[back][:-2]).T.reset_index(drop=True)
                        cme_quote.columns=['o','h','l','c','v','oi']
                    else:
                        cme_quote=pd.DataFrame(frame4.loc[near][:-2]).T.reset_index(drop=True)
                        cme_quote.columns=['o','h','l','c','v','oi']
                    quote[code]=cme_quote.iloc[0,:]

                else:
                    frame=pd.DataFrame(data['settlements']).set_index('month')
                    frame=frame[['open','high','low','settle','volume','openInterest']]
                    frame=frame[(frame['open']!='')&(frame['open']!='-')]
                    frame2=frame.apply(rep).astype(float)
                    frame2['sum']=frame2['volume']+frame2['openInterest']
                    frame2['num']= range(1, len(frame2) + 1)
                    frame3=frame2.sort_values(by=['sum'],ascending=False)
                    frame4=frame3.iloc[:2,:].sort_values(by=['num'])
                    
                    back=list(frame4.index)[-1]
                    near=list(frame4.index)[0]
                
                    if frame4.volume.idxmax()==frame4.openInterest.idxmax()==back:
                        cme_quote=pd.DataFrame(frame4.loc[back][:-2]).T.reset_index(drop=True)
                        cme_quote.columns=['o','h','l','c','v','oi']
                    else:
                        cme_quote=pd.DataFrame(frame4.loc[near][:-2]).T.reset_index(drop=True)
                        cme_quote.columns=['o','h','l','c','v','oi']
                    quote[code]=cme_quote.iloc[0,:]
                #else:
                #    print('the day is off')        
            else:
                pass
    return(quote)
#--------------Ver1.0---------------
#def quote_CME():      #CALL
#    yesterday=(datetime.datetime.today()-timedelta(1)).strftime('%m/%d/%Y')
#    code_list=pd.read_csv('CME_SymbolCode.csv',index_col='symbol').astype(str).T.to_dict('records')[0]
#    quote={}
#    for code in code_list:    
#        url='https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/'+code_list[code]+'/FUT?strategy=DEFAULT&tradeDate='+yesterday+'&pageSize=50&_=1553243269621'
#        package =requests.get(url)   
#        data=package.json()
#        #compare
#        temp= r"[0-2]?[0-9] [a-zA-Z]+ \d{4}"  
#        updated=re.search(temp,data['updateTime'])[0].split()
#        updated[1]=month_to_num(updated[1])
#        update_str=updated[1]+'/'+updated[0]+'/'+updated[2]
#        temp= r"[0-2]?[0-9]/[0-2]?[0-9]/\d{4}"  
#        yesterday_str=re.search(temp,yesterday)[0]
#        
#        if yesterday_str==update_str:     #昨天資料有更新就↓
#            frame=pd.DataFrame(data['settlements']).set_index('month')
#            frame=frame[['open','high','low','settle','volume','openInterest']]
#            frame=frame[(frame['open']!='')&(frame['open']!='-')]
#            frame2=frame.apply(rep).astype(float)
#            frame2['sum']=frame2['volume']+frame2['openInterest']
#            frame2['num']= range(1, len(frame2) + 1)
#            frame3=frame2.sort_values(by=['sum'],ascending=False)
#            frame4=frame3.iloc[:2,:].sort_values(by=['num'])
#            
#            back=list(frame4.index)[-1]
#            near=list(frame4.index)[0]
#        
#            if frame4.volume.idxmax()==frame4.openInterest.idxmax()==back:
#                cme_quote=pd.DataFrame(frame4.loc[back][:-2]).T.reset_index(drop=True)
#                cme_quote.columns=['o','h','l','c','v','oi']
#            else:
#                cme_quote=pd.DataFrame(frame4.loc[near][:-2]).T.reset_index(drop=True)
#                cme_quote.columns=['o','h','l','c','v','oi']
#            quote[code]=cme_quote.iloc[0,:]
#        else:
#            pass
#    return(quote)
#====================================================================================
    
def quote_CME_hand(year,month,day):
    if month < 10: 
        month = '0%s'%(month)
    if day < 10: 
        day = '0%s'%(day)
    code_list=pd.read_csv('CME_SymbolCode.csv',index_col='symbol').astype(str).T.to_dict('records')[0]
    quote={}
    for code in code_list:
        print(code)    
        url='https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/'+code_list[code]+'/FUT?strategy=DEFAULT&tradeDate='+'%s/%s/%s'% (month,day,year)+'&pageSize=50&_=1553243269621' 
        print(url)
        #package =requests.get(url)
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}
        package=requests.get(url=url,headers=headers)
        print(package)   
        data=package.json()
        print(data)
        if code =='FV' or code=='TU' or code=='TY' or code=='WN' or code=='US' or code=='ZC' or code=='ZS' or code=='ZW' :
            if data['empty']==False:
                frame=pd.DataFrame(data['settlements']).set_index('month')
                frame=frame[['open','high','low','settle','volume','openInterest']]
                frame=frame[(frame['open']!='')&(frame['open']!='-')]
                framesep = frame.apply(rep2).apply(rep3).fillna(0)
                frameconvert = framesep.apply(split_save,args=(code,),axis=1)
                frame2=frame.apply(rep).astype(float)
                frame2= (frame2 + frameconvert)
                frame2['sum']=frame2['volume']+frame2['openInterest']
                frame2['num']= range(1, len(frame2) + 1)
                frame3=frame2.sort_values(by=['sum'],ascending=False)
                frame4=frame3.iloc[:2,:].sort_values(by=['num'])
                
                back=list(frame4.index)[-1]
                near=list(frame4.index)[0]

                if frame4.volume.idxmax()==frame4.openInterest.idxmax()==back:
                    cme_quote=pd.DataFrame(frame4.loc[back][:-2]).T.reset_index(drop=True)
                    cme_quote.columns=['o','h','l','c','v','oi']
                else:
                    cme_quote=pd.DataFrame(frame4.loc[near][:-2]).T.reset_index(drop=True)
                    cme_quote.columns=['o','h','l','c','v','oi']
                quote[code]=cme_quote.iloc[0,:]
            else:
                print('the day is off')
                
        else:
            if data['empty']==False:
                frame=pd.DataFrame(data['settlements']).set_index('month')
                frame=frame[['open','high','low','settle','volume','openInterest']]
                frame=frame[(frame['open']!='')&(frame['open']!='-')]
                frame2=frame.apply(rep).astype(float)
                frame2['sum']=frame2['volume']+frame2['openInterest']
                frame2['num']= range(1, len(frame2) + 1)
                frame3=frame2.sort_values(by=['sum'],ascending=False)
                frame4=frame3.iloc[:2,:].sort_values(by=['num'])
                
                back=list(frame4.index)[-1]
                near=list(frame4.index)[0]
            
                if frame4.volume.idxmax()==frame4.openInterest.idxmax()==back:
                    cme_quote=pd.DataFrame(frame4.loc[back][:-2]).T.reset_index(drop=True)
                    cme_quote.columns=['o','h','l','c','v','oi']
                else:
                    cme_quote=pd.DataFrame(frame4.loc[near][:-2]).T.reset_index(drop=True)
                    cme_quote.columns=['o','h','l','c','v','oi']
                quote[code]=cme_quote.iloc[0,:]
            else:
                print('the day is off')
    else:
        pass
    print(quote)
    return(quote)

#--------------Ver1.0---------------
#def quote_CME_hand(year,month,day):
#    if month < 10: 
#        month = '0%s'%(month)
#    if day < 10: 
#        day = '0%s'%(day)
#    code_list=pd.read_csv('CME_SymbolCode.csv',index_col='symbol').astype(str).T.to_dict('records')[0]
#    quote={}
#    for code in code_list:    
#        url='https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/'+code_list[code]+'/FUT?strategy=DEFAULT&tradeDate='+'%s/%s/%s'% (month,day,year)+'&pageSize=50&_=1553243269621' 
#        
#        package =requests.get(url)   
#        data=package.json()
#        frame=pd.DataFrame(data['settlements']).set_index('month')
#        frame=frame[['open','high','low','settle','volume','openInterest']]
#        frame=frame[(frame['open']!='')&(frame['open']!='-')]
#        frame2=frame.apply(rep).astype(float)
#        frame2['sum']=frame2['volume']+frame2['openInterest']
#        frame2['num']= range(1, len(frame2) + 1)
#        frame3=frame2.sort_values(by=['sum'],ascending=False)
#        frame4=frame3.iloc[:2,:].sort_values(by=['num'])
#        
#        back=list(frame4.index)[-1]
#        near=list(frame4.index)[0]
#    
#        if frame4.volume.idxmax()==frame4.openInterest.idxmax()==back:
#            cme_quote=pd.DataFrame(frame4.loc[back][:-2]).T.reset_index(drop=True)
#            cme_quote.columns=['o','h','l','c','v','oi']
#        else:
#            cme_quote=pd.DataFrame(frame4.loc[near][:-2]).T.reset_index(drop=True)
#            cme_quote.columns=['o','h','l','c','v','oi']
#        quote[code]=cme_quote.iloc[0,:]
#    return(quote)
#====================================================================================
