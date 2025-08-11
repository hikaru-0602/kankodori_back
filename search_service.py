from typing import Optional, List, Dict, Any
from fastapi import UploadFile


async def search_tourist_spots(
    text: Optional[str] = None,
    image: Optional[UploadFile] = None,
    range: int = 50
) -> Dict[str, Any]:
    if range == 0:
        return {"results": ["text"]}
    elif range == 100:
        return {"results": ["image"]}
    else:
        return {"results": ["text", "image"]}

    return response


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
