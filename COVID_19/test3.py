from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import time

# #크롬 드라이버 자동 업데이트
# from webdriver_manager.chrome import ChromeDriverManager

#옵션 설정
options = webdriver.ChromeOptions()

# headless 옵션 설정
options.add_argument('headless')
options.add_argument('no-sandbox')

# 사람처럼 보이게 하는 옵션들
options.add_argument('disable-gpu')   # 가속 사용 x
options.add_argument('lang=ko_KR')    # 가짜 플러그인 탑재
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')  # user-agent 이름 설정

#브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option('detach', True)

#불필요한 에러메시지 없애기
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

url = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports'

#웹 브라우저 띄우기
browser = webdriver.Chrome(options = chrome_options)

browser.maximize_window() #화면 최대화
browser.get(url)
browser.implicitly_wait(2) #로딩이 끝날때까지 2초를 기다림

def get_download_url(selector):
    try:

        #COVID-19 역학 보고서 버튼 찾기
        browser.find_element(By.CSS_SELECTOR, selector).click()
    except:
        print(f'에러!!! {selector}를 다시 확인해주세요')
        time.sleep(2) # 아직 페이지가 뜨지도 않았는데 바로 다음 명령어가 실행될 수도 있으니까, 2초 정도 여유를 준다.

    try:
        #download_btn 찾기
        download_btn = browser.find_element(By.CSS_SELECTOR, '#PageContent_C001_Col00 > article > section > div > div.dynamic-content__figure-container > div > a')

        #download_btn에서 COVID_19 역학 보고서 다운 url 추출
        onclick = download_btn.get_attribute('onclick')
        download_url = onclick.split("'")[3]
        print(download_url)
    except:
        print(f'에러! {selector}를 다시 확인해주세요')
        time.sleep(2) 
    
    
#PageContent_C006_Col01 > div:nth-child(6) > a:nth-child(1)
#PageContent_C006_Col01 > div:nth-child(6) > a:nth-child(1)

for i in range(6, 80):
    for j in range(1, 11):
        selector = f'#PageContent_C006_Col01 > div:nth-child({i}) > a:nth-child({j})'
        get_download_url(selector)




