import MeCab
from typing import List


def extract_keywords_only(text: str) -> List[str]:
    """
    形態素解析でキーワードを抽出し、重複削除する

    Args:
        text: 解析対象のテキスト

    Returns:
        抽出されたキーワードのリスト（重複削除済み）
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

    # 重複削除して返却
    return list(set(keywords))
