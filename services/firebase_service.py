import numpy as np
from typing import Optional, List, Any, Dict
from repositories.firebase_repository import FirebaseDataManager

# モジュールレベルでシングルトンインスタンスを保持
_firebase_manager = FirebaseDataManager()


async def get_photo_data() -> Optional[List[Any]]:
    """
    place_data.json内のphoto配列を取得

    Returns:
        photo配列、取得失敗時はNone
    """
    try:
        place_data = await _firebase_manager.get_place_data()
        if not place_data:
            return None

        if 'photo' in place_data and isinstance(place_data['photo'], list):
            return place_data['photo']
        else:
            print("photoキーが見つからないか、配列ではありません")
            return None

    except Exception as e:
        print(f"photo_data取得エラー: {e}")
        return None


async def add_query_image(new_item: Dict[str, Any]) -> bool:
    """
    query_imageに新しいアイテムを追加

    Args:
        new_item: 追加するアイテム

    Returns:
        成功時True、失敗時False
    """
    try:
        # ビジネス検証（例：必須フィールドチェック）
        if not new_item.get('id'):
            print("idフィールドが必要です")
            return False

        return await _firebase_manager.append_to_query_image(new_item)
    except Exception as e:
        print(f"query_image追加エラー: {e}")
        return False


async def get_feature(filename: str) -> Optional[tuple[Dict[str, Any], List[str]]]:
    """
    特徴量データとラベルを取得

    Args:
        filename: 特徴量ファイル名

    Returns:
        (特徴量データ, ラベルリスト) のタプル、取得失敗時はNone
    """
    try:
        # ビジネス検証（例：ファイル名形式チェック）
        if not filename.endswith('.npy'):
            filename += '.npy'

        # npyファイルを取得
        raw_data = await _firebase_manager.get_feature_npy(filename)
        if raw_data is None:
            return None

        # 辞書形式でない場合はエラー
        if not isinstance(raw_data, dict):
            print(f"エラー: ロードされたデータは辞書形式ではありません: {filename}")
            return None

        # 特徴量データとラベルを抽出
        features = raw_data
        labels = list(raw_data.keys())

        return features, labels

    except Exception as e:
        print(f"特徴量取得エラー: {e}")
        return None


async def get_api_query_images() -> List[str]:
    """
    API query画像のリストを取得

    Returns:
        画像ファイル名のリスト
    """
    try:
        return await _firebase_manager.list_api_query_images()
    except Exception as e:
        print(f"API query画像リスト取得エラー: {e}")
        return []
