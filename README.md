# hitoQ

<p align="center">
  <img src="https://raw.githubusercontent.com/gengaret/hitoQ/main/docs/images/logo.png" alt="hitoQ Logo" width="200"/>
</p>

<p align="center">
  <strong>Q&Aを通じて自分を表現できるプロフィールサービス</strong>
</p>

<p align="center">
  <img alt="Language: Python" src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white">
  <img alt="Framework: FastAPI" src="https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi&logoColor=white">
  <img alt="Language: TypeScript" src="https://img.shields.io/badge/TypeScript-5.x-blue?logo=typescript&logoColor=white">
  <img alt="Framework: SvelteKit" src="https://img.shields.io/badge/SvelteKit-2.x-orange?logo=svelte&logoColor=white">
  <img alt="License: Apache 2.0" src="https://img.shields.io/badge/License-Apache_2.0-blue.svg">
</p>

---

**hitoQ (ヒトキュー)** は、用意された質問に答えたり、友達から質問を受け取ったりすることで、あなたの多面的な魅力を引き出すプロフィールを簡単に作成・共有できるサービスです。

従来のプロフィール項目だけでは伝わらない、あなたの価値観、好きなこと、ユニークな一面を、Q&A形式で楽しく表現してみませんか？

## 主な機能

- **Q&Aプロフィール**: 豊富な質問テンプレートから選んで回答するだけで、あなただけのユニークなプロフィールが完成します。
- **メッセージ機能**: 他のユーザーに質問を送ったり、感想を伝えたりできます。
- **リアクション機能**: 気になる回答に「いいね」をしたり、コメントを送ってコミュニケーションできます。
- **カスタマイズ**: プロフィール項目を自由に追加・編集して、あなただけのオリジナルページを作成できます。
- **X (Twitter) 認証**: 安全なOAuth2.0認証で、簡単かつセキュアにログインできます。

## 技術スタック

`hitoQ` は、モダンでスケーラブルな技術スタックで構築されています。

| カテゴリ           | フロントエンド                                                                   | バックエンド                                                                                               |
| :----------------- | :------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------- |
| **フレームワーク** | [SvelteKit](https://kit.svelte.dev/)<br>[Tailwind CSS](https://tailwindcss.com/) | [FastAPI](https://fastapi.tiangolo.com/)<br>[SQLAlchemy](https://www.sqlalchemy.org/)                      |
| **言語**           | [TypeScript](https://www.typescriptlang.org/)                                    | [Python 3.11+](https://www.python.org/)                                                                    |
| **パッケージ管理** | [pnpm](https://pnpm.io/)                                                         | [uv](https://github.com/astral-sh/uv)                                                                      |
| **DB**             | -                                                                                | [PostgreSQL](https://www.postgresql.org/)<br>[Alembic](https://alembic.sqlalchemy.org/en/latest/)          |
| **テスト**         | [Vitest](https://vitest.dev/)                                                    | [pytest](https://docs.pytest.org/)                                                                         |
| **その他**         | [ESLint](https://eslint.org/)<br>[Prettier](https://prettier.io/)                | [Sentry](https://sentry.io/)<br>[Ruff](https://github.com/astral-sh/ruff)<br>[Mypy](http://mypy-lang.org/) |

## ローカルでの起動方法

このプロジェクトはDockerを使用して、簡単に開発環境を構築できます。

### 前提条件

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 手順

1.  **リポジトリをクローン**

    ```bash
    git clone https://github.com/gengaret/hitoQ.git
    cd hitoQ
    ```

2.  **環境変数の設定**

    `.env.example` をコピーして `.env` ファイルを作成します。

    ```bash
    cp .env.example .env
    ```

    次に、`.env` ファイルを開き、最低限以下の項目を設定してください。特に `SECRET_KEY` と `SESSION_SECRET_KEY` は必ずユニークな値に変更してください。

    ```dotenv
    # Application Security
    SECRET_KEY= # `openssl rand -hex 32` などで生成した強力なキーを設定
    SESSION_SECRET_KEY= # `openssl rand -hex 32` などで生成した強力なキーを設定

    # Twitter OAuth Configuration (Twitterログインを試す場合)
    TWITTER_CLIENT_ID=your_twitter_client_id
    TWITTER_CLIENT_SECRET=your_twitter_client_secret
    ```

3.  **Dockerコンテナを起動**

    以下のコマンドを実行して、すべてのサービスをビルドしてバックグラウンドで起動します。

    ```bash
    docker-compose -f .devcontainer/docker-compose.yml up -d --build
    ```

    初回起動時は、依存関係のダウンロードとビルドのため、数分かかることがあります。

## アクセスポイント

コンテナが正常に起動したら、以下のURLにアクセスできます。

- **フロントエンド**: [http://localhost:5173](http://localhost:5173)
- **バックエンドAPI**: [http://localhost:8000](http://localhost:8000)
- **APIドキュメント (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## ライセンス

このプロジェクトは [Apache License 2.0](LICENSE) の下で公開されています。
