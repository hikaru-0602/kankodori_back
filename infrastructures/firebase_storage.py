"""
Firebase Storage操作のInfrastructure層

Firebase Storage SDKの直接操作のみを担当
Repository層から呼び出される低レベルAPI
"""

from typing import Optional
from firebase_admin import storage
import os


async def check_blob_exists(blob_path: str) -> bool:
    """
    指定パスのBlobが存在するかチェック

    Args:
        blob_path: チェックするBlobのパス

    Returns:
        存在する場合True、それ以外False
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(blob_path)
        return blob.exists()
    except Exception as e:
        print(f"Blob存在チェックエラー ({blob_path}): {e}")
        return False


async def upload_blob(
    blob_path: str,
    data: bytes,
    content_type: str = "image/jpeg",
    make_public: bool = True
) -> Optional[str]:
    """
    バイナリデータをFirebase Storageに保存

    Args:
        blob_path: 保存先のパス
        data: 保存するバイナリデータ
        content_type: コンテンツタイプ
        make_public: 公開設定するかどうか

    Returns:
        成功時は公開URL、失敗時はNone
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(blob_path)
        blob.upload_from_string(data, content_type=content_type)

        if make_public:
            blob.make_public()
            return blob.public_url

        return blob.public_url
    except Exception as e:
        print(f"Blob保存エラー ({blob_path}): {e}")
        return None


async def get_blob_public_url(blob_path: str) -> Optional[str]:
    """
    Blobの公開URLを取得

    Args:
        blob_path: BlobのStorageパス

    Returns:
        公開URL、存在しない場合はNone
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(blob_path)

        if blob.exists():
            blob.make_public()
            return blob.public_url
        return None
    except Exception as e:
        print(f"URL取得エラー ({blob_path}): {e}")
        return None


async def list_blobs_with_prefix(prefix: str) -> list[str]:
    """
    指定プレフィックスのBlob一覧を取得

    Args:
        prefix: 検索するプレフィックス (例: "api/query_image/")

    Returns:
        Blob名のリスト
    """
    try:
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]
    except Exception as e:
        print(f"Blob一覧取得エラー ({prefix}): {e}")
        return []


async def download_blob_to_file(blob_path: str, local_path: str) -> bool:
    """
    Blobをローカルファイルにダウンロード

    Args:
        blob_path: StorageのBlobパス
        local_path: ダウンロード先のローカルパス

    Returns:
        成功時True、失敗時False
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(blob_path)

        if not blob.exists():
            print(f"Blob not found: {blob_path}")
            return False

        blob.download_to_filename(local_path)
        return True
    except Exception as e:
        print(f"Blobダウンロードエラー ({blob_path}): {e}")
        return False


async def upload_file_to_blob(local_path: str, blob_path: str, make_public: bool = True) -> Optional[str]:
    """
    ローカルファイルをBlobにアップロード

    Args:
        local_path: アップロードするローカルファイルパス
        blob_path: 保存先のStorageパス
        make_public: 公開設定するかどうか

    Returns:
        成功時は公開URL、失敗時はNone
    """
    try:
        if not os.path.exists(local_path):
            print(f"Local file not found: {local_path}")
            return None

        bucket = storage.bucket()
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(local_path)

        if make_public:
            blob.make_public()
            return blob.public_url

        return blob.public_url
    except Exception as e:
        print(f"ファイルアップロードエラー ({local_path} -> {blob_path}): {e}")
        return None
