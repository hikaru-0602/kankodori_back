from services.mecab import keyword
from services.bert import text_vector
from services.firebase_service import get_feature
from services.similarity_service import similarity_sort

async def image_caluculate(text: str):
    # 1. 形態素解析 + 地名フィルタリング（mecab.pyで実行）
    filtered_data = await keyword(text)

    # 2. テキストベクトル化
    vector = text_vector(text)

    # 3. npyファイルからベクトルデータ取得
    features, labels = await get_feature("vit.npy")

    # 4. コサイン類似度計算とソート
    similarity_results = similarity_sort(filtered_data, vector, features, labels)

    return similarity_results, filtered_data
