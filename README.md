# hitoQ

hitoQは、Q&A形式でプロフィールを作成・共有できるソーシャルプロフィールサービスです。

## 🚀 サービス概要

hitoQは、従来のプロフィールサービスとは異なり、質問と回答を通じて自分自身を表現できるプラットフォームです。

### 主な機能

- **Q&Aプロフィール**: 質問に答えることで自分らしさを表現
- **バケットリスト**: やりたいことリストを作成・管理
- **プロフィール項目**: 基本的なプロフィール情報の設定
- **X（Twitter）認証**: OAuth2.0によるセキュアなログイン

### 技術スタック

**フロントエンド**

- SvelteKit
- TypeScript
- Tailwind CSS
- Vite

**バックエンド**

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic (データベースマイグレーション)
- Python 3.11+

## 🏗️ アーキテクチャ

```
hitoq/
├── frontend/           # SvelteKitフロントエンド
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api/    # API クライアント
│   │   │   ├── components/  # UI コンポーネント
│   │   │   ├── types/  # TypeScript型定義
│   │   │   └── utils/  # ユーティリティ関数
│   │   └── routes/     # ページとAPI ルート
└── backend/            # FastAPI バックエンド
    └── src/
        ├── db/         # データベース設定
        ├── router/     # API ルーター
        ├── schema/     # Pydantic スキーマ
        └── service/    # ビジネスロジック
```

## 🔧 セットアップ

### 必要な環境

- Node.js 18+
- Python 3.11+
- PostgreSQL
- pnpm (推奨)

### 開発環境の起動

**バックエンド**

```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload
```

**フロントエンド**

```bash
cd frontend
pnpm install
pnpm run dev
```

## 🌐 アクセス

- フロントエンド: http://localhost:5173
- バックエンド API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## 📊 データモデル

### 質問カテゴリ

- `self-introduction`: 自己紹介
- `values`: 価値観
- `otaku`: 趣味・オタク
- `misc`: その他

### 主要なエンティティ

- **User**: ユーザー情報
- **Question**: 質問
- **Answer**: 回答
- **ProfileItem**: プロフィール項目
- **BucketListItem**: バケットリスト項目
