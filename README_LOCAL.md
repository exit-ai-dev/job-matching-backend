# Job Matching Fullstack (Frontend + FastAPI Backend)

このフォルダは、以下2つのzipを統合したローカル実行用構成です。

- frontend/ : React(Vite)
- backend/  : FastAPI + PostgreSQL

## 前提
- Node.js 18+ 推奨
- Python 3.11+
- PostgreSQL 14+（または docker-compose）

## 1) DBを用意（docker-compose 推奨）
```bash
cd job-matching-fullstack
docker compose up -d db
```

初回のみスキーマ投入:
```bash
docker compose exec -T db psql -U devuser -d jobmatch < backend/db_schema_complete.sql
docker compose exec -T db psql -U devuser -d jobmatch < backend/create_chat_sessions.sql
```

## 2) バックエンド起動
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# mac/linux:
# source .venv/bin/activate

pip install -r requirements.txt

# .env が無ければ作成（例）
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=jobmatch
# DB_USER=devuser
# DB_PASSWORD=devpass
# SECRET_KEY=dev-secret
# ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000

uvicorn main:app --reload --port 8000
```

## 3) フロントエンド起動
```bash
cd frontend
npm install
# MSWモックを無効化（デフォルト false）
# VITE_API_BASE_URL=http://localhost:8000/api
# VITE_USE_MOCK=false
npm run dev
```

ブラウザで: http://localhost:5173

## 求職者の動作確認フロー
1. /register で「求職者(seeker)」として新規登録
2. /preferences で希望条件を入力して保存
3. /chat で初回質問 → 回答 → スコアリング → 求人提案

