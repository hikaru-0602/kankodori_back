import json
import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
from PIL import Image
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Firebase Admin SDKの初期化
def initialize_firebase():
    """Firebase Admin SDKを初期化"""
    if not firebase_admin._apps:
        if os.path.exists("firebase-key.json"):
            # ローカルではファイルから認証
            cred = credentials.Certificate("firebase-key.json")
        else:
            # Cloud RunなどではADCを利用
            cred = credentials.ApplicationDefault()

        bucket_name = os.environ.get("FIREBASE_STORAGE_BUCKET", "kankodori-23918.firebasestorage.app")
        if not bucket_name:
            raise ValueError("FIREBASE_STORAGE_BUCKET環境変数が設定されていません")

        firebase_admin.initialize_app(cred, {
            'storageBucket': bucket_name
        })

async def upload_storage(local_path: str, storage_path: str) -> Optional[str]:
    """
    ローカル画像をFirebase Storageにアップロード

    Args:
        local_path: ローカルファイルパス
        storage_path: Storageでのパス (例: "images/sample.jpg")

    Returns:
        アップロード成功時は公開URL、失敗時はNone
    """
    try:
        initialize_firebase()
        bucket = storage.bucket()
        blob = bucket.blob(storage_path)

        blob.upload_from_filename(local_path)
        blob.make_public()

        return blob.public_url
    except Exception as e:
        print(f"アップロードエラー: {e}")
        return None

async def download_storage(storage_path: str, local_path: str) -> bool:
    """
    Firebase Storageから画像をダウンロード

    Args:
        storage_path: Storageでのパス
        local_path: ダウンロード先のローカルパス

    Returns:
        成功時True、失敗時False
    """
    try:
        initialize_firebase()
        bucket = storage.bucket()
        blob = bucket.blob(storage_path)

        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)

        return True
    except Exception as e:
        print(f"ダウンロードエラー: {e}")
        return False

async def get_image_url(storage_path: str) -> Optional[str]:
    """
    Firebase Storageの画像公開URLを取得

    Args:
        storage_path: Storageでのパス

    Returns:
        公開URL、存在しない場合はNone
    """
    try:
        initialize_firebase()
        bucket = storage.bucket()
        blob = bucket.blob(storage_path)

        if blob.exists():
            blob.make_public()
            return blob.public_url
        return None
    except Exception as e:
        print(f"URL取得エラー: {e}")
        return None

async def upload_pil_image_to_storage(image: Image.Image, storage_path: str) -> Optional[str]:
    """
    PIL ImageオブジェクトをFirebase Storageにアップロード

    Args:
        image: PIL Imageオブジェクト
        storage_path: Storageでのパス

    Returns:
        アップロード成功時は公開URL、失敗時はNone
    """
    try:
        initialize_firebase()

        # 一時ファイルに保存
        temp_path = f"/tmp/{os.path.basename(storage_path)}"
        image.save(temp_path)

        # アップロード
        url = await upload_storage(temp_path, storage_path)

        # 一時ファイル削除
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return url
    except Exception as e:
        print(f"PIL画像アップロードエラー: {e}")
        return None
