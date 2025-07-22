# hitoQ Backend Tests

このディレクトリには hitoQ バックエンドの包括的なテストスイートが含まれています。

## テスト構成

### テストファイル

- `conftest.py` - pytest設定、フィクスチャ、テスト用データベース設定
- `pytest.ini` - pytest設定ファイル
- `test_fixtures.py` - テスト用のヘルパー関数とフィクスチャ
- `test_auth.py` - 認証関連エンドポイントのテスト
- `test_users.py` - ユーザー管理エンドポイントのテスト
- `test_profile.py` - プロフィール関連エンドポイントのテスト
- `test_bucket_list.py` - バケットリスト関連エンドポイントのテスト
- `test_qna.py` - Q&A機能エンドポイントのテスト
- `test_services.py` - サービスレイヤーの単体テスト
- `test_integration.py` - 統合テスト・ワークフローテスト

### テストマーカー

- `@pytest.mark.unit` - 単体テスト
- `@pytest.mark.integration` - 統合テスト
- `@pytest.mark.auth` - 認証関連テスト
- `@pytest.mark.slow` - 実行時間の長いテスト

## テストの実行方法

### 全テスト実行

```bash
python -m pytest
```

### 特定のテストファイル実行

```bash
python -m pytest test/test_auth.py
```

### マーカーでフィルタリング

```bash
python -m pytest -m unit          # 単体テストのみ
python -m pytest -m integration   # 統合テストのみ
python -m pytest -m auth          # 認証テストのみ
```

### カバレッジ付き実行

```bash
python -m pytest --cov=src --cov-report=html
```

### 特定のテストクラスまたはメソッド実行

```bash
python -m pytest test/test_auth.py::TestAuthEndpoints::test_health_endpoint
```

## テスト用データベース

テストでは SQLite インメモリデータベースを使用しています：

- 各テスト関数で独立したデータベースセッション
- テスト間でのデータ汚染を防止
- 高速なテスト実行

## フィクスチャ

### 主要フィクスチャ

- `test_db_session` - テスト用データベースセッション
- `client` - FastAPI TestClient
- `sample_user_data` - テスト用ユーザーデータ
- `test_user_in_db` - データベースに作成済みのテストユーザー
- `sample_profile_item_data` - テスト用プロフィールアイテムデータ
- `sample_bucket_list_item_data` - テスト用バケットリストアイテムデータ

## テストカバレッジ

現在のテストは以下をカバーしています：

### エンドポイント

- 基本的なヘルスチェック・ルートエンドポイント
- 認証エンドポイント（Twitter OAuth、JWT管理）
- ユーザー管理（作成、取得、更新）
- プロフィールアイテム（CRUD操作）
- バケットリストアイテム（CRUD操作）
- Q&A機能（回答作成）

### テストシナリオ

- 正常系（成功ケース）
- 異常系（エラーケース）
- バリデーションエラー
- 認証・認可エラー
- データ不整合エラー
- 統合ワークフロー

### サービスレイヤー

- ユーザーサービスの単体テスト
- プロフィールサービスの単体テスト
- バケットリストサービスの単体テスト
- Q&Aサービスの単体テスト

## 今後の改善点

1. **モック化の改善** - 外部API（Twitter）の完全なモック化
2. **パフォーマンステスト** - 大量データでの性能測定
3. **セキュリティテスト** - SQLインジェクション、XSS対策の検証
4. **エンドツーエンドテスト** - 実際のブラウザを使った統合テスト

## 注意事項

- テスト実行前に必要な依存関係がインストールされていることを確認してください
- 実際のデータベースではなく、テスト用の SQLite を使用しています
- 一部のテストは外部サービス（Twitter API）の動作に依存する場合があります
