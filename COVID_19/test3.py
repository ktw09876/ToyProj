from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# #크롬 드라이버 자동 업데이트
# from webdriver_manager.chrome import ChromeDriverManager

#옵션 설정
options = webdriver.ChromeOptions()

# headless 옵션 설정
options.add_argument('headless')
options.add_argument("no-sandbox")

# 브라우저 윈도우 사이즈
options.add_argument('window-size=1920x1080')

# 사람처럼 보이게 하는 옵션들
options.add_argument("disable-gpu")   # 가속 사용 x
options.add_argument("lang=ko_KR")    # 가짜 플러그인 탑재
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')  # user-agent 이름 설정

#브라우저 꺼짐 방지
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

#불필요한 에러메시지 없애기
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

#웹 브라우저 띄우기
browser = webdriver.Chrome(options = chrome_options)

browser.maximize_window() #화면 최대화
browser.get('https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports')
browser.implicitly_wait(2) #로딩이 끝날때까지 10를 기다림

#쇼핑 매뉴 클릭
browser.find_element(By.CSS_SELECTOR, '#PageContent_C006_Col01 > div:nth-child(4) > a').click()
# time.sleep(5) # 쇼핑 배너를 클릭한 뒤, 아직 페이지가 뜨지도 않았는데 바로 다음 명령어가 실행될 수도 있으니까, 2초 정도 여유를 준다.

# #검색창 클릭 
# search = browser.find_element(By.CSS_SELECTOR, 
#     '#__next > div > div.pcHeader_header__tXOY4 > div > div > div._gnb_header_area_150KE > div > div._gnbLogo_gnb_logo_3eIAf > div > div._gnbSearch_gnb_search_3O1L2 > form > div._gnbSearch_inner_2Zksb > div > input'
#                               ).click() #적용 안됨 원인 찾아보기


# # #검색어 입력
# search.send_keys('아이폰 13')
# search.send_keys(Keys.ENTER)
