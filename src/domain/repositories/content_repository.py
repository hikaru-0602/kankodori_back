from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from fastapi import UploadFile
from PIL import Image


class ContentGenerationRepository(ABC):
    """コンテンツ生成リポジトリインターフェース（既存のservicesに対応）"""

    @abstractmethod
    async def text_generate(self, image: UploadFile) -> Optional[str]:
        """画像からテキストを生成する（既存のtext_generate_service.py）"""
        pass

    @abstractmethod
    async def image_generate(self, prompt: str) -> Optional[Image.Image]:
        """テキストから画像を生成する（既存のimage_generate_service.py）"""
        pass

    @abstractmethod
    def create_enhanced_prompt(self, user_input: str) -> str:
        """プロンプトを強化する（既存のimage_generate_service.py）"""
        pass

    @abstractmethod
    async def random_suggest(self) -> Dict[str, List[str]]:
        """ランダム画像提案（既存のsuggestion_service.py）"""
        pass