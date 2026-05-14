import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from typing import Optional
import os


class SentenceBertVectorizer:
    """日本語Sentence-BERTモデルを使用したテキストベクトル化クラス"""

    def __init__(self):
        self.model = None
        self._is_initialized = False

    def _initialize_model(self):
        """Sentence-BERTモデルを初期化"""
        if not self._is_initialized:
            try:
                model_path = '/app/models/sbert_initialized.pth'
                if os.path.exists(model_path):
                    print("事前初期化済みSentence-BERTモデルを読み込み中...")
                    saved_data = torch.load(model_path, map_location='cpu', weights_only=False)
                    self.model = saved_data['model']
                    print("事前初期化済みSentence-BERTモデルの読み込み完了")
                else:
                    print("Sentence-BERTモデルをダウンロード中...")
                    model_name = 'sonoisa/sentence-bert-base-ja-mean-tokens-v2'
                    self.model = SentenceTransformer(model_name)
                    print("Sentence-BERTモデルのダウンロード完了")

                self._is_initialized = True

            except Exception as e:
                print(f"モデル初期化エラー: {e}")
                raise e

    def vectorize_text(self, text: str) -> Optional[np.ndarray]:
        """
        テキストをベクトル化する

        Args:
            text: ベクトル化するテキスト

        Returns:
            768次元のベクトル（失敗時はNone）
        """
        try:
            self._initialize_model()

            if not text or not text.strip():
                print("空のテキストが入力されました")
                return None

            vector = self.model.encode(text, convert_to_numpy=True)
            return vector

        except Exception as e:
            print(f"テキストベクトル化エラー: {e}")
            return None


# シングルトンインスタンス
_sbert_vectorizer = SentenceBertVectorizer()

def get_bert_vectorizer() -> SentenceBertVectorizer:
    """Sentence-BERTベクトライザーのシングルトンインスタンスを取得"""
    return _sbert_vectorizer

def vectorize_text(text: str) -> Optional[np.ndarray]:
    """
    テキストをベクトル化する便利関数

    Args:
        text: ベクトル化するテキスト

    Returns:
        768次元のベクトル（失敗時はNone）
    """
    vectorizer = get_bert_vectorizer()
    return vectorizer.vectorize_text(text)
