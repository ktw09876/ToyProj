import s3_upload as ul #내가 작성한 .py를 임포트할 수 있음

import findspark 
findspark.init()
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
################################### s3 데이터를 읽고 가공 후 저장 #######################################################


input_s3_covid_path = f's3a://{ul.bucket_name}/{ul.covid_folder_name}/'
input_s3_iso_path = f's3a://{ul.bucket_name}/{ul.iso_folder_name}/'
output_local_file_path = 'C:/Users/dhqhf/vscode-workspace/ToyProj/COVID_19/output/'

spark_conf = SparkConf().setAll([
      ('spark.hadoop.fs.s3a.access.key', ul.aws_access_key_id)
    , ('spark.hadoop.fs.s3a.secret.key', ul.aws_secret_access_key)
    , ('spark.hadoop.fs.s3a.endpoint', f's3.{ul.region_name}.amazonaws.com')
    , ('spark.hadoop.fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem')
    , ('spark.hadoop.home', 'C:/hadoop/hadoop2/hadoop-3.2.4')
    #메모리 관리 문제 해결중...
    # , ('spark.executor.memory', '8g')
    # , ('spark.executor.memoryOverhead', '2g')
    # , ('spark.driver.memory', '4g')
    # , ('spark.driver.extraJavaOptions', '-Xss4m')
])

spark = (
         SparkSession.builder
        .appName('Learning_Spark')
        .config(conf = spark_conf)
        .getOrCreate()
    )

json_schema = StructType([
    StructField('Converted_Country', StringType(), True),
    StructField('json_Country_Region', StringType(), True),
])

#json 파일 불러오기
json_data = spark.read.option('multiline', 'true').schema(json_schema).json(f'{input_s3_covid_path}country_convert.json')

file_paths = (
             spark.sparkContext.binaryFiles(f's3a://{ul.bucket_name}/{ul.covid_folder_name}')
            .keys()
            .collect()
        )

#월별 daily_repoty url을 리스트로 가져옴
url_groups  = {}
for url in file_paths:
    if url.endswith('.csv'):
        date_start_index = url.rfind('/') + 1 
        date = url[date_start_index:date_start_index + 2] 
        if date not in url_groups:
            url_groups[date] = []  
        url_groups[date].append(url) 

#컬럼명을 내가 원하는 날짜형태로 수정하는 함수
def rename_columns(df):
    renamed_columns = []

    for col_name in df.columns[1:]: #두번째 컬럼부터
        #'mm/dd/yyyy'형태의 컬럼명을 'yyyy/mm/dd'형태로 변환, 좀 더 나은 방법 없을까?
        yyyy = col_name.split('/')[2]
        mm = col_name.split('/')[0]
        dd = col_name.split('/')[1]
        fileName = f'{yyyy}/{mm}/{dd}' 

        renamed_columns.append(fileName) #빈 리스트에 추가
        
    renamed_columns.insert(0, df.columns[0]) #첫번째 컬럼에 'Country_Region' 추가
    
    # #기존 컬럼명과 'yyyy/mm/dd'형태로 만든 컬럼명을 묶어서(zip) 새로운 컬럼명으로 수정(withColumnRenamed) --> 스택 오버 플로우 가능성 있음 
    # for old_name, new_name in zip(df.columns, renamed_columns):
    #     df = df.withColumnRenamed(old_name, new_name)
    
    #다른 방법
    df = df.selectExpr(*[f"`{col_name}` as `{new_name}`" for col_name, new_name in zip(df.columns, renamed_columns)])

    #컬럼명을 날짜별로 정렬
    df_sorted = df.select('Country_Region', *sorted(df.columns[1:]))

    return df_sorted

#각각의 .csv파일의 컬럼명'Country/Region'를 'Country_Region'로 수정, 'Confirmed'에 값이 없는 행 삭제
def create_daily_report_df(path, filename):
    result_df = None

    #해당 경로의 .csv파일을 읽어온다
    df = spark.read.option('header', 'true').csv(f'{path}{filename}')

    #만약 result_df의 컬럼중에 'Confirmed'컬럼이 있으면
    if 'Confirmed' in df.columns:
        result_df = df.dropna(subset = ['Confirmed']) #'Confirmed'의 값이 없는 행 삭제
        result_df = result_df.withColumn('Confirmed', result_df['Confirmed'].cast('int')) #'Confirmed'값을 int형으로 타입 변환

    #만약 result_df의 컬럼중에 'Confirmed'컬럼이 없으면
    else: 
        print(f"에러!! 해당 파일에서는 컬럼명 'Confirmed'를 찾을 수 없습니다: {filename}")
        print(df.columns)
        result_df = None

    #'Country/Region' --> 'Country_Region' 컬럼명 수정
    result_df = result_df.withColumnRenamed('Country/Region', 'Country_Region')
    
    return result_df

#최종 데이터프레임을 만드는 함수
def create_final_df(input_s3_covid_path, path):
    file_list = []
    first_df = True
    final_df = None

    #covid_daily_report.csv 파일 이름만 있는 리스트를 얻는다
    for file_path in path:
        if file_path.split('.')[-1] == 'csv':
            fileName = file_path.split('/')[-1]
            file_list.append(fileName)

    for file in file_list:
        date_column = file.split('.')[0].replace('-', '/')

        #각각의 .csv파일의 컬럼명'Country/Region'를 'Country_Region'로 수정, 'Confirmed'에 값이 없는 행 삭제
        df = create_daily_report_df(input_s3_covid_path, file)

        #반환 받은 데이터프레임에 값이 있으면
        if df is not None:

            #'Country_Region'로 groupBy sum()하고 컬럼명을 날짜형태로 수정
            df = df.groupBy('Country_Region').sum('Confirmed')
            df = df.withColumnRenamed('sum(Confirmed)', date_column)

            #'Country_Region'컬럼으로 전체 df를 조인
            if first_df:
                final_df = df
                first_df = False
            else:
                final_df = final_df.join(df, on = 'Country_Region', how = 'outer') #조인 방식 아우터인지 레프트인지 확인
        else:
            final_df = df

    #결측값을 0으로 수정
    df = final_df.fillna(0)

    #조인하지 않고 더 쉽게 하는 방법 없나?
    #'Country_Region'를 기준으로 json_data를 레프트 조인
    df = df.join(json_data, df['Country_Region'] == json_data['Converted_Country'], how = 'left')
    df = df.drop('Converted_Country', 'json_Country_Region')

    # 컬럼명을 내가 원하는 날짜형태로 수정
    result_df = rename_columns(df)
    
    return result_df

# #하나의 데이터프레임에 모아서 생성
# df = create_final_df(input_s3_covid_path, file_paths)
# # df_final_country = create_country_Flag(country_path)

# #파티션 수 늘리기
# df_final_country = df.repartition(10) #셔플 사용, 파티션을 늘리거나 줄이거나 할 수 있음

# #데이터프레임 저장
# (
#     df.coalesce(1)
#     .write
#     .format('parquet')
#     .mode("overwrite")
#     .save(output_local_file_path) 
# )
# print(f'경로: {output_local_file_path} 결과 파일 저장 성공')

#해당 파일이 메인프로그램인지 모듈(import 되어 사용되는)인지 구분하기 위한 코드
#if __name__  =  =  '__main__': 이하 코드는 현재 스크립트가 다른 곳에서 import되어 사용될 경우 실행하지 않을 코드임
if __name__ == '__main__': 
    #월별로 데이터를 가공 후 다른 폴더에 각각 저장
    for date_prefix, url_list in url_groups.items():
        # 데이터 가공
        df = create_final_df(input_s3_covid_path, url_list)

        #파티션 수 늘리기
        df_final_country = df.repartition(10) #셔플 사용, 파티션을 늘리거나 줄이거나 할 수 있음

        #결과 데이터프레임을 저장
        output_folder_path = f'{output_local_file_path}{date_prefix}' #메모리 관리 문제 해결중...coalesce(1) #강제가 아닌 이상 셔플 사용X, 파티션을 줄이기만 가능
        (
             df_final_country
            .coalesce(1)
            .write
            .format('parquet')
            .mode('overwrite')
            .save(output_folder_path) 
        )
        print(f'경로: {output_local_file_path}{date_prefix} 결과 파일 저장 성공')



# 결과 데이터프레임을 S3에 업로드는 iam 계정 업로드 권한 문제로 보류
