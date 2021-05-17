#!/usr/bin/env python
# coding: utf-8


# In[3]:


# making list of list 
import openpyxl
import statistics as stats
from datetime import timezone
from datetime import datetime

book = openpyxl.load_workbook('CMoneyDatabase.xlsm')

# 央行利率
sheet=book['資金流']


namedict={'0':'foreigner','1':'investor'}
for k in range(2): # json files denote foreigner or investor
    mylist=[]
    for i in range(11):    # row serial which denote classify
        for j in range(6): # column serial which denote day

            innerlist=[]
            columndict={"0":"q","1":"r","2":"s","3":"t","4":"u","5":"v"}
            innerlist.append(i)
            innerlist.append(j)
            # data really locates , (0,0) is on (Q,4)
            innerlist.append(round(sheet[columndict[str(j)]+str(14*k+4+i)].value,1))
            mylist.append(innerlist)

    print(mylist)

    import json
    with open('{}_flow.json'.format(namedict[str(k)]), 'w') as json_file:
        json.dump(mylist, json_file)


