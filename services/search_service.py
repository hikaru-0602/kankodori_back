from typing import Optional, List, Dict, Any
from fastapi import UploadFile
from services.text_generate_service import text_generate
from services.image_generate_service import image_generate
from services.text_service import text_calucute


async def search_tourist_spots(
    text: Optional[str] = None,
    image: Optional[UploadFile] = None,
    range: int = 50
) -> Dict[str, Any]:
    if range < 100 and not text:
        text = await text_generate(image)

    if range > 0 and not image:
        image = await image_generate(text)

    if range == 0:
        me = await text_calucute(text)
        return {"results": text}
    elif range > 0 and range < 100:
        return {"results": "複合"}
    else:
        return {"results": "画像のみ"}


async def get_suggested_images() -> Dict[str, List[str]]:
    """
    画像提案処理

    Returns:
        提案画像リスト
    """
    # TODO: 実際の画像データベース連携
    suggested_images = [
        "img_001",
        "img_002",
        "img_003",
        "img_004",
        "img_005",
        "img_006"
    ]

    return {"suggested_images": suggested_images}
