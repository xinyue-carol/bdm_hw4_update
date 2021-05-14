# -*- coding: utf-8 -*-
"""bdm_hw4_df.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BLzl99BOycX4kgoIbAa46icKaDLflaVI
"""

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.functions import col, lit, expr
import datetime
import json
import numpy as np
import sys
import ast
import itertools
 
def main(sc, spark):

    dfPlaces = spark.read.csv('/data/share/bdm/core-places-nyc.csv', header=True, escape='"')
    dfPattern = spark.read.csv('/data/share/bdm/weekly-patterns-nyc-2019-2020/*', header=True, escape='"')
    
    #step C.
    CAT_CODES = {'445210', '722515', '445299', '445120', '452210', '311811', '722410', '722511', '445220', '445292', '445110', '445291', '445230', '446191', '446110', '722513', '452311'}
    CAT_GROUP = {'452210': 0, '452311': 0, '445120': 1, '722410': 2, '722511': 3, '722513': 4, '446110': 5, '446191': 5, '722515': 6, '311811': 6, '445210': 7, '445299': 7, '445230': 7, '445291': 7, '445220': 7, '445292': 7, '445110': 8}
    #step D, E, F ,G
    dfD = dfPlaces.select('placekey','naics_code').filter(dfPlaces.naics_code.isin(CAT_CODES))
    udfToGroup = F.udf(lambda x: CAT_GROUP[x])
    dfE = dfD.withColumn('group', udfToGroup('naics_code').cast("Integer"))
    dfF = dfE.drop('naics_code').cache()
    groupCount = dfF.groupBy("group").count().toPandas().set_index('group')['count'].to_dict()

    #step h.
    def expandVisits(date_range_start, visits_by_day):
          visitsByDay=ast.literal_eval(visits_by_day)
          begin_date = datetime.datetime.strptime(date_range_start[:10], "%Y-%m-%d")
          my_dates=[]
          for i in range(7):
            my_dates.append((begin_date + datetime.timedelta(days=i)).isoformat()[:10])
          expanded_list=[]
          for idx, value in enumerate(my_dates):
            if value[:4] !="2018":
              expanded_list.append( (int(value[:4]), value[5:], visitsByDay[idx]))
              return expanded_list


    visitType = T.StructType([T.StructField('year', T.IntegerType()),
                              T.StructField('date', T.StringType()),
                              T.StructField('visits', T.IntegerType())])

    udfExpand = F.udf(expandVisits, T.ArrayType(visitType))

    dfH = dfPattern.join(dfF, 'placekey') \
        .withColumn('expanded', F.explode(udfExpand('date_range_start', 'visits_by_day'))) \
        .select('group', 'expanded.*')
    #step I.
    def computeStats(group, visits):
      vis_len= len(visits)
      real_len =groupCount[group]
      n=real_len-vis_len
      zeros=list(itertools.repeat(0, n))
      fin_lis=zeros+visits
      media = np.median(fin_lis)
      sd =np.std(fin_lis)
      mx=np.max

      low = media - sd
      low = low if low > 0 else 0
      high = media + sd
      high = high if high > 0 else 0  
      return int(media), int(low), int(high)

    statsType = T.StructType([T.StructField('median', T.IntegerType()),
                              T.StructField('low', T.IntegerType()),
                              T.StructField('high', T.IntegerType())])

    udfComputeStats = F.udf(computeStats, statsType)

    dfI = dfH.groupBy('group', 'year', 'date') \
        .agg(F.collect_list('visits').alias('visits')) \
        .withColumn('stats', udfComputeStats('group', 'visits'))
    #stepJ.
    dfJ = dfI.select('group','year', 'date','stats.*').sort("year","date").withColumn("2020",lit('2020')).withColumn("date",expr(" 2020 ||'-'|| date")).drop('2020')

    #output
    OUTPUT_PREFIX = sys.argv[1]
    filelist=['big_box_grocers','convenience_stores','drinking_places','full_service_restaurants','limited_service_restaurants','pharmacies_and_drug_stores','snack_and_retail_bakeries','specialty_food_stores','supermarkets_except_convenience_stores']
    for i in range(len(filelist)):
      filename = filelist[i]
      groupcode=str('group='+str(i))
      dfJ.filter(f'{groupcode}') \
          .drop('group') \
          .coalesce(1) \
          .write.csv(f'{OUTPUT_PREFIX}/{filename}',
                    mode='overwrite', header=True)


if __name__=='__main__':
    sc = SparkContext()
    spark = SparkSession(sc)
    main(sc, spark)
