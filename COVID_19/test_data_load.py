import unittest
from pyspark.sql import SparkSession
from unittest.mock import patch, Mock

import s3_upload as ul
import data_load as dl

#구현중
class TestDataload(unittest.TestCase):

    #클래스의 테스트 함수를 실행하기 전에 한 번만 호출
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName('Test').getOrCreate()

    #json 데이터프레임 생성
    def create_mock_json_data(self):
        
        data = [
            ('Country1', 'json_Country1'),
            ('Country2', 'json_Country2'),
            ('Country3', 'json_Country3')
        ]
        columns = ['Converted_Country', 'json_Country_Region']
        return self.spark.createDataFrame(data, columns)

    #데이터프레임 생성
    def create_mock_dataframe(self):
        
        data = [
            ('Country1', 10, 15, 20),
            ('Country2', 5, 8, 12),
            ('Country3', 15, 28, 32)
        ]
        columns = ['Country_Region', '08/27/2023', '08/28/2023', '08/29/2023']
        return self.spark.createDataFrame(data, columns)

    #데이터프레임을 전달 받아서 컬럼명을 날짜형태로 수정하는 함수
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

    #각각의 .csv파일의 컬럼명'Country/Region'를 'Country_Region'로 수정, 'Confirmed'에 값이 없는 행 삭제
    def test_create_daily_report_df(self):
        
        mock_spark = Mock()
        mock_spark.read.option.return_value.csv.return_value = Mock()

        data = [
            ('Country1', 10, 15, 20),
            ('Country2', None, 8, 12),
            ('Country3', 15, None, 32)
        ]
        columns = ['Country_Region', 'Confirmed', '08/28/2023', '08/29/2023']
        mock_df = self.spark.createDataFrame(data, columns)

        mock_spark.createDataFrame.return_value = mock_df

        with patch('data_load.create_daily_report_df', return_value=mock_df) as mock_create_daily_report:
            result_df = dl.create_daily_report_df(mock_spark, 'path', 'filename')
            result_df.show(5)
            
            expected_data = [
                ('Country1', 10),
                ('Country2', 8),
                ('Country3', 15)
            ]
            expected_columns = ['Country_Region', 'Confirmed']
            expected_df = self.spark.createDataFrame(expected_data, expected_columns)
            expected_df.show(5)
            self.assertEqual(result_df.collect(), expected_df.collect())


    # def test_create_final_df(self):
    #     
    #     mock_s3_path = 's3_path'
    #     mock_file_paths = ['file1.csv', 'file2.csv']

    #     result_df = dl.create_final_df(mock_s3_path, mock_file_paths)
  
    #     expected_data = [
    #         ('Country1', 10, 15, 20),
    #         ('Country2', 5, 8, 12),
    #         ('Country3', 15, 28, 32)
    #     ]
    #     expected_columns = ['Country_Region', '08/27/2023', '08/28/2023', '08/29/2023']
    #     expected_df = self.spark.createDataFrame(expected_data, expected_columns)

    #     self.assertEqual(result_df.collect(), expected_df.collect())
    

        

if __name__ == '__main__':
    unittest.main(exit=False)
