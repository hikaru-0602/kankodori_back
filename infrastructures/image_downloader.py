import httpx
from typing import Optional
from PIL import Image
from io import BytesIO


async def download_image_from_url(url: str, timeout: int = 30) -> Optional[bytes]:
    """
    URLから画像をダウンロードしてバイトデータとして返す

    Args:
        url: 画像のURL
        timeout: タイムアウト秒数（デフォルト30秒）

    Returns:
        画像のバイトデータ（失敗時はNone）
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except Exception as e:
        print(f"画像ダウンロードエラー ({url}): {e}")
        return None


async def download_image_as_pil(url: str, timeout: int = 30) -> Optional[Image.Image]:
    """
    URLから画像をダウンロードしてPIL Imageとして返す

    Args:
        url: 画像のURL
        timeout: タイムアウト秒数（デフォルト30秒）

    Returns:
        PIL Image オブジェクト（失敗時はNone）
    """
    try:
        image_data = await download_image_from_url(url, timeout)
        if image_data is None:
            return None

        return Image.open(BytesIO(image_data))
    except Exception as e:
        print(f"PIL Image変換エラー ({url}): {e}")
        return None
