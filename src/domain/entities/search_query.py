from typing import Optional
from dataclasses import dataclass
from fastapi import UploadFile


@dataclass
class SearchQuery:
    """検索クエリエンティティ - 既存のsearch_tourist_spots関数の引数に対応"""
    text: Optional[str] = None
    image: Optional[UploadFile] = None
    range_value: int = 50

    def requires_text_generation(self) -> bool:
        """テキスト生成が必要かどうかを判定する（既存ロジック）"""
        return self.range_value < 100 and self.text is None

    def requires_image_generation(self) -> bool:
        """画像生成が必要かどうかを判定する（既存ロジック）"""
        return self.range_value > 0 and self.image is None

    def get_search_strategy(self) -> str:
        """検索戦略を取得する（既存のrange値判定ロジック）"""
        if self.range_value == 0:
            return "text_only"
        elif self.range_value == 100:
            return "image_only"
        else:
            return "hybrid"
