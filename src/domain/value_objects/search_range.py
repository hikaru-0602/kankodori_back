from dataclasses import dataclass


@dataclass(frozen=True)
class SearchRange:
    """検索範囲値オブジェクト - 既存のintegrate_similarities関数のrange_value処理に対応"""
    value: int

    def __post_init__(self):
        if not 0 <= self.value <= 100:
            raise ValueError("検索範囲は0から100の間である必要があります")

    def get_text_weight(self) -> float:
        """テキストの重みを取得する（既存のtext_weight計算ロジック）"""
        return self.value * 0.01

    def get_image_weight(self) -> float:
        """画像の重みを取得する（既存のimage_weight計算ロジック）"""
        return 1.0 - self.get_text_weight()
