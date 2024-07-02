import os
###현재 작업 디렉토리를 스크립트 위치로 변경
script_dir = os.path.dirname(__file__) #현재 스크립트의 절대 경로 중 폴더까지의 경로를 가져온다
os.chdir(script_dir) #해당 경로로 작업 경로를 변경한다
# print(f"script path: {os.getcwd()}") #변경된 경로 확인

import re
import time
import requests
import configparser as parser
import boto3
from botocore.config import Config
from io import BytesIO
from datetime import datetime

class MinioUpload():
    def __init__(self, base_url: str):

        ###minio 접속 정보
        self.ip, self.port, self.username, self.password, self.bucket_name = self.read_conf(os.path.join('..', 'setting', 'setting.ini'))

        # boto3 클라이언트 생성
        self.s3_client = boto3.client(
             's3'
            ,endpoint_url = f'http://{self.ip}:{self.port}'
            ,aws_access_key_id = self.username
            ,aws_secret_access_key = self.password
            ,config = Config(signature_version = 's3v4')
            ,region_name = 'us-east-1'  # MinIO에 맞는 아무 값이나 설정 가능
        )
        
        ###로그 경로
        self.res_log = os.path.join('..', 'logs')

        # 로그 디렉토리 생성
        if not os.path.exists(self.res_log):
            os.makedirs(self.res_log)

        self.base_url = base_url 
        self.covid_folder_name = 'csse_covid_19_daily_reports'
        self.upload_file_count = 0 #업로드된 전체 파일 수 초기화
    
    ###설정 파일(.ini) 를 읽어 MiniO 접속 정보를 반환
    def read_conf(self, conf_path: str) -> str:
        config = parser.ConfigParser()
        config.read(conf_path)

        ip = config['MiniO']['ip']
        port = config['MiniO']['port']
        username = config['MiniO']['access_key']
        password = config['MiniO']['secret_key']
        bucket_name = config['MiniO']['bucket_name']

        return ip, port, username, password, bucket_name
    
    ###.csv가 있는 GitHub 저장소의 폴더에 접근
    def git_repository_access(self, gra_base_url: str, gra_log_path: str) -> list:
        try:
            git_response = requests.get(gra_base_url) #api 호출
            if git_response.status_code in(200, 201): ###성공, 서버가 요청에 응답함
                git_response_json = git_response.json()

                return git_response_json

        ###GitHub 폴더에 접근 실패
        except Exception as e:
            print('You cannot access the GitHub repository')
            self.error_log_write(gra_log_path, f'You cannot access the GitHub repository: {e}')

    ###로그 파일 경로와 에러메세지를 전달 받아서 시간과 에러메세지를 저장
    def error_log_write(self, elw_log_path, elw_message):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # 시간 기록
        with open(os.path.join(elw_log_path, 'error_log.txt'), 'a') as error_logs:
            error_logs.write(f'{current_time} {elw_message}\n')

    ###파일을 MiniO에 업로드
    def upload_minio(self, um_client: boto3, um_file_name: str, um_data_stream: BytesIO, um_log_path: str) -> None:

        ### 성공, 파일을 MiniO에 업로드
        try: 
            um_client.put_object(
                 Bucket = self.bucket_name #버킷 이름
                ,Key = um_file_name #파일 이름
                ,Body = um_data_stream  #파일 내용을 포함하는 스트림
                ,ContentLength = um_data_stream.getbuffer().nbytes  # 스트림의 크기
                ,ContentType = 'application/csv' # MIME 유형
            )
            print(f'File upload successful!!! {um_file_name}')

        ###실패
        except Exception as e:
            print('error!!! Upload failed')
            self.error_log_write(um_log_path, f'error!!! Upload failed: {e}')

    ###GitHub 에서 .csv를 다운로드해서 MiniO에 업로드
    def git_to_minio(self, git_response_json, gtm_s3_client, gtm_log_path, gtm_ttl_count):

        ###.csv의 downlaod url 을 가지고 다시 api 호출, 각 daily report 를 다운
        for key in git_response_json:
            try:
                if re.compile(r'\d{2}-\d{2}-\d{4}\.csv$').match(key['name']): #json 데이터 중에 key가 'name'인 값이 날짜형식이면서 .csv로 끝나는 대상
                    download_url = key['download_url']                        #download url 추출
                    file_name = key['name']
                    
                    csv_response = requests.get(download_url)                 #해당 .csv를 download
                    if csv_response.status_code in(200, 201):                 #성공, 서버가 요청에 응답함

                        ###MiniO에 업로드
                        self.upload_minio(gtm_s3_client, file_name, BytesIO(csv_response.content), gtm_log_path)
                        gtm_ttl_count += 1                                    #total count 1 증가
                    time.sleep(1)                                             #업로드 주기 조절

            except Exception as e:
                print(f'The .csv cannot be downloaded file name: {file_name}')
                self.error_log_write(gtm_log_path, f'The .csv cannot be downloaded file name: {file_name} {e}')
            
        print(f'total uploaded count: {gtm_ttl_count}')


def main():
    cli = MinioUpload('https://api.github.com/repos/CSSEGISandData/COVID-19/contents/csse_covid_19_data/csse_covid_19_daily_reports') #daily_report.csv가 있는 깃허브 api 경로

    ###GitHub 폴더에 접근
    data_json = cli.git_repository_access(cli.base_url, cli.res_log)

    ###GitHub의 .csv를 MiniO에 업로드
    cli.git_to_minio(data_json, cli.s3_client, cli.res_log, cli.upload_file_count)


#https://www.arcgis.com/apps/dashboards/bda7594740fd40299423467b48e9ecf6 세계 코로나 현황 대시보드
# 오른쪽 상단 메뉴 --> raw data --> 존스 홉킨스 대학교 시스템 과학 및 엔지니어링 센터(CSSE)깃허브 주소
# 존스 홉킨스 대학교 시스템 과학 및 엔지니어링 센터(CSSE)깃허브 주소 https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/
if __name__ == '__main__':
    main()
