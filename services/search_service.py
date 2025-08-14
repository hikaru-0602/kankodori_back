from typing import Optional, List, Dict, Any
from fastapi import UploadFile
from services.text_generate_service import text_generate
from services.image_generate_service import image_generate
from services.text_service import text_caluculate
from services.image_service import image_caluculate
from services.integration_service import integrate_similarities


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
        text_similar = await text_caluculate(text)
        return {"results": text_similar}
    elif range > 0 and range < 100:
        text_similar, filtered_data = await text_caluculate(text)
        image_similar, _ = await image_caluculate(image, filtered_data)

        # テキストと画像の類似度を統合
        integrated_results = integrate_similarities(text_similar, image_similar, range)

        return {"results": integrated_results}
    else:
        image_similar = await image_caluculate(image)
        return {"results": image_similar}


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
