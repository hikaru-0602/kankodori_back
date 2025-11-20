from typing import List, Dict, Any


def integrate_similarities(
    text_results: List[Dict[str, Any]],
    image_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

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

        result_item = {
            "id": id_value,
            "name": text_item.get("name", "") if text_item else "",
            "location": text_item.get("location", "") if text_item else "",
            "text_similarity": text_similarity,
            "image_similarity": image_similarity
        }

        integrated_results.append(result_item)

    return integrated_results


def integrate_with_weights(
    text_results: List[Dict[str, Any]],
    image_results: List[Dict[str, Any]],
    text_weight: float,
    image_weight: float,
    top_n: int = 1
) -> List[Dict[str, Any]]:
    """
    テキストと画像の類似度を指定した重みで統合し、上位N件を返す

    Args:
        text_results: テキスト検索結果
        image_results: 画像検索結果
        text_weight: テキストの重み（0.0～1.0）
        image_weight: 画像の重み（0.0～1.0）
        top_n: 返す上位N件（デフォルト1）

    Returns:
        統合された検索結果の上位N件
    """
    # IDをキーとした辞書に変換
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

        # 重み付き統合スコアを計算
        integrated_score = (text_similarity * text_weight) + (image_similarity * image_weight)

        result_item = {
            "id": id_value,
            "name": text_item.get("name", "") if text_item else "",
            "location": text_item.get("location", "") if text_item else "",
            "text_similarity": text_similarity,
            "image_similarity": image_similarity,
            "integrated_score": integrated_score
        }

        integrated_results.append(result_item)

    # 統合スコアでソート（降順）
    integrated_results.sort(key=lambda x: x["integrated_score"], reverse=True)

    # 上位N件を返す
    return integrated_results[:top_n]
