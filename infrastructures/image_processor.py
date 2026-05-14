from PIL import Image
import io
from typing import Optional
from fastapi import UploadFile


class ImageProcessor:
    """画像処理を行うインフラ層クラス"""

    @staticmethod
    async def process_uploaded_image(image: UploadFile) -> Optional[Image.Image]:
        """
        アップロードされた画像をPIL Imageに変換

        Args:
            image: アップロードされた画像ファイル

        Returns:
            PIL Image オブジェクト
        """
        try:
            image_content = await image.read()
            pil_image = Image.open(io.BytesIO(image_content)).convert("RGB")
            return pil_image
        except Exception as e:
            print(f"画像処理エラー: {str(e)}")
            return None
        finally:
            await image.seek(0)
