from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import uvicorn
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


@app.post("/batch-search")
async def batch_search(request: Request) -> Dict[str, Any]:
    """
    バッチ検索（実験用）

    test/set.txt ファイルに記載された[テキスト,画像URL]のペアで一括検索を実行
    結果は test/batch_search_results.json にキャッシュされる
    """

    import os
    import csv
    import json

    # ファイルパス設定
    test_dir = os.path.join(os.path.dirname(__file__), "test")
    set_file_path = os.path.join(test_dir, "set.txt")
    cache_file_path = os.path.join(test_dir, "batch_search_results.json")

    # キャッシュファイルが存在する場合は読み込んで返す
    if os.path.exists(cache_file_path):
        print("キャッシュファイルが見つかりました。キャッシュから結果を返します。")
        try:
            with open(cache_file_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                return cached_data
        except Exception as e:
            print(f"キャッシュ読み込みエラー: {str(e)}")
            # キャッシュ読み込み失敗時は処理を続行

    # set.txt の存在確認
    if not os.path.exists(set_file_path):
        return {"error": "test/set.txt が見つかりません"}

    results = []
    query_image_filenames = []

    # 画像保存用ディレクトリ
    query_dir = os.path.join(test_dir, "query")
    result_dir = os.path.join(test_dir, "result")

    try:
        from services.search_service import search_with_url_and_weights
        from services.batch_image_service import (
            save_query_image,
            save_result_image,
            save_query_images_json
        )

        with open(set_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader, start=1):
                if len(row) < 2:
                    print(f"行 {idx}: スキップ（データ不足）")
                    continue

                text = row[0].strip()
                image_url = row[1].strip()

                print(f"[{idx}] 検索中: テキスト='{text}', URL={image_url[:60]}...")

                try:
                    # 3つの重み比率で検索
                    search_result = await search_with_url_and_weights(text, image_url)

                    result_item = {
                        "id": idx,
                        "query_text": text,
                        "query_image_url": image_url,
                        "text_100_image_0": search_result.get("text_100_image_0"),
                        "text_50_image_50": search_result.get("text_50_image_50"),
                        "text_0_image_100": search_result.get("text_0_image_100")
                    }

                    results.append(result_item)
                    print(f"[{idx}] 成功")

                    # 画像保存処理（このエンドポイントのみ）
                    # 1. クエリ画像を保存
                    query_filename = await save_query_image(image_url, idx, query_dir)
                    if query_filename:
                        query_image_filenames.append(query_filename)

                    # 2. 結果画像を保存（3つ、ファイル名は観光地ID）
                    await save_result_image(
                        search_result.get("text_100_image_0"),
                        result_dir
                    )
                    await save_result_image(
                        search_result.get("text_50_image_50"),
                        result_dir
                    )
                    await save_result_image(
                        search_result.get("text_0_image_100"),
                        result_dir
                    )

                except Exception as e:
                    print(f"[{idx}] エラー: {str(e)}")
                    # エラーの場合もNullで記録
                    result_item = {
                        "id": idx,
                        "query_text": text,
                        "query_image_url": image_url,
                        "text_100_image_0": None,
                        "text_50_image_50": None,
                        "text_0_image_100": None,
                        "error": str(e)
                    }
                    results.append(result_item)

        # 結果をJSONとして整形
        response_data = {"results": results}

        # JSONファイルに保存
        try:
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)
            print(f"結果を {cache_file_path} に保存しました")
        except Exception as e:
            print(f"JSON保存エラー: {str(e)}")

        # クエリ画像のファイル名リストをJSONとして保存
        if query_image_filenames:
            save_query_images_json(query_image_filenames, test_dir)

        return response_data

    except Exception as e:
        print(f"バッチ検索エラー: {str(e)}")
        return {
            "error": f"バッチ検索処理中にエラーが発生しました: {str(e)}"
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
