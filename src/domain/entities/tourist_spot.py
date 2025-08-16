from dataclasses import dataclass


@dataclass
class TouristSpot:
    """観光地エンティティ - 既存の実装に合わせた最小限のビジネスオブジェクト"""
    id: str
    name: str
    location: str
    similarity: float

    def calculate_weighted_similarity(
        self,
        text_similarity: float,
        image_similarity: float,
        text_weight: float
    ) -> float:
        """重み付きの類似度を計算する（integrate_similarities関数のロジック）"""
        image_weight = 1.0 - text_weight
        return text_similarity * text_weight + image_similarity * image_weight
