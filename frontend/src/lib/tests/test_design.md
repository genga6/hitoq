# フロントエンドテスト設計

## 現在の構造分析

### frontend/src/ 構造

```
src/
├── lib/
│   ├── api-client/      # APIクライアント
│   ├── components/      # 再利用可能コンポーネント
│   ├── stores/          # Svelte stores
│   ├── types/           # TypeScript型定義
│   └── utils/           # ユーティリティ関数
└── routes/              # SvelteKit ルート (ページ)
```

## 提案するテスト構造

```
src/lib/tests/
├── unit/                    # ユニットテスト
│   ├── api-client/         # APIクライアントのテスト
│   │   ├── auth.test.ts
│   │   ├── users.test.ts
│   │   ├── qna.test.ts
│   │   ├── messages.test.ts
│   │   └── profile.test.ts
│   ├── stores/             # Storeのテスト
│   │   ├── theme.test.ts
│   │   ├── toast.test.ts
│   │   ├── errorStore.test.ts
│   │   └── loadingStore.test.ts
│   ├── utils/              # ユーティリティのテスト
│   │   ├── validation.test.ts
│   │   ├── dateFormat.test.ts
│   │   ├── performance.test.ts
│   │   └── userVisitTracking.test.ts
│   └── types/              # 型定義のテスト
│       └── typeGuards.test.ts
├── component/               # コンポーネントテスト
│   ├── ui/                 # UIコンポーネント
│   │   ├── Button.test.ts
│   │   ├── Modal.test.ts
│   │   ├── Toast.test.ts
│   │   ├── Avatar.test.ts
│   │   └── Card.test.ts
│   ├── form/               # フォームコンポーネント
│   │   ├── ValidatedInput.test.ts
│   │   ├── TextareaForm.test.ts
│   │   └── Editable.test.ts
│   ├── domain/             # ドメインコンポーネント
│   │   ├── qna/
│   │   │   └── QuestionAnswerCard.test.ts
│   │   ├── messaging/
│   │   │   ├── MessageForm.test.ts
│   │   │   └── ThreadMessage.test.ts
│   │   └── users/
│   │       └── CategoryFilter.test.ts
│   ├── feedback/           # フィードバックコンポーネント
│   │   ├── LoadingSpinner.test.ts
│   │   ├── ErrorBoundary.test.ts
│   │   └── EmptyState.test.ts
│   └── layout/             # レイアウトコンポーネント
│       ├── Header.test.ts
│       └── Footer.test.ts
├── integration/            # 結合テスト
│   ├── pages/              # ページレベルテスト
│   │   ├── home.test.ts
│   │   ├── profile.test.ts
│   │   ├── qna.test.ts
│   │   └── settings.test.ts
│   ├── workflows/          # ユーザーワークフロー
│   │   ├── auth-flow.test.ts
│   │   ├── profile-setup.test.ts
│   │   ├── qna-workflow.test.ts
│   │   └── messaging-flow.test.ts
│   └── api-integration/    # API統合テスト
│       ├── auth-api.test.ts
│       ├── user-api.test.ts
│       └── qna-api.test.ts
├── e2e/                    # E2Eテスト (Playwright)
│   ├── auth.spec.ts
│   ├── profile.spec.ts
│   ├── qna.spec.ts
│   └── messaging.spec.ts
├── fixtures/               # テストデータ・フィクスチャ
│   ├── mockData.ts
│   ├── userFixtures.ts
│   ├── profileFixtures.ts
│   └── qnaFixtures.ts
├── mocks/                  # モックデータとスタブ
│   ├── apiMocks.ts
│   ├── browserMocks.ts
│   └── storesMocks.ts
├── utils/                  # テストユーティリティ
│   ├── renderHelpers.ts    # レンダリングヘルパー
│   ├── mockHelpers.ts      # モックヘルパー
│   └── testUtils.ts        # テスト共通ユーティリティ
└── setup/                  # テスト設定
    ├── vitest.config.ts    # Vitest設定
    ├── setup.ts            # テストセットアップ
    └── global.d.ts         # グローバル型定義
```

## テストレベル分類

### 1. ユニットテスト (unit/)

- **api-client**: HTTP通信のモック化テスト
- **stores**: Svelte store の状態管理テスト
- **utils**: 純粋関数のロジックテスト
- **types**: TypeScript 型定義・型ガードテスト

### 2. コンポーネントテスト (component/)

- **UI コンポーネント**: プロパティ・イベント・見た目のテスト
- **フォーム**: バリデーション・入力処理のテスト
- **ドメイン**: ビジネスロジック込みのコンポーネント
- **フィードバック**: エラー・ローディング状態のテスト

### 3. 結合テスト (integration/)

- **ページ**: SvelteKit ページの統合テスト
- **ワークフロー**: 複数コンポーネント連携テスト
- **API統合**: 実際のAPIとの通信テスト

### 4. E2Eテスト (e2e/)

- **Playwright**: 実ブラウザでの完全なユーザーシナリオ

## テストツール・ライブラリ

### 主要テストツール

- **Vitest**: ユニット・結合テスト
- **@testing-library/svelte**: Svelteコンポーネントテスト
- **Playwright**: E2Eテスト
- **MSW**: APIモック
- **@vitest/ui**: テストUI

### アサーション・マッチャー

- **@testing-library/jest-dom**: DOM要素のマッチャー
- **@testing-library/user-event**: ユーザーインタラクション

## 実装優先順位

### Phase 1: ユニットテスト基盤

1. **utils/** - 純粋関数テスト (最優先)
2. **stores/** - 状態管理テスト
3. **api-client/** - API通信テスト

### Phase 2: コンポーネントテスト

1. **ui/** - 基本UIコンポーネント
2. **form/** - フォームコンポーネント
3. **domain/** - ドメインコンポーネント

### Phase 3: 統合・E2E テスト

1. **integration/pages/** - ページテスト
2. **integration/workflows/** - ワークフローテスト
3. **e2e/** - E2Eテスト

## テスト実行コマンド

```bash
# 全テスト実行
npm run test

# ユニットテストのみ
npm run test:unit

# コンポーネントテストのみ
npm run test:component

# E2Eテストのみ
npm run test:e2e

# ウォッチモード
npm run test:watch

# カバレッジ付き
npm run test:coverage

# UI付きテスト実行
npm run test:ui
```

## Svelte 5 Runes 対応

### テスト対象

- `$state()` の状態変更テスト
- `$derived()` の計算値テスト
- `$effect()` の副作用テスト
- `$props()` のプロパティテスト

### 注意点

- 旧記法 (`onMount`, `on:click`) のテストは行わない
- 新記法 (`$effect`, `onclick`) でのテストに統一
- rune を使った reactivity のテストに重点を置く

## モック戦略

### API モック

- MSW (Mock Service Worker) でHTTPリクエストをインターセプト
- 開発環境・テスト環境で同じモックを使用

### ブラウザ機能モック

- `localStorage`, `sessionStorage`
- `window.location`, `window.history`
- `IntersectionObserver`, `ResizeObserver`

### 外部サービスモック

- Twitter OAuth
- 画像アップロード
- 通知機能

この設計により、SvelteKit + TypeScript + Svelte 5 Runes に最適化された、保守しやすいテスト構造を構築できます。
