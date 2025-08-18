# hitoQ Terraform Configuration

このディレクトリには、hitoQアプリケーションをRenderにデプロイするためのTerraform設定が含まれています。

## 前提条件

1. [Terraform](https://www.terraform.io/downloads.html)がインストールされていること
2. [Render API key](https://dashboard.render.com/u/settings/api-keys)が取得済みであること
3. GitHubリポジトリが設定済みであること

## セットアップ手順

### 1. Terraform初期化

```bash
cd terraform
terraform init
```

### 2. 変数ファイルの作成

```bash
cp terraform.tfvars.example terraform.tfvars
```

`terraform.tfvars`を編集して、実際の値を設定してください：

- `render_api_key`: RenderのAPI key
- `github_repo_url`: GitHubリポジトリのURL
- `db_password`: データベースのパスワード
- `secret_key`: アプリケーションの秘密鍵
- `session_secret_key`: セッションの秘密鍵
- `twitter_client_id`: Twitter OAuthのクライアントID
- `twitter_client_secret`: Twitter OAuthのクライアントシークレット
- `sentry_dsn`: バックエンドのSentry DSN
- `public_sentry_dsn`: フロントエンドのSentry DSN

### 3. デプロイメント実行

#### プランの確認

```bash
terraform plan
```

#### リソースの作成

```bash
terraform apply
```

### 4. デプロイ後の確認

デプロイが完了すると、以下のURLが出力されます：

- Backend URL: `https://hitoq-backend.onrender.com`
- Frontend URL: `https://hitoq.onrender.com`

## 環境変数の更新

本番デプロイ後、以下の環境変数を実際のURLに更新してください：

- `TWITTER_REDIRECT_URI`: `https://[backend-url]/auth/callback/twitter`
- `FRONTEND_URLS`: `https://[frontend-url]`

## トラブルシューティング

### よくある問題

1. **Build失敗**: Dockerfileの設定やビルドプロセスを確認
2. **Database接続エラー**: DATABASE_URLが正しく設定されているか確認
3. **CORS エラー**: FRONTEND_URLSが正しく設定されているか確認

### ログの確認

Renderダッシュボードでサービスのログを確認できます：

- Backend: https://dashboard.render.com/web/[service-id]
- Frontend: https://dashboard.render.com/web/[service-id]

## リソースの削除

```bash
terraform destroy
```

**注意**: この操作はデータベースも削除するため、本番環境では十分注意してください。
