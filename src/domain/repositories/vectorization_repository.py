from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import numpy as np
from fastapi import UploadFile


class VectorizationRepository(ABC):
    """ベクトル化・類似度計算リポジトリインターフェース（既存のservicesに対応）"""

    @abstractmethod
    def text_vector(self, text: str) -> Optional[np.ndarray]:
        """テキストをベクトル化する（既存のbert.py）"""
        pass

    @abstractmethod
    def get_image_vector(self, image_data: bytes) -> Optional[np.ndarray]:
        """画像をベクトル化する（既存のvit.py）"""
        pass

    @abstractmethod
    async def keyword(self, text: str) -> List[Dict]:
        """形態素解析・地名抽出（既存のmecab.py）"""
        pass

    @abstractmethod
    def similarity_sort(
        self,
        filtered_data: List[Dict],
        query_vector: np.ndarray,
        features: np.ndarray,
        labels: List[str]
    ) -> List[Dict]:
        """類似度計算・ソート（既存のsimilarity_service.py）"""
        pass

    @abstractmethod
    def filter_location(self, keywords: List[str], data: List[Dict]) -> List[Dict]:
        """地名フィルタリング（既存のlocation_service.py）"""
        pass

    @abstractmethod
    async def text_caluculate(self, text: str):
        """テキスト類似度計算（既存のtext_service.py）"""
        pass

    @abstractmethod
    async def image_caluculate(self, image: UploadFile, filtered_data: Optional[List[Dict]] = None):
        """画像類似度計算（既存のimage_service.py）"""
        pass

    @abstractmethod
    def integrate_similarities(
        self,
        text_results: List[Dict],
        image_results: List[Dict],
        range_value: int
    ) -> List[Dict]:
        """類似度統合（既存のintegration_service.py）"""
        pass