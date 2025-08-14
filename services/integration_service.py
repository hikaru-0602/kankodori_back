from typing import List, Dict, Any


def integrate_similarities(
    text_results: List[Dict[str, Any]],
    image_results: List[Dict[str, Any]],
    range_value: int
) -> List[Dict[str, Any]]:
    """
    テキストと画像の類似度結果をrange値に基づいて統合する

    Args:
        text_results: テキスト類似度結果のリスト [{"id": str, "name": str, "location": str, "similarity": float}, ...]
        image_results: 画像類似度結果のリスト [{"id": str, "similarity": float}, ...]
        range_value: 0-100の範囲値（テキストの重みを決定）

    Returns:
        統合された類似度結果のリスト（類似度の高い順）
    """

    # 重みを計算
    text_weight = range_value * 0.01
    image_weight = 1 - text_weight

    # IDをキーとした辞書に変換（テキスト結果から追加情報も保持）
    text_dict = {item["id"]: item for item in text_results}
    image_dict = {item["id"]: item["similarity"] for item in image_results}

    # 全てのIDを取得
    all_ids = set(text_dict.keys()) | set(image_dict.keys())

    integrated_results = []

    for id_value in all_ids:
        # 各類似度を取得（存在しない場合は0）
        text_item = text_dict.get(id_value)
        text_similarity = text_item["similarity"] if text_item else 0.0
        image_similarity = image_dict.get(id_value, 0.0)

        # 重み付けして統合
        integrated_similarity = (text_similarity * text_weight +
                               image_similarity * image_weight)

        result_item = {
            "id": id_value,
            "similarity": integrated_similarity
        }

        # テキスト結果から追加情報を含める
        if text_item:
            if "name" in text_item:
                result_item["name"] = text_item["name"]
            if "location" in text_item:
                result_item["location"] = text_item["location"]

        integrated_results.append(result_item)

    # 類似度の高い順にソート
    integrated_results.sort(key=lambda x: x["similarity"], reverse=True)

    return integrated_results
