from pyspark.sql import SparkSession
from pyspark.sql import Row

import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from itertools import product


#SparkSession 생성
spark = SparkSession.builder.appName("Read_CSV").getOrCreate()

# 내가 접속한 브라우저 정보를 알려줌, 로봇이 아닌 사람이 접근했다고 알리는 기능
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}


def url_mapping(url_list):
    #불러올 .csv 경로
    int_months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11']
    csv_file = ''
    days_in_each_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30]
    result = []
    start_idx = 0

    for int_month in int_months:
        covid_paths = f'COVID_19/output/{int_month}/'
        covid_files = os.listdir(covid_paths)
        for file_name in covid_files:
            if file_name.endswith('.csv'):
                csv_file = file_name
        
        df = spark.read.csv(
                    f'{covid_paths}{csv_file}'
                    , header = True
                    , inferSchema = True
                )
    
    #url_list를 월 날짜 개수 별로 나눔
    for days in days_in_each_month:
        end_idx = start_idx + days
        result.append(url_list[start_idx:end_idx])
        start_idx = end_idx
    
        # 새로운 행을 생성
        values = ['report_down'] + result # 'report_down'은 첫번째 컬럼, 나머지는 result
        new_row = Row(*values)
    
    new_df = df.union(spark.createDataFrame([new_row]))
    new_df.tail(5)



def download_url(url):
    response = requests.get(url)
    if response.status_code == 200:  # 상태 코드가 200일 때만
        # print(f"URL: {url}, Status Code: {status_code}")

        # #BeautifulSoup()로 웹페이지 분석
        soup = BeautifulSoup(response.text, 'html.parser')

        #COVID-19 역학 보고서 버튼 찾기
        download_btn = soup.select_one('#PageContent_C001_Col00 > article > section > div > div.dynamic-content__figure-container > div > a')

        # #COVID-19 역학 보고서 버튼에서 보고서 다운 url 추출
        onclick_list = download_btn['onclick'].split("'")
        download_url = ''

        for download_url in onclick_list:
            if download_url.startswith('https://'):
                return download_url
    else:
        return ''

def get_download_url():
    #report_url 생성
    years = ['2020', '2021', '2022', '2023']
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november']
    days = [str(i) for i in range(1, 32)]

    # 모든 조합 생성
    combinations = product(years, months, days)
    date_list = []
    url_list = []
#https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports
    for year, month, day in combinations:
        url1 = f'https://www.who.int/publications/m/item/weekly-update-on-covid-19---{day}-{month}-{year}'
        # url2 = f'https://www.who.int/publications/m/item/weekly-epidemiological-update---{day}-{month}-{year}'

        url_list.append(download_url(url1))

        # url_status(url2)

        # URL에서 날짜 정보 추출
        # date_str = url1.split('---')[-1]

        #date_str의 첫번째 스펠링을 대문자로
        # date_str = date_str.capitalize()
        # try:
        #     date = datetime.strptime(date_str, '%d-%B-%Y').strftime('%Y/%m/%d')
        #     date_list.append(date)
        # except:
        #     print('error 날짜 범위르 벗어났습니다')

        return url_list
    
if __name__ == "__main__":

    download_url_list = get_download_url()
    url_mapping(download_url_list)

    #데이터프레임의 컬럼 날짜와 동일한 url의 날짜의 download_url을 추가 ing...
    # for col in df.columns:
    #     if col == date:
            

    

    # combinations = product(years_in, months_is, days_is)

    # for year, month, day in combinations:
    #     url1 = f'https://www.who.int/publications/m/item/weekly-update-on-covid-19---{day}-{month}-{year}'




spark.stop()