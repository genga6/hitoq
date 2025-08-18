# HTTPS設定・検証ガイド

このガイドでは、hitoQアプリケーションでHTTPS接続を正しく設定し、セキュリティを確保するための手順を説明します。

## 🔐 1. Renderでの基本HTTPS設定

### 自動HTTPS設定の確認

Renderではデフォルトで以下が自動設定されます：

1. **SSL証明書の自動発行**
   - Let's Encryptによる無料SSL証明書
   - 自動更新機能

2. **HTTPS強制リダイレクト**
   - HTTP（port 80）→ HTTPS（port 443）への自動リダイレクト

### 設定確認手順

1. **Renderダッシュボードでの確認**

   ```
   1. Render Dashboard → Your Service
   2. Settings → SSL/TLS
   3. 「Force HTTPS」が有効になっていることを確認
   4. 証明書ステータスが「Active」であることを確認
   ```

2. **コマンドラインでの確認**

   ```bash
   # HTTPリクエストがHTTPSにリダイレクトされることを確認
   curl -I http://your-app-name.onrender.com
   # 期待される結果: HTTP/1.1 301 Moved Permanently
   # Location: https://your-app-name.onrender.com

   # HTTPS接続が正常に動作することを確認
   curl -I https://your-app-name.onrender.com
   # 期待される結果: HTTP/2 200
   ```

## 🌐 2. カスタムドメインでのHTTPS設定

### カスタムドメイン追加手順

1. **ドメインの追加**

   ```
   1. Render Dashboard → Service Settings
   2. Custom Domains → Add Custom Domain
   3. ドメイン名を入力（例: hitoq.example.com）
   4. CNAMEレコードの設定指示に従う
   ```

2. **DNS設定**

   ```
   # ドメイン管理画面で以下のCNAMEレコードを追加
   CNAME hitoq your-app-name.onrender.com
   ```

3. **SSL証明書の発行確認**
   ```bash
   # SSL証明書の詳細確認
   openssl s_client -connect your-domain.com:443 -servername your-domain.com
   ```

## 🔧 3. アプリケーション側のHTTPS設定

### FastAPI（バックエンド）設定

現在の設定確認：

```python
# backend/src/main.py での CORS設定例
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # HTTPSのURLのみ許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SvelteKit（フロントエンド）設定

```javascript
// vite.config.ts でのCSP設定例
export default defineConfig({
  plugins: [sveltekit()],
  server: {
    headers: {
      "Strict-Transport-Security":
        "max-age=63072000; includeSubDomains; preload",
      "Content-Security-Policy":
        "default-src 'self' https:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:;",
    },
  },
});
```

## 🧪 4. HTTPS設定の検証テスト

### 基本接続テスト

```bash
# 1. HTTPSアクセステスト
curl -v https://your-domain.com/health
# 期待される結果: SSL handshake成功、200 OK

# 2. HTTPリダイレクトテスト
curl -v http://your-domain.com
# 期待される結果: 301/302リダイレクト → HTTPS

# 3. セキュリティヘッダーの確認
curl -I https://your-domain.com
# 確認項目:
# - Strict-Transport-Security
# - X-Frame-Options
# - X-Content-Type-Options
```

### SSL/TLS設定品質テスト

```bash
# SSL Labs テスト（ブラウザで実行）
# https://www.ssllabs.com/ssltest/analyze.html?d=your-domain.com

# または、testssl.sh を使用
git clone https://github.com/drwetter/testssl.sh.git
cd testssl.sh
./testssl.sh https://your-domain.com
```

### セキュリティヘッダー検証

```bash
# securityheaders.com でのテスト（ブラウザで実行）
# https://securityheaders.com/?q=your-domain.com

# または、curl でヘッダー確認
curl -I https://your-domain.com | grep -E "(Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Content-Security-Policy)"
```

## 🔍 5. 継続的な監視・メンテナンス

### 証明書の有効期限監視

```bash
# 証明書の有効期限確認
echo | openssl s_client -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates

# 自動監視スクリプト例
#!/bin/bash
DOMAIN="your-domain.com"
DAYS_BEFORE_EXPIRY=30

EXPIRY_DATE=$(echo | openssl s_client -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_EPOCH=$(date +%s)
DAYS_UNTIL_EXPIRY=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))

if [ $DAYS_UNTIL_EXPIRY -lt $DAYS_BEFORE_EXPIRY ]; then
    echo "警告: SSL証明書の有効期限が ${DAYS_UNTIL_EXPIRY} 日後に切れます"
fi
```

### 定期的なセキュリティチェック

1. **月次チェック**
   - SSL Labs テストの実行
   - セキュリティヘッダーの確認
   - 証明書有効期限の確認

2. **四半期チェック**
   - Full security scan の実行
   - HTTPS設定の見直し
   - 新しいセキュリティ標準への対応確認

## 🚨 6. トラブルシューティング

### よくある問題と解決策

#### 問題1: Mixed Content エラー

```
現象: HTTPS サイトで HTTP リソースが読み込めない
解決策: すべてのリソースURLをHTTPSに変更

# 悪い例
<img src="http://example.com/image.jpg">

# 良い例
<img src="https://example.com/image.jpg">
# または
<img src="//example.com/image.jpg">  // プロトコル相対URL
```

#### 問題2: CORS エラー

```
現象: フロントエンドからAPIへのリクエストが CORS エラー
解決策: CORSミドルウェアでHTTPSオリジンを許可

# backend/src/main.py
allow_origins=[
    "https://your-frontend-domain.com",  # HTTPSのみ
    # "http://localhost:3000",  # 開発環境のみ
]
```

#### 問題3: SSL証明書エラー

```
現象: 証明書が無効または期限切れ
確認方法:
  curl -v https://your-domain.com 2>&1 | grep -E "(certificate|SSL)"

対処法:
  1. Renderダッシュボードで証明書ステータス確認
  2. DNS設定の確認
  3. Renderサポートへの問い合わせ
```

## ✅ 7. デプロイ前チェックリスト

- [ ] Renderで「Force HTTPS」が有効
- [ ] SSL証明書が正常に発行・設定済み
- [ ] HTTPからHTTPSへのリダイレクトが動作
- [ ] セキュリティヘッダーが適切に設定
- [ ] CORS設定でHTTPSオリジンのみ許可
- [ ] Mixed Contentエラーがない
- [ ] SSL Labs テストでA評価以上
- [ ] 証明書の自動更新が設定済み

## 📋 8. 本番運用での推奨設定

### セキュリティヘッダーの設定

```python
# FastAPI でのセキュリティヘッダー設定例
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# HTTPS強制
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["your-domain.com"])

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### 監視・アラート設定

1. **Uptime monitoring** (例: UptimeRobot, Pingdom)
2. **SSL certificate monitoring**
3. **Security header monitoring**

---

**重要**: 本番環境では必ずHTTPS通信のみを使用し、定期的なセキュリティチェックを実施してください。
