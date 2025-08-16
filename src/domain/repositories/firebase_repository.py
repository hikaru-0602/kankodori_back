from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import numpy as np
from PIL import Image


class FirebaseRepository(ABC):
    """Firebase リポジトリインターフェース（Firebase関連の全処理を統合）"""

    # === 初期化・設定 ===
    @abstractmethod
    def initialize_firebase(self) -> None:
        """Firebase Admin SDK初期化"""
        pass

    # === 低レベル ストレージ操作 ===
    @abstractmethod
    async def upload_storage(self, local_path: str, storage_path: str) -> Optional[str]:
        """ローカル画像をFirebase Storageにアップロード"""
        pass

    @abstractmethod
    async def download_storage(self, storage_path: str, local_path: str) -> bool:
        """Firebase Storageから画像をダウンロード"""
        pass

    @abstractmethod
    async def get_image_url(self, storage_path: str) -> Optional[str]:
        """Firebase Storageの画像公開URLを取得"""
        pass

    @abstractmethod
    async def upload_pil_image_to_storage(self, image: Image.Image, storage_path: str) -> Optional[str]:
        """PIL ImageオブジェクトをFirebase Storageにアップロード"""
        pass

    # === データ管理・中間レイヤー ===
    @abstractmethod
    async def get_place_data(self) -> Optional[Dict]:
        """place_data.jsonを取得"""
        pass

    @abstractmethod
    async def get_query_image_data(self) -> Optional[List[Dict]]:
        """query_image.jsonを取得"""
        pass

    @abstractmethod
    async def append_to_query_image(self, new_item: Dict) -> bool:
        """query_image.jsonの末尾に新しいアイテムを追加"""
        pass

    @abstractmethod
    async def get_feature_npy(self, filename: str) -> Optional[np.ndarray]:
        """featureディレクトリ内の.npyファイルを取得"""
        pass

    @abstractmethod
    async def list_api_query_images(self) -> List[str]:
        """api/query_imageディレクトリ内のファイル名一覧を取得"""
        pass

    # === 高レベル サービス層API ===
    @abstractmethod
    async def get_photo_data(self) -> Optional[List]:
        """写真データを取得する"""
        pass

    @abstractmethod
    async def add_query_image(self, new_item: Dict) -> bool:
        """クエリ画像を追加する"""
        pass

    @abstractmethod
    async def get_feature(self, filename: str) -> Optional[tuple[Dict, List[str]]]:
        """特徴量ファイルを取得する"""
        pass

    @abstractmethod
    async def get_api_query_images(self) -> List[str]:
        """API用画像リストを取得する"""
        pass