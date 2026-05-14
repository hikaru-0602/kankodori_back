import os
import io
from PIL import Image
from typing import Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# グローバル変数でクライアントを保持
_client = None

def initialize_gemini_client():
    """Geminiクライアントを初期化"""
    global _client

    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY環境変数が設定されていません")
        _client = genai.Client(api_key=api_key)
        print("Geminiクライアントの初期化が完了しました")

def get_gemini_client():
    """Geminiクライアントを取得"""
    return _client

def generate_text_from_image(pil_image: Image.Image) -> Optional[str]:
    """
    PIL ImageからGeminiモデルを使用してテキストを生成

    Args:
        pil_image: PIL Image オブジェクト

    Returns:
        生成されたテキスト（日本語）
    """
    try:
        # クライアント初期化
        initialize_gemini_client()
        client = get_gemini_client()

        # PIL Imageをバイトデータに変換
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        # キャプション生成
        prompt = """この画像をもとに，観光地検索に使える日本語キャプションを1文で作成してください。
画像に写っているもの，風景の特徴，雰囲気を具体的に含めてください。
画像から判断できない地名や施設名は書かないでください。
出力はキャプション本文だけにしてください。
出力は日本語で行ってください。"""

        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[
                prompt,
                types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),
            ],
        )

        return response.text

    except Exception as e:
        print(f"テキスト生成エラー: {str(e)}")
        return None
