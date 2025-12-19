from ..application.interfaces import ImageStorageService
import boto3
import os
import uuid

class S3ImageStorage(ImageStorageService):
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "ncu-barter-platform")
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )

    def upload_image(self, file_content: bytes, filename: str, content_type: str) -> str:
        # 如果沒有設定 AWS Key，回傳假網址 (開發測試用)
        if not os.getenv("AWS_ACCESS_KEY_ID"):
            return f"https://fake-s3-url.com/{filename}"

        # 產生唯一檔名避免衝突
        ext = filename.split('.')[-1]
        unique_filename = f"items/{uuid.uuid4()}.{ext}"

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=unique_filename,
            Body=file_content,
            ContentType=content_type
            # ACL='public-read' # 視你的 Bucket 設定是否公開
        )
        
        # 回傳公開連結
        region = os.getenv("AWS_REGION", "us-east-1")
        return f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{unique_filename}"