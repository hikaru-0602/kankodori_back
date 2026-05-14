import numpy as np
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# 環境変数からモデルタイプを取得（デフォルトは'bert'）
# 設定方法:
#   - BERTモデルを使用: BERT_MODEL_TYPE=bert (デフォルト)
#   - Sentence-BERTモデルを使用: BERT_MODEL_TYPE=sentence-bert
# .envファイルまたは環境変数で設定可能
MODEL_TYPE = os.environ.get('BERT_MODEL_TYPE', 'bert').lower()  # 'bert' または 'sentence-bert'


class BertVectorizer:
    """日本語BERT/Sentence-BERTモデルを使用したテキストベクトル化クラス"""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_type = MODEL_TYPE
        self._is_initialized = False

    def _initialize_model(self):
        """BERT/Sentence-BERTモデルを初期化"""
        if not self._is_initialized:
            try:
                import os

                if self.model_type == 'sentence-bert':
                    # Sentence-BERTモデルの初期化
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
                else:
                    # BERTモデルの初期化（デフォルト）
                    model_path = '/app/models/bert_initialized.pth'
                    if os.path.exists(model_path):
                        print("事前初期化済みBERTモデルを読み込み中...")
                        saved_data = torch.load(model_path, map_location='cpu', weights_only=False)
                        self.model = saved_data['model']
                        self.tokenizer = saved_data['tokenizer']
                        print("事前初期化済みBERTモデルの読み込み完了")
                    else:
                        print("BERTモデルをダウンロード中...")
                        model_name = 'cl-tohoku/bert-base-japanese-whole-word-masking'
                        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                        self.model = AutoModel.from_pretrained(model_name)
                        self.model.eval()  # 推論モードに設定
                        print("BERTモデルのダウンロード完了")

                self._is_initialized = True
                print(f"使用モデルタイプ: {self.model_type}")

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
            # モデル初期化
            self._initialize_model()

            if not text or not text.strip():
                print("空のテキストが入力されました")
                return None

            if self.model_type == 'sentence-bert':
                # Sentence-BERTでエンコード（類似度計算に最適化された埋め込み）
                vector = self.model.encode(text, convert_to_numpy=True)
            else:
                # BERTモデルでエンコード
                # テキストをトークン化
                inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512, padding=True)

                # モデルでエンコード
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # 最後の隠れ層の平均を取る（mean pooling）
                    # outputs.last_hidden_stateの形状: [batch_size, seq_len, hidden_size]
                    # attention_maskを使って有効なトークンのみを平均
                    attention_mask = inputs['attention_mask']
                    # attention_maskを拡張して形状を合わせる
                    attention_mask_expanded = attention_mask.unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
                    # 有効なトークンの合計
                    sum_embeddings = torch.sum(outputs.last_hidden_state * attention_mask_expanded, dim=1)
                    sum_mask = torch.clamp(attention_mask_expanded.sum(dim=1), min=1e-9)
                    # 平均を計算
                    vector = (sum_embeddings / sum_mask).squeeze().cpu().numpy()

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
