# 画像生成コード．一回につき0.03$ほど

import os
from dotenv import load_dotenv
from infrastructures.translation_client import translate_to_english
from infrastructures.huggingface_client import get_huggingface_client

# .envから環境変数読み込み
load_dotenv()

def edit_prompt(user_input):
    """プロンプトに条件を付け加える"""
    add_prompt = f"{user_input}，このプロンプトに基づいて写真で撮影したようなリアルな風景画像を出力してください。人物は絶対に映してはいけません。"
    english_prompt = translate_to_english(add_prompt)
    return english_prompt

async def image_generate(prompt):
    """画像を生成する"""
    try:
        # HuggingFaceクライアント取得
        hf_client = get_huggingface_client()

        # api/query_waitディレクトリのパス設定
        script_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(script_dir, "api", "query_wait")
        os.makedirs(images_dir, exist_ok=True)

        # 元のプロンプトをファイル名にする
        filename = f"{prompt}.jpg"
        output_path = os.path.join(images_dir, filename)

        # すでにファイルが存在する場合は既存画像を読み込んで返す
        if os.path.exists(output_path):
            from PIL import Image
            existing_image = Image.open(output_path)
            return existing_image

        # プロンプト拡張・翻訳
        print(f"元のプロンプト: {prompt}")
        english_prompt = edit_prompt(prompt)
        print(f"拡張・翻訳プロンプト: {english_prompt}")

        # 画像生成
        image = hf_client.generate_image(english_prompt)

        # 画像を保存
        image.save(output_path)
        return image

    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
