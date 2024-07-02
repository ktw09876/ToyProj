import os
###현재 작업 디렉토리를 스크립트 위치로 변경
script_dir = os.path.dirname(__file__) #현재 스크립트의 절대 경로 중 폴더까지의 경로를 가져온다
os.chdir(script_dir) #해당 경로로 작업 경로를 변경한다
# print(f'script path: {os.getcwd()}') #변경된 경로 확인
import s3_upload as ul
import data_load as dl

import configparser as parser

class DbInser():
    def __init__(self, dl) -> None:

        ###postgres 접속 정보
        self.host, self.port, self.dbname, self.username, self.password = self.read_conf(os.path.join('..', 'setting', 'setting.ini'))
        self.jdbc_url = f'jdbc:postgresql://{self.host}:{self.port}/{self.dbname}'
        self.db_properties = {
            'user': f'{self.username}',
            'password': f'{self.password}',
            'driver': 'org.postgresql.Driver'
        }

        ###데이터프레임의 경로 중에서 년도를 리스트형태로 가져온다
        self.years = os.listdir(dl.output)

    ###설정 파일(.ini) 를 읽어 postgreSQL 접속 정보를 반환
    def read_conf(self, conf_path: str) -> str:
        config = parser.ConfigParser()
        config.read(conf_path)

        host = config['PostgreSQL']['host']
        port = config['PostgreSQL']['port']
        dbname = config['PostgreSQL']['dbname']
        username = config['PostgreSQL']['username']
        password = config['PostgreSQL']['password']

        return host, port, dbname, username, password
    

def main():
    ul_cli = ul.MinioUpload('https://api.github.com/repos/CSSEGISandData/COVID-19/contents/csse_covid_19_data/csse_covid_19_daily_reports')
    dl_cli = dl.DataLoad(ul_cli)
    in_cli = DbInser(dl_cli)

    ### 데이터프레임을 읽어옴
    for year in in_cli.years:
        file_list = os.path.join(dl_cli.output, year)

        for file in os.listdir(file_list):
            if file.endswith('.csv'):

                final_df = dl_cli.spark.read.csv(
                     os.path.join(dl_cli.output, year)
                    ,header = True
                    ,inferSchema = True #스키마(데이터타입)를 자동으로 추론한다 False 의 경우 모든 데이터를 문자열(String)로 읽어온다
                )
                final_df.show(10) #결과 확인

                final_df.write.jdbc(
                     properties = in_cli.db_properties
                    ,url = in_cli.jdbc_url
                    ,table = f'test1.covid_{year}'
                    ,mode = 'overwrite'
                )

    dl_cli.spark.stop()

if __name__ == '__main__':
    main()