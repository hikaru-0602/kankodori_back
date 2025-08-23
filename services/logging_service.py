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
    response_data: Dict[str, Any],
    processing_time_ms: int,
    client_info: Optional[Dict[str, str]] = None
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
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "api_endpoint": api_endpoint,
            "request_data": request_data,
            "response_data": response_data,
            "processing_time_ms": processing_time_ms,
            "client_info": client_info or {}
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
    image_source: str = "user_upload"
) -> Dict[str, Any]:
    """
    search APIのリクエストデータを構築

    Args:
        text: 検索テキスト
        image_present: 画像が存在するかどうか
        text_source: テキストの出所 ('user_input' | 'ai_generated')
        image_source: 画像の出所 ('user_upload' | 'suggested')

    Returns:
        request_data辞書
    """
    return {
        "text": text,
        "text_source": text_source,
        "image": {
            "present": image_present,
            "source": image_source if image_present else None
        }
    }

def create_request_data_suggest() -> Dict[str, Any]:
    """
    suggest-images APIのリクエストデータを構築

    Returns:
        request_data辞書
    """
    return {}

def create_response_data(
    status: str,
    result: Any = None,
    error_message: Optional[str] = None,
    result_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    レスポンスデータを構築

    Args:
        status: レスポンス状態 ('success' | 'error')
        result: APIレスポンス結果
        error_message: エラーメッセージ（エラー時）
        result_count: 結果件数

    Returns:
        response_data辞書
    """
    response_data = {
        "status": status
    }

    if result is not None:
        response_data["result"] = result
    if error_message:
        response_data["error_message"] = error_message
    if result_count is not None:
        response_data["result_count"] = result_count

    return response_data

def create_client_info(user_agent: Optional[str], ip: Optional[str]) -> Dict[str, str]:
    """
    クライアント情報を構築

    Args:
        user_agent: User-Agentヘッダー
        ip: クライアントIP

    Returns:
        client_info辞書
    """
    return {
        "user_agent": user_agent or "Unknown",
        "ip": ip or "Unknown"
    }
