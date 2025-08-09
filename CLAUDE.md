# hitoQ プロジェクト開発ガイド

このドキュメントは、hitoQ プロジェクトの開発における共通の規則とガイドラインをまとめています。

## プロジェクト概要

- **フロントエンド**: SvelteKit + TypeScript + Tailwind CSS
- **バックエンド**: FastAPI + Python + PostgreSQL
- **認証**: Twitter OAuth 2.0
- **メッセージング**: リアルタイムメッセージング機能
- **デプロイ**: Docker

## フロントエンド開発規則

### Svelte 5 Runes 記法の使用

- **必須**: Svelte 5 の rune 記法を使用する
- `onMount`, `on:click` などの旧記法は使用しない
- 状態管理は `$state()`, `$derived()`, `$effect()` を使用
- プロパティは `$props()` を使用

#### 例：

```typescript
// ✅ 正しい（Svelte 5 rune記法）
let count = $state(0);
let doubled = $derived(count * 2);

const { message, onUpdate } = $props<{
  message: string;
  onUpdate: (value: string) => void;
}>();

// ❌ 使用禁止（旧記法）
export let message: string;
onMount(() => {});
```

### TypeScript規則

- **型 `any` の使用禁止**: ESLintで設定済み
- どうしても必要な場合は `// eslint-disable-next-line @typescript-eslint/no-explicit-any` を追記
- 型定義は `$lib/types/` に配置
- 未使用の変数は ESLint で警告される場合、明示的に使用するか `// eslint-disable-next-line` を追記

### コード分割

- **500行以上のファイルは分割を検討**
- コンポーネントは適切な粒度で分割
- 共通のロジックは `$lib/utils/` に配置
- API クライアントは `$lib/api-client/` に配置

#### コンポーネント分離の指針

**機能単位での分割を優先**：

- ページ内の論理的なセクション単位で分割（例：設定ページ → プライバシー設定、通知設定、テーマ設定）
- 50-100行を超える独立した機能ブロックは分離を検討
- 同じフォルダ内での分割でも問題なし（`routes/settings/PrivacySettings.svelte` など）

**再利用性での分割**：

- 複数箇所で使用される場合のみ `$lib/components/` に配置
- 本当に汎用的で再利用される小さなコンポーネント（Button、Modal など）のみ

**避けるべき過度な分割**：

- 10-20行程度の小さなコンポーネントへの分割
- 単一箇所でのみ使用される汎用コンポーネント化
- 責務が明確でない細かすぎる分割

### UI/デザイン統一

- **Tailwind CSS** を使用
- 色彩は一貫性を保つ（primary: orange-400, orange-500 など）
- レスポンシブデザインを考慮
- アクセシビリティに配慮（aria-label, role 属性など）

### イベントハンドリング

```typescript
// ✅ 正しい（Svelte 5）
<button onclick={() => handleClick()}>Click</button>

// ❌ 使用禁止（旧記法）
<button on:click={handleClick}>Click</button>
```

### ライフサイクル

```typescript
// ✅ 正しい（Svelte 5）
$effect(() => {
  // 副作用の処理
  return () => {
    // クリーンアップ
  };
});

// ❌ 使用禁止（旧記法）
onMount(() => {});
onDestroy(() => {});
```

## バックエンド開発規則

### Python コーディング規則

- **コードフォーマット**: Ruff を使用
- **型チェック**: mypy を使用
- **行長**: 88文字
- **Python バージョン**: 3.11+

### FastAPI 規則

- ルーターは機能別に分割（`src/router/`）
- サービス層は `src/service/` に配置
- データベースモデルは `src/db/tables.py`
- スキーマは `src/schema/` に配置

### データベース

- **ORM**: SQLAlchemy
- **マイグレーション**: Alembic
- **命名規則**: snake_case

### エラーハンドリング

- 適切な HTTP ステータスコードを使用
- エラーログは構造化ログ（structlog）で記録
- Sentry によるエラー監視

## 共通開発規則

### Git コミット規則

- コミットメッセージは日本語で記述
- 機能追加: `feat: 新機能の説明`
- バグ修正: `fix: 修正内容の説明`
- リファクタリング: `refactor: リファクタリング内容`

### 開発フロー

1. 機能ブランチの作成: `feature/#issue-number-description`
2. 開発・テスト
3. プルリクエスト作成
4. コードレビュー
5. マージ

### テスト

- **フロントエンド**: Vitest を使用
- **バックエンド**: pytest を使用
- テストは機能実装と同時に記述

### 環境変数

- `.env` ファイルで管理
- 本番環境では環境変数で設定
- 機密情報は絶対にコミットしない

## ツール設定

### 使用可能なコマンド

#### フロントエンド

```bash
# 開発サーバー起動
npm run dev

# ビルド
npm run build

# リンター・フォーマッター
npm run lint
npm run format

# テスト
npm run test
```

#### バックエンド

```bash
# 開発サーバー起動
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# リンター・フォーマッター
ruff check
ruff format

# 型チェック
mypy src/

# テスト
pytest
```

## アーキテクチャ

### フロントエンド構造

```
frontend/src/
├── routes/          # SvelteKit ルート
├── lib/
│   ├── components/  # 再利用可能コンポーネント
│   ├── api-client/  # API クライアント
│   ├── types/       # TypeScript 型定義
│   └── utils/       # ユーティリティ関数
└── app.html         # HTML テンプレート
```

### バックエンド構造

```
backend/src/
├── router/          # FastAPI ルーター
├── service/         # ビジネスロジック
├── schema/          # Pydantic スキーマ
├── db/              # データベース関連
├── config/          # 設定ファイル
└── main.py          # アプリケーションエントリーポイント
```

## パフォーマンス

- 画像は適切なサイズで最適化
- API レスポンスは適切なキャッシュヘッダーを設定
- データベースクエリは適切にインデックスを使用
- フロントエンドでは不要な再レンダリングを避ける

## セキュリティ

- 認証にはJWTトークンを使用
- CORS設定は適切に制限
- SQLインジェクション対策（ORMを適切に使用）
- XSS対策（適切なエスケープ）
- 機密情報の適切な管理

---

このガイドラインに従って開発を進めることで、一貫性のある保守しやすいコードベースを維持できます。
