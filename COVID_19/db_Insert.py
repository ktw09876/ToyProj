import data_load as dl #내가 작성한 .py를 임포트할 수 있음

from pyspark.sql import SparkSession
################################### 처리한 데이터프레임을 DB에 인서트 #######################################################


spark = (
     SparkSession.builder.appName('Insert Oracle') #spark UI에 표시되는 이름
    .config('spark.jars', 'file:///c:/spark/spark-3.4.1-bin-hadoop3/jars/ojdbc11.jar') #오라클 드라이버 위치
    .getOrCreate()
)

#오라클 접속 정보
url = 'jdbc:oracle:thin:@//localhost:1521/xe' 
properties = {
    'user': 'c##test_user',
    'password': '1111',
    'driver': 'oracle.jdbc.driver.OracleDriver'
}

#DB에 인서트
for date_prefix, url_list in dl.url_groups.items():
    table_name = f'COVID_19_{date_prefix}'  #테이블 이름 지정

    #오라클에 해당 테이블이 있는지 조건 검사
    if spark.catalog.tableExists(table_name): #만약 테이블이 이미 있다면
        print(f'이미 생성 되어 있는 테이블 입니다. 테이블명: {table_name}')
    else:
        #오라클에 자동으로 테이블 생성 및 인서트
        #데이터 가공
        df = dl.create_final_df(dl.input_s3_covid_path, url_list)
        count = df.count() #인서트될 데이터프레임 카운트

        #파티션 수 늘리기
        df_final_country = df.repartition(10) #셔플 사용, 파티션을 늘리거나 줄이거나 할 수 있음

        df.coalesce(1).write.jdbc(url = url, table = table_name, mode = 'overwrite', properties = properties)
        print(f'삽입된 data는 총{count}개 입니다.')



spark.stop()
