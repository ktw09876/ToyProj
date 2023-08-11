import luigi
from luigi_test import S3_Upload, DataLoad, DBInsertTask

if __name__ == '__main__':
    tasks_to_run = [S3_Upload(), DataLoad(), DBInsertTask()]
    luigi.build(tasks_to_run, local_scheduler=True)