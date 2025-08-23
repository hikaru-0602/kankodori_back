from fastapi import FastAPI, File, Form, UploadFile, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import uvicorn
import controllers.search_controller as search_controller
from firebase_admin import auth
from infrastructures.firebase_config import initialize_firebase

# Firebase初期化
initialize_firebase()

app = FastAPI(
    title="観光地検索 API",
    description="テキストや画像から観光地検索",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 全てのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_firebase_token(request: Request) -> str:
    """
    Firebase IDトークンを検証してUIDを返す

    Returns:
        ユーザーUID

    Raises:
        HTTPException: 認証失敗時
    """
    auth_header = request.headers.get('authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    token = auth_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/")
async def root():
    return {"message": "こんにちは！APIへようこそ。"}


@app.post("/search")
async def search_tourist_spots(
    request: Request,
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
) -> Dict[str, Any]:
    """
    観光地検索

    テキストや画像から観光地を検索します
    - text, imageのいずれかは必須です
    - 検索条件に応じて結果を返します
    - search_range指定で検索範囲を調整します
    - 条件に応じて指定されていない検索条件を生成します
    """
    # Firebase認証
    user_uid = await verify_firebase_token(request)
    print(f"Authenticated user: {user_uid}")

    return await search_controller.search_tourist_spots(text, image)

@app.get("/suggest-images")
async def suggest_images(request: Request) -> Dict[str, Any]:
    """
    画像提案

    ユーザーが選択可能な画像候補を提案
    """
    # Firebase認証
    user_uid = await verify_firebase_token(request)
    print(f"Authenticated user: {user_uid}")

    return await search_controller.suggest_images()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
