import unittest
from moto import mock_s3
import boto3
import s3_upload as ul

#구현중
class TestS3Upload(unittest.TestCase):

    @mock_s3
    def test_check_file_exists(self):
        
        s3 = boto3.client('s3', region_name=ul.region_name)
        s3.create_bucket(Bucket='test_bucket')
        s3.upload_file(Filename='test_file', Bucket='test_bucket', Key='test_path/test_file')

        result = ul.check_file('test_bucket', 'test_path', 'test_file')
        self.assertTrue(result)

    @mock_s3
    def test_check_file_not_exists(self):
        
        s3 = boto3.client('s3', region_name=ul.region_name)
        s3.create_bucket(Bucket='test_bucket')

        result = ul.check_file('test_bucket', 'test_path', 'test_file')
        self.assertFalse(result)

    @mock_s3
    def test_upload_to_s3(self):
        
        s3 = boto3.client('s3', region_name=ul.region_name)
        s3.create_bucket(Bucket='test_bucket')

        ul.upload_to_s3('test_bucket', 'test_path', b'Test content')

        
        objects = s3.list_objects_v2(Bucket='test_bucket', Prefix='test_path')
        self.assertEqual(len(objects.get('Contents', [])), 1)

if __name__ == '__main__':
    unittest.main(exit=False)