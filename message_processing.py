import os
import requests
import time
from utils.config import AUTODL_MODEL_URL


def download_file(message_id, save_path, access_token):
    """ 下载用户发送的多媒体文件（图片/影片）并存储 """
    content_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    print(f"🔹 正在下载文件: {content_url}")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    max_retries = 3
    retries = 0
    while retries < max_retries:
        response = requests.get(content_url, stream=True, headers=headers)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            print(f"✅ 文件已成功下载并存储: {save_path}")
            return save_path
        elif response.status_code == 202:
            print(f"收到 202 状态码，等待 5 秒后重试（第 {retries + 1} 次）")
            time.sleep(5)
            retries += 1
        else:
            print(f"❌ 下载失败: {response.status_code}, {response.text}")
            break

    print(f"❌ 达到最大重试次数，下载失败。")
    return None


def call_autodl_service(message_type, message_content):
    """ 调用远程 AUTODL 服务 """
    proxies = {}
    try:
        data = {
            "input_type": message_type,
            "input_content": message_content
        }
        response = requests.post(AUTODL_MODEL_URL, json=data, proxies=proxies)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"调用模型服务时出现异常: {e}")
    return {}


def process_message(event, access_token):
    user_id = event.get('source', {}).get('userId')

    message = event.get('message', {})
    message_type = message.get('type')
    message_id = message.get('id')

    if message_type == 'text':
        message_content = message.get('text')
        file_path = None
    elif message_type == 'image':
        message_content = f"images/{message_id}.jpg"
        file_path = download_file(message_id, message_content, access_token)
        if file_path is None:
            message_content = None
    elif message_type == 'video':
        message_content = f"videos/{message_id}.mp4"
        file_path = download_file(message_id, message_content, access_token)
        if file_path is None:
            message_content = None
    else:
        message_content = None

    print(f"📨 收到用户 {user_id} 的 {message_type} 消息: {message_content}")

    # 调用远程 AUTODL 服务
    if message_content is not None:
        response = call_autodl_service(message_type, message_content)
        reply_text = response.get("reply", "抱歉，调用模型服务失败，请稍后再试。")
    else:
        reply_text = "无法处理此消息，请稍后重试。"

    return reply_text


def process_sticker_message(event):
    user_id = event.get('source', {}).get('userId')
    sticker_id = event.get('message', {}).get('sticker_id')
    package_id = event.get('message', {}).get('package_id')

    print(f"📨 收到用户 {user_id} 的贴图，Sticker ID: {sticker_id}，Package ID: {package_id}")
    return "你发送的贴图很可爱哦！"