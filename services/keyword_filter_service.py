from typing import List, Dict, Any, Set
from infrastructures.mecab_tokenizer import extract_keywords
from services.firebase_service import get_photo_data


async def keyword(text: str) -> List[Dict[str, Any]]:
    """
    形態素解析でキーワードを抽出し、地名でフィルタリングした結果を返す

    Args:
        text: 解析対象のテキスト

    Returns:
        地名でフィルタリングされたデータリスト
    """
    # 抽出対象の品詞
    target_pos = ["名詞", "形容詞", "動詞", "形容動詞", "形状詞"]

    # 形態素解析実行
    keywords = extract_keywords(text, target_pos)

    # 重複削除
    keywords = list(set(keywords))

    # データ取得
    photo_data = await get_photo_data()
    if not photo_data:
        print("photo_dataが取得できませんでした")
        return []

    # 地名フィルタリング
    filtered_data = filter_location(keywords, photo_data)

    return filtered_data


def filter_location(keywords: List[str], data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

    # 3. 一致する地名がない場合は元のデータをそのまま返す
    if not filtered_data:
        return data

    return filtered_data
