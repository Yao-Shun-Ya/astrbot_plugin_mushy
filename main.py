import os
import astrbot.api.message_components as Comp 

# 必要的 API 和组件
from astrbot.api.event import filter
from astrbot.api.star import Context, Star, register
from astrbot.core.star.filter.event_message_type import EventMessageType 
from astrbot.api.all import *

@register("astrbot_plugin_mushy", "YourName", "特定人触发图文回复", "1.0.0")
class QQSpecialReply(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        
        # 白名单 ID
        self.ALLOWED_USERS = ["3525426079", "2720356281"] 
        
        # 触发配置
        self.TRIGGER_MAP = {
            "今日小憩": {
                "file": "小憩.png",
                "msg": "鲸鱼小憩会一直和你在一起的哦～"
            },
            "今日爻舜": {
                "file": "爻舜.png",
                "msg": "笨蛋爻舜会一直和你在一起的哦～"
            }
        }

    @filter.event_message_type(EventMessageType.ALL)
    async def check_and_reply(self, event: AstrMessageEvent):
        
        print(f"[MUSH-DEBUG] Plugin received message. Sender ID: {event.get_sender_id()}")
        
        if not hasattr(event, 'message_str') or not event.message_str:
            return

        message = event.message_str.strip()
        
        if message not in self.TRIGGER_MAP:
            return

        sender_id = event.get_sender_id()
        if sender_id not in self.ALLOWED_USERS:
            print(f"[MUSH-DEBUG] Blocked user: {sender_id}. Ignoring command.")
            return

        data = self.TRIGGER_MAP[message]
        reply_text = data["msg"]      
        image_filename = data["file"] 
        
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(plugin_dir, image_filename)

        if not os.path.exists(image_path):
            print(f"[MUSH-DEBUG] ERROR: Image file not found at {image_path}")
            yield event.plain_result(f"错误：找不到图片 {image_filename}")
            return

        # 拦截并发送
        event.stop_event()
        
        # 构造组件
        text_comp = Comp.Plain(reply_text)
        image_comp = Comp.Image.fromFileSystem(image_path)
        
        # 图片在前
        print(f"[MUSH-DEBUG] Sending combined image then text: {image_path}")
        yield event.chain_result([image_comp, text_comp])
