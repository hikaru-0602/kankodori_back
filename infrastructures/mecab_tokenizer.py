import MeCab
from typing import List


class MeCabTokenizer:
    """MeCabを使用したトークン化クラス"""

    def __init__(self):
        self.mecab = None
        self._is_initialized = False

    def _initialize_mecab(self):
        """MeCabを初期化"""
        if not self._is_initialized:
            try:
                self.mecab = MeCab.Tagger()
                self._is_initialized = True
            except RuntimeError as e:
                print(f"MeCab初期化エラー: {e}")
                raise e

    def extract_keywords(self, text: str, target_pos: List[str]) -> List[str]:
        """
        形態素解析でキーワードを抽出

        Args:
            text: 解析対象のテキスト
            target_pos: 抽出対象の品詞リスト

        Returns:
            キーワードのリスト
        """
        try:
            self._initialize_mecab()

            keywords = []

            # 形態素解析実行
            node = self.mecab.parseToNode(text)

            while node:
                features = node.feature.split(',')
                if len(features) > 0:
                    pos = features[0]  # 主品詞
                    surface = node.surface  # 表層形

                    # 指定した品詞かつ有効な単語の場合（1文字でもOK）
                    if pos in target_pos and surface and len(surface) >= 1:
                        keywords.append(surface)

                node = node.next

            return keywords

        except Exception as e:
            print(f"形態素解析エラー: {e}")
            return []


# シングルトンインスタンス
_mecab_tokenizer = MeCabTokenizer()

def get_mecab_tokenizer() -> MeCabTokenizer:
    """MeCabトークナイザーのシングルトンインスタンスを取得"""
    return _mecab_tokenizer

def extract_keywords(text: str, target_pos: List[str]) -> List[str]:
    """
    形態素解析でキーワードを抽出する便利関数

    Args:
        text: 解析対象のテキスト
        target_pos: 抽出対象の品詞リスト

    Returns:
        キーワードのリスト
    """
    tokenizer = get_mecab_tokenizer()
    return tokenizer.extract_keywords(text, target_pos)
