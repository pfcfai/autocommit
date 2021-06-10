#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
IO='/home/spark/autocommit/EXCEL_AutoUpdate/CMoneyDatabase.xlsm'
df=pd.read_excel(io=IO,sheet_name="樹",usecols="P,V:Y")
df=df[df['買超概算']<-5]
df = df.drop(['三大買超佔比'], axis=1).reset_index(drop=True)
print(df)


# In[2]:


def add_one(x):
    if x > 20:
        return '很強'
    elif 20>x>10:
        return '上漲ing'
    elif 10>x>0:
        return '緩緩上漲'
    elif 0>x>-10:
        return '緩緩下跌'
    elif -10>x>-20:
        return '下跌ing'
    else:
        return '很弱'
 
df['node1'] = df['區間漲幅'].apply(add_one)
df = df.drop(['區間漲幅'], axis=1)
print(df)


# In[3]:


def round_one(x):
    y=round(x,2)
    z=y
    return z
    

#df['node2']=df['代號']+' * '+df['test']
df['node2']=df['代號']
df['node3']=df['買超概算'].apply(round_one)
df = df.drop(['買超概算'], axis=1).drop(['代號'], axis=1)

print(df)


# In[4]:


df['node4'] = df['分類']
df = df.drop(['分類'], axis=1)

print(df)


# In[5]:


# making dict like 
# [{  name: 'Europe',
#     data: [{ name: 'Germany', value: 767.1},...]},{}]
# ['TWSE','很強'],['TWSE','上漲ing'],['TWSE','緩緩上漲'],['TWSE','緩緩下跌'],['TWSE','下跌ing'],['TWSE','很弱']]

dict={'緩緩下跌':'list1','下跌ing':'list2','很弱':'list3','緩緩上漲':'list4','上漲ing':'list5','很強':'list6'}
list1=[]
list2=[]
list3=[]
list4=[]
list5=[]
list6=[]

for i in range(len(df)):
    levelname=df.iloc[i][0]
    dataname=df.iloc[i][1]
    datavalue=df.iloc[i][2]
    print(df.iloc[i][0],df.iloc[i][1],df.iloc[i][2])

    dict2={}
    if levelname=='緩緩下跌':
        dict2['name']=df.iloc[i][1]
        dict2['value']=df.iloc[i][2]
        list1.append(dict2)
    elif levelname=='下跌ing':
        dict2['name']=df.iloc[i][1]
        dict2['value']=df.iloc[i][2]
        list2.append(dict2)
    elif levelname=='很弱':
        dict2['name']=df.iloc[i][1]
        dict2['value']=df.iloc[i][2]
        list3.append(dict2)
    elif levelname=='緩緩上漲':
        dict2['name']=df.iloc[i][1]
        dict2['value']=df.iloc[i][2]
        list4.append(dict2)
    elif levelname=='上漲ing':
        dict2['name']=df.iloc[i][1]
        dict2['value']=df.iloc[i][2]
        list5.append(dict2)
    elif levelname=='很強':
        dict2['name']=df.iloc[i][1]
        dict2['value']=df.iloc[i][2]
        list6.append(dict2)
        
    print(list1)
    print(list2)
    dict['list1']=list1
    dict['list2']=list2
    dict['list3']=list3
    dict['list4']=list4
    dict['list5']=list5
    dict['list6']=list6


# In[6]:


import json
with open('/home/spark/autocommit/EXCEL_AutoUpdate/Bubble.json', 'w') as json_file:
    json.dump(dict, json_file)


# In[ ]:




