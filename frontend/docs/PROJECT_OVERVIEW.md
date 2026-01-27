# exitotrinity - プロジェクト概要

> **新規セッション開始時は必ずこのドキュメントから読むこと**

## クイックリファレンス

| 項目 | 内容 |
|------|------|
| プロジェクト名 | exitotrinity（エグジトトリニティ） |
| 種別 | AI求人マッチングプラットフォーム |
| フロントエンド | React 19 + TypeScript + Vite + TailwindCSS 4 |
| バックエンド | FastAPI (Python) + SQLite + OpenAI |
| ホスティング | Azure Static Web Apps (FE) + Azure App Service (BE) |
| 認証方式 | JWT + LINE LIFF |

---

## 📚 重要ドキュメント一覧

新規セッション時は以下の順序で読むことを推奨:

1. **このドキュメント** - プロジェクト全体像を把握
2. **[API_REFERENCE.md](./API_REFERENCE.md)** - API設計の詳細
3. **[INCOMPLETE_FEATURES.md](./INCOMPLETE_FEATURES.md)** - 実装状況一覧
4. **[DESIGN_SPEC.md](../DESIGN_SPEC.md)** - デザインシステム・UI仕様
5. **[SCREEN_SPEC.md](../SCREEN_SPEC.md)** - 画面構成・データフロー
6. **[system-architecture.html](./system-architecture.html)** - システム構成図

### デプロイ・設定関連

- **[AZURE_LINE_SETUP.md](./AZURE_LINE_SETUP.md)** - Azure環境でのLINE認証設定（詳細版）
- **[AZURE_ENV_QUICK_REFERENCE.md](./AZURE_ENV_QUICK_REFERENCE.md)** - Azure環境変数クイックリファレンス
- **[README_DEPLOY.md](../README_DEPLOY.md)** - デプロイ手順

---

## プロジェクト構成

```
job-matching-frontend/
├── src/
│   ├── features/              # 機能別ディレクトリ
│   │   ├── auth/             # 認証機能
│   │   ├── jobs/             # 求人機能
│   │   ├── applications/     # 応募機能
│   │   ├── chat/             # AIチャット機能
│   │   ├── candidates/       # 候補者管理（企業向け）
│   │   ├── onboarding/       # オンボーディング
│   │   ├── dashboard/        # ダッシュボード
│   │   └── profile/          # プロフィール設定
│   ├── shared/
│   │   ├── components/       # 共通コンポーネント
│   │   ├── lib/              # API クライアント等
│   │   ├── types/            # 型定義
│   │   ├── constants/        # 定数
│   │   └── config/           # 設定
│   ├── routes/               # ルーティング
│   └── components/ui/        # UIコンポーネント
├── docs/                      # ドキュメント
├── public/                    # 静的ファイル
└── dist/                      # ビルド成果物
```

---

## 対象ユーザーと主要機能

### 1. 求職者（seeker）

**主要機能**:
- ✅ 会員登録・ログイン（メール + LINE）
- ✅ 希望条件入力（オンボーディング）
- ✅ AI求人検索・チャット
- ✅ 求人詳細閲覧・応募
- ✅ 応募管理（進捗確認）
- ✅ プロフィール編集

**画面一覧**:
- `/` - LandingPage（ランディング）
- `/register` - RegisterPage（新規登録）
- `/login` - LoginPage（ログイン）
- `/auth/line-link` - LineLinkPage（LINE連携）
- `/preferences` - PreferencesPage（希望条件入力）
- `/home` - HomePage（ダッシュボード）
- `/chat` - ChatPage（AI求人検索）
- `/jobs` - JobsSeekerPage（求人一覧）
- `/jobs/:id` - JobDetailSeekerPage（求人詳細）
- `/applications` - ApplicationsPage（応募一覧）
- `/settings` - SettingsPage（設定）

### 2. 企業（employer）

**主要機能**:
- ✅ 会員登録・ログイン
- ✅ AI候補者検索
- ✅ 候補者管理
- ✅ スカウト送信（※未実装）
- ✅ 求人管理（※未実装）

**画面一覧**:
- `/home` - HomePage（ダッシュボード）
- `/chat` - ChatPage（AI候補者検索）
- `/candidates` - CandidatesPage（候補者一覧）
- `/candidates/:id` - CandidateDetailPage（候補者詳細）

---

## 技術スタック詳細

### フロントエンド

```json
{
  "dependencies": {
    "react": "^19.1.1",
    "react-dom": "^19.1.1",
    "react-router-dom": "^7.9.4",
    "@tanstack/react-query": "^5.62.15",
    "zustand": "^5.0.2",
    "axios": "^1.7.9",
    "react-hook-form": "^7.55.0",
    "zod": "^3.24.1",
    "@line/liff": "^2.27.3",
    "framer-motion": "^12.23.26"
  }
}
```

**主要ライブラリの役割**:
- `react-router-dom`: ルーティング
- `@tanstack/react-query`: サーバー状態管理・キャッシング
- `zustand`: クライアント状態管理（認証状態等）
- `axios`: HTTP クライアント
- `react-hook-form` + `zod`: フォーム管理・バリデーション
- `@line/liff`: LINE ログイン・連携
- `framer-motion`: アニメーション

### バックエンド

- **FastAPI**: 高速なPython Webフレームワーク
- **SQLAlchemy**: ORM
- **SQLite**: 開発用DB（本番はPostgreSQL等に変更可能）
- **OpenAI API**: AIマッチング・チャット機能
- **JWT**: 認証トークン

---

## API設計概要

**ベースURL**: 環境変数 `VITE_API_BASE_URL` で設定

### 主要エンドポイント

| カテゴリ | エンドポイント | 説明 |
|---------|--------------|------|
| 認証 | `POST /auth/register` | 新規登録 |
| 認証 | `POST /auth/login` | ログイン |
| 認証 | `POST /auth/line/link` | LINE連携 |
| 認証 | `GET /auth/me` | ユーザー情報取得 |
| 求人 | `GET /jobs/` | 求人一覧 |
| 求人 | `GET /jobs/{id}` | 求人詳細 |
| 求人 | `POST /jobs/search` | 求人検索 |
| 応募 | `GET /applications/` | 応募一覧 |
| 応募 | `POST /applications/` | 応募作成 |
| ユーザー | `POST /users/preferences` | 希望条件保存 |
| ユーザー | `PUT /users/profile` | プロフィール更新 |
| AI | `POST /matching/career-chat` | AIチャット |

詳細は **[API_REFERENCE.md](./API_REFERENCE.md)** を参照。

---

## 認証フロー

```
1. ユーザー登録/ログイン
   ↓
2. JWT トークン取得
   ↓
3. localStorage に保存
   - auth-token: JWT アクセストークン
   - auth-storage: Zustand 状態
   ↓
4. 全APIリクエストに Bearer トークン付与
   ↓
5. 401エラー時 → 自動ログアウト
```

**実装場所**: `src/shared/lib/api.ts`

---

## デザインシステム

### カラーパレット

```css
/* ブランドカラー */
--color-brand-primary: #1e3a8a    /* 紺 */
--color-brand-secondary: #3b82f6  /* 青 */

/* 背景 */
--color-page: #fafafa             /* ページ背景 */
--color-surface: #ffffff          /* カード背景 */
--color-subtle: #f5f5f5           /* 薄い背景 */

/* テキスト */
--color-main: #1a1a1a             /* メインテキスト */
--color-muted: #666666            /* 補足テキスト */

/* 状態 */
--color-state-success: #10b981
--color-state-error: #dc2626
--color-state-warning: #f59e0b
--color-state-info: #0ea5e9
```

### デザインコンセプト

- **金融系コーポレート × シンプル × 信頼性**
- **参考**: トヨタファイナンスデザインシステム
- **禁止事項**:
  - グラデーション背景
  - 強いshadow（shadow-lg以上）
  - 4色以上のビビッドカラー
  - アイコンや装飾の多用

詳細は **[DESIGN_SPEC.md](../DESIGN_SPEC.md)** を参照。

---

## 開発コマンド

```bash
# 開発サーバー起動
npm run dev

# ビルド
npm run build

# プレビュー
npm run preview

# Lint
npm run lint
```

---

## 環境変数

### `.env` ファイル

```bash
# バックエンドAPIのベースURL
VITE_API_BASE_URL=https://your-backend-url.azurewebsites.net

# LINE LIFF ID
VITE_LIFF_ID=your-liff-id
```

`.env.example` をコピーして `.env` を作成してください。

---

## 画面遷移フロー

### 求職者の新規登録フロー

```
/ (LandingPage)
  ↓ 「無料で始める」クリック
/register (RegisterPage)
  ↓ 登録完了
/auth/line-link (LineLinkPage)
  ↓ LINE連携完了 or スキップ
/preferences (PreferencesPage)
  ↓ 希望条件入力完了
/home (HomePage)
```

### 企業の新規登録フロー

```
/ (LandingPage)
  ↓ 「無料で始める」クリック
/register (RegisterPage)
  ↓ 登録完了（role: employer）
/auth/line-link (LineLinkPage)
  ↓ LINE連携完了 or スキップ
/home (HomePage)
```

### ログインフロー

```
/ or /login
  ↓ ログイン
/home (HomePage)
```

---

## 状態管理

### Zustand (クライアント状態)

**実装場所**: `src/features/auth/store/authStore.ts`

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: User) => void;
}
```

### TanStack Query (サーバー状態)

- データフェッチング
- キャッシング
- 自動再取得
- ローディング・エラー管理

**使用例**:
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['jobs'],
  queryFn: () => jobsApi.getJobs()
});
```

---

## デプロイ

### フロントエンド (Azure Static Web Apps)

1. Azure Static Web Apps リソース作成
2. GitHub連携で自動デプロイ設定
3. 環境変数設定（VITE_API_BASE_URL, VITE_LIFF_ID）

設定ファイル: `staticwebapp.config.json`

### バックエンド (Azure App Service)

1. Azure App Service リソース作成
2. Python ランタイム設定
3. 環境変数設定（OPENAI_API_KEY, JWT_SECRET_KEY等）
4. GitHub Actions でデプロイ

---

## トラブルシューティング

### 1. API接続エラー

**症状**: `Network Error` または CORS エラー

**対処**:
1. `.env` の `VITE_API_BASE_URL` を確認
2. バックエンドが起動しているか確認
3. バックエンドのCORS設定を確認

### 2. 認証エラー（401）

**症状**: API リクエストが401エラー

**対処**:
1. `localStorage` の `auth-token` を確認
2. トークンの有効期限を確認
3. 再ログインを試す

### 3. LINE連携エラー

**症状**: LINE ログインが失敗

**対処**:
1. `.env` の `VITE_LIFF_ID` を確認
2. LIFF アプリの設定を確認（リダイレクトURL等）
3. LIFF SDK の初期化エラーログを確認

---

## 今後の開発予定

### 未実装機能

- [ ] 企業向け求人管理画面
- [ ] スカウト送信機能
- [ ] メッセージング機能
- [ ] 書類添削AI機能
- [ ] 面接対策AI機能
- [ ] 通知機能（LINE通知）
- [ ] 求人お気に入り機能
- [ ] 応募状況自動追跡

### 改善予定

- [ ] テストコード追加（Jest + React Testing Library）
- [ ] E2Eテスト（Playwright）
- [ ] パフォーマンス最適化
- [ ] アクセシビリティ対応強化
- [ ] SEO対策

---

## 開発時の注意事項

### 1. コーディング規約

- **Tailwind CSS**: カスタムCSSは最小限に
- **カラートークン**: 直接色コード記述禁止（例外: LINE ボタンの `#06C755`）
- **レスポンシブ**: モバイルファースト（`md:` 以上でPC対応）
- **型安全**: `any` 型の使用禁止

### 2. コミットメッセージ

```
<type>: <subject>

例:
feat: 求人検索機能を追加
fix: ログインフォームのバリデーションを修正
docs: API仕様書を更新
style: コードフォーマットを修正
```

### 3. ブランチ戦略

- `main`: 本番環境
- `develop`: 開発環境（未設定の場合は直接 main）
- `feature/*`: 機能開発
- `fix/*`: バグ修正

---

## 参考リンク

- [React 19 Documentation](https://react.dev/)
- [TailwindCSS 4 Documentation](https://tailwindcss.com/)
- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LINE LIFF Documentation](https://developers.line.biz/ja/docs/liff/)

---

**最終更新**: 2026-01-18
