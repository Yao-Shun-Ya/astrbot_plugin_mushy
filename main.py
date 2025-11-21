import os
from pathlib import Path
import astrbot.api.message_components as Comp 
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.core.star.filter.event_message_type import EventMessageType 

@register("astrbot_plugin_mushy", "YourName", "特定人触发图文回复", "1.0.0")
class QQSpecialReply(Star):
    def __init__(self, context: Context, config: AstrBotConfig): 
        super().__init__(context)
        self.config = config 
        self._load_config(config)

    def _load_config(self, config: AstrBotConfig):
        raw_allowed_users = config.get("allowed_users", [])
        self.ALLOWED_USERS_SET = {str(u) for u in raw_allowed_users}
        
        trigger_group = config.get("trigger_group", {})
        self.TRIGGER_MAP = {}
        
        if trigger_group:
            for rule_name, rule_data in trigger_group.items():
                if isinstance(rule_data, dict) and rule_data.get('trigger'):
                    trigger_key = rule_data['trigger']
                    self.TRIGGER_MAP[trigger_key] = rule_data
                    logger.debug(f"Loaded rule: {trigger_key}")
        
        if not self.TRIGGER_MAP:
             logger.warning("Final TRIGGER_MAP is empty. Please check WebUI config.")


    @filter.event_message_type(EventMessageType.ALL)
    async def check_and_reply(self, event: AstrMessageEvent):
        
        if not hasattr(event, 'message_str') or not event.message_str:
            return

        message = event.message_str.strip()
        
        if message not in self.TRIGGER_MAP:
            return

        sender_id = event.get_sender_id()
        if str(sender_id) not in self.ALLOWED_USERS_SET: 
            logger.debug(f"Blocked user: {sender_id}. Ignoring command.")
            return

        data = self.TRIGGER_MAP[message]
        reply_text = data.get("msg", "")      
        image_filename = data.get("file", "")
        
        plugin_path = Path(__file__).parent
        image_path = plugin_path / image_filename 

        if not os.path.exists(image_path):
            logger.error(f"Image file not found at {image_path}")
            yield event.plain_result(f"错误：找不到图片 {image_filename}")
            return

        event.stop_event()
        
        text_comp = Comp.Plain(reply_text)
        image_comp = Comp.Image.fromFileSystem(image_path)
        
        message_chain = [image_comp, text_comp]
        
        logger.debug(f"Sending combined image then text: {image_path}")
        
        yield event.chain_result(message_chain)
