# システム構成図・インターフェース図

## 目次
1. [システム全体構成図](#1-システム全体構成図)
2. [インフラ構成図（Azure）](#2-インフラ構成図azure)
3. [アプリケーションアーキテクチャ図](#3-アプリケーションアーキテクチャ図)
4. [データフロー図](#4-データフロー図)
5. [APIインターフェース図](#5-apiインターフェース図)
6. [認証フロー図](#6-認証フロー図)
7. [AIマッチング処理フロー図](#7-aiマッチング処理フロー図)
8. [会話チャット処理フロー図](#8-会話チャット処理フロー図)
9. [ER図（データベース）](#9-er図データベース)
10. [デプロイメントフロー図](#10-デプロイメントフロー図)

---

## 1. システム全体構成図

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[LINE App]
    end

    subgraph "Azure Cloud"
        subgraph "Frontend"
            C[Azure Static Web Apps<br/>React SPA]
        end

        subgraph "Backend"
            D[Azure App Service<br/>Docker Container<br/>FastAPI]
        end

        subgraph "Storage"
            E[Azure Blob Storage<br/>File Uploads]
            F[(Azure Database for PostgreSQL<br/>or SQLite)]
        end

        subgraph "Monitoring"
            G[Application Insights<br/>Logs & Metrics]
        end
    end

    subgraph "External Services"
        H[OpenAI API<br/>GPT-4o-mini<br/>text-embedding-3-small]
        I[LINE Platform<br/>LIFF SDK<br/>Messaging API]
        J[SendGrid<br/>Email Service]
    end

    A -->|HTTPS| C
    B -->|LIFF| C
    C -->|REST API<br/>CORS| D
    D -->|Read/Write| F
    D -->|Upload/Download| E
    D -->|Embeddings & Chat| H
    D -->|LINE Notifications| I
    D -->|Email Notifications| J
    D -->|Telemetry| G
    C -->|Telemetry| G

    style C fill:#e1f5ff
    style D fill:#ffe1e1
    style F fill:#fff4e1
    style H fill:#f0e1ff
    style I fill:#e1ffe1
    style J fill:#ffe1f0
```

---

## 2. インフラ構成図（Azure）

```mermaid
graph TB
    subgraph "Internet"
        USER[User Browser]
    end

    subgraph "Azure Cloud - Frontend"
        CDN[Azure CDN]
        STATIC[Azure Static Web Apps<br/>- React Build<br/>- Auto HTTPS<br/>- Custom Domain]
    end

    subgraph "Azure Cloud - Backend"
        APPSVC[Azure App Service<br/>- Linux Container<br/>- Auto Scale<br/>- Health Check]

        subgraph "Container"
            DOCKER[Docker Image<br/>- Python 3.10<br/>- FastAPI<br/>- Dependencies]
        end
    end

    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Flexible Server<br/>- SSL Required<br/>- Backup Enabled)]
        BLOB[Azure Blob Storage<br/>- Hot Tier<br/>- Resume Files<br/>- Portfolio Files]
        REDIS[Azure Redis Cache<br/>- Search Results<br/>- Embeddings]
    end

    subgraph "CI/CD"
        GH[GitHub Repository]
        GHACTION[GitHub Actions<br/>- Build Docker<br/>- Deploy Backend<br/>- Deploy Frontend]
    end

    subgraph "Monitoring & Security"
        INSIGHTS[Application Insights<br/>- Request Tracking<br/>- Exception Logging<br/>- Performance Metrics]
        KEYVAULT[Azure Key Vault<br/>- OpenAI API Key<br/>- DB Password<br/>- JWT Secret]
    end

    USER -->|HTTPS| CDN
    CDN --> STATIC
    STATIC -->|API Calls| APPSVC
    APPSVC --> DOCKER
    DOCKER --> DB
    DOCKER --> BLOB
    DOCKER --> REDIS
    DOCKER --> INSIGHTS
    DOCKER -.->|Secrets| KEYVAULT

    GH --> GHACTION
    GHACTION -->|Deploy| STATIC
    GHACTION -->|Deploy| APPSVC

    style STATIC fill:#4CAF50
    style APPSVC fill:#2196F3
    style DB fill:#FF9800
    style INSIGHTS fill:#9C27B0
```

---

## 3. アプリケーションアーキテクチャ図

```mermaid
graph LR
    subgraph "Frontend (React)"
        UI[UI Components<br/>Shadcn/ui]
        PAGES[Pages<br/>Feature Modules]
        STORE[State Management<br/>Zustand]
        API_CLIENT[API Client<br/>Axios]

        UI --> PAGES
        PAGES --> STORE
        PAGES --> API_CLIENT
    end

    subgraph "Backend (FastAPI)"
        ROUTER[API Endpoints<br/>Router Layer]
        SCHEMA[Pydantic Schemas<br/>Validation Layer]
        SERVICE[Business Logic<br/>Service Layer]
        ML[AI/ML Services<br/>Embedding & Matching]
        MODEL[SQLAlchemy Models<br/>ORM Layer]
        DB_SESSION[Database Session<br/>Connection Pool]

        ROUTER --> SCHEMA
        ROUTER --> SERVICE
        SERVICE --> ML
        SERVICE --> MODEL
        MODEL --> DB_SESSION
    end

    subgraph "External APIs"
        OPENAI[OpenAI API]
        LINE_API[LINE API]
        SENDGRID[SendGrid API]
    end

    subgraph "Database"
        POSTGRES[(PostgreSQL<br/>RDBMS)]
    end

    API_CLIENT -->|HTTP/REST| ROUTER
    ML --> OPENAI
    SERVICE --> LINE_API
    SERVICE --> SENDGRID
    DB_SESSION --> POSTGRES

    style PAGES fill:#61dafb
    style SERVICE fill:#10b981
    style ML fill:#8b5cf6
    style POSTGRES fill:#f59e0b
```

---

## 4. データフロー図

### 4.1 求職者の求人検索フロー

```mermaid
sequenceDiagram
    actor Seeker as 求職者
    participant FE as Frontend
    participant API as Backend API
    participant DB as Database
    participant AI as OpenAI API

    Seeker->>FE: 1. 求人検索画面を開く
    FE->>API: 2. GET /api/jobs?page=1&perPage=20
    API->>DB: 3. SELECT jobs WHERE status='published'
    DB-->>API: 4. Job List

    API->>DB: 5. SELECT user profile (skills, experience)
    DB-->>API: 6. User Profile Data

    API->>AI: 7. Generate embedding for user profile
    AI-->>API: 8. User embedding vector [1536]

    loop For each job
        API->>API: 9. Calculate cosine similarity
        API->>API: 10. Calculate match_score (0-100)
    end

    API-->>FE: 11. Job List with match_score
    FE-->>Seeker: 12. Display jobs sorted by match_score
```

### 4.2 企業の候補者検索フロー

```mermaid
sequenceDiagram
    actor Employer as 企業
    participant FE as Frontend
    participant API as Backend API
    participant DB as Database
    participant AI as OpenAI API

    Employer->>FE: 1. 候補者検索画面を開く
    FE->>API: 2. POST /api/employer/candidates/search<br/>{job_id, required_skills, top_k}

    API->>DB: 3. SELECT job WHERE id=job_id
    DB-->>API: 4. Job Data

    API->>AI: 5. Generate job embedding
    AI-->>API: 6. Job embedding vector [1536]

    API->>DB: 7. SELECT all active seekers
    DB-->>API: 8. Seeker List

    loop For each seeker
        API->>AI: 9. Generate seeker embedding (if not cached)
        AI-->>API: 10. Seeker embedding vector
        API->>API: 11. Calculate match_score
    end

    API->>API: 12. Sort by match_score, get top_k
    API-->>FE: 13. Top K candidates with match_score
    FE-->>Employer: 14. Display candidate list
```

---

## 5. APIインターフェース図

```mermaid
graph TB
    subgraph "Frontend Application"
        AUTH_PAGE[Login/Register Page]
        HOME_PAGE[Home Page]
        JOBS_PAGE[Jobs Page]
        CHAT_PAGE[Chat Page]
        APP_PAGE[Applications Page]
        SCOUT_PAGE[Scouts Page]
        CAND_PAGE[Candidates Page]
    end

    subgraph "Backend API Endpoints"
        AUTH_API[/api/auth/*<br/>POST /login<br/>POST /register<br/>POST /refresh]

        USER_API[/api/users/*<br/>GET /me<br/>PUT /profile<br/>POST /preferences]

        JOBS_API[/api/jobs/*<br/>GET /<br/>GET /:id<br/>POST /search<br/>POST / create]

        MATCH_API[/api/matching/*<br/>POST /recommendations<br/>POST /career-chat<br/>POST /calculate-score]

        APP_API[/api/applications/*<br/>GET /<br/>POST /<br/>PUT /:id/status]

        SCOUT_API[/api/scouts/*<br/>GET /<br/>POST /<br/>PUT /:id/status]

        EMP_API[/api/employer/*<br/>POST /candidates/search<br/>GET /candidates/:id]
    end

    AUTH_PAGE -->|POST| AUTH_API
    HOME_PAGE -->|GET| USER_API
    HOME_PAGE -->|GET| JOBS_API
    HOME_PAGE -->|GET| APP_API

    JOBS_PAGE -->|GET, POST| JOBS_API
    JOBS_PAGE -->|POST| MATCH_API

    CHAT_PAGE -->|POST| MATCH_API

    APP_PAGE -->|GET, POST| APP_API

    SCOUT_PAGE -->|GET, POST, PUT| SCOUT_API

    CAND_PAGE -->|POST| EMP_API

    style AUTH_API fill:#ef4444
    style USER_API fill:#3b82f6
    style JOBS_API fill:#10b981
    style MATCH_API fill:#8b5cf6
    style APP_API fill:#f59e0b
    style SCOUT_API fill:#ec4899
    style EMP_API fill:#06b6d4
```

---

## 6. 認証フロー図

### 6.1 新規登録・ログインフロー

```mermaid
sequenceDiagram
    actor User as ユーザー
    participant FE as Frontend
    participant API as Backend API
    participant DB as Database
    participant JWT as JWT Service

    User->>FE: 1. 登録フォーム送信<br/>(email, password, name, role)
    FE->>API: 2. POST /api/auth/register

    API->>API: 3. Validate input (Pydantic)
    API->>DB: 4. Check if email exists

    alt Email already exists
        DB-->>API: User found
        API-->>FE: 409 Conflict
        FE-->>User: "メールアドレスは既に登録されています"
    else Email available
        DB-->>API: No user found
        API->>API: 5. Hash password (bcrypt)
        API->>DB: 6. INSERT new user
        DB-->>API: User created

        API->>JWT: 7. Generate access_token (15min)
        JWT-->>API: access_token
        API->>JWT: 8. Generate refresh_token (7days)
        JWT-->>API: refresh_token

        API-->>FE: 9. 200 OK<br/>{user, access_token, refresh_token}
        FE->>FE: 10. Store tokens<br/>- access_token in memory<br/>- refresh_token in HttpOnly cookie
        FE-->>User: 11. Redirect to /home
    end
```

### 6.2 トークン更新フロー（Silent Refresh）

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as Backend API
    participant JWT as JWT Service
    participant DB as Database

    FE->>FE: 1. Access token expired detected<br/>(401 response or timeout)

    FE->>API: 2. POST /api/auth/refresh<br/>{refresh_token}

    API->>JWT: 3. Verify refresh_token

    alt Token invalid or expired
        JWT-->>API: Invalid
        API-->>FE: 401 Unauthorized
        FE->>FE: Clear all tokens
        FE->>FE: Redirect to /login
    else Token valid
        JWT-->>API: Valid, extract user_id

        API->>DB: 4. Check user is_active
        DB-->>API: User active

        API->>JWT: 5. Generate new access_token
        JWT-->>API: new access_token

        API->>JWT: 6. Generate new refresh_token<br/>(Token Rotation)
        JWT-->>API: new refresh_token

        API->>DB: 7. Invalidate old refresh_token

        API-->>FE: 8. 200 OK<br/>{access_token, refresh_token}
        FE->>FE: 9. Update tokens in memory/cookie
        FE->>FE: 10. Retry original request
    end
```

### 6.3 LINE連携フロー

```mermaid
sequenceDiagram
    actor User as ユーザー
    participant FE as Frontend (LIFF)
    participant LINE as LINE Platform
    participant API as Backend API
    participant DB as Database

    User->>FE: 1. Click "LINEと連携"
    FE->>LINE: 2. liff.init()
    LINE-->>FE: 3. LIFF Ready

    FE->>LINE: 4. liff.login() (if not logged in)
    User->>LINE: 5. Authorize LIFF app
    LINE-->>FE: 6. Login success

    FE->>LINE: 7. liff.getProfile()
    LINE-->>FE: 8. LINE Profile<br/>{userId, displayName, pictureUrl}

    FE->>API: 9. POST /api/auth/link-line<br/>{line_user_id, access_token}

    API->>API: 10. Verify JWT access_token
    API->>DB: 11. UPDATE users<br/>SET line_user_id=?, line_linked_at=NOW()<br/>WHERE id=?

    DB-->>API: 12. Update success
    API-->>FE: 13. 200 OK
    FE-->>User: 14. "LINE連携完了"
```

---

## 7. AIマッチング処理フロー図

```mermaid
flowchart TD
    START([Start: User opens Jobs Page]) --> FETCH_PROFILE[Fetch User Profile from DB<br/>skills, experience, location, salary]

    FETCH_PROFILE --> CHECK_CACHE{User embedding<br/>cached?}

    CHECK_CACHE -->|No| GEN_EMBED[Generate User Embedding<br/>OpenAI text-embedding-3-small<br/>Input: skills + experience + preferences]
    CHECK_CACHE -->|Yes| LOAD_CACHE[Load cached embedding]

    GEN_EMBED --> CACHE_EMBED[Cache embedding<br/>data/embeddings/user_{id}.json]
    LOAD_CACHE --> FETCH_JOBS
    CACHE_EMBED --> FETCH_JOBS

    FETCH_JOBS[Fetch all published jobs from DB]

    FETCH_JOBS --> LOOP_START{For each job}

    LOOP_START --> CHECK_JOB_CACHE{Job embedding<br/>cached?}

    CHECK_JOB_CACHE -->|No| GEN_JOB_EMBED[Generate Job Embedding<br/>Input: title + description + skills]
    CHECK_JOB_CACHE -->|Yes| LOAD_JOB_CACHE[Load job embedding]

    GEN_JOB_EMBED --> CACHE_JOB[Cache job embedding]
    CACHE_JOB --> CALC_SIM
    LOAD_JOB_CACHE --> CALC_SIM

    CALC_SIM[Calculate Cosine Similarity<br/>cosine_similarity user_vec, job_vec]

    CALC_SIM --> NORMALIZE[Normalize to 0-100 score<br/>score = similarity + 1 / 2 * 100]

    NORMALIZE --> APPLY_RULES[Apply business rules<br/>- Salary match: +10<br/>- Location match: +5<br/>- Remote work preference: +5]

    APPLY_RULES --> LOOP_END{More jobs?}

    LOOP_END -->|Yes| LOOP_START
    LOOP_END -->|No| SORT[Sort jobs by match_score DESC]

    SORT --> PAGINATE[Apply pagination<br/>Return top K results]

    PAGINATE --> END([Return Job List with Scores])

    style START fill:#10b981
    style GEN_EMBED fill:#8b5cf6
    style GEN_JOB_EMBED fill:#8b5cf6
    style CALC_SIM fill:#f59e0b
    style END fill:#ef4444
```

---

## 8. 会話チャット処理フロー図

```mermaid
sequenceDiagram
    actor User as ユーザー
    participant FE as Frontend
    participant API as Backend API
    participant CONV as Conversation Storage
    participant PROFILE as Profile Service
    participant OPENAI as OpenAI GPT-4o-mini
    participant SEARCH as Vector Search Service

    User->>FE: 1. Enter message<br/>"年収800万以上のReact求人ある？"
    FE->>API: 2. POST /api/matching/career-chat<br/>{message, conversation_history, seeker_profile}

    API->>CONV: 3. Load conversation history<br/>from data/conversations/{session_id}.json
    CONV-->>API: 4. Previous messages []

    API->>PROFILE: 5. Enrich user context<br/>Get latest profile data
    PROFILE-->>API: 6. User profile<br/>{skills, experience, salary_min, location}

    API->>API: 7. Build system prompt<br/>"あなたはキャリアアドバイザーです。<br/>ユーザーのスキル: [React, TypeScript]<br/>希望年収: 800万円以上..."

    API->>OPENAI: 8. POST /v1/chat/completions<br/>{<br/>  model: "gpt-4o-mini",<br/>  messages: [system, ...history, user],<br/>  temperature: 0.7,<br/>  max_tokens: 500<br/>}

    OPENAI-->>API: 9. AI Response<br/>"はい、条件に合う求人が見つかりました..."

    API->>API: 10. Parse response<br/>Extract job_ids if mentioned

    alt AI mentioned specific jobs
        API->>SEARCH: 11. Search jobs by criteria<br/>{salary_min: 8000000, skills: ["React"]}
        SEARCH-->>API: 12. Matching jobs [job_88, job_92]
        API->>API: 13. Calculate match scores
    end

    API->>CONV: 14. Save conversation<br/>Append user message & AI response
    CONV-->>API: 15. Saved

    API-->>FE: 16. Response<br/>{<br/>  reply: "...",<br/>  recommended_jobs: [{id, title, score}],<br/>  usage: {prompt_tokens, completion_tokens}<br/>}

    FE-->>User: 17. Display AI response<br/>+ Show recommended job cards
```

---

## 9. ER図（データベース）

```mermaid
erDiagram
    USERS ||--o{ JOBS : "creates (employer)"
    USERS ||--o{ APPLICATIONS : "applies (seeker)"
    USERS ||--o{ SCOUTS_SENT : "sends (employer)"
    USERS ||--o{ SCOUTS_RECEIVED : "receives (seeker)"
    JOBS ||--o{ APPLICATIONS : "has"
    JOBS ||--o{ SCOUTS : "related_to"

    USERS {
        string id PK "UUID"
        string email UK "NOT NULL"
        string password_hash "NOT NULL"
        string name "NOT NULL"
        enum role "seeker/employer"
        string line_user_id UK "NULLABLE"
        datetime line_linked_at
        text skills "JSON, seeker only"
        string experience_years "seeker only"
        string desired_salary_min "seeker only"
        string desired_salary_max "seeker only"
        string desired_location "seeker only"
        string desired_employment_type "seeker only"
        string resume_url "seeker only"
        string company_name "employer only"
        string industry "employer only"
        string company_size "employer only"
        text company_description "employer only"
        string profile_completion "0-100"
        boolean is_active "DEFAULT TRUE"
        boolean is_verified "DEFAULT FALSE"
        datetime created_at
        datetime updated_at
        datetime last_login_at
    }

    JOBS {
        string id PK "UUID"
        string employer_id FK "NOT NULL"
        string title "NOT NULL"
        string company "NOT NULL"
        text description "NOT NULL"
        string location "NOT NULL"
        enum employment_type "full-time/part-time/contract/internship"
        integer salary_min "NULLABLE"
        integer salary_max "NULLABLE"
        string salary_text "NULLABLE"
        text required_skills "JSON"
        text preferred_skills "JSON"
        text requirements "NULLABLE"
        text benefits "NULLABLE"
        text tags "JSON"
        boolean remote "DEFAULT FALSE"
        enum status "draft/published/closed"
        boolean featured "DEFAULT FALSE"
        text embedding "JSON, 1536 dimensions"
        text meta_data "JSON"
        datetime posted_date
        datetime created_at
        datetime updated_at
    }

    APPLICATIONS {
        string id PK "UUID"
        string seeker_id FK "NOT NULL"
        string job_id FK "NOT NULL"
        string status "applied/reviewing/interview/rejected/hired"
        text cover_letter "NULLABLE"
        datetime applied_at "NOT NULL"
        datetime updated_at
    }

    SCOUTS {
        string id PK "UUID"
        string employer_id FK "NOT NULL"
        string seeker_id FK "NOT NULL"
        string job_id FK "NOT NULL"
        text message "NULLABLE"
        string status "sent/read/replied/rejected"
        datetime created_at "NOT NULL"
        datetime read_at "NULLABLE"
        datetime replied_at "NULLABLE"
    }
```

---

## 10. デプロイメントフロー図

```mermaid
flowchart TD
    DEV[Developer] -->|git push| GH[GitHub Repository<br/>main branch]

    GH -->|Trigger| GHA[GitHub Actions Workflow]

    GHA --> CHECK{Which component?}

    CHECK -->|Backend change detected| BE_WORKFLOW[Backend Workflow]
    CHECK -->|Frontend change detected| FE_WORKFLOW[Frontend Workflow]

    subgraph "Backend Deployment"
        BE_WORKFLOW --> BE_TEST[Run Tests<br/>pytest]
        BE_TEST --> BE_BUILD[Build Docker Image<br/>docker build]
        BE_BUILD --> BE_PUSH[Push to ACR<br/>Azure Container Registry]
        BE_PUSH --> BE_DEPLOY[Deploy to App Service<br/>az webapp deploy]
        BE_DEPLOY --> BE_HEALTH[Health Check<br/>GET /health]

        BE_HEALTH -->|Success| BE_SUCCESS[Deployment Success]
        BE_HEALTH -->|Fail| BE_ROLLBACK[Auto Rollback<br/>Previous version]
    end

    subgraph "Frontend Deployment"
        FE_WORKFLOW --> FE_TEST[Run Tests<br/>npm test]
        FE_TEST --> FE_BUILD[Build SPA<br/>npm run build]
        FE_BUILD --> FE_DEPLOY[Deploy to Static Web Apps<br/>Azure SWA CLI]
        FE_DEPLOY --> FE_CDN[Invalidate CDN Cache]
        FE_CDN --> FE_SUCCESS[Deployment Success]
    end

    BE_SUCCESS --> NOTIFY[Send Notification<br/>Slack/Email]
    FE_SUCCESS --> NOTIFY
    BE_ROLLBACK --> NOTIFY

    NOTIFY --> MONITOR[Application Insights<br/>Monitor for errors]

    style GH fill:#333333,color:#ffffff
    style BE_DEPLOY fill:#2196F3
    style FE_DEPLOY fill:#4CAF50
    style BE_ROLLBACK fill:#ef4444
    style MONITOR fill:#9C27B0
```

---

## 追加図: コンポーネント間の依存関係

```mermaid
graph TD
    subgraph "Frontend Components"
        A[Pages/Routes] --> B[Feature Modules]
        B --> C[UI Components]
        B --> D[API Client]
        B --> E[State Management<br/>Zustand]
    end

    subgraph "Backend Services"
        F[API Endpoints] --> G[Pydantic Schemas]
        F --> H[Business Services]
        H --> I[ML Services]
        H --> J[Database Models]
        I --> K[External APIs]
        J --> L[SQLAlchemy Session]
    end

    D -->|HTTP/REST| F

    style A fill:#61dafb
    style F fill:#10b981
    style I fill:#8b5cf6
    style K fill:#f59e0b
```

---

## 使用方法

このMarkdownファイルは以下で閲覧できます：

1. **GitHub/GitLab**: Mermaid図が自動レンダリングされます
2. **VSCode**: Mermaid Preview拡張機能をインストール
3. **オンラインビューア**: https://mermaid.live/ にコピー&ペースト
4. **HTMLエクスポート**: Markdownエディタ（Typora, MarkText等）でHTML/PDFにエクスポート

---

## 図の説明

| 図番号 | 図名 | 説明 |
|--------|------|------|
| 1 | システム全体構成図 | クライアント、Azure、外部サービスの全体像 |
| 2 | インフラ構成図 | Azure上の各サービスとCI/CD、監視の配置 |
| 3 | アプリケーションアーキテクチャ図 | フロントエンド・バックエンドの内部構造 |
| 4 | データフロー図 | 求職者・企業の主要フローのシーケンス |
| 5 | APIインターフェース図 | 各画面とAPIエンドポイントの対応関係 |
| 6 | 認証フロー図 | 登録、ログイン、トークン更新、LINE連携 |
| 7 | AIマッチング処理フロー図 | 埋め込み生成からスコア計算までの詳細 |
| 8 | 会話チャット処理フロー図 | ユーザーメッセージからAI応答までのフロー |
| 9 | ER図 | データベーステーブルのリレーション |
| 10 | デプロイメントフロー図 | GitHub ActionsによるCI/CDパイプライン |

---

**作成日**: 2025-12-25
**バージョン**: 1.0
**プロジェクト**: Job Matching Platform
