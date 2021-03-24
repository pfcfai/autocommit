#!/usr/bin/env python
# coding: utf-8



import pandas as pd

df_nt=pd.read_csv('https://raw.githubusercontent.com/laurenttang/pfcfProject/main/Overseas3D/NTD.csv') 
df_nt=pd.read_csv('https://raw.githubusercontent.com/laurenttang/pfcfProject/main/FTDOpenData015.csv')
NTD=df_nt['NTD/USD'].iloc[-1]
print(NTD)



# making list of list 
import openpyxl
from openpyxl.reader.excel import load_workbook

wb=openpyxl.load_workbook('/home/pfcf/pfcfProject/FTDOpenData015.xlsx')

print(wb.sheetnames[0])
sheet=wb['FTDOpenData015']

def recordlist(i):
    date=sheet['A'+str(i)].value
    twse=sheet['B'+str(i)].value
    

    record=[date,twse]
    return record

mylist=[recordlist(i) for i in range(3,3292)]
print(mylist)

# save as json
import json

my_details = {
    'name': 'John Doe',
    'age': 29
}

with open('test.json', 'w') as json_file:
    json.dump(mylist, json_file)
