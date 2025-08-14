import numpy as np
from typing import Optional
from infrastructures.bert_vectorizer import vectorize_text


def text_vector(text: str) -> Optional[np.ndarray]:
    """
    テキストをベクトル化する

    Args:
        text: ベクトル化するテキスト

    Returns:
        768次元のベクトル（失敗時はNone）
    """
    if not text or not text.strip():
        return None

    try:
        vector = vectorize_text(text)
        return vector
    except Exception as e:
        print(f"テキストベクトル化エラー: {e}")
        return None
