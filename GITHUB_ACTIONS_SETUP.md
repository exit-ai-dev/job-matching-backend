# GitHub Actions セットアップガイド

## 🔴 現在のエラー

```
Error: Publish profile is invalid for app-name and slot-name provided
```

このエラーは、GitHubシークレットの`AZURE_WEBAPP_PUBLISH_PROFILE`が正しく設定されていないことを示しています。

---

## ✅ 解決手順

### ステップ1: Azureから最新の発行プロファイルをダウンロード

1. **Azure Portal**にログイン
   https://portal.azure.com

2. 左メニューから**App Services**を選択

3. アプリ**job-ai-app-affnfdgqbue2euf0**をクリック

4. 左サイドバーから**デプロイ センター**をクリック

5. 上部の**発行プロファイルのダウンロード**をクリック
   - ファイル名: `job-ai-app-affnfdgqbue2euf0.PublishSettings`

6. ダウンロードしたファイルをテキストエディタで開く

---

### ステップ2: GitHubシークレットを設定

1. **GitHubリポジトリ**を開く
   https://github.com/your-username/your-repo

2. **Settings**タブをクリック

3. 左サイドバーから**Secrets and variables** → **Actions**をクリック

4. 既存の`AZURE_WEBAPP_PUBLISH_PROFILE`があれば**削除**

5. **New repository secret**をクリック

6. シークレットを追加:
   - **Name**: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - **Secret**: ダウンロードした`.PublishSettings`ファイルの**全内容**をコピー＆ペースト
     ```xml
     <?xml version="1.0" encoding="utf-8"?>
     <publishData>
       <publishProfile
         profileName="job-ai-app-affnfdgqbue2euf0 - Web Deploy"
         ...
       </publishProfile>
     </publishData>
     ```

7. **Add secret**をクリック

---

### ステップ3: ワークフローを手動実行

1. GitHubリポジトリの**Actions**タブを開く

2. 左サイドバーから**Deploy to Azure Web App**をクリック

3. 右上の**Run workflow** → **Run workflow**をクリック

4. ワークフローが成功することを確認（緑のチェックマーク）

---

## 🔧 別の方法: Azure CLIでデプロイ

GitHub Actionsが動かない場合は、ローカルからAzure CLIでデプロイできます。

### Azure CLIのインストール（まだの場合）

**Windows (PowerShell)**:
```powershell
winget install -e --id Microsoft.AzureCLI
```

または公式サイトからダウンロード:
https://aka.ms/installazurecliwindows

---

### Azure CLIでデプロイ

```bash
# Azureにログイン
az login

# リソースグループ名を確認
az webapp list --query "[].{name:name, resourceGroup:resourceGroup}" -o table

# デプロイ（リソースグループ名を実際の値に置き換えてください）
cd C:\Users\Exitotrinity-13\job-matching-backend

az webapp up \
  --name job-ai-app-affnfdgqbue2euf0 \
  --resource-group your-resource-group \
  --runtime PYTHON:3.10 \
  --sku B1
```

---

## 🔍 よくある問題と解決策

### 問題1: 発行プロファイルをコピーしたが動かない

**原因**:
- XML形式が壊れている
- 空白や改行が余分に入っている
- 一部が欠けている

**解決**:
1. `.PublishSettings`ファイルを再ダウンロード
2. メモ帳やVS Codeで開く
3. **全選択（Ctrl+A）** → **コピー（Ctrl+C）**
4. GitHubシークレットに**そのまま貼り付け**
5. 前後に余分なスペースがないか確認

---

### 問題2: アプリ名が違うと言われる

**原因**: ワークフローファイルのアプリ名と実際のAzure App Service名が一致していない

**解決**:
`.github/workflows/azure-webapp.yml`の10行目を確認:
```yaml
AZURE_WEBAPP_NAME: job-ai-app-affnfdgqbue2euf0
```

Azure Portalで実際のアプリ名と一致しているか確認

---

### 問題3: GitHub Actionsの権限エラー

**原因**: リポジトリの設定でActions権限が制限されている

**解決**:
1. GitHub → **Settings** → **Actions** → **General**
2. **Workflow permissions**で**Read and write permissions**を選択
3. **Save**をクリック

---

## 🚀 推奨: VS Code拡張機能を使用

GitHub Actionsが複雑な場合は、VS Code拡張機能で直接デプロイする方が簡単です。

### インストール

1. VS Codeを開く
2. 拡張機能マーケットプレイスで**Azure App Service**を検索
3. インストール

### デプロイ方法

1. VS Code左サイドバーのAzureアイコンをクリック
2. **Sign in to Azure**でログイン
3. **APP SERVICE**セクションでアプリを右クリック
4. **Deploy to Web App...**を選択
5. `C:\Users\Exitotrinity-13\job-matching-backend`フォルダを選択
6. 確認メッセージで**Deploy**をクリック

数分でデプロイ完了！

---

## 📋 チェックリスト

デプロイ前に以下を確認:

- [ ] `requirements.txt`が軽量版（requirements.production.txt）になっている
- [ ] `.env`ファイルがGitにコミットされていない（`.gitignore`に含まれている）
- [ ] Azure Portal → App Service → **構成**で環境変数が設定されている
  - [ ] `DATABASE_URL`
  - [ ] `SECRET_KEY`
  - [ ] `CORS_ORIGINS`
  - [ ] `OPENAI_API_KEY`（AIマッチング使用時）
- [ ] スタートアップコマンドが設定されている
  ```
  python -m uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

---

## 🎯 まとめ

GitHub Actionsでのデプロイが複雑な場合は、**VS Code拡張機能**または**Azure CLI**の使用をお勧めします。

最も簡単な方法:
```bash
cd C:\Users\Exitotrinity-13\job-matching-backend
az login
az webapp up --name job-ai-app-affnfdgqbue2euf0 --runtime PYTHON:3.10
```

これで数分でデプロイ完了します！
