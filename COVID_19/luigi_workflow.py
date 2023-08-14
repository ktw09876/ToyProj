import luigi as lui
from datetime import datetime

import s3_upload as ul
import data_load as dl
import db_Insert as db



#파일 이름 날짜 포맷
timestamp_format = '%Y%m%d_%H%M%S'
timestamp = datetime.now().strftime(timestamp_format)

#결과 로그 파일 경로
result_path = 'COVID_19/output/result/'
upload_result = f'{result_path}s3_upload/{timestamp}_upload_result.txt'
data_result = f'{result_path}DataLoad/{timestamp}_data_result.txt'
insert_result = f'{result_path}DBInsert/{timestamp}_insert_result.txt'



#s3_upload.py
class S3Update(lui.Task):
    def run(self):   
        print('S3Update 시작')

        # 깃허브에 있는 iso파일을 aws S3에 저장
        if ul.response_iso.status_code == 200: #성공, 서버가 요청에 응답함
            iso_total_cnt = ul.from_git_to_s3_load_all(ul.bucket_name, ul.iso_folder_name, ul.response_iso) #깃허브의 iso파일을 업로드 할 때
            print(f'업로드한 파일은 총 {iso_total_cnt}개 입니다')
        else:
            #Luigi의 경우 
            print(f'실패, iso파일을 가져오지 못 했습니다. status_code = {ul.response_iso.status_code}')

        # 깃허브에 있는 covid파일을 aws S3에 저장
        if ul.response_covid.status_code == 200: #성공, 서버가 요청에 응답함
            covid_total_cnt = ul.from_git_to_s3_load_all(ul.bucket_name, ul.covid_folder_name, ul.response_covid) #깃허브의 모든 covid파일을 업로드 할 때
            print(f'업로드한 파일은 총 {covid_total_cnt}개 입니다')
        else:
            print(f'실패, iso파일을 가져오지 못 했습니다. status_code = {ul.response_covid.status_code}')

        #결과 로그 생성
        #루이지에서는 encoding 지원이 제한적인 것 같다
        with self.output().open('w') as f:
            f.write(f'upload iso = {iso_total_cnt}/upload covid = {covid_total_cnt}')

        print('S3Update 실행 완료')

    #결과 로그 파일 생성
    def output(self):
        return lui.LocalTarget(upload_result) #결과 파일 날짜별로 확인
    

#data_load.py
class DataLoad(lui.Task):
    def requires(self): #의존성 설정 
        return S3Update() #s3_upload()가 실행되어야지만 DataLoad()가 실행된다

    def run(self):
        print('DataLoad 시작')
        for date_prefix, url_list in dl.url_groups.items():

            # 데이터 가공
            df = dl.create_final_df(dl.input_s3_covid_path, url_list)

            #파티션 수 늘리기
            df_final_country = df.repartition(10) #셔플 사용, 파티션을 늘리거나 줄이거나 할 수 있음

            #결과 데이터프레임을 저장
            output_folder_path = f'{dl.output_local_file_path}{date_prefix}' #메모리 관리 문제 해결중...coalesce(1) #강제가 아닌 이상 셔플 사용X, 파티션을 줄이기만 가능
            (
                df_final_country
                .coalesce(1)
                .write
                .format('parquet')
                .mode('overwrite')
                .save(output_folder_path) 
            )

            #결과 로그 생성
            with self.output().open('w') as f:
                f.write(f'{timestamp}_path = {dl.output_local_file_path}{date_prefix} Save Result File Successful')

        print('DataLoad 실행 완료')

    #결과 로그 파일 생성
    def output(self):
        return lui.LocalTarget(data_result) #결과 로그 파일 날짜별로 확인


#db_Insert.py
class DBInsert(lui.Task): 
    def requires(self): #의존성 설정 
        return DataLoad() #DataLoad()가 실행되어야지만 DBInsert()가 실행된다
    
    def run(self):
        print('DBInsert 시작')

        #DB에 인서트
        for date_prefix, url_list in dl.url_groups.items():
            table_name = f'COVID_19_{date_prefix}'  #테이블 이름 지정

            #오라클에 해당 테이블이 있는지 조건 검사
            if db.spark.catalog.tableExists(table_name): #만약 테이블이 이미 있다면

                #결과 로그 생성
                with self.output().open('w', encoding='utf-8') as f:
                    f.write(f'{timestamp}_이미 생성 되어 있는 테이블 입니다. 테이블명: {table_name}')
            else:
                
                #데이터 가공
                df = dl.create_final_df(dl.input_s3_covid_path, url_list)
                count = df.count() #인서트될 데이터프레임 카운트

                #파티션 수 늘리기
                df.repartition(10) #셔플 사용, 파티션을 늘리거나 줄이거나 할 수 있음

                #오라클에 자동으로 테이블 생성 및 인서트
                df.coalesce(1).write.jdbc(url = db.url, table = table_name, mode = 'overwrite', properties = db.properties)

        #결과 로그 파일 생성 예시
        with self.output().open('w') as f:
            for date_prefix, url_list in dl.url_groups.items():
                f.write(f'{timestamp}_{table_name} count(*) = {count}')

        print('DBInsert 실행 완료')

    #결과 로그 파일 생성
    def output(self):
        return lui.LocalTarget(insert_result) #결과 로그 파일 날짜별로 확인


if __name__ == '__main__':
    # lui.run([ 'DBInsert', '--local-scheduler' ])#단일작업을 실행할 때 여러 작업을 실행할 때는 luigi.build() - 여러 작업을 동시에 실행할 수 있다
    lui.build(
              [DBInsert()] #실행시킬 작업, DBInsert()만 실행시켜도 의존성 때문에 s3_upload(), DataLoad(), DBInsert() 모두 실행
            , local_scheduler = True #UI가 아닌 로컬 스케줄러를 이용하겠다
        ) 