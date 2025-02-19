import requests, logging
from pyngrok import ngrok, conf
from pyngrok.conf import PyngrokConfig
import os,logging

# 关闭已有 ngrok 进程（防止重复）
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["ALL_PROXY"] = ""

ngrok.kill()

# 从 utils/config.py 导入配置
from utils.config import FLASK_PORT, LINE_CHANNEL_ACCESS_TOKEN, LINE_API_URL, NGROK_REGION, NGROK_AUTH_TOKEN, NGROK_PATH

def start_ngrok():
    """ 启动 ngrok 并返回公网 URL """
    print("🚀 正在启动 ngrok ...")
    # 停止所有 ngrok会话
    #ngrok.kill()
    # 重新配置
    new_config = PyngrokConfig(
        region=NGROK_REGION,
        auth_token=NGROK_AUTH_TOKEN,
        ngrok_path=NGROK_PATH
    )
    conf.set_default(new_config)
    tunnel = ngrok.connect(FLASK_PORT, "http")  # 连接 Flask 服务器
    public_url = tunnel.public_url
    print(f"✅ ngrok 启动成功，公网 URL: {public_url}")

    # 自动更新 LINE Webhook URL
    update_line_webhook(public_url + "/callback")

    return public_url

def update_line_webhook(new_url):
    """ 更新 LINE Developer Webhook URL """
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {"endpoint": new_url}

    print("Start LINE Developer Webhook ...")
    response = requests.put(
        LINE_API_URL,
        headers=headers,
        json=body,
        timeout = 10  # 设置超时为 10 秒
    )
    print("End LINE Developer Webhook update")

    if response.status_code == 200:
        print(f"✅ Webhook 更新成功: {new_url}")
    else:
        print(f"❌ Webhook 更新失败: {response.status_code}, {response.text}")