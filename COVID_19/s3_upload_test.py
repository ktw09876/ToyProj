import unittest as uni
import s3_upload as ul


# TestCase를 작성
class CustomTests(uni.TestCase): 

    def test_from_git_to_s3_load_all(self):
        

        ul.from_git_to_s3_load_all()


# unittest를 실행
if __name__ == '__main__':  
    uni.main()