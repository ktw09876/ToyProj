import asyncio
import aiohttp
from bs4 import BeautifulSoup
from itertools import product

# 내가 접속한 브라우저 정보를 알려줌, 로봇이 아닌 사람이 접근했다고 알리는 기능
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

async def url_status(session, url):
    try:
        async with session.get(url, headers=headers) as response:
            status_code = response.status
            if status_code == 200:  # 상태 코드가 200일 때만 출력
                # print(f"URL: {url}, Status Code: {status_code}")

                # #BeautifulSoup()로 웹페이지 분석
                soup = BeautifulSoup(response.text, 'html.parser')

                # # #COVID-19 역학 보고서 버튼 찾기
                download_btn = soup.select_one('#PageContent_C001_Col00 > article > section > div > div.dynamic-content__figure-container > div > a')
                print(download_btn)

                # #COVID-19 역학 보고서 버튼에서 보고서 다운 url 추출
                onclick_list = download_btn['onclick'].split("'")
                for onclick in onclick_list:
                    if onclick.startswith('https://'):
                        download_url = onclick
                        break

                print(download_url)

    except Exception as e:
        print(f"실패! URL: {url}, Exception: {e}, Status Code: {status_code}")

async def download_url():
    years = ['2020', '2021', '2022', '2023']
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    days = [str(i) for i in range(1, 32)]

    # 모든 조합 생성
    combinations = product(years, months, days)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for year, month, day in combinations:
            url1 = f'https://www.who.int/publications/m/item/weekly-update-on-covid-19---{day}-{month}-{year}'
            url2 = f'https://www.who.int/publications/m/item/weekly-epidemiological-update---{day}-{month}-{year}'
            task1 = url_status(session, url1)
            tasks.append(task1)
            task2 = url_status(session, url2)
            tasks.append(task2)
        
        await asyncio.gather(*tasks)  # 비동기 작업을 병렬로 실행

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_url())
