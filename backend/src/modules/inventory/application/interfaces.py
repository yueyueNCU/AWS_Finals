from typing import Protocol

class ImageStorageService(Protocol):
    def upload_image(self, file_content: bytes, filename: str, content_type: str) -> str:
        """上傳圖片並回傳 URL"""
        ...