from typing import Optional
from fastapi import UploadFile
from infrastructures.image_processor import ImageProcessor
from infrastructures.translation_client import translate_to_japanese

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
        pil_image = await ImageProcessor.process_uploaded_image(image)
        if pil_image is None:
            return None

        # 2. 画像からテキスト生成
        english_text = ImageProcessor.generate_text_from_image(pil_image)
        if english_text is None:
            return None

        # 3. 日本語に翻訳
        japanese_text = translate_to_japanese(english_text)
        
        return japanese_text

    except Exception as e:
        print(f"テキスト生成サービスエラー: {str(e)}")
        return None
