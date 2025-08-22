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

# AI モデルを事前ダウンロード・初期化・保存
RUN mkdir -p /app/models && python -c "\
import torch; \
import pickle; \
from transformers import BertJapaneseTokenizer, BertModel, ViTImageProcessor, ViTModel, BlipProcessor, BlipForConditionalGeneration; \
print('Downloading and initializing BERT model...'); \
bert_tokenizer = BertJapaneseTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking'); \
bert_model = BertModel.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking'); \
bert_model.eval(); \
torch.save({'tokenizer': bert_tokenizer, 'model': bert_model}, '/app/models/bert_initialized.pth'); \
print('Downloading and initializing ViT model...'); \
vit_processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224', use_fast=True); \
vit_model = ViTModel.from_pretrained('google/vit-base-patch16-224'); \
vit_model.eval(); \
torch.save({'processor': vit_processor, 'model': vit_model}, '/app/models/vit_initialized.pth'); \
print('Downloading and initializing BLIP model...'); \
blip_processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-large'); \
blip_model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-large'); \
blip_model.eval(); \
torch.save({'processor': blip_processor, 'model': blip_model}, '/app/models/blip_initialized.pth'); \
print('All models downloaded, initialized and saved successfully!')"

# アプリケーションのソースコードをコピー
COPY . .

# アプリケーションがリッスンするポートを$PORT環境変数から取得
EXPOSE 8080

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080 || exit 1

# アプリケーションを起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
