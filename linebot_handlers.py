# linebot_handlers.py

import os, requests, time, torch
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent, ImageMessageContent, VideoMessageContent, StickerMessageContent
from utils.config import AUTODL_MODEL_URL

class LineBotHandlers:
    def __init__(self, line_channel_access_token, line_channel_secret):
        self.line_channel_access_token = line_channel_access_token
        self.line_channel_secret = line_channel_secret

        config = Configuration(access_token=line_channel_access_token)
        api_client = ApiClient(configuration=config)
        self.line_bot_api = MessagingApi(api_client)
        self.handler = WebhookHandler(line_channel_secret)

        # 创建存储目录（图片 / 影片）
        os.makedirs("images", exist_ok=True)
        os.makedirs("videos", exist_ok=True)

    def setup_handlers(self):
        # 处理文字消息
        @self.handler.add(MessageEvent, message=TextMessageContent)
        def handle_text_message(event):
            user_message = event.message.text
            user_id = event.source.user_id

            print(f"📨 收到用户 {user_id} 的文字消息: {user_message}")

            # 强制不使用代理
            proxies = {}

            # 调用AutoDL云端模型服务
            try:
                data = {"input_text": user_message}
                response = requests.post(AUTODL_MODEL_URL, json=data, proxies=proxies)
                print(response.json())
                if response.status_code == 200:
                    result = response.json()
                    reply_text = result["reply"]
                else:
                    reply_text = "抱歉，调用模型服务失败，请稍后再试。"
            except Exception as e:
                print(f"调用模型服务时出现异常: {e}")
                reply_text = "抱歉，调用模型服务时出现异常，请稍后再试。"

            # 让Bot回复用户
            reply_message = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
            try:
                self.line_bot_api.reply_message(reply_message)
                print(f"✅ 已成功回复用户: {reply_text}")
            except Exception as e:
                print(f"❌ 发送消息失败: {e}")

        # 处理贴图消息
        @self.handler.add(MessageEvent, message=StickerMessageContent)
        def handle_sticker_message(event):
            user_id = event.source.user_id
            sticker_id = event.message.sticker_id
            package_id = event.message.package_id

            print(f"📨 收到用户 {user_id} 的贴图，Sticker ID: {sticker_id}，Package ID: {package_id}")

            reply_text = "你发送的贴图很可爱哦！"
            reply_message = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
            try:
                self.line_bot_api.reply_message(reply_message)
                print(f"✅ 已成功回复用户: {reply_text}")
            except Exception as e:
                print(f"❌ 发送消息失败: {e}")

        # 处理图片消息
        @self.handler.add(MessageEvent, message=ImageMessageContent)
        def handle_image_message(event):
            user_id = event.source.user_id
            message_id = event.message.id

            # 下载图片
            image_path = f"images/{message_id}.jpg"
            self.download_file(message_id, image_path)

            print(f"收到用户 {user_id} 的图片，已保存至 {image_path}")

            # 回复用户
            reply_text = f"你的图片已收到！存储位置: {image_path}"
            reply_message_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )

            try:
                self.line_bot_api.reply_message(reply_message_request)
                print(f"✅ 已成功回复用户: {reply_text}")
            except Exception as e:
                print(f"❌ 发送消息失败: {e}")

        # 处理影片消息
        @self.handler.add(MessageEvent, message=VideoMessageContent)
        def handle_video_message(event):
            user_id = event.source.user_id
            message_id = event.message.id

            # 下载影片
            video_path = f"videos/{message_id}.mp4"

            print(f"🎥 收到用户 {user_id} 的影片，尝试下载至: {video_path}")

            self.download_file(message_id, video_path)

            # 确保文件实际存在
            if os.path.exists(video_path):
                print(f"✅ 影片已存储: {video_path}")
                reply_text = f"你的影片已收到！存储位置: {video_path}"
            else:
                print(f"❌ 影片下载失败！请检查 download_file() 方法。")
                reply_text = "⚠️ 抱歉，影片下载失败，请稍后重试。"

            # 回复用户
            reply_message_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )

            try:
                self.line_bot_api.reply_message(reply_message_request)
                print(f"✅ 已成功回复用户: {reply_text}")
            except Exception as e:
                print(f"❌ 发送消息失败: {e}")

        return self.handler

    def download_file(self, message_id, save_path):
        """ 下载用户发送的多媒体文件（图片/影片）并存储 """
        content_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
        headers = {"Authorization": f"Bearer {self.line_channel_access_token}"}

        print(f"🔹 正在下载文件: {content_url}")

        max_retries = 3
        retries = 0
        while retries < max_retries:
            response = requests.get(content_url, headers=headers, stream=True)
            if response.status_code == 200:
                # 创建目录（如果不存在）
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)

                print(f"✅ 文件已成功下载并存储: {save_path}")
                return
            elif response.status_code == 202:
                print(f"收到 202 状态码，等待 5 秒后重试（第 {retries + 1} 次）")
                time.sleep(5)
                retries += 1
            else:
                print(f"❌ 下载失败: {response.status_code}, {response.text}")
                break

        print(f"❌ 达到最大重试次数，下载失败。")