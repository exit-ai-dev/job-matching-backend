#!/bin/bash
# Azure App Service クイックフィックススクリプト

# 設定（実際の値に置き換えてください）
APP_NAME="job-ai-app-affnfdgqbue2euf0"
RESOURCE_GROUP="your-resource-group"

echo "=== Azure App Service クイックフィックス ==="
echo "App Name: $APP_NAME"
echo ""

# 1. スタートアップタイムアウトを延長
echo "[1/6] スタートアップタイムアウトを延長中..."
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings WEBSITES_CONTAINER_START_TIME_LIMIT=600

# 2. スタートアップコマンド設定
echo "[2/6] スタートアップコマンドを設定中..."
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port \$PORT"

# 3. Python バージョン確認
echo "[3/6] Python バージョンを確認中..."
az webapp config show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query linuxFxVersion

# 4. アプリケーション設定確認
echo "[4/6] 環境変数を確認中..."
az webapp config appsettings list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[].{Name:name, Value:value}" -o table

# 5. ログストリーミング有効化
echo "[5/6] ログストリーミングを有効化中..."
az webapp log config \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --application-logging filesystem \
  --level information

# 6. アプリを再起動
echo "[6/6] アプリケーションを再起動中..."
az webapp restart \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

echo ""
echo "=== 完了 ==="
echo "ログを確認するには以下を実行:"
echo "az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "ヘルスチェック:"
echo "curl https://$APP_NAME.azurewebsites.net/health"
