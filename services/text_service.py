from services.mecab import extract_keywords_only
from infrastructures.bert_vectorizer import vectorize_text

async def text_caluculate(text: str):
    # 1. 形態素解析 + 地名フィルタリング（mecab.pyで実行）
    filtered_data = await extract_keywords_only(text)

    # 2. テキストベクトル化
    text_vector = vectorize_text(text)
    if text_vector is None:
        print("テキストのベクトル化に失敗しました")
        return filtered_data  # ベクトル化失敗でも地名フィルタリング結果は返す

    # TODO: 後でベクトル類似度計算を追加
    print(f"入力テキストのベクトル形状: {text_vector.shape}")

    return filtered_data
