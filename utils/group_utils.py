from typing import Dict, Any
from plugins.napcat_plugin.adapter_client import adapter_client

class GroupUtils:
    """群管理工具类 - 使用现有adapter连接"""
    
    @staticmethod
    async def get_groups(params: Dict[str, Any]) -> Dict[str, Any]:
        """获取群列表"""
        request_params = {"no_cache": params.get("no_cache", False)}
        
        try:
            result = await adapter_client.send_request("get_group_list", request_params)
            if result.get("status") == "ok":
                groups = result.get("data", [])
                return {
                    "content": f"获取群列表成功，共{len(groups)}个群",
                    "success": True,
                    "groups": groups
                }
            else:
                return {
                    "content": f"获取群列表失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"获取群列表失败: {str(e)}", "success": False}
    
    @staticmethod
    async def get_group_members(params: Dict[str, Any]) -> Dict[str, Any]:
        """获取群成员列表"""
        group_id = params.get("group_id")
        if not group_id:
            return {"content": "缺少必要参数: group_id", "success": False}
            
        request_params = {
            "group_id": group_id,
            "no_cache": params.get("no_cache", False)
        }
        
        try:
            result = await adapter_client.send_request("get_group_member_list", request_params)
            if result.get("status") == "ok":
                members = result.get("data", [])
                return {
                    "content": f"获取群{group_id}成员列表成功，共{len(members)}个成员",
                    "success": True,
                    "members": members
                }
            else:
                return {
                    "content": f"获取群成员列表失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"获取群成员列表失败: {str(e)}", "success": False}
    
    @staticmethod
    async def group_sign(params: Dict[str, Any]) -> Dict[str, Any]:
        """群签到"""
        group_id = params.get("group_id")
        if not group_id:
            return {"content": "缺少必要参数: group_id", "success": False}
            
        try:
            result = await adapter_client.send_request("set_group_sign", {"group_id": group_id})
            if result.get("status") == "ok":
                return {
                    "content": f"群{group_id}签到成功",
                    "success": True
                }
            else:
                return {
                    "content": f"群签到失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"群签到失败: {str(e)}", "success": False}
    
    @staticmethod
    async def group_poke(params: Dict[str, Any]) -> Dict[str, Any]:
        """群戳一戳"""
        group_id = params.get("group_id")
        user_id = params.get("user_id")
        
        if not all([group_id, user_id]):
            return {"content": "缺少必要参数: group_id, user_id", "success": False}
            
        try:
            result = await adapter_client.send_request("group_poke", {
                "group_id": group_id,
                "user_id": user_id
            })
            if result.get("status") == "ok":
                return {
                    "content": f"在群{group_id}戳了{user_id}一下",
                    "success": True
                }
            else:
                return {
                    "content": f"群戳一戳失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"群戳一戳失败: {str(e)}", "success": False}