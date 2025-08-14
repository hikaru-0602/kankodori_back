import torch
import numpy as np
from PIL import Image
from transformers import ViTImageProcessor, ViTModel
from typing import Optional
import io


class ViTVectorizer:
    """Vision Transformerを使用した画像ベクトル化クラス"""

    def __init__(self):
        self.processor = None
        self.model = None
        self._is_initialized = False

    def _initialize_model(self):
        """ViTモデルとプロセッサを初期化"""
        if not self._is_initialized:
            print("ViTモデルを初期化中...")
            try:
                model_name = 'google/vit-base-patch16-224'
                self.processor = ViTImageProcessor.from_pretrained(model_name)
                self.model = ViTModel.from_pretrained(model_name)

                # 評価モードに設定
                self.model.eval()

                self._is_initialized = True
                print("ViTモデルの初期化が完了しました")

            except Exception as e:
                print(f"ViTモデル初期化エラー: {e}")
                raise e

    def process_image(self, image_data: bytes) -> Optional[torch.Tensor]:
        """
        画像データを前処理してテンソルを返す

        Args:
            image_data: 画像のバイトデータ

        Returns:
            前処理済みのテンソル（失敗時はNone）
        """
        try:
            # モデル初期化
            self._initialize_model()

            if not image_data:
                print("空の画像データが入力されました")
                return None

            # バイトデータをPIL Imageに変換
            image = Image.open(io.BytesIO(image_data))

            # RGBに変換（グレースケールやRGBAの場合）
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # 画像を前処理
            inputs = self.processor(images=image, return_tensors="pt")

            return inputs

        except Exception as e:
            print(f"画像前処理エラー: {e}")
            return None

    def extract_features(self, inputs: torch.Tensor) -> Optional[np.ndarray]:
        """
        前処理済みテンソルからベクトルを抽出

        Args:
            inputs: 前処理済みテンソル

        Returns:
            768次元のベクトル（失敗時はNone）
        """
        try:
            self._initialize_model()

            # ベクトル化実行
            with torch.no_grad():
                outputs = self.model(**inputs)

                # [CLS]トークンの出力を使用（画像全体の表現）
                cls_embedding = outputs.last_hidden_state[:, 0, :]

                # numpy配列に変換して返却
                vector = cls_embedding.squeeze().cpu().numpy()

                return vector

        except Exception as e:
            print(f"特徴量抽出エラー: {e}")
            return None


# シングルトンインスタンス
_vit_vectorizer = ViTVectorizer()

def get_vit_vectorizer() -> ViTVectorizer:
    """ViTベクトライザーのシングルトンインスタンスを取得"""
    return _vit_vectorizer

def process_image(image_data: bytes) -> Optional[torch.Tensor]:
    """
    画像を前処理する便利関数

    Args:
        image_data: 画像のバイトデータ

    Returns:
        前処理済みのテンソル（失敗時はNone）
    """
    vectorizer = get_vit_vectorizer()
    return vectorizer.process_image(image_data)

def extract_features(inputs: torch.Tensor) -> Optional[np.ndarray]:
    """
    特徴量を抽出する便利関数

    Args:
        inputs: 前処理済みテンソル

    Returns:
        768次元のベクトル（失敗時はNone）
    """
    vectorizer = get_vit_vectorizer()
    return vectorizer.extract_features(inputs)
