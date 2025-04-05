import json
import logging
import os
import datetime
from flask import Flask, request
from flask_cors import CORS

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({"message": "Welcome to API Gateway with Lambda Authorizer simulation"})

@app.route('/protected')
def protected():
    """
    保護されたAPIエンドポイント
    認証済みユーザーからのリクエストを処理し、レスポンスを返します
    """
    try:
        # リクエスト情報のログ記録
        request_data = {
            "path": request.path,
            "method": request.method,
            "remote_addr": request.remote_addr,
            "headers": dict(request.headers)
        }
        logger.info(f"Request received: {json.dumps(request_data)}")

        # Nginxから転送された認証情報の取得
        principal_id = request.headers.get('X-Principal-ID', 'unknown')

        # コンテキスト情報（サンプル）
        context_data = {
            "stringKey": "sample string value",
            "numberKey": 123,
            "booleanKey": True
        }

        # 現在の日時
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # レスポンスデータの作成
        response_data = {
            "message": "認証成功！保護されたリソースにアクセスできました",
            "principalId": principal_id,
            "timestamp": current_time,
            "authContext": context_data
        }

        # クエリパラメータがある場合は追加
        if request.args:
            response_data["queryParams"] = dict(request.args)

        # 正常なレスポンスを返す
        return json.dumps(response_data, ensure_ascii=False)

    except Exception as e:
        # エラーログの記録
        logger.error(f"Error processing request: {str(e)}", exc_info=True)

        # エラーレスポンスを返す
        return json.dumps({
            "message": "内部サーバーエラーが発生しました",
            "errorType": type(e).__name__
        }, ensure_ascii=False), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
