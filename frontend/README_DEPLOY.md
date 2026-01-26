# デプロイ & ローカル開発手順

## ローカル開発
- 依存関係インストール: `npm ci`
- 開発サーバー: `npm run dev`（既存の `npm run dev` フローはそのままです）

## 必要な環境変数（SWA も同じキーで注入）
- `VITE_API_BASE_URL` : 例 `http://localhost:8000/api`（ローカル）、`https://<app-name>.azurewebsites.net/api`（本番想定）

### Azure Static Web Apps での設定箇所
1. Azure ポータル → 対象の Static Web App を開く
2. **Settings > Environment variables**（または Configuration）を開く
3. `VITE_API_BASE_URL` を追加し、保存後に **Save** で反映

## GitHub Actions（自動デプロイ）
- ブランチ `main` へ push すると `.github/workflows/azure-static-web-apps.yml` でビルド & デプロイ
- 必要な Secrets:
  - `AZURE_STATIC_WEB_APPS_API_TOKEN`（SWA の Deploy API token）

## 直リンク 404 対策
- `staticwebapp.config.json` で SPA fallback を設定。React Router のパスは `/index.html` にフォールバックし、`/assets/*` や拡張子付き静的ファイルは除外しています。

## よくあるエラーと対処
- API URL 未設定: `VITE_API_BASE_URL` が設定されているかローカル・SWA を確認
- CORS: バックエンド側で `https://<SWAドメイン>` を許可する
- 直リンク 404: `staticwebapp.config.json` がデプロイされているか確認
