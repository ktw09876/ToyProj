import unittest
from pyspark.sql import SparkSession
from unittest.mock import Mock

import data_load as dl


class TestDataload(unittest.TestCase):

    #클래스의 테스트 함수를 실행하기 전에 한 번만 호출
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName('Test').getOrCreate()

    def test_rename_columns(self):
        #테스트용 데이터프레임 생성
        data = [
              ('Country1', 10, 15, 20)
            , ('Country2', 5, 8, 12)
            , ('Country3', 15, 28, 32)
        ]
        columns = ['Country_Region', '08/27/2023', '08/28/2023', '08/29/2023']
        df = self.spark.createDataFrame(data, columns)

        #data_load.py의 rename_columns() 호출, 테스트용 데이터프레임 전달
        renamed_df = dl.rename_columns(df)

        #renamed_df의 컬럼과 예상 데이터프레임의 컬럼을 비교
        result_columns = ['Country_Region', '2023/08/27', '2023/08/28', '2023/08/29']
        self.assertEqual(renamed_df.columns, result_columns)

class S3Client:
    def download_file(self):
        return "Mocked data"

class MyDataService:
    def __init__(self, s3_client):
        self.s3_client = s3_client

    def process_data(self):
        data = self.s3_client.download_file("my_bucket", "data.csv")
        

class TestMyDataService(unittest.TestCase):

    def test_process_data_with_mock(self):
        
        mock_s3_client = Mock(spec=S3Client)

        
        mock_s3_client.download_file.return_value = "Mocked data"

        
        my_data_service = MyDataService(s3_client=mock_s3_client)

        
        my_data_service.process_data()

        
        mock_s3_client.download_file.assert_called_once_with("my_bucket", "data.csv")

        

if __name__ == '__main__':
    unittest.main(exit=False)
