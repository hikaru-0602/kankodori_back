from deep_translator import GoogleTranslator
from typing import Optional


def translate_text(text: str, target_lang: str, source_lang: str = 'auto') -> Optional[str]:
    """
    テキストを指定言語に翻訳する

    Args:
        text: 翻訳するテキスト
        target_lang: 翻訳先言語 ('ja', 'en' など)
        source_lang: 翻訳元言語 (デフォルト: 'auto'で自動検出)

    Returns:
        翻訳後のテキスト（失敗時は元のテキスト）
    """
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"翻訳エラー: {str(e)}")
        return text


def translate_to_japanese(text: str) -> str:
    """テキストを日本語に翻訳する"""
    return translate_text(text, target_lang='ja')


def translate_to_english(text: str) -> str:
    """テキストを英語に翻訳する"""
    return translate_text(text, target_lang='en')
