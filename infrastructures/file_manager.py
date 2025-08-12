import os
from typing import Optional
from PIL import Image


class FileManager:
    """ファイル操作を行うインフラ層クラス"""

    @staticmethod
    def setup_directory(base_path: str, sub_dirs: list[str]) -> str:
        """
        ディレクトリを作成し、パスを返す

        Args:
            base_path: ベースとなるパス
            sub_dirs: 作成するサブディレクトリのリスト

        Returns:
            作成されたディレクトリのパス
        """
        full_path = os.path.join(base_path, *sub_dirs)
        os.makedirs(full_path, exist_ok=True)
        return full_path

    @staticmethod
    def get_script_directory() -> str:
        """
        現在のスクリプトのディレクトリパスを取得

        Returns:
            スクリプトのディレクトリパス
        """
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        ファイルが存在するかチェック

        Args:
            file_path: チェックするファイルパス

        Returns:
            ファイルが存在する場合True
        """
        return os.path.exists(file_path)

    @staticmethod
    def load_image(file_path: str) -> Optional[Image.Image]:
        """
        画像ファイルを読み込む

        Args:
            file_path: 画像ファイルのパス

        Returns:
            PIL Image オブジェクト（失敗時はNone）
        """
        try:
            return Image.open(file_path)
        except Exception as e:
            print(f"画像読み込みエラー: {str(e)}")
            return None

    @staticmethod
    def save_image(image: Image.Image, file_path: str) -> bool:
        """
        画像を保存する

        Args:
            image: 保存するPIL Image オブジェクト
            file_path: 保存先のファイルパス

        Returns:
            保存に成功した場合True
        """
        try:
            image.save(file_path)
            return True
        except Exception as e:
            print(f"画像保存エラー: {str(e)}")
            return False

    @staticmethod
    def create_filename(prompt: str, extension: str = ".jpg") -> str:
        """
        プロンプトからファイル名を生成

        Args:
            prompt: ファイル名のベースとなる文字列
            extension: ファイル拡張子

        Returns:
            生成されたファイル名
        """
        return f"{prompt}{extension}"
