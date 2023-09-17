from pyspark.sql import SparkSession

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


def download_url(url):
    response = requests.get(url)
    if response.status_code == 200:  # 상태 코드가 200일 때만
        # print(f"URL: {url}, Status Code: {status_code}")

        # #BeautifulSoup()로 웹페이지 분석
        soup = BeautifulSoup(response.text, 'html.parser')

        # # #COVID-19 역학 보고서 버튼 찾기
        download_btn = soup.select_one('#PageContent_C001_Col00 > article > section > div > div.dynamic-content__figure-container > div > a')

        # #COVID-19 역학 보고서 버튼에서 보고서 다운 url 추출
        onclick_list = download_btn['onclick'].split("'")
        download_url = ''

        for onclick in onclick_list:
            if onclick.startswith('https://'):
                download_url = onclick

            # print(download_url)
            return download_url


def get_download_url():
    #report_url 생성
    years = ['2020', '2021', '2022', '2023']
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    days = [str(i) for i in range(1, 32)]

    # 모든 조합 생성
    combinations = product(years, months, days)

    for year, month, day in combinations:
        url1 = f'https://www.who.int/publications/m/item/weekly-update-on-covid-19---{day}-{month}-{year}'
        # url2 = f'https://www.who.int/publications/m/item/weekly-epidemiological-update---{day}-{month}-{year}'

        url = download_url(url1)
        # url_status(url2)

        # URL에서 날짜 정보 추출
        date_str = url1.split('---')[-1]
        date = datetime.strptime(date_str, '%d-%B-%Y').strftime('%Y/%m/%d')

        return url, date
    
if __name__ == "__main__":

    # #불러올 .csv 경로
    # int_months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    # csv_file = ''
    # for int_month in int_months:
    #     try:
    #         covid_paths = f'output/{int_month}/'
    #         covid_files = os.listdir(covid_paths)
    #         for file_name in covid_files:
    #             if file_name.endswith('.csv'):
    #                 csv_file = file_name
    #                 print(csv_file)
    #     except:
    #         print(f'해당 경로를 찾을 수 없습니다 경로:{covid_paths}')

    #     df = spark.read.csv(
    #               f'{covid_paths}{csv_file}'
    #             , header = True
    #             , inferSchema = True
    #         )

    df = spark.read.csv(
                  'output/01/part-00000-19221339-8484-434b-9a77-05282cda94e5-c000.csv'
                , header = True
                , inferSchema = True
            )
    download_url, date = get_download_url()

    #데이터프레임의 컬럼 날짜와 동일한 url의 날짜의 download_url을 추가 ing...
    for col in df.columns:
        if col == date:
            

    

    # combinations = product(years_in, months_is, days_is)

    # for year, month, day in combinations:
    #     url1 = f'https://www.who.int/publications/m/item/weekly-update-on-covid-19---{day}-{month}-{year}'




spark.stop()