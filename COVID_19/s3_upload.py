import requests
import boto3
######################################## 깃허브에서 s3로 업로드 #######################################################


AWS_ACCESS_KEY_ID  = 'AKIA6JQPP6QSR3INWGVJ' #액세스 키 ID
AWS_SECRET_ACCESS_KEY = 'wppNOtXjI+2mGfBjKcEoEGcSWU49dWCk8vRhV4Bb' #시크릿 액세스 키
AWS_REGION = 'ap-northeast-2' #버킷의 리전 코드(아시아 태평양(서울))

base_url_covid = 'https://api.github.com/repos/CSSEGISandData/COVID-19/contents/csse_covid_19_data/csse_covid_19_daily_reports' #daily_report.csv가 있는 깃허브 경로
base_url_iso = 'https://api.github.com/repos/CSSEGISandData/COVID-19/contents/csse_covid_19_data' #국가정보가 있는 깃허브 경로
bucket_name = 'ktw09876' #버킷 이름
covid_folder_name = 'csse_covid_19_daily_reports' #버킷 내 coivd_폴더 이름
iso_folder_name = 'csse_covid_19_daily_reports/iso' #버킷 내 국가정보_폴더 이름

#base_url로 get요청을 보내고 그에 해당하는 응답을 반환함
response_covid = requests.get(base_url_covid) 
response_iso = requests.get(base_url_iso) 

#S3클라이언트를 생성
client = boto3.client( 
    's3' #Amazon S3(Simple Storage Service)에 접근하겠다, 
    , aws_access_key_id = AWS_ACCESS_KEY_ID #액세스 키 ID
    , aws_secret_access_key = AWS_SECRET_ACCESS_KEY #시크릿 액세스 키
    , region_name = AWS_REGION #버킷의 리전 코드(아시아 태평양(서울))
)

#S3의 파일과 깃허브의 파일을 비교하는 함수
def check_file(bucket, folder, file):
    response = client.list_objects_v2(
        Bucket = bucket,
        Prefix = f'{folder}/{file}'  
    )
    return 'Contents' in response #response에 'Contents'가 있냐 없냐에 따라 true, false를 반환

#S3에 파일을 업로드하는 함수
def upload_to_s3(bucket_name, path, csv_content):
    client.put_object(
              Bucket = bucket_name #버킷 이름
            , Key = path #업로드할 파일의 경로
            , Body = csv_content
        )

#깃허브에 있는 모든 .csv파일을 가져오는 함수
def from_git_to_s3_load_all(bucket_name, folder, response):
    files = response.json()
    uploaded_file_count = 0

    for file_info in files:
        if file_info['name'].endswith('Table.csv'): #만약 'name'의 값이 '.csv'로 끝난다면
            url = file_info['download_url'] #download_url의 값을 url 변수에 할당한다
            response = requests.get(url) #그렇게 얻은 url을 서버에 요청

            if response.status_code == 200: #응답된 코드가 200이면
                csv_content = response.content #.text보다 .content를 사용하는 게 인코딩 문제 방지에 좋다
                file_name = url.split('/')[-1] #깃허브에서 가져올 파일 이름
                iso_path = f'{folder}/{file_name}' #S3에 업로드할 경로

                #여기도 이미 있는 파일인지 확인 필요
                if check_file(bucket_name, folder, file_name):
                    print(f'이미 있는 파일 입니다 경로: {bucket_name}/{folder}/, 파일명: {file_name}')
                else:
                    upload_to_s3(bucket_name, iso_path, csv_content)
                    print(f'Uploaded: {file_name} to s3://{bucket_name}/{iso_path}')
                    uploaded_file_count += 1
            else:
                print(f'Failed to fetch data from {url}. Status code: {response.status_code}')

        #원하는 년도 데이터 업로드
        # elif file_info['name'].endswith('.csv'): #만약 'name'의 값이 'csv'로 끝난다면
        elif file_info['name'].endswith('2022.csv'): #만약 'name'의 값이 'csv'로 끝난다면
            url = file_info['download_url'] #download_url의 값을 url 변수에 할당한다
            response = requests.get(url)
            if response.status_code == 200: #응답된 코드가 200이면
                csv_content = response.content
                file_name = url.split('/')[-1] #깃허브에서 가져올 파일 이름
                covid_path = f'{folder}/{file_name}' #S3에 업로드할 경로

                #S3 경로에 같은 이름의 파일이 있는 지 확인
                if check_file(bucket_name, folder, file_name):
                    print(f'이미 있는 파일 입니다 경로: {bucket_name}/{folder}/, 파일명: {file_name}')
                else:
                    upload_to_s3(bucket_name, covid_path, csv_content)
                    print(f'업로드: s3://{bucket_name}/{covid_path}')
                    uploaded_file_count += 1
            else:
                print(f'데이터를 가져오지 못 했습니다. 경로: {url}. Status code: {response.status_code}')

    return uploaded_file_count



#깃허브 주소 https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/
#해당 파일이 메인프로그램인지 모듈(import 되어 사용되는)인지 구분하기 위한 코드
#if __name__  =  =  '__main__': 이하 코드는 현재 스크립트가 다른 곳에서 import되어 사용될 경우 실행하지 않을 코드임
if __name__ == '__main__': 
    
    # 깃허브에 있는 iso파일을 aws S3에 저장
    #더 빠르게 하는 방법 없나?
    if response_iso.status_code == 200: #성공, 서버가 요청에 응답함
        total_cnt = from_git_to_s3_load_all(bucket_name, iso_folder_name, response_iso) #깃허브의 isd파일을 업로드 할 때
        print(f'업로드한 파일은 총 {total_cnt}개 입니다')
    else:
        print('실패, isd파일을 가져오지 못 했습니다.')

    # 깃허브에 있는 covid파일을 aws S3에 저장
    if response_covid.status_code == 200: #성공, 서버가 요청에 응답함
        total_cnt = from_git_to_s3_load_all(bucket_name, covid_folder_name, response_covid) #깃허브의 모든 covid파일을 업로드 할 때
        print(f'업로드한 파일은 총 {total_cnt}개 입니다')
    else:
        print('실패, covid파일을 가져오지 못 했습니다.')

