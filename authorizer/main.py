import os
import logging
from flask import Flask, request, jsonify

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 環境変数から認証シークレットを取得
AUTH_SECRET = os.environ.get('AUTH_SECRET', 'your_secret_token_here')

@app.route('/authorize')
def authorize():
    """
    APIリクエストの認証を処理する関数
    Nginxのauth_requestモジュールから呼び出される

    Returns:
        200 - 認証成功
        401 - 認証失敗
    """
    try:
        # Authorizationヘッダーを取得
        auth_header = request.headers.get('Authorization')

        logger.info(f"Authorization request received: {request.headers}")

        if not auth_header:
            logger.warning("No Authorization header found")
            return "", 401

        # Bearer トークンの検証
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # 'Bearer ' の後の部分を取得

            # トークン検証ロジック
            if token == AUTH_SECRET:
                logger.info("Authentication successful")

                # 認証成功のレスポンスにプリンシパルIDを含める
                response = jsonify({"isAuthorized": True})
                response.headers['X-Principal-ID'] = 'user'
                return response, 200

        logger.warning("Authentication failed")
        return "", 401

    except Exception as e:
        logger.error(f"Error during authorization: {str(e)}", exc_info=True)
        return "", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
