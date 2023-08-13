import pendulum
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

# timezone 한국시간으로 변경
kst = pendulum.timezone("Asia/Seoul")

# 기본 args 생성
default_args = {
    'owner' : 'Hello World',
    'email' : ['airflow@airflow.com'],
    'email_on_failure': False,
}

# DAG 생성 
# 2022/06/21 @once 한번만 실행하는 DAG생성
with DAG(
    dag_id='ex_hello_world', #web ui에 나오는 이름 꼭 작성해야함
    default_args=default_args, # 기본 설정
    start_date=datetime(2022, 6,21, tzinfo=kst), # 시작일시 
    description='print hello world', # 설명
    schedule_interval='@once', # cron 표현식으로 스케줄링 하겠다
    tags=['test']  # tag는 작성해도되고 안해도되지만 ui에서 filtering이 가능하므로 작성하는 것이 좋다.
) as dag:

    # python Operator에서 사용할 함수 정의
    def print_hello():
        print('hello world')

    #기본제공되는 DummyOperator
    t1 = DummyOperator(
        task_id='dummy_task_id',
        retries=5,
    )

    t2 = PythonOperator(
        task_id='Hello_World',
        python_callable=print_hello
    )

    #의존성 설정
    t1 >> t2