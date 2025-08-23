from fastapi import FastAPI, File, Form, UploadFile, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import uvicorn
import time
import controllers.search_controller as search_controller
from firebase_admin import auth
from infrastructures.firebase_config import initialize_firebase
from services.logging_service import (
    save_api_log,
    create_request_data_search,
    create_request_data_suggest,
    create_response_data_search,
    create_response_data_suggest
)

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
    start_time = time.time()

    # Firebase認証
    user_uid = await verify_firebase_token(request)
    print(f"Authenticated user: {user_uid}")

    # リクエストデータ作成
    request_data = create_request_data_search(
        text=text,
        image_present=image is not None,
        text_source="user_input",
        image_source="user_upload" if image else None
    )

    try:
        # API処理実行
        result = await search_controller.search_tourist_spots(text, image)

        # 成功時のログ保存
        response_data = create_response_data_search(
            status="success",
            result=result,
            total_candidates=len(result.get('results', [])) if isinstance(result, dict) else None
        )

        await save_api_log(
            user_id=user_uid,
            api_endpoint="search",
            request_data=request_data,
            response_data=response_data
        )

        return result

    except Exception as e:
        # エラー時のログ保存
        response_data = create_response_data_search(
            status="error",
            error_message=str(e)
        )

        await save_api_log(
            user_id=user_uid,
            api_endpoint="search",
            request_data=request_data,
            response_data=response_data
        )

        raise

@app.get("/suggest-images")
async def suggest_images(request: Request) -> Dict[str, Any]:
    """
    画像提案

    ユーザーが選択可能な画像候補を提案
    """
    start_time = time.time()

    # Firebase認証
    user_uid = await verify_firebase_token(request)
    print(f"Authenticated user: {user_uid}")

    # リクエストデータ作成
    request_data = create_request_data_suggest()
    try:
        # API処理実行
        result = await search_controller.suggest_images()

        # 成功時のログ保存
        response_data = create_response_data_suggest(
            status="success",
            result=result
        )

        await save_api_log(
            user_id=user_uid,
            api_endpoint="suggest-images",
            request_data=request_data,
            response_data=response_data
        )

        return result

    except Exception as e:
        # エラー時のログ保存
        response_data = create_response_data_suggest(
            status="error",
            error_message=str(e)
        )

        await save_api_log(
            user_id=user_uid,
            api_endpoint="suggest-images",
            request_data=request_data,
            response_data=response_data
        )

        raise

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
