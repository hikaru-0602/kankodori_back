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

async def image_generate(prompt: str) -> Optional[Image.Image]:
    """
    画像を生成する（ビジネスロジック層）

    Args:
        prompt: 生成プロンプト

    Returns:
        生成された画像（失敗時はNone）
    """
    try:
        # 1. ファイル管理の準備
        script_dir = FileManager.get_script_directory()
        parent_dir = os.path.dirname(script_dir)  # infrastructures の親ディレクトリ
        images_dir = FileManager.setup_directory(parent_dir, ["api", "query_wait"])

        filename = FileManager.create_filename(prompt)
        output_path = os.path.join(images_dir, filename)

        # 2. 既存ファイルチェック（キャッシュ機能）
        if FileManager.file_exists(output_path):
            existing_image = FileManager.load_image(output_path)
            if existing_image:
                return existing_image

        # 3. プロンプト処理
        english_prompt = create_enhanced_prompt(prompt)

        # 4. 画像生成
        hf_client = get_huggingface_client()
        image = hf_client.generate_image(english_prompt)
        if image is None:
            return None

        # 5. 画像保存
        if FileManager.save_image(image, output_path):
            return image
        else:
            return None

    except Exception as e:
        print(f"画像生成サービスエラー: {e}")
        return None
