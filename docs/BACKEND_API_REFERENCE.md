# Backend API Reference

> **バックエンドAPI実装リファレンス**

## 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [技術スタック](#技術スタック)
3. [プロジェクト構成](#プロジェクト構成)
4. [APIエンドポイント](#apiエンドポイント)
5. [認証](#認証)
6. [データベース](#データベース)
7. [環境変数](#環境変数)
8. [開発・デプロイ](#開発デプロイ)

---

## プロジェクト概要

**プロジェクト名**: exitotrinity Backend
**種別**: AI求人マッチングプラットフォーム バックエンドAPI
**フレームワーク**: FastAPI (Python)

### 主要機能

- JWT認証 + LINE LIFF連携
- 求人検索・マッチング
- 応募管理
- AIチャット（OpenAI）
- スカウト機能
- 企業向け候補者管理

---

## 技術スタック

```
Python 3.10+
FastAPI 0.115.5
SQLAlchemy 2.0.36 (ORM)
Alembic 1.14.0 (マイグレーション)
PostgreSQL / SQLite
OpenAI API 1.59.7
Sentence Transformers 3.3.1
PyTorch 2.6.0
scikit-learn 1.6.0
bcrypt (パスワードハッシュ化)
python-jose (JWT)
```

---

## プロジェクト構成

```
job-matching-backend/
├── app/
│   ├── api/
│   │   └── endpoints/          # APIエンドポイント
│   │       ├── auth.py         # 認証
│   │       ├── users.py        # ユーザー管理
│   │       ├── jobs.py         # 求人（求職者向け）
│   │       ├── matching.py     # マッチング
│   │       ├── applications.py # 応募管理
│   │       ├── scouts.py       # スカウト
│   │       ├── conversation.py # 会話・チャット
│   │       └── employer.py     # 企業向け機能
│   ├── core/                   # コア機能
│   │   ├── config.py           # 設定管理
│   │   ├── dependencies.py     # 依存性注入
│   │   ├── exceptions.py       # カスタム例外
│   │   └── logging.py          # ログ設定
│   ├── db/                     # データベース
│   │   ├── base.py             # Base定義
│   │   └── session.py          # セッション管理
│   ├── ml/                     # 機械学習サービス
│   │   ├── conversation_service.py  # 会話AI
│   │   ├── embedding_service.py     # 埋め込みベクトル
│   │   └── matching_service.py      # マッチングロジック
│   ├── models/                 # SQLAlchemyモデル
│   │   ├── user.py             # ユーザーモデル
│   │   ├── job.py              # 求人モデル
│   │   ├── application.py      # 応募モデル
│   │   └── scout.py            # スカウトモデル
│   ├── schemas/                # Pydanticスキーマ
│   │   ├── auth.py             # 認証スキーマ
│   │   ├── job.py              # 求人スキーマ
│   │   ├── application.py      # 応募スキーマ
│   │   └── user.py             # ユーザースキーマ
│   ├── services/               # ビジネスロジック
│   └── main.py                 # アプリケーションエントリーポイント
├── docs/                       # ドキュメント
├── data/                       # データファイル
├── requirements.txt            # 依存パッケージ
├── Dockerfile                  # Dockerイメージ定義
└── .env                        # 環境変数
```

---

## APIエンドポイント

### ベースURL

```
本番: https://your-backend.azurewebsites.net
開発: http://localhost:8000
```

### エンドポイント一覧

#### 1. 認証API (`/api/auth`)

| エンドポイント | メソッド | 説明 | 認証 |
|--------------|---------|------|------|
| `/api/auth/register` | POST | ユーザー登録 | 不要 |
| `/api/auth/login` | POST | ログイン | 不要 |
| `/api/auth/line/link` | POST | LINE連携 | 必要 |
| `/api/auth/line/login` | POST | LINEログイン | 不要 |
| `/api/auth/me` | GET | 現在のユーザー情報取得 | 必要 |
| `/api/auth/logout` | POST | ログアウト | 必要 |

**実装**: `app/api/endpoints/auth.py`

#### 2. ユーザーAPI (`/api/users`)

| エンドポイント | メソッド | 説明 | 認証 |
|--------------|---------|------|------|
| `/api/users/preferences` | POST | 希望条件保存 | 必要 |
| `/api/users/profile` | PUT | プロフィール更新 | 必要 |
| `/api/users/profile` | GET | プロフィール取得 | 必要 |

**実装**: `app/api/endpoints/users.py`

#### 3. 求人API (`/api/jobs`)

| エンドポイント | メソッド | 説明 | 認証 |
|--------------|---------|------|------|
| `/api/jobs/` | GET | 求人一覧取得 | 不要 |
| `/api/jobs/{job_id}` | GET | 求人詳細取得 | 不要 |
| `/api/jobs/search` | POST | 求人検索 | 不要 |

**実装**: `app/api/endpoints/jobs.py`

#### 4. マッチングAPI (`/api/matching`)

| エンドポイント | メソッド | 説明 | 認証 |
|--------------|---------|------|------|
| `/api/matching/career-chat` | POST | キャリア相談チャット | 必要 |
| `/api/matching/jobs` | GET | マッチング求人取得 | 必要 |

**実装**: `app/api/endpoints/matching.py`

#### 5. 応募API (`/api/applications`)

| エンドポイント | メソッド | 説明 | 認証 |
|--------------|---------|------|------|
| `/api/applications/` | GET | 応募一覧取得 | 必要 |
| `/api/applications/{application_id}` | GET | 応募詳細取得 | 必要 |
| `/api/applications/` | POST | 応募作成 | 必要 |
| `/api/applications/{application_id}` | PUT | 応募更新 | 必要 |

**実装**: `app/api/endpoints/applications.py`

#### 6. スカウトAPI (`/api/scouts`)

| エンドポイント | メソッド | 説明 | 認証 |
|--------------|---------|------|------|
| `/api/scouts/` | GET | スカウト一覧取得 | 必要 |
| `/api/scouts/` | POST | スカウト送信 | 必要（企業のみ） |
| `/api/scouts/{scout_id}` | GET | スカウト詳細取得 | 必要 |
| `/api/scouts/{scout_id}` | PUT | スカウト更新 | 必要 |

**実装**: `app/api/endpoints/scouts.py`

#### 7. 会話API (`/api/conversation`)

| エンドポイント | メソッド | 説明 | 認証 |
|--------------|---------|------|------|
| `/api/conversation/send` | POST | メッセージ送信 | 必要 |
| `/api/conversation/history` | GET | 会話履歴取得 | 必要 |

**実装**: `app/api/endpoints/conversation.py`

#### 8. 企業API (`/api/employer`)

| エンドポイント | メソッド | 説明 | 認証 |
|--------------|---------|------|------|
| `/api/employer/candidates` | GET | 候補者一覧取得 | 必要（企業のみ） |
| `/api/employer/candidates/search` | POST | 候補者検索 | 必要（企業のみ） |
| `/api/employer/jobs` | GET | 求人管理一覧 | 必要（企業のみ） |
| `/api/employer/jobs` | POST | 求人作成 | 必要（企業のみ） |

**実装**: `app/api/endpoints/employer.py`

---

## 認証

### JWT認証フロー

```
1. ユーザー登録/ログイン
   ↓
2. JWT トークン発行
   {
     "sub": "user_id",
     "exp": expiration_timestamp
   }
   ↓
3. クライアントがリクエストヘッダーに付与
   Authorization: Bearer {token}
   ↓
4. バックエンドで検証
   - トークンの署名検証
   - 有効期限チェック
   - ユーザー存在確認
```

### パスワードハッシュ化

```python
# bcryptを使用
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
```

### トークン設定

- **有効期限**: 環境変数 `ACCESS_TOKEN_EXPIRE_MINUTES`（デフォルト: 1440分 = 24時間）
- **アルゴリズム**: HS256
- **シークレットキー**: 環境変数 `SECRET_KEY`

---

## データベース

### データベース構成

- **開発環境**: SQLite (`sqlite:///./exitotrinity.db`)
- **本番環境**: PostgreSQL

### 主要テーブル

#### users

```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    role VARCHAR NOT NULL,  -- 'seeker' or 'employer'
    line_user_id VARCHAR,
    line_linked BOOLEAN,
    company_name VARCHAR,
    industry VARCHAR,
    skills TEXT,  -- JSON配列
    experience_years VARCHAR,
    desired_salary_min INTEGER,
    desired_salary_max INTEGER,
    desired_location VARCHAR,
    desired_employment_type VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### jobs

```sql
CREATE TABLE jobs (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    company VARCHAR NOT NULL,
    location VARCHAR,
    salary_min INTEGER,
    salary_max INTEGER,
    salary_text VARCHAR,
    employment_type VARCHAR,  -- 'full_time', 'part_time', 'contract'
    remote BOOLEAN,
    tags TEXT,  -- JSON配列
    description TEXT,
    requirements TEXT,
    benefits TEXT,
    posted_date TIMESTAMP,
    status VARCHAR,  -- 'active', 'closed'
    featured BOOLEAN,
    created_at TIMESTAMP
);
```

#### applications

```sql
CREATE TABLE applications (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id),
    job_id VARCHAR REFERENCES jobs(id),
    status VARCHAR,  -- 'submitted', 'reviewing', 'interview', 'offered', 'rejected'
    message TEXT,
    resume_submitted BOOLEAN,
    portfolio_submitted BOOLEAN,
    cover_letter TEXT,
    applied_date TIMESTAMP,
    last_update TIMESTAMP
);
```

#### scouts

```sql
CREATE TABLE scouts (
    id VARCHAR PRIMARY KEY,
    employer_id VARCHAR REFERENCES users(id),
    seeker_id VARCHAR REFERENCES users(id),
    job_id VARCHAR REFERENCES jobs(id),
    message TEXT,
    status VARCHAR,  -- 'sent', 'viewed', 'replied', 'accepted', 'declined'
    sent_date TIMESTAMP,
    viewed_date TIMESTAMP
);
```

### マイグレーション

```bash
# マイグレーションファイル作成
alembic revision --autogenerate -m "migration message"

# マイグレーション実行
alembic upgrade head

# ロールバック
alembic downgrade -1
```

---

## 環境変数

### `.env` ファイル

```bash
# アプリケーション設定
APP_NAME=Job Matching API
APP_VERSION=1.0.0
ENV=production
DEBUG=false

# データベース
DATABASE_URL=postgresql://user:password@host:5432/dbname
# 開発環境
# DATABASE_URL=sqlite:///./exitotrinity.db

# JWT認証
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS設定
CORS_ORIGINS=https://your-frontend.azurestaticapps.net,http://localhost:5173
CORS_CREDENTIALS=true
CORS_METHODS=*
CORS_HEADERS=*

# OpenAI
OPENAI_API_KEY=sk-...

# LINE連携
LINE_CHANNEL_ACCESS_TOKEN=your-line-channel-access-token
LINE_CHANNEL_SECRET=your-line-channel-secret
```

### 必須環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `DATABASE_URL` | データベース接続URL | `postgresql://...` |
| `SECRET_KEY` | JWT署名用秘密鍵 | `your-secret-key` |
| `OPENAI_API_KEY` | OpenAI APIキー | `sk-...` |
| `CORS_ORIGINS` | CORS許可オリジン | `https://example.com` |

---

## 開発・デプロイ

### ローカル開発

```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージインストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .env を編集

# データベース初期化
python init_db.py

# 開発サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# イメージビルド
docker build -t job-matching-backend .

# コンテナ起動
docker run -p 8000:8000 --env-file .env job-matching-backend
```

### Azure App Service デプロイ

```bash
# Azure CLI でログイン
az login

# App Service作成
az webapp create --resource-group <rg-name> --plan <plan-name> --name <app-name> --runtime "PYTHON:3.10"

# 環境変数設定
az webapp config appsettings set --resource-group <rg-name> --name <app-name> --settings @appsettings.json

# デプロイ
az webapp up --runtime PYTHON:3.10 --sku B1
```

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/azure-webapp.yml
name: Deploy to Azure Web App

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: azure/webapps-deploy@v2
        with:
          app-name: your-app-name
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

---

## API使用例

### 1. ユーザー登録

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "山田太郎",
    "role": "seeker"
  }'
```

**レスポンス**:
```json
{
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "name": "山田太郎",
    "role": "seeker"
  },
  "token": {
    "accessToken": "jwt-token-here",
    "expiresIn": 86400
  }
}
```

### 2. 求人検索

```bash
curl -X POST http://localhost:8000/api/jobs/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "React",
    "location": "東京",
    "remote": true
  }'
```

### 3. AIチャット

```bash
curl -X POST http://localhost:8000/api/matching/career-chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "message": "リモートワーク可能な求人を探しています",
    "conversation_history": [],
    "seeker_profile": {
      "skills": ["React", "TypeScript"],
      "preferred_employment_types": ["正社員"]
    }
  }'
```

---

## エラーハンドリング

### 標準エラーレスポンス

```json
{
  "detail": "エラーメッセージ"
}
```

### HTTPステータスコード

- `200 OK`: 成功
- `201 Created`: リソース作成成功
- `400 Bad Request`: リクエストエラー
- `401 Unauthorized`: 未認証
- `403 Forbidden`: 権限不足
- `404 Not Found`: リソースが見つからない
- `422 Unprocessable Entity`: バリデーションエラー
- `500 Internal Server Error`: サーバーエラー

---

## パフォーマンス最適化

### データベースクエリ最適化

```python
# N+1問題を避ける
jobs = db.query(Job).options(
    joinedload(Job.applications)
).all()

# ページネーション
jobs = db.query(Job).offset(skip).limit(limit).all()
```

### キャッシング

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_job_by_id(job_id: str):
    # キャッシュされる
    pass
```

---

## セキュリティ

### CORS設定

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SQLインジェクション対策

- SQLAlchemy ORMを使用
- 動的SQL禁止

### パスワードセキュリティ

- bcryptでハッシュ化
- ソルト自動生成
- 平文パスワード保存禁止

---

## 参考リンク

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)

---

**最終更新**: 2026-01-18
