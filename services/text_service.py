from services.mecab import keyword
from services.bert import text_vector
from services.firebase_service import get_feature
from services.similarity_service import similarity_sort
import os
from dotenv import load_dotenv

load_dotenv()

# 環境変数からnpyファイル名を取得（デフォルトは'bert_ja_mean.npy'）
# 設定方法:
#   - BERTモデル用: BERT_NPY_FILE=bert_ja_mean.npy (デフォルト)
#   - Sentence-BERTモデル用: BERT_NPY_FILE=sentence_bert_ja_mean_ver2.npy
# .envファイルまたは環境変数で設定可能
BERT_NPY_FILE = os.environ.get('BERT_NPY_FILE', 'bert_ja_mean.npy')

async def text_caluculate(text: str):
    # 1. 形態素解析 + 地名フィルタリング（mecab.pyで実行）
    filtered_data = await keyword(text)

    # 2. テキストベクトル化
    vector = text_vector(text)

    # 3. npyファイルからベクトルデータ取得
    features, labels = await get_feature(BERT_NPY_FILE)

    # 4. コサイン類似度計算とソート
    similarity_results = similarity_sort(filtered_data, vector, features, labels)

    return similarity_results, filtered_data
