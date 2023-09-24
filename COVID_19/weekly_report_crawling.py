from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

import time
import re
import pandas as pd


#download url을 전달 받아서 url에 있는 날짜를 추출하는 함수
#확인된 url 패턴
# https://www.who.int/docs/default-source/coronaviruse/situation-reports/20230601_weekly_epi_update_145.pdf?sfvrsn=33c590af_4&download=true
# https://cdn.who.int/media/docs/default-source/documents/emergencies/who_mou_august_2023.pdf?sfvrsn=852da432_1&download=true
# https://cdn.who.int/media/docs/default-source/documents/emergencies/who-mou-february-2023.pdf?sfvrsn=98ca2024_3&download=true
# https://www.who.int/docs/default-source/coronaviruse/covid-19-who-monthly-update-october-2022.pdf?sfvrsn=57f64f6b_1&download=true
# https://www.who.int/docs/default-source/coronaviruse/covid-19-who-monthly-update-october-2022.pdf?sfvrsn=57f64f6b_1&download=true
# https://www.who.int/docs/default-source/coronaviruse/situation-reports/who_mou_26may.pdf?sfvrsn=6bbf0599_1&download=true
# https://www.who.int/docs/default-source/coronaviruse/weekly-updates/wou_3nov_cleared.pdf?sfvrsn=19e7a718_3&download=true
#좀 더 효율적인 방법 생각해보기
def get_url_date(download_url):
    url_date = ''
    url_date_sort = ''

    catch_spilt = download_url.split('/')[-1]
    if catch_spilt.startswith('20'):
        try:  
            url_date = catch_spilt.split('_')[0]
            url_date_sort = datetime.strptime(url_date, '%Y%m%d')
            url_date_sort = url_date_sort.strftime('%Y/%m/%d')
            return url_date_sort, download_url
        except:
            print(f'.startswith("20")중에서 새로운 패턴입니다 확인해주세요 패턴: {catch_spilt}')
        
    
    # https://cdn.who.int/media/docs/default-source/documents/emergencies/who_mou_august_2023.pdf?sfvrsn=852da432_1&download=true
    # https://cdn.who.int/media/docs/default-source/documents/emergencies/who-mou-february-2023.pdf?sfvrsn=98ca2024_3&download=true
    elif catch_spilt.startswith('who'):
        date_pattern = r'(\w+)[_-](\w+)[_-](\d{4})'
        match = re.search(date_pattern, catch_spilt)
        if match:
            month = match.group(2)
            year = match.group(3)
            date_form = f'{year}/{month}'
            
            return date_form, download_url
        
        else:
            print(f"에러! 해당 패턴이 확인되지 않습니다! 패턴:{download_url}")
    # https://www.who.int/docs/default-source/coronaviruse/covid-19-who-monthly-update-october-2022.pdf?sfvrsn=57f64f6b_1&download=true
    elif catch_spilt.startswith('covid'):
        date_pattern = r'(\w+)-(\d{4})'
        match = re.search(date_pattern, catch_spilt)
        if match:
            month = match.group(1)
            year = match.group(2)
            date_form = f'{year}/{month}'
            
            return date_form, download_url
    # https://www.who.int/docs/default-source/coronaviruse/weekly-updates/wou_3nov_cleared.pdf?sfvrsn=19e7a718_3&download=true
    # elif:

    else:
        print(f'에러!! 해당 download_url을 다시 확인해주세요 url: {download_url}')


#COVID-19 역학 보고서 박스의 selector를 전달 받아서 COVID-19 역학 보고서의 download url을 추출하는 함수
def get_download_url(selector):
    
    download_btn = ''
    onclick = ''
    download_url = ''

    try:
        #넘겨 받은 셀렉터 클릭
        selector.click()

        #download_btn 찾기
        download_btn = driver.find_element(By.CSS_SELECTOR, '#PageContent_C001_Col00 > article > section > div > div.dynamic-content__figure-container > div > a')

        #download_btn에서 COVID_19 역학 보고서 다운 url 추출
        onclick = download_btn.get_attribute('onclick')
        download_url = onclick.split("'")[3]
        print(download_url)
    except:
        print(f'에러!!! {selector}를 다시 확인해주세요')
        time.sleep(5)
    
    driver.back()
    time.sleep(5) # 아직 페이지가 뜨지도 않았는데 바로 다음 명령어가 실행될 수도 있으니까, 2초 정도 여유를 준다.

    return download_url

#매개변수 없이 각 코로나 역학 보고서 박스에 있는 날짜에서 'yyyy/mm/dd'형태의 날짜를 리스트형태로 얻는 함수
# def get_span_date():
    elements = ''
        
    #class가 'sf-meeting-report-list__data'인 대상, 리스트 형태임
    elements = browser.find_elements(By.CLASS_NAME, 'sf-meeting-report-list__data')

    #class가 'sf-meeting-report-list__data'인 대상에서 <span>의 값을 가져옴
    #257개
    span_list = []
    for element in elements:
        span_element = ''
        span_text = ''

        #<span> 찾기
        span_element = element.find_element(By.TAG_NAME, 'span')

        #<span>의 값을 가져옴
        span_text = span_element.text

        #'17 August 2023'형태에서 날짜 추출
        date_val = datetime.strptime(span_text, '%d %B %Y')
        
        #'yyyy/mm/dd'형태로 전환
        date_sort = date_val.strftime('%Y/%m/%d')

        print(date_sort)
        #리스트 추가
        span_list.append(date_sort)



if __name__ == "__main__":
    # #크롬 드라이버 자동 업데이트
    # from webdriver_manager.chrome import ChromeDriverManager

    #옵션 설정
    options = webdriver.ChromeOptions()

    # 사람처럼 보이게 하는 옵션들
    options.add_argument('disable-gpu')   # 가속 사용 x
    options.add_argument('lang=ko_KR')    # 가짜 플러그인 탑재
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')  # user-agent 이름 설정

    chrome_options = Options()
    chrome_options.add_experimental_option('detach', True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    url = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports'

    # 웹 브라우저 띄우기
    driver = webdriver.Chrome(options=chrome_options)
    # driver.maximize_window() #화면 최대화
    driver.get(url)
    driver.implicitly_wait(5) #로딩이 끝날때까지 2초를 기다림

    result = ''
    download_url_catch = ''
    result_url_date = ''
    result_download_url = ''
    download_url_list = []
    url_date_list = []
    url_list = []
    element_list = []

    element_list = driver.find_elements(By.CSS_SELECTOR, '#PageContent_C006_Col01> .sf-meeting-report-list> .sf-meeting-report-list__item')
    for element in element_list:

        #download url 추출
        download_url_catch = get_download_url(element)
        download_url_list.append(download_url_catch)

        #download_url에서 날짜 추출
        result = get_url_date(download_url_catch)

        if result is not None:
        
            result_url_date, result_download_url = result
            url_date_list.append(result_url_date)
            url_list.append(result_download_url)
        else:
            print(f'에러!!!! url을 확인해주세요 전달한 url: {download_url_catch}, 결과url: {result}')
 
    #데이터프레임 생성, 저장
    data = {
          '날짜': url_date_list
        , 'report_url': url_list
    }

    df = pd.DataFrame(data)
    df.to_csv('ToyProj/COVID_19/output/COVID_weekly_report/report.csv', encoding = 'utf-8-sig', index = False)

driver.quit()
