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
    image: Optional[UploadFile] = None,
    search_range: int = 50
) -> Dict[str, Any]:
    if search_range < 100 and text==None:
        text = await text_generate(image)

    if search_range > 0 and image==None:
        image = await image_generate(text)

    if search_range == 0:
        text_similar = await text_caluculate(text)
        print("text only")
        print(search_range)
        return {"results": text_similar}
    elif search_range > 0 and search_range < 100:
        text_similar, filtered_data = await text_caluculate(text)
        image_similar = await image_caluculate(image, filtered_data)

        # テキストと画像の類似度を統合
        integrated_results = integrate_similarities(text_similar, image_similar, search_range)
        print("text and image")
        print(search_range)
        return {"results": integrated_results}
    else:
        image_similar = await image_caluculate(image)
        print("image only")
        print(search_range)
        return {"results": image_similar}


async def get_suggested_images() -> Dict[str, List[str]]:
    """
    画像提案処理

    Returns:
        提案画像リスト
    """
    image_suggest = await random_suggest()

    return {"suggested_images": image_suggest}
