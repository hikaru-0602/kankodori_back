import re
from typing import Optional, Tuple
from fastapi import UploadFile
from firebase_admin import storage
from infrastructures.firebase_config import initialize_firebase
from services.image_generate_service import image_generate

# Firebase初期化
initialize_firebase()

def clean_filename(text: str) -> str:
    """テキストからファイル名を生成"""
    filename = re.sub(r'[^\w\s-]', '', text)
    filename = re.sub(r'[-\s]+', '_', filename)
    filename = filename.strip('_')
    return filename[:50] if len(filename) > 50 else filename

async def check_image_exists_in_folder(folder_path: str, filename_base: str) -> Optional[str]:
    """指定フォルダに同名ファイルが存在するかチェック"""
    try:
        bucket = storage.bucket()
        extensions = ['.jpg', '.jpeg', '.png', '.webp']

        for ext in extensions:
            blob_path = f"{folder_path}/{filename_base}{ext}"
            blob = bucket.blob(blob_path)
            if blob.exists():
                return blob_path
        return None

    except Exception as e:
        print(f"画像存在チェックエラー ({folder_path}): {e}")
        return None

async def find_existing_image(text: str) -> Optional[str]:
    """両フォルダで既存画像を検索"""
    if not text:
        return None

    filename_base = clean_filename(text)

    # api/query_image → api/search_image の順で検索
    for folder in ["api/query_image", "api/search_image"]:
        path = await check_image_exists_in_folder(folder, filename_base)
        if path:
            print(f"既存画像発見 ({folder}): {path}")
            return path
    return None

async def save_image_to_storage(image_data: bytes, blob_path: str, content_type: str = "image/jpeg") -> bool:
    """画像データをFirebase Storageに保存"""
    try:
        bucket = storage.bucket()
        blob = bucket.blob(blob_path)
        blob.upload_from_string(image_data, content_type=content_type)
        blob.make_public()
        print(f"画像保存成功: {blob_path}")
        return True
    except Exception as e:
        print(f"画像保存エラー: {e}")
        return False

async def process_uploaded_image(image: UploadFile, text: str, user_id: str) -> Tuple[Optional[str], str]:
    """アップロード画像の処理"""
    filename_base = clean_filename(text)

    # 既存画像チェック
    existing_path = await check_image_exists_in_folder("api/query_image", filename_base)
    if existing_path:
        return existing_path, "suggested"

    # 新規保存
    original_filename = image.filename or "image.jpg"
    ext = "." + original_filename.split(".")[-1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        ext = '.jpg'

    blob_path = f"api/search_image/{filename_base}{ext}"
    image_data = await image.read()

    if await save_image_to_storage(image_data, blob_path, image.content_type or "image/jpeg"):
        return blob_path, "user_upload"
    return None, "user_upload"

async def process_generated_image(text: str, user_id: str) -> Tuple[Optional[str], str]:
    """生成画像の処理"""
    if not text:
        return None, "none"

    # 既存画像チェック
    existing_path = await find_existing_image(text)
    if existing_path:
        return existing_path, "suggested"

    # 画像生成
    print(f"画像生成開始: {text}")
    generated_image = await image_generate(text)

    if generated_image:
        # 保存
        filename_base = clean_filename(text)
        blob_path = f"api/search_image/{filename_base}.jpg"

        from io import BytesIO
        image_bytes = BytesIO()
        generated_image.save(image_bytes, format='JPEG')
        image_data = image_bytes.getvalue()

        if await save_image_to_storage(image_data, blob_path):
            return blob_path, "generate"

    print(f"画像生成失敗: {text}")
    return None, "none"

async def process_search_image(image: Optional[UploadFile], text: Optional[str], user_id: str, image_source: str = "user_upload") -> Tuple[Optional[str], str]:
    """検索画像を処理（存在チェック→保存）"""
    if not image:
        return None, image_source

    try:
        return await process_uploaded_image(image, text or "", user_id)
    except Exception as e:
        print(f"画像処理エラー: {e}")
        return None, image_source

async def process_search_with_no_image(text: Optional[str], user_id: str) -> Tuple[Optional[str], str]:
    """画像なしの検索処理（既存画像チェック→生成）"""
    if not text:
        return None, "none"

    try:
        return await process_generated_image(text, user_id)
    except Exception as e:
        print(f"画像なし検索処理エラー: {e}")
        return None, "none"
