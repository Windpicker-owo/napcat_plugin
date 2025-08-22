from typing import Dict, Any
from plugins.napcat_plugin.adapter_client import adapter_client

class MessageOpsUtils:
    """消息操作工具类 - 使用现有adapter连接"""
    
    @staticmethod
    async def get_message(params: Dict[str, Any]) -> Dict[str, Any]:
        """获取消息详情"""
        message_id = params.get("message_id")
        if not message_id:
            return {"content": "缺少必要参数: message_id", "success": False}
            
        try:
            result = await adapter_client.send_request("get_msg", {"message_id": message_id})
            if result.get("status") == "ok":
                return {
                    "content": "消息详情获取成功",
                    "success": True,
                    "message": result.get("data", {})
                }
            else:
                return {
                    "content": f"获取消息详情失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"获取消息详情失败: {str(e)}", "success": False}
    
    @staticmethod
    async def forward_message(params: Dict[str, Any]) -> Dict[str, Any]:
        """转发消息"""
        message_id = params.get("message_id")
        target_type = params.get("target_type", "group")
        target_id = params.get("target_id")
        
        if not all([message_id, target_id]):
            return {"content": "缺少必要参数: message_id, target_id", "success": False}
            
        action = "forward_friend_single_msg" if target_type == "private" else "forward_group_single_msg"
        request_params = {
            "message_id": message_id,
            "user_id" if target_type == "private" else "group_id": target_id
        }
        
        try:
            result = await adapter_client.send_request(action, request_params)
            if result.get("status") == "ok":
                return {
                    "content": f"消息转发成功到{target_type} {target_id}",
                    "success": True
                }
            else:
                return {
                    "content": f"消息转发失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"消息转发失败: {str(e)}", "success": False}