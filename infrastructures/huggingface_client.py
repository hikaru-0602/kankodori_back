import os
from huggingface_hub import InferenceClient
from typing import Optional


class HuggingFaceImageClient:
    """HuggingFace画像生成クライアント"""

    def __init__(self):
        self._client = None

    def _get_client(self) -> Optional[InferenceClient]:
        """HuggingFaceクライアントを取得（初回のみ初期化）"""
        if self._client is None:
            api_key = os.environ.get("HF_API_TOKEN")
            if not api_key:
                print("エラー: HF_API_TOKEN が設定されていません")
                return None

            self._client = InferenceClient(
                provider="fal-ai",
                api_key=api_key,
            )

        return self._client

    def generate_image(self, prompt: str, model: str = "stabilityai/stable-diffusion-3.5-large"):
        """
        画像を生成する

        Args:
            prompt: 生成プロンプト
            model: 使用モデル

        Returns:
            生成された画像（PIL Image）
        """
        client = self._get_client()
        if client is None:
            return None

        return client.text_to_image(prompt, model=model)


# シングルトンインスタンス
_image_client = HuggingFaceImageClient()

def get_huggingface_client() -> HuggingFaceImageClient:
    """HuggingFace画像生成クライアントを取得"""
    return _image_client
