import os
import io
from typing import Optional
from fastapi import UploadFile
from PIL import Image
from infrastructures.gemini_client import generate_text_from_image

async def text_generate(image: UploadFile) -> Optional[str]:
    """
    画像からテキストを生成する（ビジネスロジック層）

    Args:
        image: アップロードされた画像ファイル

    Returns:
        生成された日本語テキスト（失敗時はNone）
    """
    try:
        # 1. 画像を処理してPIL Imageに変換
        image_content = await image.read()
        pil_image = Image.open(io.BytesIO(image_content)).convert("RGB")
        await image.seek(0)

        # 2. Geminiで日本語テキストを直接生成
        japanese_text = generate_text_from_image(pil_image)
        return japanese_text

    except Exception as e:
        print(f"テキスト生成サービスエラー: {str(e)}")
        return None
