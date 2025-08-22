from typing import Dict, Any
from plugins.napcat_plugin.adapter_client import adapter_client

class MessageUtils:
    """消息发送工具类 - 使用现有adapter连接"""
    
    @staticmethod
    async def send_message(params: Dict[str, Any]) -> Dict[str, Any]:
        """发送消息"""
        message_type = params.get("type", "group")
        target_id = params.get("target_id")
        message = params.get("message", "")
        
        if not all([target_id, message]):
            return {"content": "缺少必要参数: target_id, message", "success": False}
            
        action = "send_private_msg" if message_type == "private" else "send_group_msg"
        request_params = {
            "user_id" if message_type == "private" else "group_id": target_id,
            "message": message,
            "auto_escape": params.get("auto_escape", False)
        }
        
        try:
            result = await adapter_client.send_request(action, request_params)
            if result.get("status") == "ok":
                return {
                    "content": "消息发送成功",
                    "success": True,
                    "message_id": result.get("data", {}).get("message_id"),
                    "data": result.get("data", {})
                }
            else:
                return {
                    "content": f"消息发送失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"消息发送失败: {str(e)}", "success": False}