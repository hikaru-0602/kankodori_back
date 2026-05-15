import json
import os
import numpy as np
from typing import Optional, List, Dict, Any
from infrastructures.firebase_config import initialize_firebase, download_storage, upload_storage
from infrastructures import firebase_storage


class StorageRepository:
    """Firebase Storageの統一管理クラス"""

    def __init__(self):
        self._is_initialized = False

    def _ensure_initialized(self):
        """Firebase初期化を確認"""
        if not self._is_initialized:
            initialize_firebase()
            self._is_initialized = True

    # ==================== Blob基本操作 ====================

    async def check_blob_exists(self, blob_path: str) -> bool:
        """
        指定パスのBlobが存在するかチェック

        Args:
            blob_path: チェックするBlobのパス

        Returns:
            存在する場合True、それ以外False
        """
        self._ensure_initialized()
        return await firebase_storage.check_blob_exists(blob_path)

    async def save_blob(
        self,
        data: bytes,
        blob_path: str,
        content_type: str = "image/jpeg",
        make_public: bool = True
    ) -> bool:
        """
        バイナリデータをFirebase Storageに保存

        Args:
            data: 保存するバイナリデータ
            blob_path: 保存先のパス
            content_type: コンテンツタイプ
            make_public: 公開設定するかどうか

        Returns:
            成功時True、失敗時False
        """
        self._ensure_initialized()
        url = await firebase_storage.upload_blob(blob_path, data, content_type, make_public)
        if url:
            print(f"Blob保存成功: {blob_path}")
            return True
        else:
            return False

    async def get_blob_url(self, blob_path: str) -> Optional[str]:
        """
        Blobの公開URLを取得

        Args:
            blob_path: BlobのStorageパス

        Returns:
            公開URL、存在しない場合はNone
        """
        self._ensure_initialized()
        return await firebase_storage.get_blob_public_url(blob_path)

    async def list_blobs(self, prefix: str) -> List[str]:
        """
        指定プレフィックスのBlob一覧を取得

        Args:
            prefix: 検索するプレフィックス (例: "api/query_image/")

        Returns:
            ファイル名のリスト
        """
        self._ensure_initialized()
        blob_names = await firebase_storage.list_blobs_with_prefix(prefix)

        # プレフィックスを除去してファイル名のみを返す
        filenames = []
        for blob_name in blob_names:
            filename = blob_name.replace(prefix, "")
            if filename:
                filenames.append(filename)

        return filenames

    # ==================== JSONファイル操作 ====================

    async def get_json(self, storage_path: str) -> Optional[Dict[str, Any]]:
        """
        JSONファイルを取得

        Args:
            storage_path: StorageのJSONファイルパス

        Returns:
            JSON内容、取得失敗時はNone
        """
        try:
            self._ensure_initialized()

            local_path = f"/tmp/{os.path.basename(storage_path)}"

            # firebase_storageを使用してダウンロード
            success = await firebase_storage.download_blob_to_file(storage_path, local_path)
            if not success:
                return None

            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if os.path.exists(local_path):
                os.remove(local_path)

            return data
        except Exception as e:
            print(f"JSON取得エラー ({storage_path}): {e}")
            return None

    async def save_json(
        self,
        storage_path: str,
        data: Dict[str, Any] | List[Any]
    ) -> bool:
        """
        JSONファイルを保存

        Args:
            storage_path: 保存先のStorageパス
            data: 保存するデータ

        Returns:
            成功時True、失敗時False
        """
        try:
            self._ensure_initialized()
            temp_path = f"/tmp/{os.path.basename(storage_path)}"

            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # firebase_storageを使用してアップロード
            url = await firebase_storage.upload_file_to_blob(temp_path, storage_path, make_public=True)

            if os.path.exists(temp_path):
                os.remove(temp_path)

            return url is not None
        except Exception as e:
            print(f"JSON保存エラー ({storage_path}): {e}")
            return False

    async def append_to_json_array(
        self,
        storage_path: str,
        new_item: Dict[str, Any]
    ) -> bool:
        """
        JSON配列の末尾にアイテムを追加

        Args:
            storage_path: StorageのJSONファイルパス
            new_item: 追加するアイテム

        Returns:
            成功時True、失敗時False
        """
        try:
            current_data = await self.get_json(storage_path)
            if current_data is None:
                current_data = []

            if not isinstance(current_data, list):
                print(f"エラー: {storage_path}は配列ではありません")
                return False

            current_data.append(new_item)
            return await self.save_json(storage_path, current_data)
        except Exception as e:
            print(f"JSON配列追加エラー ({storage_path}): {e}")
            return False

    # ==================== 特徴量ファイル操作 ====================

    async def get_npy(self, storage_path: str) -> Optional[np.ndarray]:
        """
        .npyファイルを取得

        Args:
            storage_path: Storageの.npyファイルパス (拡張子は自動補完)

        Returns:
            numpy配列、取得失敗時はNone
        """
        try:
            self._ensure_initialized()

            if not storage_path.endswith('.npy'):
                storage_path += '.npy'

            filename = os.path.basename(storage_path)
            local_path = f"/tmp/{filename}"

            # firebase_storageを使用してダウンロード
            success = await firebase_storage.download_blob_to_file(storage_path, local_path)
            if not success:
                return None

            data = np.load(local_path, allow_pickle=True)

            if os.path.exists(local_path):
                os.remove(local_path)

            return data
        except Exception as e:
            print(f"npy取得エラー ({storage_path}): {e}")
            return None

    async def save_npy(self, storage_path: str, data: np.ndarray) -> bool:
        """
        numpy配列を.npyファイルとして保存

        Args:
            storage_path: 保存先のStorageパス
            data: 保存するnumpy配列

        Returns:
            成功時True、失敗時False
        """
        try:
            self._ensure_initialized()

            if not storage_path.endswith('.npy'):
                storage_path += '.npy'

            filename = os.path.basename(storage_path)
            temp_path = f"/tmp/{filename}"

            np.save(temp_path, data)

            # firebase_storageを使用してアップロード
            url = await firebase_storage.upload_file_to_blob(temp_path, storage_path, make_public=True)

            if os.path.exists(temp_path):
                os.remove(temp_path)

            return url is not None
        except Exception as e:
            print(f"npy保存エラー ({storage_path}): {e}")
            return False

    # ==================== ドメイン固有メソッド ====================

    async def get_place_data(self) -> Optional[Dict[str, Any]]:
        """
        place_data.jsonを取得

        Returns:
            place_data全体、取得失敗時はNone
        """
        return await self.get_json("place_data.json")

    async def get_photo_data(self) -> Optional[List[Any]]:
        """
        place_data.json内のphoto配列を取得

        Returns:
            photo配列、取得失敗時はNone
        """
        try:
            place_data = await self.get_place_data()
            if not place_data:
                return None

            if 'photo' in place_data and isinstance(place_data['photo'], list):
                return place_data['photo']
            else:
                print("photoキーが見つからないか、配列ではありません")
                return None
        except Exception as e:
            print(f"photo_data取得エラー: {e}")
            return None

    async def get_query_image_data(self) -> Optional[List[Dict[str, Any]]]:
        """
        query_image.jsonを取得

        Returns:
            query_image配列、取得失敗時はNone
        """
        data = await self.get_json("query_image.json")
        if data is None or not isinstance(data, list):
            return None
        return data

    async def append_to_query_image(self, new_item: Dict[str, Any]) -> bool:
        """
        query_image.jsonの末尾に新しいアイテムを追加

        Args:
            new_item: 追加するアイテム(idフィールド必須)

        Returns:
            成功時True、失敗時False
        """
        if not new_item.get('id'):
            print("idフィールドが必要です")
            return False

        return await self.append_to_json_array("query_image.json", new_item)

    async def get_feature_npy(self, filename: str) -> Optional[np.ndarray]:
        """
        featureディレクトリ内の.npyファイルを取得

        Args:
            filename: 取得したい.npyファイル名 (例: "image_001.npy" または "image_001")

        Returns:
            numpy配列、取得失敗時はNone
        """
        storage_path = f"features/{filename}"
        return await self.get_npy(storage_path)

    async def get_feature_with_labels(
        self,
        filename: str
    ) -> Optional[tuple[Dict[str, Any], List[str]]]:
        """
        特徴量データとラベルを取得

        Args:
            filename: 特徴量ファイル名 (拡張子省略可)

        Returns:
            (特徴量データ, ラベルリスト) のタプル、取得失敗時はNone
        """
        try:
            raw_data = await self.get_feature_npy(filename)
            if raw_data is None:
                return None

            if isinstance(raw_data, np.ndarray) and raw_data.shape == ():
                raw_data = raw_data.item()

            if not isinstance(raw_data, dict):
                print(f"エラー: ロードされたデータは辞書形式ではありません: {filename}")
                print(f"実際のデータ型: {type(raw_data)}")
                return None

            features = raw_data
            labels = list(raw_data.keys())

            return features, labels
        except Exception as e:
            print(f"特徴量取得エラー: {e}")
            return None

    async def list_api_query_images(self) -> List[str]:
        """
        api/query_imageディレクトリ内のファイル名一覧を取得

        Returns:
            ファイル名のリスト
        """
        return await self.list_blobs("api/query_image/")

    async def list_api_search_images(self) -> List[str]:
        """
        api/search_imageディレクトリ内のファイル名一覧を取得

        Returns:
            ファイル名のリスト
        """
        return await self.list_blobs("api/search_image/")
