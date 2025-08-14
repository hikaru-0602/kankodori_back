from services.mecab import extract_keywords_only
from services.firebase_service import get_photo_data

async def text_calucute(text: str):
    # 1. キーワード抽出
    keywords = extract_keywords_only(text)

    # 2. データ取得
    photo_data = await get_photo_data()
    if not photo_data:
        return []

    # 3. 地名フィルタリング
    filtered_data = []
    matched_locations = set()

    for data in photo_data:
        location = data.get('location', '')

        # 2文字以上のキーワードで地名マッチング
        for keyword in keywords:
            if len(keyword) >= 2 and keyword in location:
                matched_locations.add(location)
                break

    # 4. マッチした地名のデータをすべて収集
    for data in photo_data:
        if data.get('location') in matched_locations:
            filtered_data.append(data)

    return filtered_data
