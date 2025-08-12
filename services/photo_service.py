import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Optional, List, Any
from repositories.firebase_repository import FirebaseDataManager


class PhotoService:
    """写真データ関連のビジネスロジック"""

    def __init__(self):
        self.firebase_manager = FirebaseDataManager()

    async def get_photo_data(self) -> Optional[List[Any]]:
        """
        place_data.json内のphoto配列を取得

        Returns:
            photo配列、取得失敗時はNone
        """
        try:
            place_data = await self.firebase_manager.get_place_data()
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