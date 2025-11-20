import os
# ⭐ 修复导入：从正确的路径导入 filter 对象
from astrbot.api.event import filter
from astrbot.api.star import Context, Star, register
# ⭐ 导入 EventMessageType，以便使用 ALL 常量（如果需要）
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

    # ⭐ 最终修复：使用 filter.event_message_type(EventMessageType.ALL) 监听所有消息
    @filter.event_message_type(EventMessageType.ALL)
    async def check_and_reply(self, event: AstrMessageEvent):
        
        # 诊断日志：检查插件是否被其他插件拦截，是否正常运行
        print(f"[MUSH-DEBUG] Plugin received message. Sender ID: {event.get_sender_id()}")
        
        # 确保是文本消息，否则不处理
        if not hasattr(event, 'message_str') or not event.message_str:
            return

        message = event.message_str.strip()
        
        # 1. 检查触发词
        if message not in self.TRIGGER_MAP:
            return

        # 2. 检查权限
        sender_id = event.get_sender_id()
        if sender_id not in self.ALLOWED_USERS:
            print(f"[MUSH-DEBUG] Blocked user: {sender_id}. Ignoring command.")
            return

        # 3. 获取数据
        data = self.TRIGGER_MAP[message]
        reply_text = data["msg"]      
        image_filename = data["file"] 
        
        # 4. 寻找图片路径
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(plugin_dir, image_filename)

        # 5. 检查文件是否存在
        if not os.path.exists(image_path):
            print(f"[MUSH-DEBUG] ERROR: Image file not found at {image_path}")
            yield event.plain_result(f"错误：找不到图片 {image_filename}")
            return

        # 6. 拦截并发送
        event.stop_event()
        
        yield event.plain_result(reply_text)
        yield event.image_result(image_path)