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
