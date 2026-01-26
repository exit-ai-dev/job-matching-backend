# exitotrinity - API設計リファレンス

## 目次
1. [プロジェクト概要](#プロジェクト概要)
2. [アーキテクチャ](#アーキテクチャ)
3. [APIエンドポイント一覧](#apiエンドポイント一覧)
4. [型定義](#型定義)
5. [認証フロー](#認証フロー)
6. [環境変数](#環境変数)

---

## プロジェクト概要

**プロジェクト名**: exitotrinity（エグジトトリニティ）
**種別**: AI求人マッチングプラットフォーム
**対象ユーザー**: 求職者（seeker）と企業（employer）

### 技術スタック

**フロントエンド**:
- React 19 + TypeScript + Vite
- TailwindCSS 4
- Zustand（状態管理）
- TanStack Query（データフェッチング）
- React Hook Form + Zod（フォーム管理）
- LINE LIFF SDK（LINE連携）
- Axios（HTTP クライアント）

**バックエンド**:
- FastAPI (Python)
- SQLite（デフォルトDB）
- SQLAlchemy（ORM）
- JWT認証
- OpenAI API（AIマッチング/チャット）

**ホスティング**:
- フロントエンド: Azure Static Web Apps
- バックエンド: Azure App Service

---

## アーキテクチャ

```
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│                 │        │                 │        │                 │
│  React SPA      │◄──────►│  FastAPI        │◄──────►│  OpenAI API     │
│  (Frontend)     │  REST  │  (Backend)      │        │                 │
│                 │  /api  │                 │        └─────────────────┘
└─────────────────┘        └─────────────────┘
        │                          │
        │                          │
        ▼                          ▼
┌─────────────────┐        ┌─────────────────┐
│ Azure Static    │        │  SQLite DB      │
│ Web Apps        │        │                 │
└─────────────────┘        └─────────────────┘
        │
        ▼
┌─────────────────┐
│  LINE LIFF      │
│                 │
└─────────────────┘
```

### データフロー

1. **認証フロー**: ユーザー登録/ログイン → JWT トークン発行 → localStorage保存
2. **API リクエスト**: すべてのリクエストにBearerトークンを付与
3. **401エラー時**: 自動ログアウト → ログイン画面へリダイレクト

---

## APIエンドポイント一覧

### ベースURL

```
開発環境: http://localhost:8000
本番環境: https://your-backend-url.azurewebsites.net
```

### 1. 認証API (`/auth/*`)

#### POST `/auth/register`
新規ユーザー登録

**リクエスト**:
```typescript
{
  email: string;
  password: string;
  name: string;
  role: 'seeker' | 'employer';
  companyName?: string;  // 企業の場合のみ
  industry?: string;     // 企業の場合のみ
}
```

**レスポンス**: `AuthResponse`
```typescript
{
  user: User;
  token: {
    accessToken: string;
    tokenType: string;
    expiresIn: number;
  };
}
```

#### POST `/auth/login`
ログイン

**リクエスト**:
```typescript
{
  email: string;
  password: string;
}
```

**レスポンス**: `AuthResponse`

#### POST `/auth/line/link`
LINE アカウント連携

**リクエスト**:
```typescript
{
  lineUserId: string;
  lineDisplayName: string;
  linePictureUrl?: string;
  lineEmail?: string;
}
```

**レスポンス**: `AuthResponse`

#### POST `/auth/line/login`
LINE ログイン

**リクエスト**: `LineAuthData`
**レスポンス**: `AuthResponse`

#### GET `/auth/me`
現在のユーザー情報取得

**ヘッダー**: `Authorization: Bearer {token}`
**レスポンス**: `AuthResponse`

#### POST `/auth/logout`
ログアウト

**ヘッダー**: `Authorization: Bearer {token}`
**レスポンス**: `void`

---

### 2. 求人API (`/jobs/*`)

#### GET `/jobs/`
求人一覧取得

**クエリパラメータ**:
- `page?: number` - ページ番号（デフォルト: 1）
- `perPage?: number` - 1ページあたりの件数（デフォルト: 10）

**レスポンス**:
```typescript
{
  jobs: Job[];
  total: number;
  page: number;
  perPage: number;
}
```

#### GET `/jobs/{jobId}`
求人詳細取得

**パスパラメータ**:
- `jobId: string` - 求人ID

**レスポンス**: `Job`

#### POST `/jobs/search`
求人検索

**リクエスト**:
```typescript
{
  query?: string;           // フリーワード検索
  location?: string;        // 勤務地
  employmentType?: string;  // 雇用形態
  remote?: boolean;         // リモート可
  salaryMin?: number;       // 最低年収
  tags?: string[];          // 技術タグ
}
```

**レスポンス**: `JobListResponse`

---

### 3. 応募API (`/applications/*`)

#### GET `/applications/`
応募一覧取得

**ヘッダー**: `Authorization: Bearer {token}`
**レスポンス**:
```typescript
{
  applications: Application[];
  total: number;
}
```

#### GET `/applications/{applicationId}`
応募詳細取得

**パスパラメータ**:
- `applicationId: string` - 応募ID

**レスポンス**: `Application`

#### POST `/applications/`
応募作成

**リクエスト**:
```typescript
{
  jobId: string;
  message?: string;
  resumeSubmitted: boolean;
  portfolioSubmitted: boolean;
  coverLetter?: string;
}
```

**レスポンス**: `Application`

#### PUT `/applications/{applicationId}`
応募更新

**リクエスト**:
```typescript
{
  status?: string;
  notes?: string;
}
```

**レスポンス**: `Application`

---

### 4. ユーザー設定API (`/users/*`)

#### POST `/users/preferences`
希望条件保存（求職者のみ）

**リクエスト**:
```typescript
{
  salary?: number;
  jobType?: string[];
  desiredLocation?: string;
  desiredLocations?: string[];
  desiredEmploymentType?: string;
  answers?: Record<string, any>;
}
```

**レスポンス**: `void`

#### PUT `/users/profile`
プロフィール更新

**リクエスト**:
```typescript
{
  name?: string;
  // 求職者用フィールド
  skills?: string[];
  experienceYears?: string;
  desiredSalaryMin?: string;
  desiredSalaryMax?: string;
  desiredLocation?: string;
  desiredEmploymentType?: string;
  resumeUrl?: string;
  portfolioUrl?: string;
  // 企業用フィールド
  companyName?: string;
  industry?: string;
  companySize?: string;
  companyDescription?: string;
  companyWebsite?: string;
  companyLocation?: string;
  companyLogoUrl?: string;
}
```

**レスポンス**: `AuthResponse`

---

### 5. AIマッチング/チャットAPI (`/matching/*`)

#### POST `/matching/career-chat`
キャリア相談チャット

**リクエスト**:
```typescript
{
  message: string;
  conversation_history: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
  seeker_profile: {
    name?: string;
    skills: string[];
    experience?: string;
    education?: string;
    location?: string;
    desired_salary_min?: number;
    preferred_employment_types: string[];
  };
}
```

**レスポンス**:
```typescript
{
  reply: string;
}
```

---

## 型定義

### User

```typescript
interface User {
  id: string;
  email: string;
  name: string;
  role: 'seeker' | 'employer';
  lineLinked?: boolean;
  profileCompletion?: string;
  createdAt: string;

  // 求職者用フィールド
  skills?: string[];
  experienceYears?: string;
  desiredSalaryMin?: string;
  desiredSalaryMax?: string;
  desiredLocation?: string;
  desiredEmploymentType?: string;

  // 企業用フィールド
  companyName?: string;
  industry?: string;
  companySize?: string;
  companyDescription?: string;

  // LINE連携情報
  lineUserId?: string;
  lineDisplayName?: string;
  linePictureUrl?: string;
  lineEmail?: string;
}
```

### Job

```typescript
interface Job {
  id: string;
  title: string;              // 職種名
  company: string;            // 企業名
  location: string;           // 勤務地
  salary: string;             // 年収範囲（例: "500-800万円"）
  employmentType: string;     // 雇用形態
  remote: boolean;            // リモート可否
  matchScore?: number;        // マッチ度（0-100）
  tags: string[];             // 技術タグ
  description: string;        // 求人詳細
  requirements?: string[];    // 応募要件
  benefits?: string[];        // 福利厚生
  postedDate?: string;        // 投稿日
  featured: boolean;          // 注目求人フラグ
}
```

### Application

```typescript
interface Application {
  id: string;
  jobId: string;
  jobTitle: string;
  company: string;
  location: string;
  salary: string;
  matchScore?: number;
  status: string;             // ステータス（例: "書類選考中"）
  statusColor: string;        // ステータス色
  statusDetail?: string;
  appliedDate: string;        // 応募日
  lastUpdate: string;         // 最終更新日
  nextStep?: string;          // 次のステップ
  interviewDate?: string;     // 面接日
  message?: string;
  notes?: string;
  documents: {
    resume: boolean;
    portfolio: boolean;
    coverLetter: boolean;
  };
}
```

### AuthResponse

```typescript
interface AuthResponse {
  user: User;
  token: {
    accessToken: string;
    tokenType?: string;
    expiresIn: number;
  };
}
```

### ApiError

```typescript
interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
}
```

---

## 認証フロー

### トークン管理

**保存場所**: `localStorage`
- `auth-token`: JWT アクセストークン
- `auth-storage`: Zustand の認証状態

### リクエストインターセプター

すべてのAPIリクエストに自動でトークンを付与:

```typescript
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### レスポンスインターセプター

401エラー時の自動処理:

```typescript
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      // トークンをクリア
      localStorage.removeItem('auth-token');
      localStorage.removeItem('auth-storage');
      // ログイン画面へリダイレクト
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 認証フロー図

```
登録/ログイン
    ↓
POST /auth/register または /auth/login
    ↓
AuthResponse (user + token)
    ↓
localStorage に保存
    ↓
全API リクエストに Bearer トークン付与
    ↓
401 エラー → 自動ログアウト
```

---

## 環境変数

### フロントエンド (`.env`)

```bash
# バックエンドAPIのベースURL
VITE_API_BASE_URL=https://your-backend-url.azurewebsites.net

# LINE LIFF ID
VITE_LIFF_ID=your-liff-id
```

### バックエンド

```bash
# OpenAI API キー
OPENAI_API_KEY=sk-...

# データベース接続URL
DATABASE_URL=sqlite:///./exitotrinity.db

# JWT署名用の秘密鍵
JWT_SECRET_KEY=your-secret-key

# CORS許可オリジン
ALLOWED_ORIGINS=https://your-frontend-url.azurestaticapps.net
```

---

## エラーハンドリング

### 共通エラーレスポンス

```typescript
{
  message: string;           // エラーメッセージ
  errors?: {                 // バリデーションエラー詳細
    [field: string]: string[];
  };
}
```

### HTTPステータスコード

- `200 OK`: 成功
- `201 Created`: リソース作成成功
- `400 Bad Request`: リクエストエラー（バリデーションエラー等）
- `401 Unauthorized`: 未認証
- `403 Forbidden`: 権限不足
- `404 Not Found`: リソースが見つからない
- `500 Internal Server Error`: サーバーエラー

---

## API使用例

### 1. ユーザー登録

```typescript
import { authApi } from '@/shared/lib/api';

const register = async () => {
  try {
    const response = await authApi.register({
      email: 'user@example.com',
      password: 'password123',
      name: '山田太郎',
      role: 'seeker'
    });

    // トークンを保存
    localStorage.setItem('auth-token', response.token.accessToken);

    console.log('登録成功:', response.user);
  } catch (error) {
    console.error('登録失敗:', error);
  }
};
```

### 2. 求人検索

```typescript
import { jobsApi } from '@/shared/lib/api';

const searchJobs = async () => {
  try {
    const response = await jobsApi.searchJobs({
      query: 'React',
      location: '東京',
      remote: true,
      salaryMin: 5000000
    });

    console.log('検索結果:', response.jobs);
  } catch (error) {
    console.error('検索失敗:', error);
  }
};
```

### 3. AIチャット

```typescript
import { matchingApi } from '@/shared/lib/api';

const chat = async () => {
  try {
    const response = await matchingApi.careerChat({
      message: 'リモートワーク可能な求人を探しています',
      conversation_history: [],
      seeker_profile: {
        skills: ['React', 'TypeScript'],
        preferred_employment_types: ['正社員']
      }
    });

    console.log('AIの返信:', response.reply);
  } catch (error) {
    console.error('チャット失敗:', error);
  }
};
```

---

## 参考リンク

- [画面設計仕様書](./SCREEN_SPEC.md)
- [デザイン仕様書](../DESIGN_SPEC.md)
- [システムアーキテクチャ図](./system-architecture.html)
- [画面遷移図](./screen-flow.html)
