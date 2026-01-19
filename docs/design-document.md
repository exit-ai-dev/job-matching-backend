# 求人マッチングシステム WEB設計書

**バージョン**: 1.0
**作成日**: 2025年12月24日
**最終更新**: 2025年12月24日

---

## 目次

1. [プロジェクト概要](#1-プロジェクト概要)
2. [システム構成](#2-システム構成)
3. [機能一覧](#3-機能一覧)
4. [画面設計](#4-画面設計)
5. [API設計](#5-api設計)
6. [データベース設計](#6-データベース設計)
7. [認証・セキュリティ](#7-認証セキュリティ)
8. [外部API連携](#8-外部api連携)
9. [エラーハンドリング](#9-エラーハンドリング)
10. [インフラ構成](#10-インフラ構成)
11. [開発環境](#11-開発環境)

---

## 1. プロジェクト概要

### 1.1 システム概要

AI技術を活用した求人マッチングプラットフォーム。求職者と企業をマッチングし、最適な人材と求人の出会いをサポートする。

### 1.2 主な特徴

- **AIマッチング**: OpenAI APIを使用したスキルと求人の自動マッチング
- **チャット機能**: 会話ベースでの求人検索・候補者検索
- **LINE連携**: LINEアカウントでのログイン・通知機能
- **応募管理**: 応募状況の一元管理

### 1.3 対象ユーザー

- **求職者（Seeker）**: 転職・就職を希望する個人
- **企業（Employer）**: 採用活動を行う企業・人事担当者

### 1.4 技術スタック

**フロントエンド**
- React 18.3.1
- TypeScript 5.6.2
- Vite 6.0.1
- React Router 7.1.1
- Axios（HTTP通信）
- Tailwind CSS（スタイリング）

**バックエンド**
- Python 3.10+
- FastAPI 0.115.5
- SQLAlchemy 2.0.36（ORM）
- PostgreSQL / SQLite（データベース）
- OpenAI API（AI機能）
- LINE Messaging API（LINE連携）

**インフラ**
- Azure App Service（バックエンド）
- Azure Static Web Apps（フロントエンド）
- GitHub Actions（CI/CD）
- Docker（コンテナ化）

---

## 2. システム構成

### 2.1 システム構成図

```
┌─────────────────┐
│   ユーザー      │
│  (ブラウザ)     │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────┐
│ Azure Static Web Apps           │
│ (フロントエンド)                │
│ - React SPA                     │
│ - 静的ファイルホスティング      │
└────────┬────────────────────────┘
         │ HTTPS/REST API
         ▼
┌─────────────────────────────────┐
│ Azure App Service               │
│ (バックエンド)                  │
│ - FastAPI                       │
│ - Docker Container              │
└────────┬────────────────────────┘
         │
         ├─── PostgreSQL/SQLite (DB)
         │
         ├─── OpenAI API (AI機能)
         │
         └─── LINE Messaging API (通知)
```

### 2.2 アーキテクチャパターン

- **フロントエンド**: SPA（Single Page Application）
- **バックエンド**: RESTful API
- **データベース**: リレーショナルデータベース
- **認証**: JWT（JSON Web Token）ベース

---

## 3. 機能一覧

### 3.1 求職者機能

| 機能ID | 機能名 | 説明 | 優先度 |
|--------|--------|------|--------|
| F001 | 会員登録 | メールアドレスとパスワードで新規登録 | 高 |
| F002 | ログイン | メール/パスワードまたはLINEでログイン | 高 |
| F003 | プロフィール設定 | スキル、経験年数、希望条件の登録 | 高 |
| F004 | 求人検索 | キーワード、条件での求人検索 | 高 |
| F005 | AIチャット検索 | 会話形式での求人検索 | 中 |
| F006 | 求人詳細表示 | 求人の詳細情報表示 | 高 |
| F007 | 応募 | 求人への応募 | 高 |
| F008 | 応募管理 | 応募履歴の確認・管理 | 高 |
| F009 | スカウト受信 | 企業からのスカウト通知 | 中 |
| F010 | マイページ | ダッシュボード表示 | 中 |

### 3.2 企業機能

| 機能ID | 機能名 | 説明 | 優先度 |
|--------|--------|------|--------|
| E001 | 企業登録 | 企業情報の登録 | 高 |
| E002 | 求人投稿 | 求人情報の作成・公開 | 高 |
| E003 | 候補者検索 | AIチャットでの候補者検索 | 中 |
| E004 | 応募管理 | 応募者の確認・選考管理 | 高 |
| E005 | スカウト送信 | 候補者へのスカウト送信 | 中 |
| E006 | ダッシュボード | 採用状況の可視化 | 中 |

### 3.3 共通機能

| 機能ID | 機能名 | 説明 | 優先度 |
|--------|--------|------|--------|
| C001 | LINE連携 | LINEアカウントの連携 | 中 |
| C002 | 通知機能 | 応募・スカウトの通知 | 中 |
| C003 | ログアウト | セッションの終了 | 高 |

---

## 4. 画面設計

### 4.1 画面一覧

#### 4.1.1 共通画面

| 画面ID | 画面名 | パス | 説明 |
|--------|--------|------|------|
| S001 | ログイン | `/login` | ログイン画面 |
| S002 | 新規登録 | `/register` | 新規会員登録画面 |
| S003 | LINE認証 | `/line-callback` | LINE認証コールバック |

#### 4.1.2 求職者画面

| 画面ID | 画面名 | パス | 説明 |
|--------|--------|------|------|
| SK001 | ホーム | `/home` | ダッシュボード（統計表示） |
| SK002 | 求人検索 | `/jobs` | 求人一覧・検索画面 |
| SK003 | 求人詳細 | `/jobs/:id` | 求人の詳細情報 |
| SK004 | AIチャット | `/chat` | 会話型求人検索 |
| SK005 | 応募管理 | `/applications` | 応募履歴一覧 |
| SK006 | プロフィール | `/profile` | プロフィール編集 |
| SK007 | 希望条件設定 | `/preferences` | 希望条件の登録 |

#### 4.1.3 企業画面

| 画面ID | 画面名 | パス | 説明 |
|--------|--------|------|------|
| EM001 | ダッシュボード | `/home` | 採用状況ダッシュボード |
| EM002 | 求人管理 | `/jobs` | 求人の作成・編集・一覧 |
| EM003 | 候補者検索 | `/chat` | AIチャットで候補者検索 |
| EM004 | 応募者管理 | `/applications` | 応募者の選考管理 |

### 4.2 画面遷移図

```
[ログイン] ─┬─ 求職者として登録 ─→ [希望条件設定] ─→ [ホーム]
            │
            └─ 企業として登録 ─→ [ダッシュボード]

[ホーム(求職者)] ─┬─→ [求人検索] ─→ [求人詳細] ─→ [応募]
                  │
                  ├─→ [AIチャット] ─→ [求人詳細]
                  │
                  ├─→ [応募管理]
                  │
                  └─→ [プロフィール]

[ダッシュボード(企業)] ─┬─→ [求人管理]
                        │
                        ├─→ [候補者検索]
                        │
                        └─→ [応募者管理]
```

### 4.3 主要画面仕様

#### 4.3.1 ログイン画面 (S001)

**表示項目**
- メールアドレス入力欄
- パスワード入力欄
- ログインボタン
- LINE連携ボタン
- 新規登録リンク

**バリデーション**
- メールアドレス形式チェック
- パスワード必須チェック

**処理**
- `POST /api/auth/login`
- JWTトークンをlocalStorageに保存
- ホーム画面へ遷移

#### 4.3.2 求人検索画面 (SK002)

**表示項目**
- 検索キーワード入力
- フィルター（雇用形態、勤務地、働き方、年収、技術スタック）
- 求人カード一覧（タイトル、企業名、年収、勤務地、マッチ度）
- ページネーション

**処理**
- `GET /api/jobs/` - 求人一覧取得
- `POST /api/jobs/search` - 検索実行
- クライアント側フィルタリング

#### 4.3.3 AIチャット画面 (SK004 / EM003)

**表示項目**
- チャットメッセージエリア
- 入力欄
- 送信ボタン
- 検索結果カード（右側）

**処理**
- `POST /api/matching/career-chat` - AIチャット
- 会話履歴の保持
- リアルタイムメッセージ表示

---

## 5. API設計

### 5.1 API一覧

#### 5.1.1 認証API

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| POST | `/api/auth/register` | 新規登録 | 不要 |
| POST | `/api/auth/login` | ログイン | 不要 |
| POST | `/api/auth/line/link` | LINE連携 | 必要 |
| POST | `/api/auth/line/login` | LINEログイン | 不要 |
| GET | `/api/auth/me` | 現在のユーザー情報取得 | 必要 |
| POST | `/api/auth/logout` | ログアウト | 必要 |

#### 5.1.2 求人API

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/api/jobs/` | 求人一覧取得 | 必要 |
| GET | `/api/jobs/{job_id}` | 求人詳細取得 | 必要 |
| POST | `/api/jobs/search` | 求人検索 | 必要 |
| POST | `/api/jobs/` | 求人作成（企業） | 必要 |
| PUT | `/api/jobs/{job_id}` | 求人更新（企業） | 必要 |
| DELETE | `/api/jobs/{job_id}` | 求人削除（企業） | 必要 |

#### 5.1.3 応募API

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/api/applications/` | 応募一覧取得 | 必要 |
| GET | `/api/applications/{application_id}` | 応募詳細取得 | 必要 |
| POST | `/api/applications/` | 応募作成 | 必要 |
| PUT | `/api/applications/{application_id}` | 応募更新 | 必要 |

#### 5.1.4 ユーザー設定API

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| POST | `/api/users/preferences` | 希望条件保存 | 必要 |
| PUT | `/api/users/profile` | プロフィール更新 | 必要 |

#### 5.1.5 マッチングAPI

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| POST | `/api/matching/career-chat` | キャリア相談チャット | 必要 |

### 5.2 API仕様詳細

#### 5.2.1 ログインAPI

**エンドポイント**: `POST /api/auth/login`

**リクエスト**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**レスポンス（200 OK）**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "山田太郎",
    "role": "seeker",
    "lineLinked": false,
    "profileCompletion": "80",
    "createdAt": "2025-12-24T00:00:00Z",
    "skills": ["React", "TypeScript"],
    "experienceYears": "3-5年",
    "desiredSalaryMin": "500",
    "desiredSalaryMax": "800"
  },
  "token": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "expiresIn": 1800
  }
}
```

**エラーレスポンス（401 Unauthorized）**
```json
{
  "detail": "メールアドレスまたはパスワードが正しくありません"
}
```

#### 5.2.2 求人検索API

**エンドポイント**: `POST /api/jobs/search`

**リクエスト**
```json
{
  "query": "React エンジニア",
  "location": "東京都",
  "employmentType": "正社員",
  "remote": true,
  "salaryMin": 5000000,
  "tags": ["React", "TypeScript"]
}
```

**レスポンス（200 OK）**
```json
{
  "jobs": [
    {
      "id": "job-uuid",
      "title": "フロントエンドエンジニア",
      "company": "株式会社テックカンパニー",
      "location": "東京都渋谷区",
      "salary": "500-800万円",
      "employmentType": "正社員",
      "remote": true,
      "matchScore": 92,
      "tags": ["React", "TypeScript", "AWS"],
      "description": "...",
      "requirements": ["React 3年以上"],
      "benefits": ["リモート可", "フレックス"],
      "postedDate": "2025-12-20",
      "featured": false
    }
  ],
  "total": 10,
  "page": 1,
  "perPage": 20
}
```

#### 5.2.3 キャリアチャットAPI

**エンドポイント**: `POST /api/matching/career-chat`

**リクエスト**
```json
{
  "message": "年収500万円以上、リモート可能、Reactの求人を探しています",
  "conversation_history": [
    {
      "role": "user",
      "content": "こんにちは"
    },
    {
      "role": "assistant",
      "content": "どのような仕事をお探しですか？"
    }
  ],
  "seeker_profile": {
    "skills": ["React", "TypeScript"],
    "experience": "3-5年",
    "location": "東京都",
    "desired_salary_min": 5000000,
    "preferred_employment_types": ["正社員"]
  }
}
```

**レスポンス（200 OK）**
```json
{
  "reply": "承知しました。年収500万円以上、リモート可能、Reactを使用する求人をお探しですね。\n\nあなたのスキルとマッチする求人をいくつか見つけました。右側に表示していますので、ご確認ください。"
}
```

---

## 6. データベース設計

### 6.1 ER図

```
┌─────────────┐       ┌─────────────┐
│   Users     │       │    Jobs     │
├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │
│ email       │       │ employer_id │────┐
│ password    │       │ title       │    │
│ name        │       │ description │    │
│ role        │       │ requirements│    │
│ skills      │       │ location    │    │
│ created_at  │       │ salary_min  │    │
└──────┬──────┘       │ salary_max  │    │
       │              │ remote      │    │
       │              │ created_at  │    │
       │              └──────┬──────┘    │
       │                     │           │
       │                     │           │
       │              ┌──────▼──────┐    │
       │              │Applications │    │
       │              ├─────────────┤    │
       │              │ id (PK)     │    │
       └──────────────┤ user_id (FK)│    │
                      │ job_id (FK) │────┘
                      │ status      │
                      │ message     │
                      │ applied_at  │
                      └─────────────┘
```

### 6.2 テーブル定義

#### 6.2.1 users テーブル

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | VARCHAR(36) | NO | UUID | ユーザーID（主キー） |
| email | VARCHAR(255) | NO | - | メールアドレス（ユニーク） |
| password_hash | VARCHAR(255) | NO | - | パスワードハッシュ |
| name | VARCHAR(100) | NO | - | 氏名 |
| role | ENUM | NO | - | ロール（seeker/employer） |
| skills | TEXT | YES | NULL | スキル（JSON配列） |
| experience_years | VARCHAR(50) | YES | NULL | 経験年数 |
| desired_salary_min | VARCHAR(50) | YES | NULL | 希望年収（下限） |
| desired_salary_max | VARCHAR(50) | YES | NULL | 希望年収（上限） |
| desired_location | VARCHAR(100) | YES | NULL | 希望勤務地 |
| desired_employment_type | VARCHAR(50) | YES | NULL | 希望雇用形態 |
| company_name | VARCHAR(200) | YES | NULL | 企業名（企業の場合） |
| industry | VARCHAR(100) | YES | NULL | 業種（企業の場合） |
| company_size | VARCHAR(50) | YES | NULL | 企業規模 |
| company_description | TEXT | YES | NULL | 企業説明 |
| line_user_id | VARCHAR(100) | YES | NULL | LINE User ID |
| line_display_name | VARCHAR(100) | YES | NULL | LINE表示名 |
| line_picture_url | TEXT | YES | NULL | LINEプロフィール画像URL |
| line_email | VARCHAR(255) | YES | NULL | LINEメールアドレス |
| profile_completion | VARCHAR(10) | YES | "0" | プロフィール完成度（%） |
| is_active | BOOLEAN | NO | TRUE | アカウント有効フラグ |
| last_login_at | TIMESTAMP | YES | NULL | 最終ログイン日時 |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY: `id`
- UNIQUE: `email`
- INDEX: `role`
- INDEX: `line_user_id`

#### 6.2.2 jobs テーブル

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | VARCHAR(36) | NO | UUID | 求人ID（主キー） |
| employer_id | VARCHAR(36) | NO | - | 企業ID（外部キー） |
| title | VARCHAR(200) | NO | - | 求人タイトル |
| description | TEXT | NO | - | 求人説明 |
| requirements | TEXT | YES | NULL | 応募要件（JSON配列） |
| benefits | TEXT | YES | NULL | 福利厚生（JSON配列） |
| location | VARCHAR(100) | NO | - | 勤務地 |
| salary_min | INTEGER | YES | NULL | 年収下限 |
| salary_max | INTEGER | YES | NULL | 年収上限 |
| employment_type | VARCHAR(50) | NO | - | 雇用形態 |
| remote | BOOLEAN | NO | FALSE | リモート可否 |
| tags | TEXT | YES | NULL | タグ（JSON配列） |
| is_active | BOOLEAN | NO | TRUE | 公開フラグ |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY: `id`
- FOREIGN KEY: `employer_id` REFERENCES `users(id)`
- INDEX: `is_active`
- INDEX: `location`
- INDEX: `employment_type`

#### 6.2.3 applications テーブル

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | VARCHAR(36) | NO | UUID | 応募ID（主キー） |
| user_id | VARCHAR(36) | NO | - | 求職者ID（外部キー） |
| job_id | VARCHAR(36) | NO | - | 求人ID（外部キー） |
| status | VARCHAR(50) | NO | "pending" | ステータス |
| message | TEXT | YES | NULL | 応募メッセージ |
| resume_submitted | BOOLEAN | NO | FALSE | 履歴書提出済み |
| portfolio_submitted | BOOLEAN | NO | FALSE | ポートフォリオ提出済み |
| cover_letter | TEXT | YES | NULL | 志望動機 |
| notes | TEXT | YES | NULL | メモ |
| applied_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 応募日時 |
| updated_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 更新日時 |

**インデックス**
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` REFERENCES `users(id)`
- FOREIGN KEY: `job_id` REFERENCES `jobs(id)`
- INDEX: `status`
- UNIQUE: `user_id, job_id`

---

## 7. 認証・セキュリティ

### 7.1 認証方式

**JWT（JSON Web Token）ベース認証**

- トークン生成: ログイン時にサーバーがJWTを発行
- トークン保存: フロントエンドはlocalStorageに保存
- トークン送信: リクエストヘッダー `Authorization: Bearer <token>`
- トークン有効期限: 30分
- アルゴリズム: HS256

### 7.2 パスワード管理

- ハッシュ化: bcrypt
- ソルト: 自動生成
- 最小長: 8文字（フロントエンドバリデーション）

### 7.3 CORS設定

**許可オリジン**
```
https://gray-sky-0b7ccbf00.6.azurestaticapps.net
http://localhost:5173
```

**許可メソッド**
```
GET, POST, PUT, DELETE, OPTIONS, PATCH
```

**許可ヘッダー**
```
Accept, Accept-Language, Content-Type, Authorization, Origin, X-Requested-With
```

**認証情報の送信**: 許可（`credentials: true`）

### 7.4 APIセキュリティ

1. **認証が必要なエンドポイント**
   - すべてのユーザー固有のデータAPI
   - 作成・更新・削除操作

2. **認証不要なエンドポイント**
   - `/api/auth/register`
   - `/api/auth/login`
   - `/api/auth/line/login`

3. **ロールベースアクセス制御**
   - 求職者: 自分の応募のみ操作可能
   - 企業: 自社の求人・応募者のみ操作可能

### 7.5 データ保護

- **環境変数管理**: 機密情報は`.env`ファイルで管理（Gitには含めない）
- **APIキー**: OpenAI API Keyは環境変数で設定
- **データベース接続情報**: 環境変数で管理

---

## 8. 外部API連携

### 8.1 OpenAI API

**目的**: AIマッチング、チャット機能

**使用モデル**
- テキスト生成: `gpt-4o-mini`
- 埋め込み: `text-embedding-3-small`

**主な用途**
- キャリア相談チャット
- スキルと求人のマッチングスコア計算
- 自然言語での求人検索

**設定**
```python
OPENAI_API_KEY=sk-proj-...
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

**エラーハンドリング**
- APIキー無効: 401エラー
- レート制限: 429エラー → リトライ処理
- タイムアウト: 30秒

### 8.2 LINE Messaging API

**目的**: LINE連携、通知配信

**使用機能**
- LIFF（LINE Front-end Framework）
- Messaging API

**LINE連携フロー**
1. ユーザーがLINE連携ボタンをクリック
2. LIFFで認証
3. LINE User IDを取得
4. バックエンドのユーザーアカウントと紐付け

**設定**
```
VITE_LINE_LIFF_ID=（フロントエンド環境変数）
```

---

## 9. エラーハンドリング

### 9.1 HTTPステータスコード

| コード | 意味 | 使用場面 |
|-------|------|---------|
| 200 | OK | リクエスト成功 |
| 201 | Created | リソース作成成功 |
| 400 | Bad Request | バリデーションエラー |
| 401 | Unauthorized | 認証エラー |
| 403 | Forbidden | 権限エラー |
| 404 | Not Found | リソース未発見 |
| 500 | Internal Server Error | サーバーエラー |

### 9.2 エラーレスポンス形式

```json
{
  "detail": "エラーメッセージ",
  "errors": {
    "email": ["メールアドレスは必須です"],
    "password": ["パスワードは8文字以上必要です"]
  }
}
```

### 9.3 フロントエンドエラーハンドリング

**Axios インターセプター**
```typescript
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      // 未認証の場合、ログインページへリダイレクト
      localStorage.removeItem('auth-token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 9.4 主要エラーメッセージ

| エラー内容 | メッセージ |
|-----------|-----------|
| ログイン失敗 | メールアドレスまたはパスワードが正しくありません |
| メール重複 | このメールアドレスは既に登録されています |
| トークン期限切れ | セッションが期限切れです。再度ログインしてください |
| 権限エラー | この操作を実行する権限がありません |
| データ取得失敗 | データの取得に失敗しました |
| API接続エラー | サーバーに接続できません |

---

## 10. インフラ構成

### 10.1 Azure構成

**フロントエンド: Azure Static Web Apps**
- URL: `https://gray-sky-0b7ccbf00.6.azurestaticapps.net`
- デプロイ方法: GitHub Actions（自動デプロイ）
- 設定ファイル: `.github/workflows/azure-static-web-apps.yml`

**バックエンド: Azure App Service**
- URL: `https://job-ai-app-affnfdgqbue2euf0.japanwest-01.azurewebsites.net`
- リージョン: Japan West
- デプロイ方法: Docker Container（GitHub Container Registry）
- 設定ファイル: `.github/workflows/azure-container.yml`

### 10.2 環境変数

**バックエンド（Azure App Service）**
```
CORS_ORIGINS=https://gray-sky-0b7ccbf00.6.azurestaticapps.net,http://localhost:5173
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=sqlite:///./job_matching.db
SECRET_KEY=（JWT署名用シークレットキー）
```

**フロントエンド（Azure Static Web Apps）**
```
VITE_API_BASE_URL=https://job-ai-app-affnfdgqbue2euf0.japanwest-01.azurewebsites.net/api
VITE_LINE_LIFF_ID=（LINE LIFF ID）
```

### 10.3 CI/CDパイプライン

**フロントエンド**
1. `main`ブランチへのpush
2. GitHub Actions起動
3. `npm run build`
4. Azure Static Web Appsへデプロイ

**バックエンド**
1. `main`ブランチへのpush
2. GitHub Actions起動
3. Dockerイメージビルド
4. GitHub Container Registryへpush
5. Azure App Serviceへデプロイ

### 10.4 データベース

**現在**: SQLite（開発・検証用）
```
DATABASE_URL=sqlite:///./job_matching.db
```

**本番推奨**: PostgreSQL
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

---

## 11. 開発環境

### 11.1 必要なツール

**共通**
- Git
- GitHub アカウント
- Azure アカウント

**フロントエンド**
- Node.js 18.x以上
- npm または yarn
- Visual Studio Code（推奨）

**バックエンド**
- Python 3.10以上
- pip
- Docker Desktop（コンテナ化用）

### 11.2 ローカル開発手順

**フロントエンド**
```bash
cd job-matching-frontend
npm install
npm run dev
# http://localhost:5173 で起動
```

**バックエンド**
```bash
cd job-matching-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# http://localhost:8000 で起動
```

### 11.3 環境設定ファイル

**フロントエンド: `.env`**
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_LINE_LIFF_ID=
```

**バックエンド: `.env`**
```
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=sqlite:///./job_matching.db
CORS_ORIGINS=http://localhost:5173
SECRET_KEY=your-secret-key-here
```

---

## 付録

### A. 用語集

| 用語 | 説明 |
|-----|------|
| SPA | Single Page Application - ページ遷移なしで動作するWebアプリ |
| REST API | HTTPメソッドを使用したAPI設計スタイル |
| JWT | JSON Web Token - トークンベース認証方式 |
| CORS | Cross-Origin Resource Sharing - オリジン間リソース共有 |
| ORM | Object-Relational Mapping - オブジェクトとDBのマッピング |
| LIFF | LINE Front-end Framework - LINE内で動作するWebアプリ |

### B. 参考リンク

- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)
- [React ドキュメント](https://react.dev/)
- [OpenAI API ドキュメント](https://platform.openai.com/docs)
- [Azure ドキュメント](https://docs.microsoft.com/azure/)

### C. 変更履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|---------|--------|
| 1.0 | 2025-12-24 | 初版作成 | Claude Code |

---

**文書終了**
