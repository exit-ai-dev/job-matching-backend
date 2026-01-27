#!/bin/bash
# Azure App Service - 依存関係ビルドを有効化

APP_NAME="job-ai-app-affnfdgqbue2euf0"

echo "=== Azure Oryx ビルドを有効化 ==="
echo "App Name: $APP_NAME"
echo ""

# リソースグループを自動取得
echo "[1/3] リソースグループを取得中..."
RESOURCE_GROUP=$(az webapp show --name $APP_NAME --query resourceGroup -o tsv)

if [ -z "$RESOURCE_GROUP" ]; then
    echo "エラー: アプリが見つかりません。az login を実行してログインしてください。"
    exit 1
fi

echo "Resource Group: $RESOURCE_GROUP"
echo ""

# デプロイ時のビルドを有効化
echo "[2/3] デプロイ時のビルドを有効化中..."
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true ENABLE_ORYX_BUILD=true

# スタートアップコマンドを設定
echo "[3/3] スタートアップコマンドを設定中..."
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port \$PORT"

echo ""
echo "=== 完了 ==="
echo ""
echo "次のステップ:"
echo "1. GitHub Actions ワークフローを再実行してください"
echo "2. デプロイ完了後、以下でログを確認:"
echo "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "3. ヘルスチェック:"
echo "   curl https://$APP_NAME.azurewebsites.net/health"
