#!/usr/bin/env python3
"""
ngrokのURLを取得してFirestoreのapi_server_urlコレクションを更新するスクリプト
"""

import requests
import json
import time
import sys
from firebase_admin import firestore
from infrastructures.firebase_config import initialize_firebase


def get_ngrok_url(max_retries=10, retry_interval=2):
    """
    ngrok APIからトンネルURLを取得

    Args:
        max_retries: 最大リトライ回数
        retry_interval: リトライ間隔（秒）

    Returns:
        str: ngrokのpublic URL、取得失敗時はNone
    """
    for attempt in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            response.raise_for_status()

            data = response.json()
            tunnels = data.get("tunnels", [])

            if tunnels:
                # HTTPSのURLを優先して返す
                for tunnel in tunnels:
                    public_url = tunnel.get("public_url", "")
                    if public_url.startswith("https://"):
                        return public_url

                # HTTPSが見つからない場合は最初のURLを返す
                return tunnels[0].get("public_url")

            print(f"Attempt {attempt + 1}: No tunnels found, retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: Error connecting to ngrok API: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)

    print("Failed to get ngrok URL after all retries")
    return None


def update_firestore_url(ngrok_url):
    """
    FirestoreのAPI server URLを更新

    Args:
        ngrok_url: ngrokで生成されたURL

    Returns:
        bool: 更新成功時True、失敗時False
    """
    try:
        # Firebase初期化
        initialize_firebase()
        db = firestore.client()

        # api_server_urlコレクションのurlドキュメントを更新
        doc_ref = db.collection('api_server_url').document('url')
        doc_ref.set({
            'url': ngrok_url,
            'updated_at': firestore.SERVER_TIMESTAMP
        }, merge=True)

        print(f"Successfully updated Firestore with URL: {ngrok_url}")
        return True

    except Exception as e:
        print(f"Error updating Firestore: {e}")
        return False


def main():
    """メイン処理"""
    print("Getting ngrok URL...")
    ngrok_url = get_ngrok_url()

    if not ngrok_url:
        print("Failed to get ngrok URL")
        sys.exit(1)

    print(f"Got ngrok URL: {ngrok_url}")

    print("Updating Firestore...")
    success = update_firestore_url(ngrok_url)

    if success:
        print("✅ Successfully updated API server URL in Firestore")
        sys.exit(0)
    else:
        print("❌ Failed to update Firestore")
        sys.exit(1)


if __name__ == "__main__":
    main()
