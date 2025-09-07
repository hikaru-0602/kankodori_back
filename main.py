from fastapi import FastAPI, File, Form, UploadFile, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import uvicorn
import time
import controllers.search_controller as search_controller
from infrastructures.firebase_config import verify_firebase_token
from services.logging_service import (
    save_api_log,
    create_request_data_search,
    create_response_data_search
)
from services.image_storage_service import process_search_image

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
    allow_headers=["*"],  # 全てのヘッダーを許可（ngrok-skip-browser-warningを含む）
)

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
    #print(f"Authenticated user: {user_uid}")

    try:
        # API処理実行
        result = await search_controller.search_tourist_spots(text, image)

        # メタデータから実際の値を取得
        metadata = result.get("metadata", {})
        internal = result.get("_internal", {})

        actual_text = metadata.get("actual_text")
        text_generated = metadata.get("text_generated", False)
        image_generated = metadata.get("image_generated", False)
        actual_image = internal.get("actual_image")

        # テキストと画像のソースを判定
        text_source = "generate" if text_generated else "user_input"
        base_image_source = "generate" if image_generated else "user_upload"

        # 画像処理（存在チェック→保存）
        if actual_image is not None:
            # 画像がある場合（アップロードまたは生成）
            storage_path, final_image_source = await process_search_image(
                image=actual_image,
                text=actual_text,
                user_id=user_uid,
                image_source=base_image_source
            )
        else:
            # 画像がない場合
            storage_path, final_image_source = None, "none"

        # リクエストデータ作成
        request_data = create_request_data_search(
            text=actual_text,
            image_present=actual_image is not None,
            text_source=text_source,
            image_source=final_image_source,
            storage_path=storage_path
        )

        # レスポンス用にinternalデータを削除
        clean_result = {k: v for k, v in result.items() if k != "_internal"}

        # 成功時のログ保存
        response_data = create_response_data_search(
            status="success",
            result=clean_result,
            total_candidates=len(result.get('results', [])) if isinstance(result, dict) else None
        )

        await save_api_log(
            user_id=user_uid,
            api_endpoint="search",
            request_data=request_data,
            response_data=response_data
        )

        return clean_result

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

    # Firebase認証
    user_uid = await verify_firebase_token(request)
    #print(f"Authenticated user: {user_uid}")
    # API処理実行
    result = await search_controller.suggest_images()
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
