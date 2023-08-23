import unittest
from unittest.mock import Mock, patch
from s3_upload import check_file, upload_to_s3, from_git_to_s3_load_all


class TestS3Upload(unittest.TestCase):

    @patch('s3_upload.client.list_objects_v2')
    def test_check_file(self, mock_list_objects_v2):
        mock_list_objects_v2.return_value = {'Contents': [{'Key': 'test_file.csv'}]}
        result = check_file('test_bucket', 'test_folder', 'test_file.csv')
        self.assertTrue(result)

    @patch('s3_upload.client.put_object')
    def test_upload_to_s3(self, mock_put_object):
        upload_to_s3('test_bucket', 'test_path', 'test_content')
        mock_put_object.assert_called_once_with(Bucket='test_bucket', Key='test_path', Body='test_content')

    def test_from_git_to_s3_load_all(self):
        
        pass




if __name__ == '__main__':
    unittest.main()