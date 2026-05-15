"""
ログデータの永続化を担当するRepository層

Firestoreを使ったログ管理のドメイン抽象化
"""

from typing import Dict, Any
from datetime import datetime, timezone
from infrastructures.firebase_config import initialize_firebase
from infrastructures import firebase_firestore


class LogRepository:
    """APIログの永続化を担当"""

    def __init__(self):
        self._is_initialized = False

    def _ensure_initialized(self):
        """Firebase初期化を確認"""
        if not self._is_initialized:
            initialize_firebase()
            self._is_initialized = True

    async def save_api_log(
        self,
        user_id: str,
        api_endpoint: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any]
    ) -> bool:
        """
        APIアクセスログをユーザーごとに保存

        Args:
            user_id: ユーザーID (Firebase UID)
            api_endpoint: APIエンドポイント名
            request_data: リクエストデータ
            response_data: レスポンスデータ

        Returns:
            成功時True、失敗時False
        """
        self._ensure_initialized()

        try:
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "api_endpoint": api_endpoint,
                "request_data": request_data,
                "response_data": response_data
            }

            # サブコレクションに追加
            doc_id = await firebase_firestore.add_document_to_subcollection(
                parent_collection='users',
                parent_document_id=user_id,
                subcollection='api_logs',
                data=log_data
            )

            if doc_id:
                print(f"API log saved: {api_endpoint} by user {user_id}")
                return True
            else:
                return False

        except Exception as e:
            import traceback
            print(f"ログ保存エラー詳細: {e}")
            print(f"エラータイプ: {type(e)}")
            print(f"トレースバック: {traceback.format_exc()}")
            return False
