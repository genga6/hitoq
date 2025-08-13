# 新しいテスト構造設計

## テストディレクトリ構造

```
test/
├── unit/                    # ユニットテスト
│   ├── middleware/         # src/middleware/ のテスト
│   │   └── test_logging.py
│   ├── router/             # src/router/ のテスト
│   │   ├── test_auth_router.py
│   │   ├── test_block_router.py
│   │   ├── test_message_router.py
│   │   ├── test_profile_router.py
│   │   ├── test_qna_router.py
│   │   ├── test_user_router.py
│   │   ├── test_username_router.py
│   │   └── test_visit_router.py
│   └── service/            # src/service/ のテスト
│       ├── test_user_service.py
│       ├── test_categories_service.py
│       ├── test_config_manager.py
│       ├── test_message_service.py
│       ├── test_profile_service.py
│       ├── test_qna_service.py
│       ├── test_user_service.py
│       ├── test_visit_service.py
│       └── test_yaml_loader.py
├── integration/            # 結合テスト
│   ├── test_auth.py
│   ├── test_block_router.py
│   ├── test_message_router.py
│   ├── test_profile_router.py
│   ├── test_qna_router.py
│   ├── test_user_router.py
│   ├── test_username_router.py
│   ├── test_visit_router.py
│   ├── test_user_registration.py
│   ├── test_profile_setup.py
│   ├── test_qna_workflow.py
│   ├── test_messaging_workflow.py
│   └── test_discovery_workflow.py

```

## テストレベル分類

### 1. ユニットテスト (unit/)

- 個別の関数・クラス・メソッドの単体テスト
- 外部依存をモック化
- 高速実行、高カバレッジ

### 2. 結合テスト (integration/)

- 複数コンポーネント間の連携テスト
- データベースとの結合テスト
- API エンドポイントテスト

## テストマーカー

```python
@pytest.mark.unit          # ユニットテスト
@pytest.mark.integration   # 結合テスト
@pytest.mark.workflow      # ワークフローテスト
@pytest.mark.slow          # 実行時間の長いテスト
@pytest.mark.external      # 外部サービス依存テスト
@pytest.mark.database      # データベース依存テスト
@pytest.mark.auth          # 認証関連テスト
```
