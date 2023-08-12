import luigi
import s3_upload as s3
import data_load as dl
import db_Insert as db

class S3_Upload(luigi.Task):
    def run(self):
        if s3.response_iso.status_code == 200: #성공, 서버가 요청에 응답함
            total_cnt = s3.from_git_to_s3_load_all(s3.bucket_name, s3.iso_folder_name, s3.response_iso) #깃허브의 iso파일을 업로드 할 때
            print(f'luigi_업로드한 파일은 총 {total_cnt}개 입니다')
        else:
            print('실패, iso파일을 가져오지 못 했습니다.')

        # 깃허브에 있는 covid파일을 aws S3에 저장
        if s3.response_covid.status_code == 200: #성공, 서버가 요청에 응답함
            total_cnt = s3.from_git_to_s3_load_all(s3.bucket_name, s3.covid_folder_name, s3.response_covid) #깃허브의 모든 covid파일을 업로드 할 때
            print(f'luigi_업로드한 파일은 총 {total_cnt}개 입니다')
        else:
            print('실패, covid파일을 가져오지 못 했습니다.')


class DataLoad(luigi.Task):
    def requires(self):
        print('S3_Upload실행 완료')
        return S3_Upload()
    
    def run(self):
        print('DataLoad시작')
        #월별로 데이터를 가공 후 다른 폴더에 각각 저장
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
                .mode("overwrite")
                .save(output_folder_path) 
            )
            print(f'경로: {dl.output_local_file_path}{date_prefix} 결과 파일 저장 성공')




class DBInsertTask(luigi.Task):
    def requires(self):
            return DataLoad()

    def run(self):
        #DB에 인서트
        for date_prefix, url_list in dl.url_groups.items():
            table_name = f'COVID_19_{date_prefix}'  #테이블 이름 지정

            #오라클에 해당 테이블이 있는지 조건 검사
            if db.spark.catalog.tableExists(table_name): #만약 테이블이 이미 있다면
                print(f'luigi_이미 생성 되어 있는 테이블 입니다. 테이블명: {table_name}')
            else:
                #오라클에 자동으로 테이블 생성 및 인서트
                #데이터 가공
                df = dl.create_final_df(dl.input_s3_covid_path, url_list)
                count = df.count() #인서트될 데이터프레임 카운트

                #파티션 수 늘리기
                df.repartition(10) #셔플 사용, 파티션을 늘리거나 줄이거나 할 수 있음

                df.coalesce(1).write.jdbc(url = db.url, table = table_name, mode = 'overwrite', properties = db.properties)
                print(f'luigi_{table_name}테이블에 삽입된 data는 총{count}개 입니다.')


# if __name__ == '__main__':
#     luigi.run()

if __name__ == '__main__':
    tasks_to_run = [S3_Upload(), DataLoad(), DBInsertTask()]
    luigi.build(tasks_to_run, local_scheduler=True)
