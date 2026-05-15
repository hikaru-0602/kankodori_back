"""
設定データの永続化を担当するRepository層

Firestoreを使った設定管理のドメイン抽象化
"""

from typing import Optional
from infrastructures.firebase_config import initialize_firebase
from infrastructures import firebase_firestore
from firebase_admin import firestore


class ConfigRepository:
    """アプリケーション設定の永続化を担当"""

    def __init__(self):
        self._is_initialized = False

    def _ensure_initialized(self):
        """Firebase初期化を確認"""
        if not self._is_initialized:
            initialize_firebase()
            self._is_initialized = True

    async def update_server_url(self, url: str) -> bool:
        """
        APIサーバーURLを更新

        Args:
            url: 新しいサーバーURL

        Returns:
            成功時True、失敗時False
        """
        self._ensure_initialized()

        data = {
            'url': url,
            'updated_at': firestore.SERVER_TIMESTAMP
        }

        return await firebase_firestore.save_document(
            collection='api_server_url',
            document_id='url',
            data=data,
            merge=True
        )

    async def get_server_url(self) -> Optional[str]:
        """
        現在のAPIサーバーURLを取得

        Returns:
            URL文字列、存在しない場合はNone
        """
        self._ensure_initialized()

        doc = await firebase_firestore.get_document(
            collection='api_server_url',
            document_id='url'
        )

        return doc.get('url') if doc else None
