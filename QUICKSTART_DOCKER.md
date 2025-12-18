# Dockerデプロイ - クイックスタート

## 🎯 3ステップでAzureにデプロイ

### ステップ1: ローカルでテスト（オプションだが推奨）

```powershell
cd C:\Users\Exitotrinity-13\job-matching-backend

# Dockerイメージをビルド
docker build -t job-matching-backend .

# 起動してテスト
docker run -p 8888:8000 job-matching-backend

# 別のターミナルでヘルスチェック
curl http://localhost:8888/health
# {"status":"healthy"} が返ってくればOK

# 停止（Ctrl+Cで停止）
```

### ステップ2: Azure設定

```powershell
# Azure CLIでログイン
az login

# コンテナモードに設定（自動スクリプト）
.\azure-setup-container.ps1
```

実行後、表示されるメッセージに従って:
- リポジトリをパブリックにする
- **または** GitHub Personal Access Token (PAT) を設定

#### GitHub PATの作成（プライベートリポジトリの場合）

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)"
3. Note: `Azure Container Pull`
4. 権限: `read:packages` のみチェック
5. "Generate token" → **トークンをコピー**

6. Azureに認証情報を設定:
```powershell
# リソースグループを取得
$RESOURCE_GROUP = az webapp show --name job-ai-app-affnfdgqbue2euf0 --query resourceGroup -o tsv

# GitHubユーザー名とPATを設定
az webapp config container set `
  --name job-ai-app-affnfdgqbue2euf0 `
  --resource-group $RESOURCE_GROUP `
  --docker-custom-image-name "ghcr.io/<your-github-username>/job-matching-backend:latest" `
  --docker-registry-server-url https://ghcr.io `
  --docker-registry-server-user "<your-github-username>" `
  --docker-registry-server-password "<your-github-pat>"
```

### ステップ3: デプロイ

```bash
# Gitにコミット&プッシュ
git add .
git commit -m "Add Docker support for Azure deployment"
git push origin main
```

GitHub Actionsが自動的に:
1. Dockerイメージをビルド（3-5分）
2. GitHub Container Registryにプッシュ（1-2分）
3. Azure App Serviceにデプロイ（1-2分）

**合計: 5-10分で完了**

## ✅ 成功確認

### GitHub Actionsを確認

1. GitHubリポジトリ → **Actions** タブ
2. "Deploy Docker Container to Azure" ワークフロー
3. すべてのステップが緑色のチェックマークになるまで待つ

### ヘルスチェック

```powershell
curl https://job-ai-app-affnfdgqbue2euf0.azurewebsites.net/health
```

期待される応答:
```json
{"status":"healthy"}
```

### API仕様書を確認

ブラウザで以下にアクセス:
```
https://job-ai-app-affnfdgqbue2euf0.azurewebsites.net/docs
```

FastAPIのSwagger UIが表示されればデプロイ成功です！

## 🔧 環境変数の設定（本番環境用）

```powershell
az webapp config appsettings set `
  --name job-ai-app-affnfdgqbue2euf0 `
  --resource-group $RESOURCE_GROUP `
  --settings `
    SECRET_KEY="<ランダムな文字列>" `
    CORS_ORIGINS="https://<your-frontend>.azurewebsites.net" `
    DATABASE_URL="<PostgreSQL接続文字列>" `
    DEBUG=False `
    LOG_LEVEL=INFO
```

## 🔄 次回以降のデプロイ

コードを修正したら、pushするだけ:

```bash
git add .
git commit -m "Update code"
git push origin main
```

GitHub Actionsが自動的に新しいDockerイメージをビルドしてデプロイします。

## 🆘 トラブルシューティング

### デプロイが失敗する

```powershell
# ログを確認
az webapp log tail --name job-ai-app-affnfdgqbue2euf0 --resource-group $RESOURCE_GROUP
```

### よくあるエラー

1. **"Image pull failed"**
   - リポジトリがプライベートで、GitHub PATが設定されていない
   - → ステップ2の認証情報設定を実行

2. **"Container didn't respond"**
   - 環境変数 `WEBSITES_PORT=8000` が設定されていない
   - → Azure Portal → 構成 → アプリケーション設定で確認

3. **"denied: permission_denied"**
   - GitHub Actionsの権限不足
   - → リポジトリ → Settings → Actions → General → Workflow permissions → "Read and write permissions"

## 📚 詳細ガイド

詳しい情報は [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) を参照してください。

## 🎉 完了

これで、タイムアウトなしで安定したAzureデプロイが実現できました！
