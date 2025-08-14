import torch
import numpy as np
from transformers import BertTokenizer, BertModel
from typing import Optional


class BertVectorizer:
    """日本語BERTモデルを使用したテキストベクトル化クラス"""

    def __init__(self):
        self.tokenizer = None
        self.model = None
        self._is_initialized = False

    def _initialize_model(self):
        """BERTモデルとトークナイザーを初期化"""
        if not self._is_initialized:
            print("日本語BERTモデルを初期化中...")
            try:
                model_name = 'cl-tohoku/bert-base-japanese-whole-word-masking'
                self.tokenizer = BertTokenizer.from_pretrained(model_name)
                self.model = BertModel.from_pretrained(model_name)

                # 評価モードに設定
                self.model.eval()

                self._is_initialized = True
                print("日本語BERTモデルの初期化が完了しました")

            except Exception as e:
                print(f"BERTモデル初期化エラー: {e}")
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

            # テキストをトークン化
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                max_length=512,
                truncation=True,
                padding=True
            )

            # ベクトル化実行
            with torch.no_grad():
                outputs = self.model(**inputs)

                # [CLS]トークンの出力を使用（文全体の表現）
                cls_embedding = outputs.last_hidden_state[:, 0, :]

                # numpy配列に変換して返却
                vector = cls_embedding.squeeze().cpu().numpy()

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
