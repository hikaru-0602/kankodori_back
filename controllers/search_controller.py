from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from services.search_service import search_tourist_spots as search_service, get_suggested_images


async def search_tourist_spots(
    text: Optional[str] = None,
    image: Optional[UploadFile] = None
) -> Dict[str, Any]:

    # text の undefined/空文字チェック
    if text and (text.strip() == "" or text.strip().lower() == "undefined"):
        text = None

    # image の undefined/空文字チェック
    if image and (not hasattr(image, 'filename') or not image.filename):
        image = None

    # 入力チェック
    if text==None and image==None:
        raise HTTPException(
            status_code=400,
            detail="text または image のいずれかは必須です"
        )

    return await search_service(text, image)


async def suggest_images() -> Dict[str, Any]:
    """
    画像提案の処理

    Returns:
        提案画像リスト
    """
    return await get_suggested_images()
