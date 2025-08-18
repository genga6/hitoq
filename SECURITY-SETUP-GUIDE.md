# hitoQ セキュリティ設定ガイド

このガイドでは、hitoQアプリケーションを安全にデプロイするためのセキュリティ設定手順を説明します。

## 🔒 1. 強力な環境変数の生成

デプロイ前に、以下の環境変数に強力なランダム値を設定する必要があります：

### 必須の環境変数

#### SECRET_KEY（32バイト）

FastAPI JWTトークンの署名用キー

```bash
openssl rand -hex 32
```

#### SESSION_SECRET_KEY（32バイト）

セッション管理用の秘密キー

```bash
openssl rand -hex 32
```

#### DB_PASSWORD（強力なパスワード）

PostgreSQLデータベースのパスワード

```bash
# 32文字の強力なパスワード生成
openssl rand -base64 32
```

### セットアップ手順

1. **キーの生成**

   ```bash
   # すべてのキーを一度に生成
   echo "SECRET_KEY=$(openssl rand -hex 32)"
   echo "SESSION_SECRET_KEY=$(openssl rand -hex 32)"
   echo "DB_PASSWORD=$(openssl rand -base64 32 | tr -d '=+/')"
   ```

2. **Renderでの設定**
   - Renderダッシュボードにログイン
   - サービス設定 → Environment Variables
   - 上記の値を Secret として設定
   - **重要**: これらの値は絶対に公開リポジトリにコミットしないでください

3. **その他の環境変数**

   ```bash
   # Twitter OAuth設定（Twitter Developer Consoleで取得）
   TWITTER_CLIENT_ID=your_twitter_client_id
   TWITTER_CLIENT_SECRET=your_twitter_client_secret
   TWITTER_REDIRECT_URI=https://your-domain.com/auth/callback/twitter

   # CORS設定
   FRONTEND_URLS=https://your-domain.com

   # オプション: エラートラッキング
   SENTRY_DSN=your_sentry_dsn_if_using

   # ログレベル
   LOG_LEVEL=INFO
   ```

## 🌐 2. HTTPS設定の確認

### Renderでの設定

1. Renderダッシュボードでサービスを選択
2. Settings → Custom Domains
3. 「Force HTTPS」が有効になっていることを確認
4. HTTP → HTTPS リダイレクトが設定されていることを確認

### 設定後の確認

```bash
# HTTPアクセスがHTTPSにリダイレクトされることを確認
curl -I http://your-domain.com
# Location: https://your-domain.com が返されることを確認
```

## 🔍 3. 依存関係の脆弱性チェック

### フロントエンド（npm）

```bash
cd frontend
pnpm audit
# 脆弱性が見つかった場合
pnpm audit fix
```

### バックエンド（Python）

```bash
cd backend
# uvのセキュリティチェック
uv pip install safety
safety check
```

### GitHubのDependabot

1. GitHubリポジトリ → Settings → Security & analysis
2. Dependabot security updates を有効化
3. Dependabot alerts を確認し、必要に応じて修正

## 🛡️ 4. デプロイ前チェックリスト

- [ ] データベースポートが外部公開されていない（docker-compose.prod.yml）
- [ ] すべての環境変数が強力なランダム値で設定されている
- [ ] HTTPS強制リダイレクトが有効
- [ ] 依存関係の脆弱性スキャンが完了
- [ ] Twitter OAuth設定が正しい
- [ ] CORSの許可ドメインが正しい

## 🚨 5. セキュリティインシデント対応

### 環境変数の漏洩が疑われる場合

1. **即座に実行**：
   ```bash
   # 新しいキーを生成
   NEW_SECRET=$(openssl rand -hex 32)
   NEW_SESSION_SECRET=$(openssl rand -hex 32)
   ```
2. Renderの環境変数を即座に更新
3. サービスを再起動
4. ユーザーに再ログインを促す

### 不審なアクティビティの監視

- Renderのログを定期的に確認
- Sentryでエラーパターンを監視
- データベースの異常なクエリを監視

## 📞 6. サポート・問い合わせ

セキュリティに関する問題や質問がある場合：

1. プロジェクトのIssueを作成（機密情報を含む場合は避ける）
2. 緊急の場合は開発チームに直接連絡

---

**重要**: このガイドの内容は定期的に見直し、最新のセキュリティ脅威に対応するため更新してください。
