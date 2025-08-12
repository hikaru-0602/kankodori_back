from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from services.search_service import search_tourist_spots as search_service, get_suggested_images


async def search_tourist_spots(
    text: Optional[str] = None,
    image: Optional[UploadFile] = None,
    search_range: int = 50
) -> Dict[str, Any]:
    """
    観光地検索の処理

    Args:
        text: 検索テキスト
        image: 検索画像
        search_range: 検索範囲

    Returns:
        検索結果

    Raises:
        HTTPException: 入力パラメータが無効な場合
    """
    # 入力チェック
    if not text and not image:
        raise HTTPException(
            status_code=400,
            detail="text または image のいずれかは必須です"
        )

    return await search_service(text, image, search_range)


async def suggest_images() -> Dict[str, Any]:
    """
    画像提案の処理

    Returns:
        提案画像リスト
    """
    return await get_suggested_images()
