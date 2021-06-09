#!/usr/bin/env python
# coding: utf-8


# In[2]:


import pandas as pd
IO='/home/spark/autocommit/EXCEL_AutoUpdate/CMoneyDatabase.xlsm'
df=pd.read_excel(io=IO,sheet_name="樹",usecols="l,N:Q")
df=df[df['三大買超佔比']>5]
df = df.drop(['三大買超佔比'], axis=1).reset_index(drop=True)
print(df)


# In[3]:


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


# In[4]:


def round_one(x):
    y=round(x,2)
    z=str(y)+"(億)"
    return z
    

#df['node2']=df['代號']+' * '+df['test']
df['node2']=df['代號']
df['node3']=df['買超概算'].apply(round_one)
df = df.drop(['買超概算'], axis=1).drop(['代號'], axis=1)

print(df)


# In[5]:


'''
def delete_one(x):
    if x[0] == '電':
        return x[0:7]
    else:
        return x[0:5]
'''   
#df['node3'] = df['分類'].apply(delete_one)
df['node4'] = df['分類']
df = df.drop(['分類'], axis=1)

print(df)


# In[6]:





# In[7]:


#making list
mylist=[['TWSE','很強'],['TWSE','上漲ing'],['TWSE','緩緩上漲'],['TWSE','緩緩下跌'],['TWSE','下跌ing'],['TWSE','很弱']]
for i in range(len(df)):
    stem=df.iloc[i][0:2].tolist()
    mylist.append(stem)
for i in range(len(df)):
    leaf=df.iloc[i][1:3].tolist()
    mylist.append(leaf)
#for i in range(len(df)):
#    leaf2=[df.iloc[i][1],df.iloc[i][3]]
#    mylist.append(leaf2)
print(mylist)


# In[8]:


import json
with open('/home/spark/autocommit/EXCEL_AutoUpdate/Tree_flow.json', 'w') as json_file:
    json.dump(mylist, json_file)


