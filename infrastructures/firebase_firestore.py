"""
Firebase Firestore操作のInfrastructure層

Firestore SDKの直接操作のみを担当
Repository層から呼び出される低レベルAPI
"""

from typing import Optional, Dict, Any, List
from firebase_admin import firestore


def get_firestore_client():
    """Firestoreクライアントを取得"""
    return firestore.client()


async def save_document(
    collection: str,
    document_id: str,
    data: Dict[str, Any],
    merge: bool = False
) -> bool:
    """
    ドキュメントを保存

    Args:
        collection: コレクション名
        document_id: ドキュメントID
        data: 保存するデータ
        merge: マージするかどうか

    Returns:
        成功時True、失敗時False
    """
    try:
        db = get_firestore_client()
        doc_ref = db.collection(collection).document(document_id)
        doc_ref.set(data, merge=merge)
        return True
    except Exception as e:
        print(f"Firestore保存エラー ({collection}/{document_id}): {e}")
        return False


async def get_document(collection: str, document_id: str) -> Optional[Dict[str, Any]]:
    """
    ドキュメントを取得

    Args:
        collection: コレクション名
        document_id: ドキュメントID

    Returns:
        ドキュメントデータ、存在しない場合はNone
    """
    try:
        db = get_firestore_client()
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Firestore取得エラー ({collection}/{document_id}): {e}")
        return None


async def add_document_to_collection(collection: str, data: Dict[str, Any]) -> Optional[str]:
    """
    コレクションに自動生成IDでドキュメント追加

    Args:
        collection: コレクション名
        data: 保存するデータ

    Returns:
        生成されたドキュメントID、失敗時はNone
    """
    try:
        db = get_firestore_client()
        doc_ref = db.collection(collection).document()
        doc_ref.set(data)
        return doc_ref.id
    except Exception as e:
        print(f"Firestoreドキュメント追加エラー ({collection}): {e}")
        return None


async def add_document_to_subcollection(
    parent_collection: str,
    parent_document_id: str,
    subcollection: str,
    data: Dict[str, Any]
) -> Optional[str]:
    """
    サブコレクションに自動生成IDでドキュメント追加

    Args:
        parent_collection: 親コレクション名
        parent_document_id: 親ドキュメントID
        subcollection: サブコレクション名
        data: 保存するデータ

    Returns:
        生成されたドキュメントID、失敗時はNone
    """
    try:
        db = get_firestore_client()
        doc_ref = (
            db.collection(parent_collection)
            .document(parent_document_id)
            .collection(subcollection)
            .document()
        )
        doc_ref.set(data)
        return doc_ref.id
    except Exception as e:
        print(f"Firestoreサブコレクション追加エラー ({parent_collection}/{parent_document_id}/{subcollection}): {e}")
        return None


async def query_documents(
    collection: str,
    field: str,
    operator: str,
    value: Any,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    ドキュメントをクエリ

    Args:
        collection: コレクション名
        field: フィールド名
        operator: 比較演算子 ('==', '<', '>', '<=', '>=', 'in', 'array-contains')
        value: 比較値
        limit: 取得件数制限

    Returns:
        ドキュメントのリスト
    """
    try:
        db = get_firestore_client()
        query = db.collection(collection).where(field, operator, value)

        if limit:
            query = query.limit(limit)

        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Firestoreクエリエラー ({collection}): {e}")
        return []


async def delete_document(collection: str, document_id: str) -> bool:
    """
    ドキュメントを削除

    Args:
        collection: コレクション名
        document_id: ドキュメントID

    Returns:
        成功時True、失敗時False
    """
    try:
        db = get_firestore_client()
        db.collection(collection).document(document_id).delete()
        return True
    except Exception as e:
        print(f"Firestore削除エラー ({collection}/{document_id}): {e}")
        return False
