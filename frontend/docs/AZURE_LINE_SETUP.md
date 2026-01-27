# Azure環境でのLINE認証設定ガイド

> **Azure Static Web AppsでLINE LIFF認証を設定する完全ガイド**

最終更新: 2026-01-18

---

## 📋 目次

1. [前提条件](#前提条件)
2. [LINE Developers設定](#line-developers設定)
3. [Azure Static Web Apps 環境変数設定](#azure-static-web-apps-環境変数設定)
4. [ビルド設定の確認](#ビルド設定の確認)
5. [動作確認](#動作確認)
6. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### 必要なアカウント
- ✅ LINE Developersアカウント
- ✅ Azureアカウント
- ✅ Azure Static Web Apps リソース（作成済み）

### 必要な権限
- LINE Developers: チャネル作成・管理権限
- Azure: Static Web App への共同作成者権限以上

---

## LINE Developers設定

### 1. LINEログインチャネル作成

1. **LINE Developers Console にアクセス**
   ```
   https://developers.line.biz/console/
   ```

2. **プロバイダー選択**
   - 既存のプロバイダーを選択、または新規作成

3. **新しいチャネル作成**
   - チャネルタイプ: **LINE Login**
   - チャネル名: `exitotrinity Job Matching`（任意）
   - チャネル説明: `AI求人マッチングプラットフォーム`
   - アプリタイプ: **Webアプリ**

4. **チャネル基本設定**
   - コールバックURL:
     ```
     https://your-app-name.azurestaticapps.net/auth/line/callback
     ```
   - メールアドレス: 管理者メールアドレス

### 2. LIFF アプリ作成

1. **チャネル > LIFF タブ**を開く

2. **追加** ボタンをクリック

3. **LIFF アプリ設定**:
   ```
   LIFF アプリ名: exitotrinity Auth
   サイズ: Full
   エンドポイントURL: https://your-app-name.azurestaticapps.net/auth/line/link
   スコープ:
     ☑ profile
     ☑ openid
     ☑ email (オプション)
   ボットリンク機能: オフ
   Scan QR: オフ
   ```

4. **作成** をクリック

5. **LIFF ID をコピー**
   ```
   例: 1234567890-AbCdEfGh
   ```
   ⚠️ このIDを次のステップで使用します

---

## Azure Static Web Apps 環境変数設定

### 方法1: Azure Portal（推奨）

#### ステップ1: Static Web App を開く

1. **Azure Portal** にアクセス
   ```
   https://portal.azure.com
   ```

2. **リソース検索** から Static Web Apps を選択

3. 該当するアプリを選択

#### ステップ2: 環境変数を追加

1. 左メニューから **構成** を選択

2. **アプリケーション設定** タブを選択

3. **+ 追加** をクリック

4. 以下の設定を追加:

   **本番環境 (Production)**:
   ```
   名前: VITE_LINE_LIFF_ID
   値: 1234567890-AbCdEfGh
   ```

   **API Base URL** (必要に応じて):
   ```
   名前: VITE_API_BASE_URL
   値: https://your-backend.azurewebsites.net/api
   ```

5. **保存** をクリック

#### ステップ3: 再デプロイ

環境変数を追加した後、アプリを再デプロイする必要があります:

1. **GitHub Actions ワークフローを再実行**
   - GitHubリポジトリ → **Actions** タブ
   - 最新のワークフローを選択
   - **Re-run jobs** をクリック

2. または、コードをプッシュ:
   ```bash
   git commit --allow-empty -m "Trigger rebuild for env vars"
   git push
   ```

### 方法2: Azure CLI

```bash
# Static Web App のリソース情報を取得
az staticwebapp list --query "[].{name:name, resourceGroup:resourceGroup}" --output table

# 環境変数を設定
az staticwebapp appsettings set \
  --name <your-static-web-app-name> \
  --resource-group <your-resource-group> \
  --setting-names VITE_LINE_LIFF_ID=<your-liff-id> \
  VITE_API_BASE_URL=<your-api-url>
```

#### 例:
```bash
az staticwebapp appsettings set \
  --name job-matching-frontend \
  --resource-group exitotrinity-rg \
  --setting-names VITE_LINE_LIFF_ID=1234567890-AbCdEfGh \
  VITE_API_BASE_URL=https://job-ai-app.azurewebsites.net/api
```

### 方法3: GitHub Secrets（CI/CD統合）

GitHub Actionsワークフロー経由で設定する場合:

1. **GitHub リポジトリ > Settings > Secrets and variables > Actions**

2. **New repository secret** をクリック

3. シークレットを追加:
   ```
   Name: VITE_LINE_LIFF_ID
   Secret: 1234567890-AbCdEfGh
   ```

4. **GitHub Actions ワークフローファイル** (`.github/workflows/azure-static-web-apps-*.yml`) を更新:
   ```yaml
   - name: Build And Deploy
     uses: Azure/static-web-apps-deploy@v1
     with:
       # ... 既存の設定 ...
       app_build_command: npm run build
     env:
       VITE_LINE_LIFF_ID: ${{ secrets.VITE_LINE_LIFF_ID }}
       VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
   ```

---

## ビルド設定の確認

### Vite設定での環境変数使用

`vite.config.ts` では、`VITE_` プレフィックス付き環境変数が自動的にクライアントに公開されます。

**確認事項**:
```typescript
// vite.config.ts
export default defineConfig({
  // 環境変数は自動的に process.env から読み込まれる
  // VITE_ プレフィックス付き変数はクライアントコードで利用可能
})
```

### コード内での使用

`src/shared/lib/liff.ts` で環境変数を使用:
```typescript
const LIFF_ID = import.meta.env.VITE_LINE_LIFF_ID;

export const initializeLiff = async (): Promise<boolean> => {
  if (!LIFF_ID || LIFF_ID === 'YOUR_LIFF_ID_HERE') {
    console.warn('LIFF ID is not configured');
    return false;
  }

  await liff.init({ liffId: LIFF_ID });
  return true;
};
```

---

## 動作確認

### 1. デプロイ完了確認

```bash
# Azure CLIでデプロイ状況確認
az staticwebapp show \
  --name <your-static-web-app-name> \
  --resource-group <your-resource-group> \
  --query "defaultHostname"
```

出力例:
```
your-app-name.azurestaticapps.net
```

### 2. 環境変数の確認

ブラウザで以下をチェック:

1. アプリにアクセス:
   ```
   https://your-app-name.azurestaticapps.net
   ```

2. ブラウザのコンソールを開く (F12)

3. コンソールで確認:
   ```javascript
   console.log(import.meta.env.VITE_LINE_LIFF_ID);
   // 期待される出力: "1234567890-AbCdEfGh"
   // ⚠️ "YOUR_LIFF_ID_HERE" や undefined でないこと
   ```

### 3. LINE認証のテスト

1. **ログインページにアクセス**:
   ```
   https://your-app-name.azurestaticapps.net/login
   ```

2. **LINE ログイン** ボタンをクリック

3. **期待される動作**:
   - LINE認証画面にリダイレクト
   - 認証後、アプリにコールバック
   - ユーザー情報が正しく取得される

4. **エラーが出る場合**:
   - ブラウザコンソールでエラーメッセージを確認
   - [トラブルシューティング](#トラブルシューティング) を参照

### 4. LINE連携のテスト

1. 通常の方法でログイン（メールアドレス + パスワード）

2. **マイページ** または **LINE連携ページ** にアクセス

3. **LINE連携** ボタンをクリック

4. **期待される動作**:
   - LIFF画面が開く
   - LINE認証完了
   - アカウントが正常に連携される

---

## トラブルシューティング

### 問題1: LIFF ID が undefined

**症状**:
```
console.warn('LIFF ID is not configured');
```

**原因**:
- 環境変数が正しく設定されていない
- ビルド時に環境変数が読み込まれていない

**解決方法**:

1. **Azure Portal で環境変数を確認**:
   - Static Web Apps > 構成 > アプリケーション設定
   - `VITE_LINE_LIFF_ID` が存在するか確認

2. **再デプロイ**:
   - 環境変数追加後は必ず再デプロイが必要
   - GitHub Actions から再実行

3. **ビルドログを確認**:
   - GitHub Actions のログで環境変数が正しく設定されているか確認

### 問題2: LIFF initialization failed

**症状**:
```javascript
Error: Invalid LIFF ID
```

**原因**:
- LIFF ID の形式が間違っている
- 存在しないLIFF ID

**解決方法**:

1. **LINE Developers Consoleで確認**:
   - チャネル > LIFF
   - LIFF ID をコピー（形式: `1234567890-AbCdEfGh`）

2. **Azure環境変数を更新**:
   - 正しいLIFF IDに変更
   - 保存後、再デプロイ

### 問題3: Redirect URI mismatch

**症状**:
```
error=redirect_uri_mismatch
```

**原因**:
- LIFF設定のエンドポイントURLが間違っている

**解決方法**:

1. **LINE Developers Console**:
   - チャネル > LIFF > 該当するLIFFアプリ
   - エンドポイントURL を確認:
     ```
     https://your-app-name.azurestaticapps.net/auth/line/link
     ```
   - 必ず `https://` を使用

2. **コールバックURLも確認**:
   - チャネル > LINE Login設定
   - コールバックURL:
     ```
     https://your-app-name.azurestaticapps.net/auth/line/callback
     ```

### 問題4: 環境変数が本番環境に反映されない

**原因**:
- Azure Static Web Apps では環境変数追加後に再デプロイが必要

**解決方法**:

1. **GitHub Actions で再デプロイ**:
   ```bash
   # 空コミットでデプロイトリガー
   git commit --allow-empty -m "Trigger rebuild"
   git push
   ```

2. **または Azure CLIで強制再デプロイ**:
   ```bash
   az staticwebapp update \
     --name <app-name> \
     --resource-group <rg-name>
   ```

### 問題5: CORS エラー

**症状**:
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**原因**:
- バックエンドのCORS設定にフロントエンドURLが含まれていない

**解決方法**:

バックエンド (App Service) の環境変数を更新:

```bash
az webapp config appsettings set \
  --name <backend-app-name> \
  --resource-group <rg-name> \
  --settings CORS_ORIGINS="https://your-frontend.azurestaticapps.net,https://your-custom-domain.com"
```

⚠️ **注意**: カンマ区切りで複数ドメイン設定可能、スペースなし

---

## 📝 環境別設定まとめ

### 開発環境 (localhost)

**`.env.local`** (gitignore済み):
```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_LINE_LIFF_ID=1234567890-AbCdEfGh
```

### ステージング環境

**Azure Portal > 構成**:
```
VITE_API_BASE_URL=https://staging-backend.azurewebsites.net/api
VITE_LINE_LIFF_ID=1234567890-StAgInG
```

### 本番環境

**Azure Portal > 構成**:
```
VITE_API_BASE_URL=https://prod-backend.azurewebsites.net/api
VITE_LINE_LIFF_ID=1234567890-PrOdUcT
```

⚠️ **ベストプラクティス**: 環境ごとに異なるLIFF IDを使用することを推奨

---

## 📚 関連ドキュメント

- [LINE Developers Documentation](https://developers.line.biz/ja/docs/)
- [Azure Static Web Apps - Environment Variables](https://learn.microsoft.com/azure/static-web-apps/configuration)
- [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) - プロジェクト概要
- [API_REFERENCE.md](./API_REFERENCE.md) - API仕様
- [INCOMPLETE_FEATURES.md](./INCOMPLETE_FEATURES.md) - 実装状況

---

## 🔐 セキュリティ上の注意

### 環境変数の扱い

✅ **安全な方法**:
- Azure Portal の環境変数設定を使用
- GitHub Secrets を使用
- `.env.local` をgitignoreに追加（済み）

❌ **危険な方法**:
- LIFF ID をコードに直接記述
- `.env` ファイルをGitにコミット
- 環境変数をクライアント側ログに出力

### LIFF ID の公開について

⚠️ **注意**: LIFF ID は `VITE_` プレフィックス付きのため、ビルド後のJavaScriptに含まれます（クライアント側で参照可能）。

これは正常な動作ですが、以下に注意:
- LIFF ID 自体は秘密情報ではない
- ただし、LINE Channel Secret は絶対に公開しない
- Channel Access Token はバックエンドのみで使用

---

**最終更新**: 2026-01-18
