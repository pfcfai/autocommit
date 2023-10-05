import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import datetime

resource_path = r'/home/targets/autocommit/EXCEL_AutoUpdate/EcoCollect/CapitalFlow/res_gossiping'
if not os.path.exists(resource_path):
    os.mkdir(resource_path)
headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
ss = requests.session()
ss.cookies['over18'] = '1'
today=datetime.date.today()
print(today)
year,month,day=today.year,today.month,today.day
print(year,month,day)   

try:

    datestr=str(year)+str(month).zfill(2)+str(day).zfill(2)
    #datestr='20231003'
    print(f'querydatestr:{datestr}')
    def get_strnum(text,target):
        a=text.find(target)
        d=len(target)
        b=text[a+d:a+30].find("億")
        c=text[a+d:a+d+b]
        return c

    for i in range(1,11):
        url = f'https://www.sfb.gov.tw/ch/home.jsp?id=95&parentpath=0,2&mcustomize=news_view.jsp&dataserno={datestr}000{str(i)}&dtable=News'
        res = ss.get(url, headers = headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        article_title_html = soup.select('div[class="main-a_03"]')

        
        text=article_title_html[0].prettify()

        print(text.find("外資及陸資投資國內證券情形"))
        if text.find("外資及陸資投資國內證券情形")>0:
            buy_amount=get_strnum(text,"外資買進上市股票總金額約新臺幣")
            sell_amount=get_strnum(text,"賣出上市股票總金額約新臺幣")
            otc_buy_amount=get_strnum(text,"外資買進上櫃股票總金額約新臺幣")
            otc_sell_amount=get_strnum(text,"賣出上櫃股票總金額約新臺幣")

            net_inflow=get_strnum(text,"境外外國機構投資人、華僑及外國自然人累計")
            print(net_inflow.find("淨匯入"))
            if net_inflow.find("淨匯入")==0:
                net_inflow=float(net_inflow[net_inflow.find("約")+1:])
            else:
                net_inflow=-float(net_inflow[net_inflow.find("約")+1:])
            
            result=[buy_amount,sell_amount,otc_buy_amount,otc_sell_amount,net_inflow]
            pd.DataFrame(result).to_csv('/home/targets/autocommit/EXCEL_AutoUpdate/EcoCollect/CapitalFlow/res_gossiping/'+datestr+'000'+str(i)+'.csv', sep='\t', encoding='utf-8') 
            
            
            with open('/home/targets/autocommit/EXCEL_AutoUpdate/EcoCollect/CapitalFlow/res_gossiping/'+datestr+'000'+str(i)+'.txt', 'w', encoding='utf-8') as f:

                f.write(text)
                #print(text)
                
    print('==========================================================')
except:
    pass 


