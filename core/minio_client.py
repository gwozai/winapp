from minio import Minio
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE

class MinioManager:
    def __init__(self, bucket):
        self.client = Minio(MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, secure=MINIO_SECURE)
        self.bucket = bucket

    def list_objects(self):
        return list(self.client.list_objects(self.bucket, recursive=True))

    def get_presigned_url(self, object_name, expires=3600):
        from datetime import timedelta
        return self.client.presigned_get_object(self.bucket, object_name, expires=timedelta(seconds=expires))