import json
import os
import numpy as np
from typing import Optional, List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from infrastructures.firebase_config import download_storage, upload_storage, initialize_firebase

class FirebaseDataManager:
    """Firebase Storageのデータ管理クラス"""

    def __init__(self):
        self._is_initialized = False

    def _ensure_initialized(self):
        """Firebase初期化を確認"""
        if not self._is_initialized:
            initialize_firebase()
            self._is_initialized = True

    async def get_place_data(self) -> Optional[Dict[str, Any]]:
        """
        place_data.jsonを取得

        Returns:
            place_data全体、取得失敗時はNone
        """
        try:
            self._ensure_initialized()

            local_path = "/tmp/place_data.json"
            storage_path = "place_data.json"

            success = await download_storage(storage_path, local_path)
            if not success:
                return None

            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 一時ファイル削除
            if os.path.exists(local_path):
                os.remove(local_path)

            return data
        except Exception as e:
            print(f"place_data取得エラー: {e}")
            return None


    async def append_to_query_image(self, new_item: Dict[str, Any]) -> bool:
        """
        query_image.jsonの末尾に新しいアイテムを追加

        Args:
            new_item: 追加するアイテム

        Returns:
            成功時True、失敗時False
        """
        try:
            # 現在のデータを取得
            current_data = await self.get_query_image_data()
            if current_data is None:
                current_data = []

            # 新しいアイテムを追加
            current_data.append(new_item)

            # 一時ファイルに保存
            temp_path = "/tmp/query_image_updated.json"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)

            # Storageにアップロード
            success = await upload_storage(temp_path, "query_image.json")

            # 一時ファイル削除
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return success is not None

        except Exception as e:
            print(f"query_image追加エラー: {e}")
            return False

    async def get_feature_npy(self, filename: str) -> Optional[np.ndarray]:
        """
        featureディレクトリ内の.npyファイルを取得

        Args:
            filename: 取得したい.npyファイル名 (例: "image_001.npy")

        Returns:
            numpy配列、取得失敗時はNone
        """
        try:
            self._ensure_initialized()

            local_path = f"/tmp/{filename}"
            storage_path = f"features/{filename}"

            success = await download_storage(storage_path, local_path)
            if not success:
                return None

            # npyファイルを読み込み（pickleオブジェクトを許可）
            data = np.load(local_path, allow_pickle=True)

            # 一時ファイル削除
            if os.path.exists(local_path):
                os.remove(local_path)

            return data
        except Exception as e:
            print(f"feature npy取得エラー: {e}")
            return None

    async def list_api_query_images(self) -> List[str]:
        """
        api/query_imageディレクトリ内のファイル名一覧を取得

        Returns:
            ファイル名のリスト
        """
        try:
            from firebase_admin import storage
            self._ensure_initialized()

            bucket = storage.bucket()
            blobs = bucket.list_blobs(prefix="api/query_image/")

            filenames = []
            for blob in blobs:
                # api/query_imageディレクトリ内のファイル名のみ抽出
                filename = blob.name.replace("api/query_image/", "")
                if filename:  # 空文字列でない場合
                    filenames.append(filename)

            return filenames
        except Exception as e:
            print(f"api/query_image ファイル一覧取得エラー: {e}")
            return []
