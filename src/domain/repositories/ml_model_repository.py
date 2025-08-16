from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
import torch
from PIL import Image
from fastapi import UploadFile


class MLModelRepository(ABC):
    """機械学習モデル リポジトリインターフェース（AI・ML関連処理を統合）"""

    # === BERT関連 ===
    @abstractmethod
    def get_bert_vectorizer(self):
        """BertVectorizerインスタンスを取得"""
        pass

    @abstractmethod
    def vectorize_text(self, text: str) -> Optional[np.ndarray]:
        """テキストをBERTでベクトル化"""
        pass

    # === ViT関連 ===
    @abstractmethod
    def get_vit_vectorizer(self):
        """ViTVectorizerインスタンスを取得"""
        pass

    @abstractmethod
    def process_image(self, image_data: bytes) -> Optional[torch.Tensor]:
        """画像をViTで前処理"""
        pass

    @abstractmethod
    def extract_features(self, inputs: torch.Tensor) -> Optional[np.ndarray]:
        """ViTで特徴量を抽出"""
        pass

    # === BLIP関連 ===
    @abstractmethod
    def initialize_blip_model(self):
        """BLIPモデルを初期化"""
        pass

    @abstractmethod
    def get_blip_model(self):
        """BLIPモデルインスタンスを取得"""
        pass

    # === HuggingFace関連 ===
    @abstractmethod
    def get_huggingface_client(self):
        """HuggingFaceImageClientインスタンスを取得"""
        pass

    @abstractmethod
    def generate_image(self, prompt: str, model: str = "stabilityai/stable-diffusion-3.5-large") -> Optional[Image.Image]:
        """HuggingFaceでテキストから画像生成"""
        pass

    # === 画像処理関連 ===
    @abstractmethod
    async def process_uploaded_image(self, image: UploadFile) -> Optional[Image.Image]:
        """アップロードされた画像を処理"""
        pass

    @abstractmethod
    def generate_text_from_image(self, pil_image: Image.Image) -> Optional[str]:
        """画像からテキストを生成（BLIP使用）"""
        pass

    # === 翻訳関連 ===
    @abstractmethod
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'auto') -> Optional[str]:
        """テキストを翻訳"""
        pass

    @abstractmethod
    def translate_to_japanese(self, text: str) -> str:
        """テキストを日本語に翻訳"""
        pass

    @abstractmethod
    def translate_to_english(self, text: str) -> str:
        """テキストを英語に翻訳"""
        pass