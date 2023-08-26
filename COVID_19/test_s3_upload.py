import unittest
from unittest.mock import Mock, patch

import s3_upload as ul


class TestS3Upload(unittest.TestCase):

    @patch('s3_upload.requests.get')
    @patch('s3_upload.boto3.client')
    def test_upload_to_s3(self, mock_boto_client, mock_requests_get):
        
        mock_response = Mock() #테스트 객체 생성

        mock_response.status_code = 200 #서버 응답 200 설정
        mock_response.content = b'Test content' #csv_content = response.content
        mock_requests_get.return_value = mock_response #HTTP 요청
       
        mock_s3_client = mock_boto_client.return_value
        mock_s3_client.list_objects_v2.return_value = {
                'Contents': []
            }

        
        ul.upload_to_s3('test_bucket', 'test_path', b'Test content')
        
        mock_s3_client.put_object.assert_called_with(Bucket = 'test_bucket', Key = 'test_path', Body = b'Test content')

    def test_check_file_exists(self):
        mock_s3_client = Mock()
        mock_s3_client.list_objects_v2.return_value = {
                'Contents': [{
                        'Key': 'test_path/test_file'
                    }]
            }

        result = ul.check_file(mock_s3_client, 'test_path', 'test_file')

        self.assertTrue(result)

    def test_check_file_not_exists(self):
        mock_s3_client = Mock()
        mock_s3_client.list_objects_v2.return_value = {
                'Contents': []
            }

        result = ul.check_file(mock_s3_client, 'test_path', 'test_file')

        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main(exit = False)