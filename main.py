import os
from astrbot.api.all import *

@register("astrbot_plugin_qq_special", "YourName", "特定人触发图文回复", "1.0.2")
class QQSpecialReply(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        
        # --- 配置区域 ---
        
        # 1. 允许触发的 QQ 号 (白名单)
        self.ALLOWED_USERS = ["3525426079", "2720356281"] 
        
        # 2. 触发配置字典
        # 结构： "关键词": { "file": "图片文件名", "msg": "文字回复内容" }
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
        # ----------------

    @event_message_type(MessageType.TEXT)
    async def check_and_reply(self, event: AstrMessageEvent):
        message = event.message_str.strip()
        
        # 1. 检查是否是触发词
        if message not in self.TRIGGER_MAP:
            return

        # 2. 检查权限
        sender_id = event.get_sender_id()
        if sender_id not in self.ALLOWED_USERS:
            return

        # 3. 获取对应的数据
        data = self.TRIGGER_MAP[message]
        reply_text = data["msg"]      # 获取文字
        image_filename = data["file"] # 获取文件名
        
        # 4. 准备图片路径
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(plugin_dir, image_filename)

        if not os.path.exists(image_path):
            yield event.plain_result(f"错误：找不到图片 {image_filename}")
            return

        # 5. 拦截大模型，开始发送
        event.stop_event()
        
        # 连续发送两条消息
        # 第一条：发送文字
        yield event.plain_result(reply_text)
        
        # 第二条：发送图片
        yield event.image_result(image_path)