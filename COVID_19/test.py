import requests
from bs4 import BeautifulSoup
from itertools import product

#내가 접속한 브라우저 정보를 알려줌, 로봇이 아닌 사람이 접근했다고 알리는 기능
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

years = ['2020', '2021', '2022', '2023']
months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
days = [str(i) for i in range(1, 32)]

# 모든 조합 생성
combinations = product(years, months, days)

# 조합을 이용하여 URL 생성 및 출력
for year, month, day in combinations:
    url = f'https://www.who.int/publications/m/item/weekly-update-on-covid-19---{day}-{month}-{year}'
    
    # #print(html.status_code)했을때 200 이 나와야 정상적으로 요청이 처리됨
    response = requests.get(url, headers=headers)
    print(response.status_code)




#https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports
# years = ['2020', '2021', '2022', '2023']
# months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
# days = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
# for i in years:
#     for j in months:
#         for k in days:

#             #COVID-19 역학 보고서 url
#             url = f'https://www.who.int/publications/m/item/weekly-update-on-covid-19---{k}-{j}-{i}'
#             print(url)

            # #print(html.status_code)했을때 200 이 나와야 정상적으로 요청이 처리됨
            # response = requests.get(url, headers=headers)

            # # #BeautifulSoup()로 웹페이지 분석
            # soup = BeautifulSoup(response.text, 'html.parser')

            # # #COVID-19 역학 보고서 버튼 찾기
            # download_btn = soup.select_one('#PageContent_C001_Col00 > article > section > div > div.dynamic-content__figure-container > div > a')
            # # print(download_btn)
            # # #COVID-19 역학 보고서 버튼에서 보고서 다운 url 추출
            # onclick_list = download_btn['onclick'].split("'")
            # for onclick in onclick_list:
            #     if onclick.startswith('https://'):
            #         download_url = onclick
            #         break

            # print(download_url)

