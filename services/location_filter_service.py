from typing import List, Dict, Any, Set


def filter_by_location(keywords: List[str], data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    キーワードによる地名フィルタリング

    Args:
        keywords: 抽出されたキーワードリスト
        data: フィルタリング対象のデータリスト

    Returns:
        地名でフィルタリングされたデータリスト
    """
    if not keywords or not data:
        return []

    filtered_data = []
    matched_locations: Set[str] = set()

    # 1. 地名マッチング
    for item in data:
        location = item.get('location', '')

        # 2文字以上のキーワードで地名マッチング
        for keyword in keywords:
            if len(keyword) >= 2 and keyword in location:
                matched_locations.add(location)
                break

    # 2. マッチした地名のデータをすべて収集
    for item in data:
        if item.get('location') in matched_locations:
            filtered_data.append(item)

    print(f"マッチした地名: {list(matched_locations)}")
    print(f"フィルタリング結果: {len(filtered_data)}件")

    return filtered_data
