import random
from typing import List, Dict
from repositories.storage_repository import StorageRepository

# モジュールレベルでシングルトンインスタンスを保持
_storage_repo = StorageRepository()

async def random_suggest() -> Dict[str, List[str]]:
    """
    get_api_query_images()を呼び出し、その中からランダムで6つを返す

    Returns:
        ランダムに選択された6つの画像IDのリスト
    """
    # 全ての画像データを取得
    all_images = await _storage_repo.list_api_query_images()

    # 6つ以下の場合はそのまま返す
    if len(all_images) <= 6:
        return all_images

    # ランダムで6つ選択
    random_images = random.sample(all_images, 6)

    return random_images
