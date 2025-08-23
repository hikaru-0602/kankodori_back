from typing import Optional, Dict, Any
from datetime import datetime, timezone
from firebase_admin import firestore
from infrastructures.firebase_config import initialize_firebase

# Firestore初期化
initialize_firebase()

def get_firestore_client():
    """Firestoreクライアントを取得"""
    return firestore.client()

async def save_api_log(
    user_id: str,
    api_endpoint: str,
    request_data: Dict[str, Any],
    response_data: Dict[str, Any]
) -> bool:
    """
    APIアクセスログをFirestoreに保存

    Args:
        user_id: Firebase UID
        api_endpoint: APIエンドポイント名 ('search' | 'suggest-images')
        request_data: リクエストデータ
        response_data: レスポンスデータ
        processing_time_ms: 処理時間（ミリ秒）
        client_info: クライアント情報（IP、User-Agentなど）

    Returns:
        保存成功時True、失敗時False
    """
    try:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "api_endpoint": api_endpoint,
            "request_data": request_data,
            "response_data": response_data
        }

        # Firestoreに保存（ユーザーごとのサブコレクション）
        db = get_firestore_client()
        doc_ref = db.collection('users').document(user_id).collection('api_logs').document()
        doc_ref.set(log_data)

        print(f"API log saved: {api_endpoint} by user {user_id}")
        return True

    except Exception as e:
        import traceback
        print(f"ログ保存エラー詳細: {e}")
        print(f"エラータイプ: {type(e)}")
        print(f"トレースバック: {traceback.format_exc()}")
        return False

def create_request_data_search(
    text: Optional[str],
    image_present: bool,
    text_source: str = "user_input",
    image_source: str = "user_upload",
    storage_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    search APIのリクエストデータを構築

    Args:
        text: 検索テキスト
        image_present: 画像が存在するかどうか
        text_source: テキストの出所 ('user_input' | 'ai_generated')
        image_source: 画像の出所 ('user_upload' | 'suggested')
        storage_path: Firebase Storageのパス

    Returns:
        request_data辞書
    """
    image_data = {
        "present": image_present,
        "source": image_source if image_present else None
    }

    if image_present and storage_path:
        image_data["storage_path"] = storage_path

    return {
        "text": text,
        "text_source": text_source,
        "image": image_data
    }

def create_request_data_suggest() -> Dict[str, Any]:
    """
    suggest-images APIのリクエストデータを構築

    Returns:
        request_data辞書
    """
    return {}

def create_response_data_search(
    status: str,
    result: Any = None,
    error_message: Optional[str] = None,
    total_candidates: Optional[int] = None
) -> Dict[str, Any]:
    """
    search APIのレスポンスデータを構築

    Args:
        status: レスポンス状態 ('success' | 'error')
        result: APIレスポンス結果（上位5件の配列）
        error_message: エラーメッセージ（エラー時）
        total_candidates: 全候補数

    Returns:
        response_data辞書
    """
    response_data = {}

    if status == "success" and result is not None:
        # 上位5件のログ用データ処理
        top_results = process_search_results_for_log(result)
        response_data["top_results"] = top_results
        if total_candidates:
            response_data["total_candidates"] = total_candidates
    elif error_message:
        response_data["error_message"] = error_message

    return response_data

def create_response_data_suggest(
    status: str,
    result: Any = None,
    error_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    suggest-images APIのレスポンスデータを構築

    Args:
        status: レスポンス状態 ('success' | 'error')
        result: APIレスポンス結果
        error_message: エラーメッセージ（エラー時）

    Returns:
        response_data辞書
    """
    response_data = {}

    if status == "success" and result is not None:
        # suggested_imagesを取得
        suggested_images = result.get('suggested_images', []) if isinstance(result, dict) else []
        response_data["suggested_images"] = suggested_images
    elif error_message:
        response_data["error_message"] = error_message

    return response_data

def process_search_results_for_log(results: Any) -> list:
    """
    検索結果を上位5件のログ用データに変換

    Args:
        results: 検索API結果

    Returns:
        上位5件の配列（重複なし）
    """
    try:
        if not isinstance(results, dict) or 'results' not in results:
            return []

        raw_results = results['results']
        if not isinstance(raw_results, list):
            return []

        # combined_scoreを計算してソート
        processed = []
        seen_names = set()

        for item in raw_results:
            if not isinstance(item, dict):
                continue

            name = item.get('name', '')
            if name in seen_names:
                continue  # 重複除去

            text_sim = item.get('text_similarity', 0.0)
            image_sim = item.get('image_similarity', 0.0)
            combined_score = (text_sim + image_sim) * 0.5

            processed.append({
                "id": item.get('id', ''),
                "name": name,
                "text_similarity": text_sim,
                "image_similarity": image_sim,
                "combined_score": combined_score
            })

            seen_names.add(name)

        # combined_scoreでソートして上位5件
        processed.sort(key=lambda x: x['combined_score'], reverse=True)
        return processed[:5]

    except Exception as e:
        print(f"検索結果処理エラー: {e}")
        return []
