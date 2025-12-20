import os
import boto3
from ..application.interfaces import ImageStorageService
import uuid

class S3ImageStorage(ImageStorageService):
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        
        # 取得環境變數中的金鑰 (本機開發用)
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        if aws_access_key and aws_secret_key:
            # 情況 A: 本機開發 (有 .env 金鑰)
            print("Using AWS Access Keys from .env")
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=self.region
            )
        else:
            # 情況 B: EC2 環境 (使用 IAM Role)
            # 當不傳入 key id/secret 時，boto3 會自動去抓 EC2 的 Instance Metadata
            print("Using IAM Role (Instance Profile)")
            self.s3_client = boto3.client(
                's3',
                region_name=self.region
            )

    def upload_image(self, file_content: bytes, filename: str, content_type: str) -> str:
        # 產生唯一檔名
        ext = filename.split('.')[-1] if '.' in filename else "jpg"
        unique_filename = f"items/{uuid.uuid4()}.{ext}"

        # 上傳
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=unique_filename,
            Body=file_content,
            ContentType=content_type
        )
        
        # 回傳網址
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{unique_filename}"