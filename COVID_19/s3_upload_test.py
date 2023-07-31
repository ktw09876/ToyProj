import boto3

AWS_ACCESS_KEY_ID ="AKIA6JQPP6QSRQHKVNH5" #액세스 키 ID
AWS_SECRET_ACCESS_KEY = "oxUkXTmiDSX34sns+sGRg/ZZ1q1FSWV/Fg/UV7Wj" #시크릿 액세스 키
AWS_DEFAULT_REGION = "ap-northeast-2" #버킷의 리전 코드(아시아 태평양(서울))
client = boto3.client(
    's3'
    , aws_access_key_id=AWS_ACCESS_KEY_ID
    , aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    , region_name=AWS_DEFAULT_REGION
)

file_name = 'test.txt' # 업로드할 파일 이름 
bucket = 'ktw09876' #버켓 이름
key = 'test.txt' #버킷에 저장될 파일 이름

client.upload_file(file_name, bucket, key) #파일 업로드