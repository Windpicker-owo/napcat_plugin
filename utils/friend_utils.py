from typing import Dict, Any
from plugins.napcat_plugin.adapter_client import adapter_client

class FriendUtils:
    """好友管理工具类 - 使用现有adapter连接"""
    
    @staticmethod
    async def get_friends(params: Dict[str, Any]) -> Dict[str, Any]:
        """获取好友列表"""
        request_params = {"no_cache": params.get("no_cache", False)}
        
        try:
            result = await adapter_client.send_request("get_friend_list", request_params)
            if result.get("status") == "ok":
                friends = result.get("data", [])
                return {
                    "content": f"获取好友列表成功，共{len(friends)}个好友",
                    "success": True,
                    "friends": friends
                }
            else:
                return {
                    "content": f"获取好友列表失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"获取好友列表失败: {str(e)}", "success": False}
    
    @staticmethod
    async def get_friends_with_category(params: Dict[str, Any]) -> Dict[str, Any]:
        """获取分类好友列表"""
        try:
            result = await adapter_client.send_request("get_friends_with_category", {})
            if result.get("status") == "ok":
                return {
                    "content": "获取分类好友列表成功",
                    "success": True,
                    "categories": result.get("data", [])
                }
            else:
                return {
                    "content": f"获取分类好友列表失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"获取分类好友列表失败: {str(e)}", "success": False}
    
    @staticmethod
    async def friend_poke(params: Dict[str, Any]) -> Dict[str, Any]:
        """私聊戳一戳"""
        user_id = params.get("user_id")
        if not user_id:
            return {"content": "缺少必要参数: user_id", "success": False}
            
        try:
            result = await adapter_client.send_request("friend_poke", {"user_id": user_id})
            if result.get("status") == "ok":
                return {
                    "content": f"戳了好友{user_id}一下",
                    "success": True
                }
            else:
                return {
                    "content": f"好友戳一戳失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"好友戳一戳失败: {str(e)}", "success": False}