import requests
from bs4 import BeautifulSoup

url = "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # 날짜별 보고서 링크를 담고 있는 요소를 찾습니다.
    report_links = soup.find_all("a", {"class": "link-container"})

    # 각 보고서의 링크와 제목을 출력합니다.
    for link in report_links:
        report_url = link.get("href")
        report_title = link.text.strip()
        print(report_title, ": ", report_url)
else:
    print("웹 페이지를 가져올 수 없습니다.")
