import torch
from PIL import Image
import io
from typing import Optional
from fastapi import UploadFile
from .bert_client import initialize_blip_model, get_blip_model


class ImageProcessor:
    """画像処理を行うインフラ層クラス"""

    @staticmethod
    async def process_uploaded_image(image: UploadFile) -> Optional[Image.Image]:
        """
        アップロードされた画像をPIL Imageに変換
        
        Args:
            image: アップロードされた画像ファイル
            
        Returns:
            PIL Image オブジェクト
        """
        try:
            image_content = await image.read()
            pil_image = Image.open(io.BytesIO(image_content)).convert("RGB")
            return pil_image
        except Exception as e:
            print(f"画像処理エラー: {str(e)}")
            return None
        finally:
            await image.seek(0)

    @staticmethod
    def generate_text_from_image(pil_image: Image.Image) -> Optional[str]:
        """
        PIL ImageからBLIPモデルを使用してテキストを生成
        
        Args:
            pil_image: PIL Image オブジェクト
            
        Returns:
            生成されたテキスト（英語）
        """
        try:
            # モデル初期化と取得
            initialize_blip_model()
            processor, model = get_blip_model()

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
            return generated_text

        except Exception as e:
            print(f"テキスト生成エラー: {str(e)}")
            return None