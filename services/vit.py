import numpy as np
from typing import Optional
from infrastructures.vit_vectorizer import process_image, extract_features


def get_image_vector(image_data: bytes) -> Optional[np.ndarray]:
    """
    画像をベクトル化する

    Args:
        image_data: 画像のバイトデータ

    Returns:
        768次元のベクトル（失敗時はNone）
    """
    if not image_data:
        print("空の画像データが入力されました")
        return None

    try:
        # 1. 画像の前処理
        inputs = process_image(image_data)
        if inputs is None:
            return None

        # 2. 特徴量抽出
        vector = extract_features(inputs)

        return vector

    except Exception as e:
        print(f"画像ベクトル化エラー: {e}")
        return None
