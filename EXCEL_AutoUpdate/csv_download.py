#!/usr/bin/env python
# coding: utf-8


# this is used to download origin csv, and need to transfer to .xlsx manually

# In[1]:


import requests
csv_url='https://www.cbc.gov.tw/public/data/OpenData/外匯局/FTDOpenData015.csv'
req = requests.get(csv_url)
url_content = req.content
csv_file = open('NTD.csv', 'wb')
csv_file.write(url_content)
csv_file.close()



