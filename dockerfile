# Python 3.12の公式イメージを使用
FROM python:3.12.8

# 作業ディレクトリを設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 3110

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3110/ || exit 1

# アプリケーションを起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3110"]
