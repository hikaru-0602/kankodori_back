import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional


class BertVectorizer:
    """日本語Sentence-BERTモデルを使用したテキストベクトル化クラス"""

    def __init__(self):
        self.model = None
        self._is_initialized = False

    def _initialize_model(self):
        """Sentence-BERTモデルを初期化"""
        if not self._is_initialized:
            try:
                # 事前初期化済みモデルがあれば使用
                import os
                if os.path.exists('/app/models/sbert_initialized.pth'):
                    print("事前初期化済みSentence-BERTモデルを読み込み中...")
                    import torch
                    saved_data = torch.load('/app/models/sbert_initialized.pth', map_location='cpu', weights_only=False)
                    self.model = saved_data['model']
                    print("事前初期化済みSentence-BERTモデルの読み込み完了")
                else:
                    # 日本語のSentence-BERTモデルをダウンロード
                    print("Sentence-BERTモデルをダウンロード中...")
                    # sonoisa/sentence-bert-base-ja-mean-tokens-v2 は日本語に特化した高性能モデル
                    model_name = 'sonoisa/sentence-bert-base-ja-mean-tokens-v2'
                    self.model = SentenceTransformer(model_name)
                    print("Sentence-BERTモデルのダウンロード完了")

                self._is_initialized = True

            except Exception as e:
                print(f"Sentence-BERTモデル初期化エラー: {e}")
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
            # モデル初期化
            self._initialize_model()

            if not text or not text.strip():
                print("空のテキストが入力されました")
                return None

            # Sentence-BERTでエンコード（類似度計算に最適化された埋め込み）
            vector = self.model.encode(text, convert_to_numpy=True)

            return vector

        except Exception as e:
            print(f"テキストベクトル化エラー: {e}")
            return None


# シングルトンインスタンス
_bert_vectorizer = BertVectorizer()

def get_bert_vectorizer() -> BertVectorizer:
    """BERTベクトライザーのシングルトンインスタンスを取得"""
    return _bert_vectorizer

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
