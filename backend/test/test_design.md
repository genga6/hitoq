# 新しいテスト構造設計

## テストディレクトリ構造

```
test/
├── unit/                    # ユニットテスト
│   ├── config/             # src/config/ のテスト
│   │   ├── test_env_config.py
│   │   ├── test_config_manager.py
│   │   └── test_yaml_loader.py
│   ├── db/                 # src/db/ のテスト
│   │   ├── test_session.py
│   │   └── test_tables.py
│   ├── middleware/         # src/middleware/ のテスト
│   │   └── test_logging.py
│   ├── schema/             # src/schema/ のテスト
│   │   ├── test_user.py
│   │   ├── test_profile_item.py
│   │   ├── test_answer.py
│   │   ├── test_question.py
│   │   ├── test_message.py
│   │   ├── test_block.py
│   │   └── test_visit.py
│   └── service/            # src/service/ のテスト
│       ├── test_user_service.py
│       ├── test_profile_service.py
│       ├── test_qna_service.py
│       ├── test_message_service.py
│       ├── test_block_service.py
│       ├── test_visit_service.py
│       └── test_categories.py
├── integration/            # 結合テスト
│   ├── router/            # src/router/ のテスト
│   │   ├── test_auth.py
│   │   ├── test_user_router.py
│   │   ├── test_username_router.py
│   │   ├── test_profile_router.py
│   │   ├── test_qna_router.py
│   │   ├── test_message_router.py
│   │   ├── test_block_router.py
│   │   └── test_visit_router.py
│   ├── workflows/         # エンドツーエンドワークフロー
│   │   ├── test_user_registration.py
│   │   ├── test_profile_setup.py
│   │   ├── test_qna_workflow.py
│   │   ├── test_messaging_workflow.py
│   │   └── test_discovery_workflow.py
│   └── database/          # データベース結合テスト
│       ├── test_user_crud.py
│       ├── test_profile_crud.py
│       └── test_relationships.py
├── fixtures/              # テストフィクスチャとヘルパー
│   ├── __init__.py
│   ├── conftest.py       # 共通フィクスチャ
│   ├── user_fixtures.py  # ユーザー関連フィクスチャ
│   ├── profile_fixtures.py
│   ├── qna_fixtures.py
│   └── database_fixtures.py
├── mocks/                # モックデータとスタブ
│   ├── __init__.py
│   ├── twitter_mock.py   # Twitter API モック
│   ├── sentry_mock.py    # Sentry モック
│   └── external_services.py
└── utils/                # テストユーティリティ
    ├── __init__.py
    ├── test_helpers.py
    ├── assertions.py
    └── data_generators.py
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

### 3. ワークフローテスト (integration/workflows/)

- ユーザーの実際の使用パターンをテスト
- 複数のAPIコールの組み合わせ
- エンドツーエンドシナリオ

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

## 実装優先順位

1. **Phase 1: ユニットテスト基盤**
   - service/ のテスト (ビジネスロジック)
   - schema/ のテスト (バリデーション)
   - config/ のテスト (設定管理)

2. **Phase 2: 結合テスト**
   - router/ のテスト (API)
   - database/ のテスト (CRUD)

3. **Phase 3: ワークフローテスト**
   - workflows/ のテスト (E2E)
   - 外部サービス連携テスト
