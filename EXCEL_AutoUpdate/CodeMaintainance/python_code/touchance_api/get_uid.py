# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 14:26:09 2019

@author: studentA
"""
def uid_api(target):
    import json
    import base64
    import hashlib
    import time
    import requests
    import pandas as pd
    start = '{"Mode":"updateby","date":"2021-08-12 17:00:12"}'
    
    start = start.encode()
    start = base64.b64encode(start).decode("utf-8") 
    
    start_code = start + 'allproductspfcfapi'
    start_code = start_code.encode()
    token = hashlib.sha256(start_code).hexdigest()
    
    time = int(time.time())
    
    url = 'https://pfcf.lineapia.tw/web/pfcf_tag'
    
    my_data = {'data': start, 'token': token,'timestamp':time}
    
    r = requests.post(url, data = my_data)
    
    target_dic = {"測試":"1628233431439","經濟數據":"1634704049700","行情":"1634704100450","股期":"1634689422909","物料行情":"1682490809394"}
    
    taglist = json.loads(r.text)['responsedata']['TagList']
    data = pd.DataFrame(json.loads(r.text)['responsedata']['UserTag']).T.reset_index()
    
    follow = data[data.status=='follow'].dropna()
    find = follow['index'][follow.tag.str.contains(target_dic[target])]
    return(find)
aa = uid_api("物料行情")
print(aa)
