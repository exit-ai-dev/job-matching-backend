# Azure 公開手順（FastAPI + Azure Database for PostgreSQL + Static Web Apps）

このプロジェクトは以下の構成で Azure に公開できます。
- Backend: Azure App Service (Linux) または Azure Container Apps
- DB: Azure Database for PostgreSQL (Flexible Server)
- Frontend: Azure Static Web Apps (SWA)

---

## 1) Azure Database for PostgreSQL (Flexible Server) を作成
1. Azure Portal → PostgreSQL Flexible Server を作成
2. 接続情報を控える（host / dbname / user / password）
3. Networking:
   - 開発中: Public access + 自分のIPを許可
   - 本番: Backend を VNet 経由 or Private access 推奨（後でOK）
4. Parameter（推奨）:
   - SSL を require のまま運用（このプロジェクトは DB_SSLMODE で対応）

### スキーマ投入
バックエンドの `backend/db_schema_complete.sql` を実行してください。

---

## 2) Backend を Azure へデプロイ
### A. App Service（コードデプロイ）
- App Service (Linux / Python 3.11) を作成
- Configuration → Application settings に以下を設定

必須:
- OPENAI_API_KEY
- SECRET_KEY
- ALLOWED_ORIGINS（SWAのURLを入れる）

DB（推奨: DATABASE_URL 方式）:
- DATABASE_URL = postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require

または分割:
- DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
- DB_SSLMODE=require

起動コマンド例（Startup Command）:
- `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --access-logfile - --error-logfile - --log-level info`

### B. Docker（コンテナデプロイ）
`backend/Dockerfile` を追加済みです。
- Azure Container Registry (ACR) へ build/push
- Web App for Containers または Container Apps へデプロイ
- 環境変数（上と同じ）を設定

---

## 3) Frontend を Azure Static Web Apps (SWA) へデプロイ
Frontend の `VITE_API_BASE_URL` を設定します。例:
- `https://<backend-app-name>.azurewebsites.net/api`

SWA の Environment variables に `VITE_API_BASE_URL` を追加して再デプロイしてください。

---

## 4) 疎通チェック
- Backend: `https://<backend>/docs` が表示できる
- DB: Backend のログで「データベース接続確認: 成功」
- Frontend: ログイン/チャットが動作し、CORS エラーが出ない

---

## 補足（よくあるハマり）
- Azure PostgreSQL は SSL 必須のことが多い → `sslmode=require` を忘れない
- CORS: `ALLOWED_ORIGINS` に SWA ドメインを必ず追加
- DB 接続先ズレ: App Service の Application settings を確認
