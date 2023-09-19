import os
import requests
import pandas as pd

from datetime import datetime
from bs4 import BeautifulSoup
from itertools import product


#넘겨 받은 download_url_list를 각 월에 맞는 길이로 나눠서 데이터프레임을 생성 후 기존 데이터프레임에 추가하는 함수 ing...
def url_mapping(url_list_in):
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
        
        df = pd.read_csv(
                      f'{covid_paths}{csv_file}'
                    , header = True
                    , inferSchema = True
                )
    
    #url_list를 월 날짜 개수 별로 나눔
    for days in days_in_each_month:
        end_idx = start_idx + days
        result.append(url_list_in[start_idx:end_idx])
        start_idx = end_idx
    
        # 새로운 행을 생성
        df = df.append(new_row, ignore_index=True)
    
    new_df = df.union(pd.DataFrame([new_row]))
    new_df.tail(5)

#코로나 역학 보고서의 download url가 있는 페이지의 url을 생성하는 함수 매개변수 없음
def get_downlaod_url_list():

    #report_url 생성
    years = ['2020', '2021', '2022', '2023']
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november']
    days = [str(i) for i in range(1, 32)]

    # 모든 조합 생성
    combinations = product(years, months, days)

    result_list = []
    for year, month, day in combinations:
        url1 = f'https://www.who.int/publications/m/item/weekly-update-on-covid-19---{day}-{month}-{year}'
        # url2 = f'https://www.who.int/publications/m/item/weekly-epidemiological-update---{day}-{month}-{year}'

        downlaod_url_list = result_list.append(get_download_url(url1))
    
    return downlaod_url_list

#url을 넘겨 받아서 크롤링으로 코로나 역학 보고서의 download url을 얻어오는 함수
def get_download_url(url):

    # 내가 접속한 브라우저 정보를 알려줌, 로봇이 아닌 사람이 접근했다고 알리는 기능
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:  # 상태 코드가 200일 때만

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

#https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports
url_list = []
if __name__ == "__main__":
    url_list = get_downlaod_url_list()
    url_mapping(url_list)