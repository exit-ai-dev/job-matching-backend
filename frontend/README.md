# exitotrinity

AI求人マッチングプラットフォーム

## 📖 ドキュメント

**新規セッション開始時は必ず以下のドキュメントから読んでください:**

1. **[docs/PROJECT_OVERVIEW.md](./docs/PROJECT_OVERVIEW.md)** ⭐ **最初に読むこと**
   - プロジェクト全体像
   - 技術スタック
   - 画面構成
   - 開発ガイドライン

2. **[docs/API_REFERENCE.md](./docs/API_REFERENCE.md)**
   - 全APIエンドポイント仕様
   - 型定義
   - 認証フロー
   - 使用例

3. **[docs/INCOMPLETE_FEATURES.md](./docs/INCOMPLETE_FEATURES.md)**
   - 実装状況一覧
   - 未実装・部分実装機能
   - 実装優先順位

4. **[docs/AZURE_LINE_SETUP.md](./docs/AZURE_LINE_SETUP.md)**
   - Azure環境でのLINE認証設定
   - LIFF ID設定手順
   - トラブルシューティング

5. **[DESIGN_SPEC.md](./DESIGN_SPEC.md)**
   - デザインシステム
   - カラーパレット
   - コンポーネント仕様
   - UI実装ガイドライン

6. **[SCREEN_SPEC.md](./SCREEN_SPEC.md)**
   - 画面一覧
   - 画面遷移フロー
   - データモデル

7. **[README_DEPLOY.md](./README_DEPLOY.md)**
   - デプロイ手順

## 🚀 クイックスタート

### 環境変数の設定

```bash
cp .env.example .env
```

`.env` ファイルを編集して以下を設定:

```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_LINE_LIFF_ID=YOUR_LIFF_ID_HERE
```

**Azure環境での設定**: [docs/AZURE_LINE_SETUP.md](./docs/AZURE_LINE_SETUP.md) を参照してください。

### 開発サーバー起動

```bash
npm install
npm run dev
```

http://localhost:5173 で起動します。

### ビルド

```bash
npm run build
```

### プレビュー

```bash
npm run preview
```

## 🛠 技術スタック

- **Frontend**: React 19 + TypeScript + Vite
- **Styling**: TailwindCSS 4
- **State Management**: Zustand + TanStack Query
- **Form**: React Hook Form + Zod
- **HTTP Client**: Axios
- **LINE Integration**: LINE LIFF SDK

## 📁 プロジェクト構成

```
job-matching-frontend/
├── docs/                  # ドキュメント
│   ├── PROJECT_OVERVIEW.md   # プロジェクト概要（必読）
│   ├── API_REFERENCE.md      # API仕様
│   ├── system-architecture.html
│   ├── screen-flow.html
│   └── ui-diagram.html
├── src/
│   ├── features/          # 機能別ディレクトリ
│   ├── shared/            # 共通コード
│   ├── routes/            # ルーティング
│   └── components/ui/     # UIコンポーネント
├── public/                # 静的ファイル
├── DESIGN_SPEC.md        # デザイン仕様
├── SCREEN_SPEC.md        # 画面仕様
└── README_DEPLOY.md      # デプロイ手順
```

## 📝 開発コマンド

```bash
# 開発サーバー起動
npm run dev

# ビルド（型チェック + Vite ビルド）
npm run build

# プレビュー
npm run preview

# Lint
npm run lint
```

## 🌐 デプロイ

### フロントエンド
- **ホスティング**: Azure Static Web Apps
- **詳細**: [README_DEPLOY.md](./README_DEPLOY.md) を参照

### バックエンド
- **ホスティング**: Azure App Service
- **API Base URL**: 環境変数 `VITE_API_BASE_URL` で設定

## 🔑 環境変数

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `VITE_API_BASE_URL` | バックエンドAPIのベースURL | ✅ |
| `VITE_LINE_LIFF_ID` | LINE LIFF ID | ✅ |

**Azure環境での設定方法**: [docs/AZURE_LINE_SETUP.md](./docs/AZURE_LINE_SETUP.md) を参照

## 📚 参考リンク

- [React 19 Documentation](https://react.dev/)
- [TailwindCSS 4 Documentation](https://tailwindcss.com/)
- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [LINE LIFF Documentation](https://developers.line.biz/ja/docs/liff/)

## 📄 ライセンス

All rights reserved.

---

**最終更新**: 2026-01-18
