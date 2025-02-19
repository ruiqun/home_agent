import os, logging
from flask import Flask, request
from ngrok_manager import start_ngrok
from linebot_handlers import LineBotHandlers
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 从 utils/config.py 导入配置
from utils.config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET

# 初始化 LINE Bot 处理类
line_bot_handlers = LineBotHandlers(LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET)
handler = line_bot_handlers.setup_handlers()

@app.route("/callback", methods=['POST'])
def callback():
    """ 处理 LINE Webhook 请求 """
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 打印日志，确认 Webhook 收到数据
    print("📩 收到 Webhook 请求:")
    print("🔹 Headers:", request.headers)
    print("🔹 Body:", body)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error handling request: {e}")
        return 'Error', 500

    return 'OK', 200


if __name__ == "__main__":
    # 配置日志级别和格式
    logging.basicConfig(
        level=logging.DEBUG,  # 设置日志级别为 DEBUG
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # 启动 ngrok，并获取公网 URL
    public_url = start_ngrok()

    app.run(host="0.0.0.0", port=5001, debug=False)
    print("🔗 Ngrok 正在运行中，按 Ctrl+C 退出...")
    while True:
        pass  # 无限循环，让进程不退出