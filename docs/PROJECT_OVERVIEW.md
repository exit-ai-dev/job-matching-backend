# exitotrinity Backend - プロジェクト概要

> **新規セッション開始時は必ずこのドキュメントから読むこと**

## クイックリファレンス

| 項目 | 内容 |
|------|------|
| プロジェクト名 | exitotrinity Backend |
| 種別 | AI求人マッチングプラットフォーム バックエンドAPI |
| フレームワーク | FastAPI (Python 3.10+) |
| データベース | PostgreSQL (本番) / SQLite (開発) |
| AI/ML | OpenAI API + Sentence Transformers |
| ホスティング | Azure App Service |
| 認証 | JWT + LINE LIFF |

---

## 📚 重要ドキュメント一覧

新規セッション時は以下の順序で読むことを推奨:

1. **このドキュメント** - プロジェクト全体像を把握
2. **[BACKEND_API_REFERENCE.md](./BACKEND_API_REFERENCE.md)** - API実装の詳細
3. **[database_schema_complete.md](../database_schema_complete.md)** - データベーススキーマ
4. **[design-document.md](./design-document.md)** - システム設計書
5. **[AZURE_DEPLOYMENT.md](../AZURE_DEPLOYMENT.md)** - デプロイ手順

---

## プロジェクト構成

```
job-matching-backend/
├── app/                          # アプリケーションコード
│   ├── api/
│   │   └── endpoints/            # APIエンドポイント
│   │       ├── auth.py           # 認証（登録、ログイン、LINE連携）
│   │       ├── users.py          # ユーザー管理（プロフィール、希望条件）
│   │       ├── jobs.py           # 求人API（検索、詳細）
│   │       ├── matching.py       # マッチングAPI（AIチャット）
│   │       ├── applications.py   # 応募管理
│   │       ├── scouts.py         # スカウト機能
│   │       ├── conversation.py   # 会話履歴
│   │       └── employer.py       # 企業向け機能
│   ├── core/                     # コア機能
│   │   ├── config.py             # 設定管理（環境変数）
│   │   ├── dependencies.py       # 依存性注入（CurrentUser等）
│   │   ├── exceptions.py         # カスタム例外
│   │   └── logging.py            # ログ設定
│   ├── db/                       # データベース
│   │   ├── base.py               # Base定義
│   │   └── session.py            # セッション管理
│   ├── ml/                       # 機械学習サービス
│   │   ├── conversation_service.py  # OpenAI会話AI
│   │   ├── embedding_service.py     # 埋め込みベクトル生成
│   │   └── matching_service.py      # マッチングアルゴリズム
│   ├── models/                   # SQLAlchemyモデル
│   │   ├── user.py               # Userモデル
│   │   ├── job.py                # Jobモデル
│   │   ├── application.py        # Applicationモデル
│   │   └── scout.py              # Scoutモデル
│   ├── schemas/                  # Pydanticスキーマ
│   │   ├── auth.py               # 認証リクエスト/レスポンス
│   │   ├── job.py                # 求人スキーマ
│   │   ├── application.py        # 応募スキーマ
│   │   └── user.py               # ユーザースキーマ
│   ├── services/                 # ビジネスロジック
│   └── main.py                   # FastAPIアプリケーション
├── docs/                         # ドキュメント
│   ├── PROJECT_OVERVIEW.md       # このファイル
│   ├── BACKEND_API_REFERENCE.md  # API実装リファレンス
│   └── design-document.md        # システム設計書
├── data/                         # データファイル（ダミーデータ等）
├── requirements.txt              # 依存パッケージ
├── Dockerfile                    # Dockerイメージ定義
├── .env                          # 環境変数
└── init_db.py                    # DB初期化スクリプト
```

---

## 主要機能

### 1. 認証機能 (`/api/auth`)

- メール+パスワード認証
- JWT トークン発行・検証
- LINE LIFF 連携
- パスワードハッシュ化（bcrypt）

**実装**: `app/api/endpoints/auth.py`

### 2. 求人管理 (`/api/jobs`)

- 求人一覧取得
- 求人詳細取得
- 求人検索（フリーワード、条件指定）
- タグフィルタリング

**実装**: `app/api/endpoints/jobs.py`

### 3. AIマッチング (`/api/matching`)

- OpenAI GPT-4 を使用したキャリア相談チャット
- Sentence Transformers による埋め込みベクトル生成
- コサイン類似度によるマッチングスコア算出
- ユーザープロフィールベースのパーソナライズ

**実装**:
- `app/api/endpoints/matching.py`
- `app/ml/conversation_service.py`
- `app/ml/matching_service.py`

### 4. 応募管理 (`/api/applications`)

- 応募作成・一覧・詳細取得
- 応募ステータス管理
- 書類提出状況管理

**実装**: `app/api/endpoints/applications.py`

### 5. スカウト機能 (`/api/scouts`)

- 企業から求職者へのスカウト送信
- スカウト一覧・詳細取得
- ステータス管理（送信済み、既読、返信、承諾、辞退）

**実装**: `app/api/endpoints/scouts.py`

### 6. 企業向け機能 (`/api/employer`)

- 候補者検索
- 候補者一覧取得
- 求人管理（作成・編集・削除）

**実装**: `app/api/endpoints/employer.py`

---

## 技術スタック詳細

### コアフレームワーク

```python
FastAPI 0.115.5          # Webフレームワーク
Uvicorn 0.34.0           # ASGIサーバー
Pydantic 2.10.3          # データバリデーション
SQLAlchemy 2.0.36        # ORM
Alembic 1.14.0           # DBマイグレーション
```

### データベース

```python
psycopg[binary] 3.2.3    # PostgreSQLドライバ
# または SQLite（開発環境）
```

### 認証・セキュリティ

```python
passlib[bcrypt] 1.7.4    # パスワードハッシュ化
python-jose 3.3.0        # JWT処理
```

### AI/ML

```python
openai 1.59.7            # OpenAI API
sentence-transformers 3.3.1  # 埋め込みベクトル
torch 2.6.0              # PyTorch（ML基盤）
scikit-learn 1.6.0       # 機械学習ユーティリティ
numpy 2.2.1              # 数値計算
```

---

## データベース設計

### 主要テーブル

#### users（ユーザー）

```sql
- id (PK)
- email (UNIQUE)
- password_hash
- name
- role (seeker/employer)
- line_user_id
- company_name (企業の場合)
- skills (JSON)
- desired_salary_min/max
- created_at/updated_at
```

#### jobs（求人）

```sql
- id (PK)
- title
- company
- location
- salary_min/max
- employment_type
- remote (boolean)
- tags (JSON)
- description
- requirements
- status (active/closed)
- created_at
```

#### applications（応募）

```sql
- id (PK)
- user_id (FK)
- job_id (FK)
- status (submitted/reviewing/interview/offered/rejected)
- resume_submitted
- applied_date
- last_update
```

#### scouts（スカウト）

```sql
- id (PK)
- employer_id (FK)
- seeker_id (FK)
- job_id (FK)
- message
- status (sent/viewed/replied/accepted/declined)
- sent_date
```

詳細は **[database_schema_complete.md](../database_schema_complete.md)** を参照。

---

## API設計

### RESTful設計原則

- リソース指向のURL設計
- HTTPメソッドの適切な使用（GET, POST, PUT, DELETE）
- ステータスコードの適切な返却
- JSON形式のリクエスト/レスポンス

### 認証フロー

```
1. POST /api/auth/register または /api/auth/login
   ↓
2. JWT トークン取得
   {
     "user": {...},
     "token": {
       "accessToken": "...",
       "expiresIn": 86400
     }
   }
   ↓
3. 以降のリクエストにヘッダーで付与
   Authorization: Bearer {accessToken}
   ↓
4. バックエンドで検証
   - dependencies.py の CurrentUser
   - トークン検証・ユーザー取得
```

### エンドポイント命名規則

- 複数形を使用: `/api/jobs`, `/api/applications`
- 動詞は不要: ❌ `/api/get-jobs` → ✅ `/api/jobs`
- 階層構造: `/api/jobs/{job_id}/applications`

詳細は **[BACKEND_API_REFERENCE.md](./BACKEND_API_REFERENCE.md)** を参照。

---

## AI/MLアーキテクチャ

### 1. 会話AI（OpenAI GPT-4）

**実装**: `app/ml/conversation_service.py`

```python
class ConversationService:
    def career_chat(message, history, profile):
        # ユーザーメッセージとプロフィールを含むプロンプト生成
        # OpenAI APIコール
        # AIの返信を返す
```

**用途**:
- キャリア相談チャット
- 求人提案
- 候補者提案

### 2. 埋め込みベクトル（Sentence Transformers）

**実装**: `app/ml/embedding_service.py`

```python
class EmbeddingService:
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def generate_embedding(text):
        # テキスト→ベクトル変換
        return model.encode(text)
```

**用途**:
- スキルマッチング
- 求人説明文の埋め込み
- セマンティック検索

### 3. マッチングアルゴリズム

**実装**: `app/ml/matching_service.py`

```python
class MatchingService:
    def calculate_match_score(seeker, job):
        # スキル埋め込みの類似度
        # 希望条件との一致度
        # 総合スコア算出（0-100）
```

**マッチング要素**:
- スキルマッチ度（40%）
- 希望年収（20%）
- 勤務地（15%）
- 雇用形態（15%）
- リモート可否（10%）

---

## 環境変数

### 必須環境変数

```bash
# データベース
DATABASE_URL=postgresql://user:pass@host:5432/db

# JWT認証
SECRET_KEY=your-secret-key-256-bit
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=https://frontend.com,http://localhost:5173

# OpenAI
OPENAI_API_KEY=sk-...

# LINE（オプション）
LINE_CHANNEL_ACCESS_TOKEN=...
LINE_CHANNEL_SECRET=...
```

### 設定管理

**実装**: `app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Job Matching API"
    database_url: str
    secret_key: str
    openai_api_key: str
    # ...

    class Config:
        env_file = ".env"
```

---

## 開発ワークフロー

### ローカル開発

```bash
# 1. 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 依存パッケージインストール
pip install -r requirements.txt

# 3. 環境変数設定
cp .env.example .env
# .env を編集

# 4. データベース初期化
python init_db.py

# 5. 開発サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### APIドキュメント

開発サーバー起動後、以下のURLで自動生成されたAPIドキュメントを確認:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### テスト

```bash
# ユニットテスト
pytest tests/

# 特定のテストファイル
pytest tests/test_auth.py

# カバレッジ測定
pytest --cov=app tests/
```

---

## デプロイ

### Azure App Service

```bash
# 1. Azure CLI ログイン
az login

# 2. リソースグループ作成
az group create --name rg-job-matching --location japaneast

# 3. App Service Plan作成
az appservice plan create \
  --name plan-job-matching \
  --resource-group rg-job-matching \
  --sku B1 \
  --is-linux

# 4. Web App作成
az webapp create \
  --resource-group rg-job-matching \
  --plan plan-job-matching \
  --name app-job-matching \
  --runtime "PYTHON:3.10"

# 5. 環境変数設定
az webapp config appsettings set \
  --resource-group rg-job-matching \
  --name app-job-matching \
  --settings \
    DATABASE_URL="..." \
    SECRET_KEY="..." \
    OPENAI_API_KEY="..."

# 6. デプロイ
az webapp up --runtime PYTHON:3.10 --sku B1
```

詳細は **[AZURE_DEPLOYMENT.md](../AZURE_DEPLOYMENT.md)** を参照。

### Docker

```bash
# イメージビルド
docker build -t job-matching-backend .

# コンテナ起動
docker run -p 8000:8000 --env-file .env job-matching-backend

# Docker Compose
docker-compose up -d
```

---

## トラブルシューティング

### 1. データベース接続エラー

**症状**: `sqlalchemy.exc.OperationalError: could not connect to server`

**対処**:
1. `DATABASE_URL` を確認
2. PostgreSQLサーバーが起動しているか確認
3. ファイアウォール設定を確認

### 2. OpenAI APIエラー

**症状**: `openai.error.AuthenticationError`

**対処**:
1. `OPENAI_API_KEY` を確認
2. APIキーの有効期限を確認
3. レート制限を確認

### 3. CORSエラー

**症状**: フロントエンドから `CORS policy` エラー

**対処**:
1. `CORS_ORIGINS` にフロントエンドURLが含まれているか確認
2. URLの末尾の `/` に注意
3. `app/main.py` のCORS設定を確認

---

## パフォーマンス最適化

### 1. データベースクエリ最適化

```python
# N+1問題を避ける
from sqlalchemy.orm import joinedload

jobs = db.query(Job).options(
    joinedload(Job.applications)
).all()

# インデックス作成
from sqlalchemy import Index
Index('idx_user_email', User.email)
```

### 2. キャッシング

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_job_by_id(job_id: str, db: Session):
    return db.query(Job).filter(Job.id == job_id).first()
```

### 3. 非同期処理

```python
from fastapi import BackgroundTasks

@router.post("/send-email")
async def send_email(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_task, email)
    return {"message": "Email will be sent"}
```

---

## セキュリティ

### 1. パスワードセキュリティ

- bcrypt でハッシュ化
- ソルト自動生成
- 平文パスワード保存禁止

### 2. SQL インジェクション対策

- SQLAlchemy ORM使用
- 動的SQL禁止
- パラメータ化クエリ

### 3. JWT セキュリティ

- 強力な秘密鍵（256bit以上）
- 有効期限設定
- HTTPS通信必須

### 4. CORS設定

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 参考リンク

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Sentence Transformers](https://www.sbert.net/)
- [Azure App Service Python](https://docs.microsoft.com/azure/app-service/quickstart-python)

---

**最終更新**: 2026-01-18
