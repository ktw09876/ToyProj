# ETL, 파이프라인
2022.01.01 ~ 2022.11.13(316일) 나라별 COVID-19 확진자 분석
<img width="1000" src="https://github.com/ktw09876/ToyProj/assets/93371320/2696e54b-c445-4ebd-92ad-16e80e8decc3.png"/>

- 원본 데이터
<img width="1000" src="https://github.com/ktw09876/ToyProj/assets/93371320/f55458fb-6724-4aac-a886-4e5814719171"/>

- 가공 후 데이터
<img width="1000" src="https://github.com/ktw09876/ToyProj/assets/93371320/1bb0cb1f-736b-4ef4-8516-d1f64225a7db"/>

- weekly_report
<img width="1000" src="https://github.com/ktw09876/ToyProj/assets/93371320/7c38e3b6-4535-4b1c-aa26-5607a1e576ee"/>

1. 깃허브 api를 호출해서 .csv 데이터를 aws S3에 업로드합니다.
2. S3 데이터를 Spark를 이용해서 불러와서 가공합니다.
3. 가공이 끝난 데이터는 Oracle DB에 저장됩니다.
4. Luigi를 이용해서 워크플로를 관리합니다.

- Java: 11
- Spark: 3.4.1
- Hadoop: 3.2.4
- Python: 3.8.17
- Luigi: 3.3.0
- Oracle: 21c

## 어려웠던 점
1. 많은 양의 데이터프레임을 조인해서 하나로 만드는 과정에서 메모리 부족 문제가 생김
2. 월별로 총 12개의 데이터프레임을 만드는 것으로 해결
3. 조인 방식이나 메모리관리 방법을 좀 더 개선해보고 싶다
4. 초기 airflow를 도입하려 했으나 메모리 문제로 포기
    - wsl 우분투 + 도커 환경에 airflow를 실행해보니 전체 메모리의 약 90%를 차지
    - 이후 vscode의 연결이 끊기는 문제 발생
    - '.cfg'파일을 설정하거나 aws 세일즈를 고려하다가 비슷한 기능을 하는 luigi 도입

## 개선 및 추가해보고싶은 사항
1. 좀 더 많은 데이터를 다루는 경우 처리 방식 개선(스택오버플로우, 메모리 부족 ...)
2. 데이터를 직접 생성해볼 수 있을까?
3. 매일 자정에 실행 or 데이터 목록을 모니터링, 변화가 있으면 실행, 에러가 있다면 메세지와 함께 개인 이메일로 확인
