import MeCab
from typing import List, Dict, Any
from services.location_service import filter_location
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

    # MeCabの初期化
    try:
        mecab = MeCab.Tagger()
    except RuntimeError as e:
        print(f"MeCab初期化エラー: {e}")
        return []

    keywords = []

    # 形態素解析実行
    node = mecab.parseToNode(text)

    while node:
        features = node.feature.split(',')
        if len(features) > 0:
            pos = features[0]  # 主品詞
            surface = node.surface  # 表層形

            # 指定した品詞かつ有効な単語の場合
            if pos in target_pos and surface and len(surface) > 1:
                keywords.append(surface)

        node = node.next

    # 重複削除
    keywords = list(set(keywords))
    print(f"抽出されたキーワード: {keywords}")

    # データ取得
    photo_data = await get_photo_data()
    if not photo_data:
        print("photo_dataが取得できませんでした")
        return []

    # 地名フィルタリング
    filtered_data = filter_location(keywords, photo_data)

    return filtered_data
