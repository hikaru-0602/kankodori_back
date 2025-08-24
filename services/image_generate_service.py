# 画像生成コード．一回につき0.03$ほど

import os
from dotenv import load_dotenv
from typing import Optional
from PIL import Image
from infrastructures.translation_client import translate_to_english
from infrastructures.huggingface_client import get_huggingface_client
from infrastructures.file_manager import FileManager

# .envから環境変数読み込み
load_dotenv()

def create_enhanced_prompt(user_input: str) -> str:
    """
    プロンプトを拡張・翻訳する（ビジネスロジック）

    Args:
        user_input: ユーザー入力プロンプト

    Returns:
        拡張・翻訳されたプロンプト
    """
    enhanced_prompt = f"{user_input}，このプロンプトに基づいて写真で撮影したようなリアルな風景画像を出力してください。人物は絶対に映してはいけません。"
    english_prompt = translate_to_english(enhanced_prompt)
    return english_prompt

async def check_existing_image_in_storage(filename: str) -> Optional[str]:
    """
    Firebase Storageのクエリー・サーチディレクトリで既存画像をチェック

    Args:
        filename: チェックするファイル名

    Returns:
        見つかった画像のパス（なければNone）
    """
    from firebase_admin import storage

    try:
        bucket = storage.bucket()
        extensions = ['.jpg', '.jpeg', '.png', '.webp']

        # filename から拡張子を除去
        base_name = os.path.splitext(filename)[0]

        # api/query_image → api/search_image の順で検索
        for folder in ["api/query_image", "api/search_image"]:
            for ext in extensions:
                blob_path = f"{folder}/{base_name}{ext}"
                blob = bucket.blob(blob_path)
                if blob.exists():
                    print(f"既存画像発見 ({folder}): {blob_path}")
                    return blob_path
        return None

    except Exception as e:
        print(f"Firebase Storage画像チェックエラー: {e}")
        return None

async def load_image_from_storage(blob_path: str) -> Optional[Image.Image]:
    """
    Firebase Storageから画像を読み込み

    Args:
        blob_path: Firebase Storageのパス

    Returns:
        PIL Image オブジェクト（失敗時はNone）
    """
    from firebase_admin import storage
    from io import BytesIO

    try:
        bucket = storage.bucket()
        blob = bucket.blob(blob_path)

        image_bytes = BytesIO()
        blob.download_to_file(image_bytes)
        image_bytes.seek(0)

        return Image.open(image_bytes)

    except Exception as e:
        print(f"Firebase Storage画像読み込みエラー: {e}")
        return None

async def image_generate(prompt: str) -> Optional[Image.Image]:
    """
    画像を生成する（ビジネスロジック層）

    Args:
        prompt: 生成プロンプト

    Returns:
        生成された画像（失敗時はNone）
    """
    try:
        # 1. ファイル名を生成
        filename = FileManager.create_filename(prompt)

        # 2. Firebase Storageで既存画像チェック（クエリー・サーチ両方）
        existing_path = await check_existing_image_in_storage(filename)
        if existing_path:
            existing_image = await load_image_from_storage(existing_path)
            if existing_image:
                print(f"既存画像を使用: {existing_path}")
                return existing_image

        # 3. ローカルキャッシュチェック
        script_dir = FileManager.get_script_directory()
        parent_dir = os.path.dirname(script_dir)
        images_dir = FileManager.setup_directory(parent_dir, ["api", "query_wait"])
        output_path = os.path.join(images_dir, filename)

        if FileManager.file_exists(output_path):
            existing_image = FileManager.load_image(output_path)
            if existing_image:
                print(f"ローカルキャッシュを使用: {output_path}")
                return existing_image

        # 4. プロンプト処理
        english_prompt = create_enhanced_prompt(prompt)

        # 5. 画像生成
        print(f"新規画像生成開始: {prompt}")
        hf_client = get_huggingface_client()
        image = hf_client.generate_image(english_prompt)
        if image is None:
            return None

        # 6. ローカルキャッシュに保存
        if FileManager.save_image(image, output_path):
            print(f"ローカルキャッシュに保存: {output_path}")
            return image
        else:
            return None

    except Exception as e:
        print(f"画像生成サービスエラー: {e}")
        return None
