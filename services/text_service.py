from services.mecab import keyword
from services.bert import text_vector

async def text_caluculate(text: str):
    # 1. 形態素解析 + 地名フィルタリング（mecab.pyで実行）
    filtered_data = await keyword(text)

    # 2. テキストベクトル化
    vector = text_vector(text)

    return filtered_data
