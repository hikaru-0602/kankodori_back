from typing import List, Dict, Any, Optional, Union
from fastapi import UploadFile
from repositories.storage_repository import StorageRepository
from services.similarity_service import image_similarity_sort
from infrastructures.image_downloader import download_image_from_url
from infrastructures.vit_vectorizer import process_image, extract_features

# モジュールレベルでシングルトンインスタンスを保持
_storage_repo = StorageRepository()

async def image_caluculate(image: Union[UploadFile, str, None], filtered_data: Optional[List[Dict[str, Any]]] = None):
    # imageがNoneの場合は空の結果を返す
    if image is None:
        return []

    # 1. 画像データを読み込み
    if isinstance(image, str):
        # URL文字列の場合
        image_data = await download_image_from_url(image)
        if image_data is None:
            print(f"画像URLからのダウンロード失敗: {image}")
            return []
    elif hasattr(image, 'read'):
        # UploadFileの場合
        image_data = await image.read()
    else:
        # PIL.Imageの場合（image_generateから返された）
        import io
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_data = buffer.getvalue()

    # 2. infrastructures.vit_vectorizerを使用して画像からベクトルを抽出
    # 2-1. 画像の前処理
    inputs = process_image(image_data)
    if inputs is None:
        return []

    # 2-2. 特徴量抽出
    vector = extract_features(inputs)

    if vector is None:
        return []

    # filtered_dataがない場合はget_photo_dataから取得
    if filtered_data is None:
        filtered_data = await _storage_repo.get_photo_data()
        if not filtered_data:
            print("photo_dataの取得に失敗しました")
            return []

    # 3. npyファイルから特徴量データを取得
    result = await _storage_repo.get_feature_with_labels("vit.npy")
    if result is None:
        print("特徴量データの取得に失敗しました")
        return []

    features, labels = result

    # 4. コサイン類似度を計算してソート
    similarity_results = image_similarity_sort(filtered_data, vector, features, labels)

    return similarity_results
