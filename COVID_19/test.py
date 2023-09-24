from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


chrome_options = Options()
chrome_options.add_experimental_option('detach', True)
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

url = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports'

driver = webdriver.Chrome(options=chrome_options)


driver.get(url)


wait = WebDriverWait(driver, 10)

parent_element = driver.find_elements(By.CSS_SELECTOR, '#PageContent_C006_Col01> .sf-meeting-report-list> .sf-meeting-report-list__item')

for element in parent_element:
    element.click()

    #download_btn 찾기
    download_btn = driver.find_element(By.CSS_SELECTOR, '#PageContent_C001_Col00 > article > section > div > div.dynamic-content__figure-container > div > a')

    #download_btn에서 COVID_19 역학 보고서 다운 url 추출
    onclick = download_btn.get_attribute('onclick')
    download_url = onclick.split("'")[3]
    print(download_url)

    
    driver.back()

driver.quit()
