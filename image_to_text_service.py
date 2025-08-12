from typing import Optional
from fastapi import UploadFile
import torch
from PIL import Image
import io
from infrastructures.bert_client import initialize_blip_model, get_blip_model
from infrastructures.translation_client import translate_to_japanese

async def text_generate(image: UploadFile) -> Optional[str]:
    """
    画像からテキストを生成する（ローカルのBLIPモデルを使用、日本語を返す）

    Args:
        image: アップロードされた画像ファイル

    Returns:
        生成された日本語テキスト（失敗時はNone）
    """
    try:
        # モデル初期化
        initialize_blip_model()
        processor, model = get_blip_model()

        # 画像ファイルを読み取り、PIL Imageに変換
        image_content = await image.read()
        pil_image = Image.open(io.BytesIO(image_content)).convert("RGB")

        # プロセッサーで画像を前処理
        inputs = processor(pil_image, return_tensors="pt")

        # GPUが利用可能な場合は入力もGPUに移動
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}

        # モデルでテキスト生成
        with torch.no_grad():
            output = model.generate(**inputs, max_length=50, num_beams=5)

        # テキストデコード
        generated_text = processor.decode(output[0], skip_special_tokens=True)

        # 日本語に翻訳
        text_ja = translate_to_japanese(generated_text)

        return text_ja  # 日本語のみを返す

    except Exception as e:
        print(f"ローカルモデルでのテキスト生成エラー: {str(e)}")
        return None
    finally:
        # ファイルポインターをリセット
        await image.seek(0)
