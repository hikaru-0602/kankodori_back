import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity_ranking(
    filtered_data: List[Dict[str, Any]],
    query_vector: np.ndarray,
    features: np.ndarray,
    labels: List[str]
) -> List[Tuple[Dict[str, Any], float]]:
    """
    フィルタリングされたデータとクエリベクトル間のコサイン類似度を計算し、ソートする

    Args:
        filtered_data: 地名でフィルタリングされたデータリスト
        query_vector: クエリテキストのベクトル
        features: npyファイルから取得したベクトル配列
        labels: ベクトルに対応するIDリスト

    Returns:
        類似度の高い順にソートされた(データ, 類似度)のタプルリスト
    """
    if not filtered_data or query_vector is None:
        return []

    similarities = []

    # filtered_dataのIDリストを作成
    filtered_ids = [item.get('id') for item in filtered_data]

    # featuresとlabelsを同時にループ
    for i, (feature_vector, label_id) in enumerate(zip(features, labels)):
        # filtered_dataに含まれるIDかチェック
        if label_id in filtered_ids:
            # 対応するitemを取得
            item = next(item for item in filtered_data if item.get('id') == label_id)

            try:
                # コサイン類似度計算
                similarity = cosine_similarity([query_vector], [feature_vector])[0][0]
                similarities.append((item, similarity))
                print(f"類似度計算成功 (ID: {label_id}): {similarity}")

            except Exception as e:
                print(f"類似度計算エラー (ID: {label_id}): {e}")
                continue

    # 類似度の高い順にソート
    sorted_results = sorted(similarities, key=lambda x: x[1], reverse=True)

    print(f"類似度計算完了: {len(sorted_results)}件")
    return sorted_results
