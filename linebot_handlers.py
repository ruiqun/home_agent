import os
from linebot.v3.messaging import (
    MessagingApi,
    Configuration,
    ApiClient,
    TextMessage,
    ReplyMessageRequest
)
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks.models import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    VideoMessageContent,
    StickerMessageContent
)
from message_processing import process_message, process_sticker_message


class LineBotHandlers:
    def __init__(self, line_channel_access_token, line_channel_secret):
        self.line_channel_access_token = line_channel_access_token
        self.line_channel_secret = line_channel_secret
        config = Configuration(access_token=line_channel_access_token)
        api_client = ApiClient(configuration=config)
        self.line_bot_api = MessagingApi(api_client)
        self.handler = WebhookHandler(line_channel_secret)
        os.makedirs("images", exist_ok=True)
        os.makedirs("videos", exist_ok=True)

    def setup_handlers(self):
        @self.handler.add(MessageEvent, message=(TextMessageContent, ImageMessageContent, VideoMessageContent))
        def handle_message(event):
            reply_text = process_message(event, self.line_channel_access_token)
            reply_message = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
            try:
                self.line_bot_api.reply_message(reply_message)
                print(f"✅ 已成功回复用户: {reply_text}")
            except Exception as e:
                print(f"❌ 发送消息失败: {e}")

        @self.handler.add(MessageEvent, message=StickerMessageContent)
        def handle_sticker_message(event):
            event_dict = {
                "source": {
                    "userId": event.source.user_id if event.source.type == "user" else None
                },
                "message": {
                    "sticker_id": event.message.sticker_id,
                    "package_id": event.message.package_id
                }
            }
            reply_text = process_sticker_message(event_dict)
            reply_message = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
            try:
                self.line_bot_api.reply_message(reply_message)
                print(f"✅ 已成功回复用户: {reply_text}")
            except Exception as e:
                print(f"❌ 发送消息失败: {e}")

        return self.handler