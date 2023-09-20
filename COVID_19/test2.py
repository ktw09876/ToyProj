import findspark 
findspark.init()

from pyspark.sql import SparkSession
import pandas as pd

# 스파크 세션 생성
spark = SparkSession.builder.appName("pivot_test").getOrCreate()

# 주어진 데이터프레임 생성
data = [
    ("Afghanistan", 203167, 203265, 203395, 203497, 203574, 203681, 203829, 203942, 204094, 204287, 204392, 204417, 204510),
    ("Albania", 332969, 332996, 332996, 333027, 333046, 333055, 333058, 333071, 333088, 333103, 333125, 333138, 333156),
    ("Algeria", 270839, 270840, 270847, 270856, 270862, 270873, 270881, 270891, 270906, 270917, 270924, 270929, 270939),
    # 다른 국가/지역 데이터도 추가
]

columns = ["Country_Region", "2022/11/01", "2022/11/02", "2022/11/03", "2022/11/04", "2022/11/05", "2022/11/06", "2022/11/07", "2022/11/08", "2022/11/09", "2022/11/10", "2022/11/11", "2022/11/12", "2022/11/13"]

df = spark.createDataFrame(data, columns)
df.show()

# 데이터프레임을 Pandas로 변환
pandas_df = df.toPandas()

# "Country_Region" 열을 인덱스로 설정
pandas_df.set_index("Country_Region", inplace=True)

# 행과 열을 바꾸기 위해 transpose (T) 사용
transposed_df = pandas_df.T
print(transposed_df)
