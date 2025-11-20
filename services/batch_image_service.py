import os
from typing import Optional, Dict, Any
from infrastructures.image_downloader import download_image_from_url


async def save_query_image(
    image_url: str,
    query_id: int,
    query_dir: str
) -> Optional[str]:
    """
    クエリ画像をtest/queryディレクトリに保存

    Args:
        image_url: 画像のURL
        query_id: クエリID
        query_dir: 保存先ディレクトリ

    Returns:
        保存したファイル名（失敗時はNone）
    """
    # ディレクトリが存在しなければ作成
    os.makedirs(query_dir, exist_ok=True)

    # ファイル名
    filename = f"{query_id}.jpg"
    file_path = os.path.join(query_dir, filename)

    # 既に存在する場合はスキップ
    if os.path.exists(file_path):
        print(f"クエリ画像 {filename} は既に存在します（スキップ）")
        return filename

    # 画像をダウンロード
    image_data = await download_image_from_url(image_url)
    if image_data is None:
        print(f"クエリ画像のダウンロード失敗: {image_url}")
        return None

    # 保存
    try:
        with open(file_path, 'wb') as f:
            f.write(image_data)
        print(f"クエリ画像を保存: {filename}")
        return filename
    except Exception as e:
        print(f"クエリ画像の保存エラー: {e}")
        return None


async def save_result_image(
    result_data: Dict[str, Any],
    result_dir: str
) -> Optional[str]:
    """
    検索結果の画像をtest/resultディレクトリに保存

    Args:
        result_data: 検索結果データ（id, name, locationなどを含む）
        result_dir: 保存先ディレクトリ

    Returns:
        保存したファイル名（失敗時はNone）
    """
    if result_data is None:
        print(f"結果データがNullです")
        return None

    # ディレクトリが存在しなければ作成
    os.makedirs(result_dir, exist_ok=True)

    # 結果データから観光地IDを取得
    result_id = result_data.get("id")
    if result_id is None:
        print(f"結果データにIDがありません")
        return None

    # ファイル名は観光地のIDそのもの
    filename = f"{result_id}.jpg"
    file_path = os.path.join(result_dir, filename)

    # 既に存在する場合はスキップ
    if os.path.exists(file_path):
        print(f"結果画像 {filename} は既に存在します（スキップ）")
        return filename

    # FirebaseストレージのURLを構築
    # 画像は api/photo/{result_id}.jpg にあると仮定
    from firebase_admin import storage

    try:
        bucket = storage.bucket()
        # 拡張子を試す
        extensions = ['.jpg', '.jpeg', '.png', '.webp']
        blob = None

        for ext in extensions:
            blob_path = f"api/photo/{result_id}{ext}"
            test_blob = bucket.blob(blob_path)
            if test_blob.exists():
                blob = test_blob
                break

        if blob is None:
            print(f"結果画像が見つかりません（ID: {result_id}）")
            return None

        # 画像をダウンロード
        from io import BytesIO
        image_bytes = BytesIO()
        blob.download_to_file(image_bytes)
        image_bytes.seek(0)
        image_data = image_bytes.read()

        # 保存
        with open(file_path, 'wb') as f:
            f.write(image_data)
        print(f"結果画像を保存: {filename}")
        return filename

    except Exception as e:
        print(f"結果画像の保存エラー: {e}")
        return None


def save_query_images_json(
    query_image_filenames: list,
    test_dir: str
) -> bool:
    """
    クエリ画像のファイル名リストをJSONとして保存

    Args:
        query_image_filenames: クエリ画像のファイル名リスト
        test_dir: testディレクトリのパス

    Returns:
        成功したかどうか
    """
    import json

    json_path = os.path.join(test_dir, "query_images.json")

    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(query_image_filenames, f, ensure_ascii=False, indent=2)
        print(f"クエリ画像JSONを保存: {json_path}")
        return True
    except Exception as e:
        print(f"クエリ画像JSON保存エラー: {e}")
        return False
