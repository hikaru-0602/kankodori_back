import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity_ranking(
    filtered_data: List[Dict[str, Any]],
    query_vector: np.ndarray,
    features: np.ndarray,
    labels: List[str]
) -> List[Dict[str, Any]]:
    """
    フィルタリングされたデータとクエリベクトル間のコサイン類似度を計算し、ソートする

    Args:
        filtered_data: 地名でフィルタリングされたデータリスト
        query_vector: クエリテキストのベクトル
        features: npyファイルから取得したベクトル配列
        labels: ベクトルに対応するIDリスト

    Returns:
        類似度の高い順にソートされた{"id": id, "similarity": similarity}の辞書リスト
    """
    if not filtered_data or query_vector is None:
        return []

    similarities = []

    # filtered_dataのIDリストを作成
    filtered_ids = [item.get('id') for item in filtered_data]

    # labelsをループしてfeaturesから対応するベクトルを取得
    for label_id in labels:
        # filtered_dataに含まれるIDかチェック
        if label_id in filtered_ids:
            # 対応するitemを取得
            item = next(item for item in filtered_data if item.get('id') == label_id)

            # featuresから対応するベクトルを取得
            feature_vector = features.get(label_id)
            if feature_vector is None:
                print(f"ベクトルが見つかりません (ID: {label_id})")
                continue

            try:
                # feature_vectorの形状確認とreshape
                print(f"feature_vector shape: {feature_vector.shape}")
                print(f"query_vector shape: {query_vector.shape}")

                # feature_vectorが1次元の場合は2次元にreshape
                if feature_vector.ndim == 1:
                    feature_vector_2d = feature_vector.reshape(1, -1)
                else:
                    feature_vector_2d = feature_vector

                if query_vector.ndim == 1:
                    query_vector_2d = query_vector.reshape(1, -1)
                else:
                    query_vector_2d = query_vector

                # コサイン類似度計算
                similarity = cosine_similarity(query_vector_2d, feature_vector_2d)[0][0]
                similarities.append({"id": label_id, "similarity": float(similarity)})
                print(f"類似度計算成功 (ID: {label_id}): {similarity}")

            except Exception as e:
                print(f"類似度計算エラー (ID: {label_id}): {e}")
                continue

    # 類似度の高い順にソート
    sorted_results = sorted(similarities, key=lambda x: x["similarity"], reverse=True)

    print(f"類似度計算完了: {len(sorted_results)}件")
    return sorted_results
