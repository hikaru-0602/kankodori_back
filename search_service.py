from typing import Optional, List, Dict, Any
from fastapi import UploadFile
from image_to_text_service import text_generate


async def search_tourist_spots(
    text: Optional[str] = None,
    image: Optional[UploadFile] = None,
    range: int = 50
) -> Dict[str, Any]:
    if range == 100:
        return {"results": ["image"]}
    else:
        # range=100以外の場合、テキストが必須
        if not text:
            # テキストがない場合、画像からテキストを生成
            if image:
                generated_text = await text_generate(image)
                if generated_text:
                    text = generated_text
                else:
                    return {"error": "画像からテキストの生成に失敗しました"}
            else:
                return {"error": "range=100以外の場合、テキストが必要です"}

        if range == 0:
            return {"results": ["text"], "text_used": text}
        else:
            return {"results": ["text", "image"], "text_used": text}


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
