from fastapi import FastAPI, File, Form, UploadFile
from typing import Optional, Dict, Any
import uvicorn
import controllers.search_controller as search_controller

app = FastAPI(
    title="観光地検索 API",
    description="テキストや画像から観光地検索",
    version="1.0.0"
)

@app.post("/search")
async def search_tourist_spots(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    search_range: int = Form(50, ge=0, le=100)
) -> Dict[str, Any]:
    """
    観光地検索

    テキストや画像から観光地を検索します
    - text, imageのいずれかは必須です
    - 検索条件に応じて結果を返します
    - search_range指定で検索範囲を調整します
    - 条件に応じて指定されていない検索条件を生成します
    """
    return await search_controller.search_tourist_spots(text, image, search_range)

@app.get("/suggest-images")
async def suggest_images() -> Dict[str, Any]:
    """
    画像提案

    ユーザーが選択可能な画像候補を提案
    """
    return await search_controller.suggest_images()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
