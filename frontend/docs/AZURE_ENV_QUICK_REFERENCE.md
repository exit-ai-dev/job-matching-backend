# Azure環境変数 クイックリファレンス

> **Azure Static Web Apps での環境変数設定 - 簡易版**

最終更新: 2026-01-18

---

## 🎯 設定が必要な環境変数

### フロントエンド (Azure Static Web Apps)

```bash
# 必須
VITE_API_BASE_URL=https://your-backend.azurewebsites.net/api
VITE_LINE_LIFF_ID=1234567890-AbCdEfGh
```

### バックエンド (Azure App Service)

```bash
# 必須
DATABASE_URL=postgresql://username:password@hostname/dbname?sslmode=require
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-frontend.azurestaticapps.net
DEBUG=False
LOG_LEVEL=INFO

# オプション（LINE通知用 - 未実装）
LINE_CHANNEL_ACCESS_TOKEN=your-token
LINE_CHANNEL_SECRET=your-secret
```

---

## ⚡ クイック設定手順

### Azure Portal から設定（推奨）

#### フロントエンド

1. Azure Portal → Static Web Apps → 該当アプリを選択
2. **構成** → **アプリケーション設定**
3. **+ 追加** をクリック
4. 環境変数を追加:
   - 名前: `VITE_LINE_LIFF_ID`
   - 値: `1234567890-AbCdEfGh`
5. **保存**
6. GitHub Actions でデプロイを再実行

#### バックエンド

1. Azure Portal → App Service → 該当アプリを選択
2. **構成** → **アプリケーション設定**
3. **+ 新しいアプリケーション設定** をクリック
4. 環境変数を追加
5. **保存** → **続行**

### Azure CLI から設定

#### フロントエンド

```bash
az staticwebapp appsettings set \
  --name <your-static-web-app-name> \
  --resource-group <your-resource-group> \
  --setting-names \
    VITE_API_BASE_URL="https://your-backend.azurewebsites.net/api" \
    VITE_LINE_LIFF_ID="1234567890-AbCdEfGh"
```

#### バックエンド

```bash
az webapp config appsettings set \
  --name <your-app-service-name> \
  --resource-group <your-resource-group> \
  --settings \
    DATABASE_URL="postgresql://..." \
    OPENAI_API_KEY="sk-..." \
    SECRET_KEY="..." \
    CORS_ORIGINS="https://your-frontend.azurestaticapps.net" \
    DEBUG="False" \
    LOG_LEVEL="INFO"
```

---

## 🔍 設定確認方法

### フロントエンド

```bash
# ブラウザのコンソールで確認
console.log(import.meta.env.VITE_LINE_LIFF_ID);
# 出力: "1234567890-AbCdEfGh"（正常）
# 出力: undefined または "YOUR_LIFF_ID_HERE"（エラー）
```

### バックエンド

```bash
# ヘルスチェック
curl https://your-backend.azurewebsites.net/health
# 期待: {"status":"healthy"}

# API仕様書でテスト
https://your-backend.azurewebsites.net/docs
```

---

## ⚠️ よくあるエラー

### エラー1: 環境変数が undefined

**原因**: 環境変数追加後に再デプロイしていない

**解決**:
```bash
# GitHub Actions で再デプロイ
git commit --allow-empty -m "Trigger rebuild"
git push
```

### エラー2: CORS エラー

**原因**: バックエンドの `CORS_ORIGINS` にフロントエンドURLが含まれていない

**解決**:
```bash
az webapp config appsettings set \
  --name <backend-app> \
  --resource-group <rg> \
  --settings CORS_ORIGINS="https://your-frontend.azurestaticapps.net"
```

### エラー3: LIFF initialization failed

**原因**: LIFF ID が間違っている、または存在しない

**解決**: LINE Developers Console で正しいLIFF IDを確認

---

## 📚 詳細ドキュメント

- **LINE認証の詳細設定**: [AZURE_LINE_SETUP.md](./AZURE_LINE_SETUP.md)
- **プロジェクト概要**: [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)
- **API仕様**: [API_REFERENCE.md](./API_REFERENCE.md)

---

**最終更新**: 2026-01-18
