# AI求人マッチング（統合版）

このフォルダは、以下2つのzipを統合して **求職者フロー（登録→希望条件→チャット→求人提案）** が動くように接続したものです。

- frontend: Vite + React
- backend: FastAPI + Postgres

---

## 1) 前提

- Node.js 18+（推奨）
- Python 3.11+
- Postgres
- OpenAI API Key（チャットの質問生成に利用）

---

## 2) DBセットアップ

1. PostgresにDBを作成
2. `backend/db_schema_complete.sql` を実行
3. （推奨）チャットセッション用テーブルを作る場合は `backend/create_chat_sessions.sql` を実行

> ※ 既存DBがある場合は、テーブル差分に注意してください。

---

## 3) バックエンド起動

### 3-1. 環境変数

`backend/.env` を作成し、最低限以下を設定してください。

```bash
# DB
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=YOUR_DB
DATABASE_USER=YOUR_USER
DATABASE_PASSWORD=YOUR_PASS

# OpenAI
OPENAI_API_KEY=YOUR_OPENAI_KEY

# JWT
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS（フロントのURLを許可）
ALLOWED_ORIGINS=http://localhost:5173
```

### 3-2. 起動

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 4) フロントエンド起動

フロントは `frontend/.env` にローカルのAPIを向ける設定を入れています。

```bash
cd frontend
npm i
npm run dev
```

ブラウザで `http://localhost:5173` を開いてください。

---

## 5) 求職者の動作確認手順

1. 新規登録（求職者）
2. 希望条件入力（職種/勤務地/年収 など）
3. チャットへ遷移 → **初回表示時にバックエンドへ「初回接続」を送信**し、希望条件を考慮した初期質問を取得
4. 質問へ回答し続けると、一定条件で求人提案（右側にカード表示）

---

## 6) 主な修正点（接続内容）

### フロントエンド

- `VITE_API_BASE_URL=http://localhost:8000/api` に統一
- 認証/希望条件保存/チャット呼び出しをバックエンドに合わせて変換
  - 登録: `POST /api/user/register`
  - ログイン: `POST /api/user/login`
  - 希望条件保存: `POST /api/user/preferences`
  - チャット: `POST /api/user/chat`（初回は message=`初回接続`）

### バックエンド

- 既存の `user_preferences_profile` スキーマに合わせて、プロフィール取得/おすすめ取得のクエリを修正
- SPAから使えるように、チャットAPIはBearerトークン認証で動くように修正
- `POST /api/user/preferences` を追加
- CORSデフォルトに `http://localhost:5173` を追加

---

## 7) 1つのリポジトリとして運用する場合

このフォルダ構成のまま、Gitで管理できます。

- `backend/`
- `frontend/`

Docker化や、同時起動（concurrentlyなど）も可能です。

