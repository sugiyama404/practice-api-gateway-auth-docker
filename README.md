# API Gateway HTTP API with Lambda Authorizer のDocker Composeによるシミュレーション

このリポジトリでは、AWSの API Gateway + Lambda Authorizer 構成を、ローカル環境で再現するためのサンプル環境を構築しています。
Nginx がAPI Gatewayの役割を、AuthorizerサービスがLambda Authorizerの役割を果たします。

## アーキテクチャ

アーキテクチャは3つの主要コンポーネントで構成されています。

1. **Nginx (リバースプロキシとオーソライザーの統合):** API Gateway として機能し、リクエストのルーティングとオーソライザーサービスとの統合を行います。 `/protected` へのリクエストをインターセプトし、オーソライザーに転送し、オーソライザーのレスポンスに基づいてバックエンドAPIへのアクセスを許可または拒否します。
2. **オーソライザー (Python Flask アプリ):** Lambda オーソライザーをシミュレートします。 提供された Bearer トークンを秘密鍵に対して検証します。有効な場合は、プリンシパルIDとともに 200 OK を返します。無効な場合は、401 Unauthorized を返します。
3. **API (Python Flask アプリ):** 実際のアプリケーションロジックを提供するバックエンドAPIです。認証が必要な保護されたエンドポイント `/protected` を公開します。


## 処理の流れ
```
Client
  │
  ├─→ GET /protected with Authorization header
  │
  ↓
Nginx (acts like API Gateway)
  │
  ├─→ /auth に内部転送（Authorizerに検証を依頼）
  │     └─→ HTTP 200 OK + ユーザー情報 (Header: X-Principal-ID)
  │
  └─→ /api/protected にリクエストを転送
        └─→ FlaskがX-Principal-IDを受け取り、処理
```

1. **/protected へのリクエスト:** クライアントは `Authorization: Bearer <token>` ヘッダーを付けて `http://localhost/protected` にリクエストを送信します。

2. **Nginx がインターセプトしてオーソライザーに転送:** Nginx はリクエストをインターセプトし、`/auth` ロケーションに転送します。このロケーションは、内部的にオーソライザーサービスへのプロキシとして設定されています。 `Authorization` ヘッダーも転送されます。

3. **オーソライザーがトークンを検証:** オーソライザーサービスはリクエストを受信し、Bearer トークンを抽出します。 `.env` ファイルで定義された `AUTH_SECRET` に対してトークンを検証します。

4. **オーソライザーのレスポンス:** トークンが有効な場合、オーソライザーはユーザー識別子 (例: "user123") を含む `X-Principal-ID` ヘッダーとともに 200 OK レスポンスを返します。トークンが無効な場合は、401 Unauthorized を返します。

5. **Nginx がオーソライザーのレスポンスを処理:** Nginx はオーソライザーのレスポンスを受信します。 200 OK の場合、元のリクエストを `/protected` のバックエンドAPIに転送し、`X-Principal-ID` をヘッダーとして追加します。 401 Unauthorized の場合、Nginx はクライアントに 401 レスポンスを返します。

6. **API がリクエストを処理:** バックエンドAPIは、`X-Principal-ID` ヘッダーを含むリクエストを受信し、それに応じて処理します。




## セットアップ手順
### 1. .env ファイルを作成

ルートに .env ファイルを作成し、以下のように記述してください：

```
# .env
AUTH_SECRET=your_secret_auth
```
この AUTH_SECRET は、Bearerトークンの検証に使われます。

### 2. サービス起動

```
docker compose up --build
```

### 3. 動作確認

認証不要エンドポイント

```
curl http://localhost
```

認証が必要なエンドポイント

```
curl -H "Authorization: Bearer your_secret_auth" http://localhost/protected
```

無効なトークンを指定すると 401 Unauthorized が返ります。




























