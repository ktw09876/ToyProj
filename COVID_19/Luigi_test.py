import luigi
from luigi.util import requires

class S3UploadTask(luigi.Task):
    def run(self):
        import s3_upload
        # Call the necessary functions or logic from s3_upload.py

@requires(S3UploadTask)
class DataLoadTask(luigi.Task):
    def run(self):
        import data_load
        # Call the necessary functions or logic from data_load.py

@requires(DataLoadTask)
class DBInsertTask(luigi.Task):
    def run(self):
        import db_Insert
        # Call the necessary functions or logic from db_Insert.py

if __name__ == '__main__':
    luigi.run()
