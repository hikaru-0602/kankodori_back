from abc import ABC, abstractmethod
from typing import Optional, List
from PIL import Image


class FileManagementRepository(ABC):
    """ファイル管理 リポジトリインターフェース（ファイル操作関連処理）"""

    @abstractmethod
    def setup_directory(self, base_path: str, sub_dirs: List[str]) -> str:
        """ディレクトリ構造をセットアップ"""
        pass

    @abstractmethod
    def get_script_directory(self) -> str:
        """スクリプトディレクトリを取得"""
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """ファイルの存在確認"""
        pass

    @abstractmethod
    def load_image(self, file_path: str) -> Optional[Image.Image]:
        """画像ファイルを読み込み"""
        pass

    @abstractmethod
    def save_image(self, image: Image.Image, file_path: str) -> bool:
        """画像ファイルを保存"""
        pass

    @abstractmethod
    def create_filename(self, prompt: str, extension: str = ".jpg") -> str:
        """ファイル名を生成"""
        pass