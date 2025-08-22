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

# AI モデルを事前ダウンロード
RUN python -c "\
from transformers import BertJapaneseTokenizer, BertModel, ViTImageProcessor, ViTModel, BlipProcessor, BlipForConditionalGeneration; \
print('Downloading BERT model...'); \
BertJapaneseTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking'); \
BertModel.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking'); \
print('Downloading ViT model...'); \
ViTImageProcessor.from_pretrained('google/vit-base-patch16-224', use_fast=True); \
ViTModel.from_pretrained('google/vit-base-patch16-224'); \
print('Downloading BLIP model...'); \
BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-large'); \
BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-large'); \
print('All models downloaded successfully!')"

# アプリケーションのソースコードをコピー
COPY . .

# アプリケーションがリッスンするポートを$PORT環境変数から取得
EXPOSE 8080

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080 || exit 1

# アプリケーションを起動
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
