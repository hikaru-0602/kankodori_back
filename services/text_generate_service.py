import os
from typing import Optional
from fastapi import UploadFile
from infrastructures.image_processor import ImageProcessor
# from infrastructures.translation_client import translate_to_japanese

# 環境変数でテキスト生成モデルを切り替え
# TEXT_GENERATOR=gemini or blip (デフォルト: blip)
# TEXT_GENERATOR = os.environ.get('TEXT_GENERATOR', 'blip').lower()

# Gemini限定に変更
# if TEXT_GENERATOR == 'gemini':
#     from infrastructures.gemini import generate_text_from_image
# else:
#     from infrastructures.blip_client import generate_text_from_image

from infrastructures.gemini import generate_text_from_image

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

        # 2. 画像からテキスト生成（Gemini限定）
        # if TEXT_GENERATOR == 'gemini':
        #     # Geminiは日本語で直接生成
        #     japanese_text = generate_text_from_image(pil_image)
        #     return japanese_text
        # else:
        #     # BLIPは英語生成 → 日本語翻訳
        #     english_text = generate_text_from_image(pil_image)
        #     if english_text is None:
        #         return None
        #     japanese_text = translate_to_japanese(english_text)
        #
        #     # 日本語翻訳後のテキストをログ出力
        #     print(f"[翻訳後] 生成されたテキスト（日本語）: {japanese_text}")
        #
        #     return japanese_text

        # Geminiで日本語テキストを直接生成
        japanese_text = generate_text_from_image(pil_image)
        return japanese_text

    except Exception as e:
        print(f"テキスト生成サービスエラー: {str(e)}")
        return None
