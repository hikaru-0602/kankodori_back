import os
from typing import Optional, Tuple
from fastapi import UploadFile
from repositories.storage_repository import StorageRepository

# Repository初期化
_storage_repo = StorageRepository()

async def process_uploaded_image(image: UploadFile, text: str, user_id: str) -> Tuple[Optional[str], str]:
    """アップロード画像の処理"""
    # 元のファイル名を保持
    original_filename = image.filename or "image.jpg"
    filename_base = os.path.splitext(original_filename)[0]
    ext = "." + original_filename.split(".")[-1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        ext = '.jpg'

    # クエリー・サーチ間の重複チェック
    query_path = f"api/query_image/{filename_base}{ext}"
    search_path = f"api/search_image/{filename_base}{ext}"

    query_exists = await _storage_repo.check_blob_exists(query_path)
    search_exists = await _storage_repo.check_blob_exists(search_path)

    if query_exists:
        return query_path, "exist"
    if search_exists:
        return search_path, "exist"

    # 両方にない場合のみサーチに保存
    try:
        image.file.seek(0)
    except:
        pass

    image_data = await image.read()

    if await _storage_repo.save_blob(image_data, search_path, image.content_type or "image/jpeg"):
        return search_path, "user_upload"
    return None, "user_upload"


async def process_search_image(image: Optional[UploadFile], text: Optional[str], user_id: str, image_source: str = "user_upload") -> Tuple[Optional[str], str]:
    """検索画像を処理（存在チェック→保存）"""
    if not image:
        return None, image_source

    try:
        # 画像が生成されたものかアップロードかで分岐
        if image_source == "generate":
            # 生成画像の場合（PIL Imageオブジェクト）
            return await process_generated_image_for_storage(image, text or "", user_id)
        else:
            # アップロード画像の場合（UploadFile）
            return await process_uploaded_image(image, text or "", user_id)
    except Exception as e:
        print(f"画像処理エラー: {e}")
        return None, image_source

async def process_generated_image_for_storage(generated_image, text: str, user_id: str) -> Tuple[Optional[str], str]:
    """生成済み画像の保存処理"""
    if not text or not generated_image:
        return None, "generate"

    try:
        # 生成時のファイル名を保持（FileManager.create_filenameで整理済み）
        from infrastructures.file_manager import FileManager
        filename = FileManager.create_filename(text)
        filename_base = os.path.splitext(filename)[0]

        # クエリー・サーチ間の重複チェック
        query_path = f"api/query_image/{filename_base}.jpg"
        search_path = f"api/search_image/{filename_base}.jpg"

        query_exists = await _storage_repo.check_blob_exists(query_path)
        search_exists = await _storage_repo.check_blob_exists(search_path)

        if query_exists:
            return query_path, "suggested"
        if search_exists:
            return search_path, "suggested"

        # 両方にない場合のみサーチに保存
        from io import BytesIO
        image_bytes = BytesIO()
        generated_image.save(image_bytes, format='JPEG')
        image_data = image_bytes.getvalue()

        if await _storage_repo.save_blob(image_data, search_path):
            return search_path, "generate"

        return None, "generate"

    except Exception as e:
        print(f"生成画像保存エラー: {e}")
        return None, "generate"
