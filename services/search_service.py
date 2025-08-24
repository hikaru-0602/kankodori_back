from typing import Optional, List, Dict, Any
from fastapi import UploadFile
from services.text_generate_service import text_generate
from services.image_generate_service import image_generate
from services.text_service import text_caluculate
from services.image_service import image_caluculate
from services.integration_service import integrate_similarities
from services.suggestion_service import random_suggest


async def search_tourist_spots(
    text: Optional[str] = None,
    image: Optional[UploadFile] = None
) -> Dict[str, Any]:
    # 元の入力を記録
    original_text = text
    original_image = image

    text_generated = False
    image_generated = False

    if text==None:
        text = await text_generate(image)
        text_generated = True

    if image==None:
        image = await image_generate(text)
        image_generated = True

    text_similar, filtered_data = await text_caluculate(text)
    image_similar = await image_caluculate(image, filtered_data)

    # テキストと画像の類似度を統合
    integrated_results = integrate_similarities(text_similar, image_similar)

    return {
        "results": integrated_results,
        "metadata": {
            "actual_text": text,
            "text_generated": text_generated,
            "image_generated": image_generated,
            "has_image": image is not None,
            "original_text": original_text,
            "has_original_image": original_image is not None
        },
        "_internal": {
            "actual_image": image,
            "original_image": original_image
        }
    }


async def get_suggested_images() -> Dict[str, List[str]]:
    """
    画像提案処理

    Returns:
        提案画像リスト
    """
    image_suggest = await random_suggest()

    return {"suggested_images": image_suggest}
