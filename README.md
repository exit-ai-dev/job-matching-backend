# exitotrinity Backend

AI求人マッチングプラットフォーム バックエンドAPI

## 📖 ドキュメント

**新規セッション開始時は必ず以下のドキュメントから読んでください:**

1. **[docs/PROJECT_OVERVIEW.md](./docs/PROJECT_OVERVIEW.md)** ⭐ **最初に読むこと**
   - プロジェクト全体像
   - 技術スタック
   - ディレクトリ構成
   - 開発ガイドライン

2. **[docs/BACKEND_API_REFERENCE.md](./docs/BACKEND_API_REFERENCE.md)**
   - 全APIエンドポイント実装
   - 認証フロー
   - データベース設計
   - 環境変数

3. **[database_schema_complete.md](./database_schema_complete.md)**
   - データベーススキーマ詳細
   - テーブル定義
   - リレーション

4. **[docs/design-document.md](./docs/design-document.md)**
   - システム設計書
   - 機能仕様

5. **[AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md)**
   - Azure App Service デプロイ手順
   - CI/CD設定

6. **[DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)**
   - Dockerコンテナデプロイ手順

---

## 🚀 クイックスタート

### 環境変数の設定

```bash
cp .env.example .env
```

`.env` ファイルを編集して以下を設定:

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-...
CORS_ORIGINS=https://your-frontend.com,http://localhost:5173
```

### ローカル開発

```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージインストール
pip install -r requirements.txt

# データベース初期化
python init_db.py

# 開発サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

APIドキュメント: http://localhost:8000/docs

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

## 🛠 技術スタック

**コアフレームワーク**:
- FastAPI 0.115.5
- Python 3.10+
- SQLAlchemy 2.0.36 (ORM)
- Alembic 1.14.0 (マイグレーション)

**データベース**:
- PostgreSQL (本番)
- SQLite (開発)

**AI/ML**:
- OpenAI API 1.59.7
- Sentence Transformers 3.3.1
- PyTorch 2.6.0
- scikit-learn 1.6.0

**認証**:
- JWT (python-jose)
- bcrypt (パスワードハッシュ化)

---

## 📁 プロジェクト構成

```
job-matching-backend/
├── app/                          # アプリケーションコード
│   ├── api/endpoints/            # APIエンドポイント
│   ├── core/                     # コア機能（設定、依存性、例外）
│   ├── db/                       # データベース
│   ├── ml/                       # 機械学習サービス
│   ├── models/                   # SQLAlchemyモデル
│   ├── schemas/                  # Pydanticスキーマ
│   ├── services/                 # ビジネスロジック
│   └── main.py                   # エントリーポイント
├── docs/                         # ドキュメント
├── data/                         # データファイル
├── requirements.txt              # 依存パッケージ
├── Dockerfile                    # Dockerイメージ定義
└── .env                          # 環境変数
```

---

## 📝 主要APIエンドポイント

| カテゴリ | エンドポイント | 説明 |
|---------|--------------|------|
| 認証 | `POST /api/auth/register` | ユーザー登録 |
| 認証 | `POST /api/auth/login` | ログイン |
| 認証 | `POST /api/auth/line/link` | LINE連携 |
| 認証 | `GET /api/auth/me` | ユーザー情報取得 |
| 求人 | `GET /api/jobs/` | 求人一覧 |
| 求人 | `GET /api/jobs/{id}` | 求人詳細 |
| 求人 | `POST /api/jobs/search` | 求人検索 |
| マッチング | `POST /api/matching/career-chat` | AIチャット |
| 応募 | `GET /api/applications/` | 応募一覧 |
| 応募 | `POST /api/applications/` | 応募作成 |
| スカウト | `GET /api/scouts/` | スカウト一覧 |
| 企業 | `GET /api/employer/candidates` | 候補者一覧 |

詳細は **[docs/BACKEND_API_REFERENCE.md](./docs/BACKEND_API_REFERENCE.md)** を参照。

---

## 🔑 環境変数

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `DATABASE_URL` | データベース接続URL | ✅ |
| `SECRET_KEY` | JWT署名用秘密鍵 | ✅ |
| `OPENAI_API_KEY` | OpenAI APIキー | ✅ |
| `CORS_ORIGINS` | CORS許可オリジン | ✅ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | トークン有効期限（分） | ❌ (デフォルト: 1440) |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging用トークン（通知機能用） | ❌ |
| `LINE_CHANNEL_SECRET` | LINE Messaging用シークレット（通知機能用） | ❌ |

⚠️ **注意**: LINE認証（ログイン・アカウント連携）はフロントエンドのLIFF IDで動作します。
バックエンドのLINE環境変数は、将来実装予定のLINE通知機能（メッセージ送信）でのみ必要です。

**LINE認証の設定**: フロントエンドの [docs/AZURE_LINE_SETUP.md](../job-matching-frontend/docs/AZURE_LINE_SETUP.md) を参照

---

## 🧪 テスト

```bash
# ユニットテスト
pytest tests/

# カバレッジ測定
pytest --cov=app tests/
```

---

## 🚢 デプロイ

### Azure App Service

```bash
az webapp up --runtime PYTHON:3.10 --sku B1
```

詳細は **[AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md)** を参照。

### Docker

```bash
docker build -t job-matching-backend .
docker run -p 8000:8000 --env-file .env job-matching-backend
```

詳細は **[DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)** を参照。

---

## 📚 参考リンク

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Azure App Service Python](https://docs.microsoft.com/azure/app-service/quickstart-python)

---

## 📄 ライセンス

All rights reserved.

---

**最終更新**: 2026-01-18
