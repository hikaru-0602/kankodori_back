import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional, List
from PIL import Image
import requests
from io import BytesIO


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
                    #model_name = 'cl-tohoku/bert-base-japanese-whole-word-masking'
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

    def vectorize_image(self, image_url: str) -> Optional[np.ndarray]:
        """
        画像URLから画像をダウンロードしてベクトル化する

        Args:
            image_url: 画像のURL

        Returns:
            768次元のベクトル（失敗時はNone）
        """
        try:
            # モデル初期化
            self._initialize_model()

            # 画像をダウンロード
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # PILで画像を開く
            image = Image.open(BytesIO(response.content))

            # CLIPモデルがあるか確認（画像エンコーディング用）
            # Sentence-BERTは基本的にテキスト用なので、CLIPベースのモデルを使用
            try:
                from sentence_transformers import SentenceTransformer
                # 日本語対応のCLIPモデルを使用
                if not hasattr(self, 'clip_model'):
                    print("CLIPモデルをダウンロード中...")
                    self.clip_model = SentenceTransformer('sonoisa/clip-vit-b-32-japanese')
                    print("CLIPモデルのダウンロード完了")

                # 画像をエンコード
                vector = self.clip_model.encode(image, convert_to_numpy=True)
                return vector

            except ImportError:
                # CLIPモデルが利用できない場合は、画像をテキストとして扱う簡易的な方法
                print("CLIPモデルが利用できません。画像URLをテキストとしてベクトル化します。")
                return self.vectorize_text(image_url)

        except requests.RequestException as e:
            print(f"画像ダウンロードエラー: {e}")
            return None
        except Exception as e:
            print(f"画像ベクトル化エラー: {e}")
            return None

    def vectorize_images(self, image_urls: List[str]) -> List[Optional[np.ndarray]]:
        """
        複数の画像URLをベクトル化する

        Args:
            image_urls: 画像URLのリスト

        Returns:
            ベクトルのリスト（失敗した画像はNone）
        """
        vectors = []
        for url in image_urls:
            vector = self.vectorize_image(url.strip())
            vectors.append(vector)
        return vectors


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

def vectorize_image(image_url: str) -> Optional[np.ndarray]:
    """
    画像URLをベクトル化する便利関数

    Args:
        image_url: 画像のURL

    Returns:
        768次元のベクトル（失敗時はNone）
    """
    vectorizer = get_bert_vectorizer()
    return vectorizer.vectorize_image(image_url)

def vectorize_images(image_urls: List[str]) -> List[Optional[np.ndarray]]:
    """
    複数の画像URLをベクトル化する便利関数

    Args:
        image_urls: 画像URLのリスト

    Returns:
        ベクトルのリスト（失敗した画像はNone）
    """
    vectorizer = get_bert_vectorizer()
    return vectorizer.vectorize_images(image_urls)
