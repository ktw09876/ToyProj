import os
###현재 작업 디렉토리를 스크립트 위치로 변경
script_dir = os.path.dirname(__file__) #현재 스크립트의 절대 경로 중 폴더까지의 경로를 가져온다
os.chdir(script_dir) #해당 경로로 작업 경로를 변경한다
# print(f"script path: {os.getcwd()}") #변경된 경로 확인
import s3_upload as ul

import boto3
from functools import reduce
from pyspark.sql import SparkSession, DataFrame

class DataLoad():
    def __init__(self, ul_client: ul.MinioUpload):

        # Spark 세션 생성 #UI에 표현되는 이름
        self.spark = (
            SparkSession.builder 
            .appName("Read CSV from MinIO") #spark 어플리케이션 이름, UI에 표현되는 이름
            .config("spark.hadoop.fs.s3a.endpoint", f'http://{ul_client.ip}:{ul_client.port}') 
            .config("spark.hadoop.fs.s3a.access.key", ul_client.username) 
            .config("spark.hadoop.fs.s3a.secret.key", ul_client.password) 
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") #hadoop 파일 시스템 구현, S3에 접근하기 위해 필요
            .config("spark.hadoop.fs.s3a.path.style.access", True) #S3 스토리지의 객체에 접근할 때 필요
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", False) #SSL 연결 활성화 여부, False = http/ True = https
            .config('spark.hadoop.home', 'D:/tool/Python/hadoop/hadoop-3.3.6') #S3 스토리지의 객체에 접근할 때 필요, hadoop 경로
            .getOrCreate()
        )

        self.output = os.path.join('..', 'output')

    ###MiniO에 있는 파일을 리스트 형태로 읽어서 반환
    def bucket_read_data(self, brd_client: boto3.client, brd_bucket_name: str) -> list:
        
        #S3의 파일 리스트를 가져오기 위해 list_objects() 보다 list_objects_v2() 사용하고 싶었지만
        #MiniO 클라이언트에는 list_objects_v2() 가 없음
        #호환 되는 boto3 으로 변경
        paginator = brd_client.get_paginator('list_objects_v2') 
        list = paginator.paginate(Bucket = brd_bucket_name)

        file_list = []

        for page in list:
            if "Contents" in page:
                for obj in page["Contents"]:
                    file_list.append(obj["Key"])

        return file_list

    ###.csv파일을 데이터프레임으로 읽어서 전처리
    def process_df(self, cd_spark: SparkSession, cd_df_name: str, cd_buck_name: str) -> DataFrame:

            ### 데이터프레임을 읽어옴
            df = cd_spark.read.csv(
                f's3a://{cd_buck_name}/{cd_df_name}'
                ,header = True
                ,inferSchema = True #스키마(데이터타입)를 자동으로 추론한다 False 의 경우 모든 데이터를 문자열(String)로 읽어온다
            )
            # df.show(10) #결과 확인

            ###데이터프레임 전처리
            #'Confirmed'컬럼이 있으면
            if 'Confirmed' in df.columns:
                drop_df = df.dropna(subset = ['Confirmed'])                                 #'Confirmed'의 값이 없는 행 삭제
                cast_df = drop_df.withColumn('Confirmed', drop_df['Confirmed'].cast('int')) #'Confirmed'값을 int형으로 타입 변환
                sum_df = cast_df.groupBy('Country_Region').sum('Confirmed')                 # 각 나라(Country_Region) 별로 group by
                rename_df = sum_df.withColumnRenamed('Country/Region', 'Country_Region')    #'Country/Region' --> 'Country_Region' 컬럼명 수정

                ###'Country_Region' 와 'Confirmed' 만 가지고 새로운 데이터프레임 생성
                select_df = rename_df.select('Country_Region', 'sum(Confirmed)')
                # select_df.show(10) # 결과 확인

                return select_df
            
            #'Confirmed'컬럼이 없으면
            else: 
                print(f"Error!! The column name 'Confirmed' cannot be found in the file. {cd_df_name}")

    ###최종 데이터프레임 생성
    def create_final_df(self, cfd_df: DataFrame, cfd_columns: list) -> DataFrame:
        cfd_columns.insert(0, cfd_df.columns[0]) #날짜 형태의 리스트 첫번째에 'Country_Region' 추가
        
        ###데이터프레임 컬럼명을 날짜 형태로 모두 변경
        df_renamed = cfd_df.toDF(*cfd_columns)

        ###컬럼명을 날짜 별로 정렬
        df_sorted = df_renamed.select('Country_Region', *sorted(df_renamed.columns[1:]))

        return df_sorted

    ###데이터프레임을 join
    def join_dataframes(self, prev_df: DataFrame, next_df: DataFrame) -> DataFrame:
        return prev_df.join(next_df, on = 'Country_Region', how = "outer")

    #파일명(01-01-2021.csv)을 전달 받아서 날짜형태 문자열을 리턴
    def rename_columns(self, rnc_name: str) -> str:
        date_str = rnc_name.replace('.', '-') #'01-01-2021.csv' --> '01-01-2021-csv' 로 변환

        #'mm-dd-yyyy-csv'를 'yyyy/mm/dd'형태로 변환
        yyyy = date_str.split('-')[2]
        mm = date_str.split('-')[0]
        dd = date_str.split('-')[1]
        date_form = f'{yyyy}/{mm}/{dd}' 

        return date_form
    
    ###년도 별로 나눠서 저장 ing...
    def save_df(self, sd_df: DataFrame, sd_output: str) -> None:
        (
            sd_df
            .coalesce(1)
            .write.mode('overwrite')
            .option('header', 'true')
            .csv(fr'{sd_output}')
        )
        print(f'path: {sd_output} save access')
                 
        
def main():
    ul_cli = ul.MinioUpload('https://api.github.com/repos/CSSEGISandData/COVID-19/contents/csse_covid_19_data/csse_covid_19_daily_reports')
    dl_cli = DataLoad(ul_cli)

    ###MiniO 에 있는 파일을 리스트 형태로 읽어옴
    df_list = dl_cli.bucket_read_data(ul_cli.s3_client, ul_cli.bucket_name)

    ###각각의 파일(.csv)을 데이터프레임으로 읽어서 전처리
    result_dfs = []
    rename_cols = []

    for df_name in df_list:
        process_df = dl_cli.process_df(dl_cli.spark, df_name, ul_cli.bucket_name) #각 데이터프레임 가공
        rename_col = dl_cli.rename_columns(df_name) #파일이름을 이용해 날짜 형태의 문자열을 얻는다

        result_dfs.append(process_df)
        rename_cols.append(rename_col)

    ###전처리한 데이터프레임 join
    join_dfs = reduce(dl_cli.join_dataframes, result_dfs)
    # join_dfs.show(10) #결과 확인

    ###join한 데이터프레임과 새롭게 만든 컬럼이름 리스트를 가지고 최종 데이터프레임을 생성
    final_df = dl_cli.create_final_df(join_dfs, rename_cols)
    final_df.show(10)
    print(f'total count:{final_df.count()}')
    print(f'total column count:{len(final_df.columns)}')

    #결과 데이터프레임을 저장
    dl_cli.save_df(final_df, dl_cli.output)

    ###DB insert ing...
    
    

    dl_cli.spark.stop()

if __name__ == '__main__':
    main()