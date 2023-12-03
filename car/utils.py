from minio import Minio

from config import settings

minio_client = Minio('minio:9000',
                     access_key=settings.MINIO_STORAGE_ACCESS_KEY,
                     secret_key=settings.MINIO_STORAGE_SECRET_KEY,
                     secure=False)
