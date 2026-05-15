from services.keyword_filter_service import keyword
from infrastructures.bert_vectorizer import vectorize_text as text_vector
from services.firebase_service import get_feature
from services.similarity_service import similarity_sort


async def text_caluculate(text: str):
    # 1. 形態素解析 + 地名フィルタリング
    filtered_data = await keyword(text)

    # 2. テキストベクトル化（Sentence-BERT）
    vector = text_vector(text)
    if vector is None:
        print("テキストベクトル化に失敗しました")
        return [], filtered_data

    # 3. npyファイルからベクトルデータ取得（Sentence-BERT用）
    features, labels = await get_feature('sentence_bert_ja_mean_ver2.npy')
    if features is None or labels is None:
        print("特徴量データの取得に失敗しました")
        return [], filtered_data

    # 4. コサイン類似度計算とソート
    similarity_results = similarity_sort(filtered_data, vector, features, labels)

    return similarity_results, filtered_data
