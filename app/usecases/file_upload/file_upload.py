import cloudinary.uploader as uploader
from typing import Tuple, Dict, Any

class FileUploadUseCase:
    def upload(self, file) -> Tuple[bool, Dict[str, Any]]:
        upload_result = uploader.upload(file)
        file_url = upload_result.get('secure_url')

        return True, {
            "message": "File uploaded successfully.",
            "data": {
                "file_url": file_url
            }
        }