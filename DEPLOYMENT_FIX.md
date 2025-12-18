# Azureデプロイエラーの修正方法

## 🔴 現在のエラー

```
Application Error
WARNING: Could not find virtual environment directory /home/site/wwwroot/antenv.
WARNING: Could not find package directory /home/site/wwwroot/__oryx_packages__.
ModuleNotFoundError: No module named 'uvicorn'
```

## 💡 原因

Azure Oryxがデプロイ時にPython依存関係をインストールしていません。
zipファイルにはソースコードのみが含まれ、パッケージがインストールされていないため、uvicornが見つからずアプリが起動できません。

## ✅ 修正手順（3ステップ）

### ステップ1: Azure CLIでログイン

```powershell
az login
```

### ステップ2: Oryxビルドを有効化

#### オプションA: 自動スクリプト（推奨）

```powershell
cd C:\Users\Exitotrinity-13\job-matching-backend
.\azure-enable-build.ps1
```

#### オプションB: 手動で実行

```powershell
# リソースグループを取得
$RESOURCE_GROUP = az webapp show --name job-ai-app-affnfdgqbue2euf0 --query resourceGroup -o tsv

# ビルド設定を有効化
az webapp config appsettings set `
  --name job-ai-app-affnfdgqbue2euf0 `
  --resource-group $RESOURCE_GROUP `
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true ENABLE_ORYX_BUILD=true

# スタートアップコマンドを設定
az webapp config set `
  --name job-ai-app-affnfdgqbue2euf0 `
  --resource-group $RESOURCE_GROUP `
  --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port `$PORT"
```

### ステップ3: GitHub Actionsを再実行

1. GitHubリポジトリを開く
2. **Actions**タブをクリック
3. 最新のワークフローを選択
4. **Re-run jobs**をクリック

## 🔍 成功の確認

### 1. デプロイログを確認

```powershell
az webapp log tail --name job-ai-app-affnfdgqbue2euf0 --resource-group $RESOURCE_GROUP
```

正常な場合、以下のようなログが表示されます:

```
Detecting platforms...
Detected following platforms:
  python: 3.10.14

Oryx Build Command: python -m pip install -r requirements.txt

Collecting fastapi==0.115.5
  Downloading fastapi-0.115.5-py3-none-any.whl
Collecting uvicorn[standard]==0.34.0
  Downloading uvicorn-0.34.0-py3-none-any.whl
...
Successfully installed fastapi-0.115.5 uvicorn-0.34.0 sqlalchemy-2.0.36 ...

Starting application with: python -m uvicorn main:app --host 0.0.0.0 --port 8000
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. ヘルスチェック

```powershell
curl https://job-ai-app-affnfdgqbue2euf0.azurewebsites.net/health
```

期待される応答:
```json
{"status":"healthy"}
```

### 3. API仕様書を確認

ブラウザで以下にアクセス:
```
https://job-ai-app-affnfdgqbue2euf0.azurewebsites.net/docs
```

FastAPIのSwagger UIが表示されれば成功です。

## 🔧 修正内容の説明

### 変更1: GitHub Actions ワークフロー

**変更前**:
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```
GitHub Actionsランナー内でパッケージをインストールしていましたが、zipには含まれていませんでした。

**変更後**:
```yaml
- name: Verify requirements.txt exists
  run: |
    if [ ! -f requirements.txt ]; then
      echo "Error: requirements.txt not found"
      exit 1
    fi
```
requirements.txtの存在確認のみを行い、実際のインストールはAzure Oryxに任せます。

### 変更2: Azure App Service設定

**追加された設定**:
- `SCM_DO_BUILD_DURING_DEPLOYMENT=true`: デプロイ時にビルドを実行
- `ENABLE_ORYX_BUILD=true`: Oryxビルドシステムを有効化
- `startup-file`: 正しいスタートアップコマンドを指定

## 📚 関連ドキュメント

詳細な情報は以下のファイルを参照してください:

- [AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md) - 完全なAzureデプロイガイド
- [GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md) - GitHub Actions設定ガイド

## 🆘 トラブルシューティング

### Q1: `az: command not found` と表示される

**A**: Azure CLIがインストールされていません。以下からインストールしてください:
```powershell
winget install -e --id Microsoft.AzureCLI
```

### Q2: リソースグループが見つからない

**A**: `az login`を実行して、正しいAzureアカウントでログインしているか確認してください。

### Q3: ワークフローは成功するがアプリが動かない

**A**: ログストリームで詳細なエラーを確認してください:
```powershell
az webapp log tail --name job-ai-app-affnfdgqbue2euf0 --resource-group <your-rg>
```

### Q4: 環境変数が設定されていない

**A**: Azure Portalで以下を設定してください:
- App Service → 構成 → アプリケーション設定
  - `DATABASE_URL`
  - `SECRET_KEY`
  - `CORS_ORIGINS`

## 🎯 まとめ

この修正により:
1. ✅ GitHub Actionsワークフローがシンプルになりました
2. ✅ Azure Oryxが自動的に依存関係をインストールします
3. ✅ デプロイが正常に完了し、アプリケーションが起動します

修正後は、通常通りGitHubにpushするだけで自動デプロイされます。
