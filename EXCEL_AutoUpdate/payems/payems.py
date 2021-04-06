#!/usr/bin/env python
# coding: utf-8


# making list of list 
import openpyxl
import statistics as stats
from datetime import timezone
from datetime import datetime

book = openpyxl.load_workbook('經濟數據-FRED增益集.xlsx')

#sheet = book.active
sheet=book['就業-月']

def recordlist(alpha,i):
    data=sheet[alpha+str(i)].value
    record=data    # if you wanna only a list
    #record=[data]    # if you wanna list of list
    return record

date=[recordlist('A',i) for i in range(8,sheet.max_row+1) if recordlist('A',i) != None]
date=[each.strftime("%m/%y") for each in date]
print(date[-12:])
unrate=[recordlist('E',i) for i in range(8,sheet.max_row+1) if recordlist('E',i) != None]
print(unrate[-12:])
payems=[recordlist('B',i) for i in range(8,sheet.max_row+1) if recordlist('B',i) != None]
payems_icz=[payems[j]-payems[j-1] for j in range(len(payems)) if j>0]
print(payems_icz[-12:])
#print(sheet.max_row)
#print(len(sheet['G']))


import json

dict={}
dict['date']=date[-12:]
dict['unrate']=unrate[-12:]
dict['payems_icz']=payems_icz[-12:]
print(dict)

with open('payems.json', 'w') as json_file:
    json.dump(dict, json_file)


