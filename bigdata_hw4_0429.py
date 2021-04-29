# -*- coding: utf-8 -*-
"""edit-bigdata HW4_Draft.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11ciui3im1RcKOcq5eEFfTFVUzYybGfDI
"""

!gdown --id 1ZK8ql8arn0pkIJZIfknNscKXn85L9ZXX -O core_poi_ny.csv
!gdown --id 1NeXqsAeIJ8zukHt5cR2s19beDoz2Xw5d -O nyc_restaurant_pattern.csv
!pip install pyspark

import pyspark
sc = pyspark.SparkContext()

sc

from pyspark.sql.session import SparkSession
spark = SparkSession(sc)
from numpy import std
from numpy import median
import datetime
import json
import csv

core='hdfs:///data/share/bdm/core-places-nyc.csv'
nyc_rest='hdfs:///data/share/bdm/weekly-patterns-nyc-2019-2020/*'

#def funtions:
def geteveryday(x):
    date_list = []
    begin_date = datetime.datetime.strptime(x[1][:10], "%Y-%m-%d")
    end_date = datetime.datetime.strptime(x[2][:10], "%Y-%m-%d")
    while begin_date + datetime.timedelta(days=1) <= end_date:
        date_str = str(begin_date.year) + '-' + str(begin_date.month) + '-' + str(begin_date.day)
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return (x[0],x[3],date_list)

def combine(x):
  combinelist=zip(x[2],json.loads(x[1]))
  return tuple(combinelist)

#select data needed in core csv
coreid=sc.textFile(core)\
         .map(lambda x: next(csv.reader([x])))\
         .map(lambda x: (x[1], x[9]))\
         .cache()

#creat naics id lists for 9 sections
rest_list=set(coreid.filter(lambda x: x[1] in ['722511'])\
           .map(lambda x:x[0])\
           .collect())
bigbox_list=set(coreid.filter(lambda x: x[1]=='452210' or x[1]=='452311')\
           .map(lambda x:x[0])\
           .collect())
cstore_list=set(coreid.filter(lambda x: x[1]=='445120')\
           .map(lambda x:x[0])\
           .collect())
drink_list=set(coreid.filter(lambda x: x[1]=='722410')\
           .map(lambda x:x[0])\
           .collect())
lrest_list=set(coreid.filter(lambda x: x[1]=='722513')\
           .map(lambda x:x[0])\
           .collect())
pnd_list=set(coreid.filter(lambda x: x[1]=='446110' or x[1]=='446191')\
           .map(lambda x:x[0])\
           .collect())
snb_list=set(coreid.filter(lambda x: x[1]=='311811' or x[1]=='722515')\
           .map(lambda x:x[0])\
           .collect())
sfs_list=set(coreid.filter(lambda x: x[1] in ['445210', '445220', '445230', '445291', '445292','445299'])\
           .map(lambda x:x[0])\
           .collect())
superm_list=set(coreid.filter(lambda x: x[1]=='445110')\
           .map(lambda x:x[0])\
           .collect())

#select needed columns in weeklu patterns
data0=sc.textFile(nyc_rest)\
  .map(lambda x: next(csv.reader([x])))\
  .map(lambda x: (x[1],x[12],x[13], x[16]))\
  .cache()

#process data for 9 sections
rest_data=data0.filter(lambda x: x[0] in rest_list)\
                .map(geteveryday)\
                .flatMap(combine)\
                .groupByKey()\
                .mapValues(list)\
                .map(lambda x: (x[0][:4],datetime.datetime.strptime(x[0],"%Y-%m-%d") ,int((median(x[1])+std(x[1]))), int((median(x[1])-std(x[1]))), int(median(x[1]))))\
                .map(lambda x: x if x[3]>=0 else (x[0],x[1], x[2], 0, x[4]))\
                .map(lambda x:  x if x[0]=='2020' else (x[0], x[1].replace(year='2020'), x[2],x[3],x[4]))\
               .cache()
bigbox_data=data0.filter(lambda x: x[0] in bigbox_list)\
                .map(geteveryday)\
                .flatMap(combine)\
                .groupByKey()\
                .mapValues(list)\
                .map(lambda x: (x[0][:4],datetime.datetime.strptime(x[0],"%Y-%m-%d") ,int((median(x[1])+std(x[1]))), int((median(x[1])-std(x[1]))), int(median(x[1]))))\
                .map(lambda x: x if x[3]>=0 else (x[0],x[1], x[2], 0, x[4]))\
                .map(lambda x:  x if x[0]=='2020' else (x[0], x[1].replace(year='2020'), x[2],x[3],x[4]))\
                .cache()
cstore_data=data0.filter(lambda x: x[0] in cstore_list)\
                .map(geteveryday)\
                .flatMap(combine)\
                .groupByKey()\
                .mapValues(list)\
                .map(lambda x: (x[0][:4],datetime.datetime.strptime(x[0],"%Y-%m-%d") ,int((median(x[1])+std(x[1]))), int((median(x[1])-std(x[1]))), int(median(x[1]))))\
                .map(lambda x: x if x[3]>=0 else (x[0],x[1], x[2], 0, x[4]))\
                .map(lambda x:  x if x[0]=='2020' else (x[0], x[1].replace(year='2020'), x[2],x[3],x[4]))\
                .cache()
drink_data=data0.filter(lambda x: x[0] in drink_list)\
                .map(geteveryday)\
                .flatMap(combine)\
                .groupByKey()\
                .mapValues(list)\
                .map(lambda x: (x[0][:4],datetime.datetime.strptime(x[0],"%Y-%m-%d") ,int((median(x[1])+std(x[1]))), int((median(x[1])-std(x[1]))), int(median(x[1]))))\
                .map(lambda x: x if x[3]>=0 else (x[0],x[1], x[2], 0, x[4]))\
                .map(lambda x:  x if x[0]=='2020' else (x[0], x[1].replace(year='2020'), x[2],x[3],x[4]))\
                .cache()
lrest_data=data0.filter(lambda x: x[0] in lrest_list)\
                .map(geteveryday)\
                .flatMap(combine)\
                .groupByKey()\
                .mapValues(list)\
                .map(lambda x: (x[0][:4],datetime.datetime.strptime(x[0],"%Y-%m-%d") ,int((median(x[1])+std(x[1]))), int((median(x[1])-std(x[1]))), int(median(x[1]))))\
                .map(lambda x: x if x[3]>=0 else (x[0],x[1], x[2], 0, x[4]))\
                .map(lambda x:  x if x[0]=='2020' else (x[0], x[1].replace(year='2020'), x[2],x[3],x[4]))\
                .cache()  
pnd_data=data0.filter(lambda x: x[0] in pnd_list)\
                .map(geteveryday)\
                .flatMap(combine)\
                .groupByKey()\
                .mapValues(list)\
                .map(lambda x: (x[0][:4],datetime.datetime.strptime(x[0],"%Y-%m-%d") ,int((median(x[1])+std(x[1]))), int((median(x[1])-std(x[1]))), int(median(x[1]))))\
                .map(lambda x: x if x[3]>=0 else (x[0],x[1], x[2], 0, x[4]))\
                .map(lambda x:  x if x[0]=='2020' else (x[0], x[1].replace(year='2020'), x[2],x[3],x[4]))\
                .cache()    

snb_data=data0.filter(lambda x: x[0] in snb_list)\
                .map(geteveryday)\
                .flatMap(combine)\
                .groupByKey()\
                .mapValues(list)\
                .map(lambda x: (x[0][:4],datetime.datetime.strptime(x[0],"%Y-%m-%d") ,int((median(x[1])+std(x[1]))), int((median(x[1])-std(x[1]))), int(median(x[1]))))\
                .map(lambda x: x if x[3]>=0 else (x[0],x[1], x[2], 0, x[4]))\
                .map(lambda x:  x if x[0]=='2020' else (x[0], x[1].replace(year='2020'), x[2],x[3],x[4]))\
                .cache()
sfs_data=data0.filter(lambda x: x[0] in sfs_list)\
                .map(geteveryday)\
                .flatMap(combine)\
                .groupByKey()\
                .mapValues(list)\
                .map(lambda x: (x[0][:4],datetime.datetime.strptime(x[0],"%Y-%m-%d") ,int((median(x[1])+std(x[1]))), int((median(x[1])-std(x[1]))), int(median(x[1]))))\
                .map(lambda x: x if x[3]>=0 else (x[0],x[1], x[2], 0, x[4]))\
                .map(lambda x:  x if x[0]=='2020' else (x[0], x[1].replace(year='2020'), x[2],x[3],x[4]))\
                .cache()
superm_data=data0.filter(lambda x: x[0] in superm_list)\
                .map(geteveryday)\
                .flatMap(combine)\
                .groupByKey()\
                .mapValues(list)\
                .map(lambda x: (x[0][:4],datetime.datetime.strptime(x[0],"%Y-%m-%d") ,int((median(x[1])+std(x[1]))), int((median(x[1])-std(x[1]))), int(median(x[1]))))\
                .map(lambda x: x if x[3]>=0 else (x[0],x[1], x[2], 0, x[4]))\
                .map(lambda x:  x if x[0]=='2020' else (x[0], x[1].replace(year='2020'), x[2],x[3],x[4]))\
                .cache()

#sort and covert rdd to df with right column names
rest_data_sort=rest_data.sortBy(lambda x:x[1]).sortBy(lambda x:x[0])
df_rest = spark.createDataFrame(rest_data_sort, ['year', 'date','high','low','median'])

bigbox_data_sort=bigbox_data.sortBy(lambda x:x[1]).sortBy(lambda x:x[0])
df_bigbox = spark.createDataFrame(bigbox_data_sort, ['year', 'date','high','low','median'])

cstore_data_sort=cstore_data.sortBy(lambda x:x[1]).sortBy(lambda x:x[0])
df_cstore = spark.createDataFrame(cstore_data_sort, ['year', 'date','high','low','median'])

drink_data_sort=drink_data.sortBy(lambda x:x[1]).sortBy(lambda x:x[0])
df_drink = spark.createDataFrame(drink_data_sort, ['year', 'date','high','low','median'])

lrest_data_sort=lrest_data.sortBy(lambda x:x[1]).sortBy(lambda x:x[0])
df_lrest = spark.createDataFrame(lrest_data_sort, ['year', 'date','high','low','median'])

pnd_data_sort=pnd_data.sortBy(lambda x:x[1]).sortBy(lambda x:x[0])
df_pnd = spark.createDataFrame(pnd_data_sort, ['year', 'date','high','low','median'])

snb_data_sort=snb_data.sortBy(lambda x:x[1]).sortBy(lambda x:x[0])
df_snb = spark.createDataFrame(snb_data_sort, ['year', 'date','high','low','median'])

sfs_data_sort=sfs_data.sortBy(lambda x:x[1]).sortBy(lambda x:x[0])
df_sfs = spark.createDataFrame(sfs_data_sort, ['year', 'date','high','low','median'])

superm_data_sort=superm_data.sortBy(lambda x:x[1]).sortBy(lambda x:x[0])
df_superm = spark.createDataFrame(superm_data_sort, ['year', 'date','high','low','median'])

#output csv files
df_rest.write.csv('full_service_restaurants.csv')
df_bigbox.write.csv('big_box_grocers.csv')
df_cstore.write.csv('convenience_stores.csv')
df_drink.write.csv('drinking_places.csv')
df_lrest.write.csv('limited_service_restaurants.csv')
df_pnd.write.csv('pharmacies_and_drug_stores.csv')
df_snb.write.csv('snack_and_bakeries.csv')
df_sfs.write.csv('specialty_food_stores.csv')
df_superm.csv('supermarkets_except_convenience_stores.csv')