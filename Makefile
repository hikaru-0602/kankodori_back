# 設定
#API_URL = https://kankodori-625939020208.asia-northeast1.run.app
API_URL = http://localhost:3110

# バックエンドサーバーを開発モードで起動
back:
	uvicorn main:app --reload --port 3110 --workers 4

.PHONY: back


# コンテナをプッシュ
push:
	gcloud builds submit --tag asia-northeast1-docker.pkg.dev/kankodori-23918/kankodori/kankodori:latest .

.PHONY: push

# バックエンドサーバーを開発モードで起動
deploy:
	gcloud run deploy kankodori --image asia-northeast1-docker.pkg.dev/kankodori-23918/kankodori/kankodori:latest --set-secrets="HF_API_TOKEN=hugging-face:latest" --set-env-vars="FIREBASE_STORAGE_BUCKET=kankodori-23918.firebasestorage.app" --region asia-northeast1 --memory=16Gi --cpu=4

.PHONY: deploy

# 画像提案
suggest:
	curl "$(API_URL)/suggest-images"

.PHONY: suggest

# 画像生成検索
search:
	curl -X POST "$(API_URL)/search" \
		-H "Content-Type: multipart/form-data" \
		-F "text=函館の絶景"

.PHONY: search


.PHONY: publish
publish:
	@echo "Starting ngrok..."
	@ngrok http 3110 --region jp &
	@echo "Waiting for ngrok to start..."
	@sleep 3
	@echo "Updating Firestore with ngrok URL..."
	@python3 update_ngrok_url.py
	@echo "✅ ngrok published and Firestore updated!"
	@wait
