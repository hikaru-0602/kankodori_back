from typing import List, Dict, Any, Optional
from fastapi import UploadFile
from services.vit import get_image_vector
from services.firebase_service import get_feature, get_photo_data
from services.similarity_service import similarity_sort

async def image_caluculate(image: UploadFile, filtered_data: Optional[List[Dict[str, Any]]] = None):
    # 1. 画像データを読み込み
    image_data = await image.read()

    # 2. vit.pyを使用して画像からベクトルを抽出
    vector = get_image_vector(image_data)

    if vector is None:
        return []

    # filtered_dataがない場合はget_photo_dataから取得
    if filtered_data is None:
        filtered_data = await get_photo_data()

    # 3. npyファイルから特徴量データを取得
    features, labels = await get_feature("vit.npy")

    # 4. コサイン類似度を計算してソート
    similarity_results = similarity_sort(filtered_data, vector, features, labels)

    return similarity_results
