from typing import Dict, Any
from plugins.napcat_plugin.adapter_client import adapter_client

class FileUtils:
    """文件操作工具类 - 使用现有adapter连接"""
    
    @staticmethod
    async def upload_file(params: Dict[str, Any]) -> Dict[str, Any]:
        """上传文件"""
        file_type = params.get("type", "file")
        file_path = params.get("file_path")
        
        if not file_path:
            return {"content": "缺少必要参数: file_path", "success": False}
            
        request_params = {
            "type": file_type,
            "file": file_path
        }
        if "name" in params:
            request_params["name"] = params["name"]
        
        try:
            result = await adapter_client.send_request("upload_file", request_params)
            if result.get("status") == "ok":
                return {
                    "content": "文件上传成功",
                    "success": True,
                    "file_id": result.get("data", {}).get("file_id"),
                    "file_url": result.get("data", {}).get("url")
                }
            else:
                return {
                    "content": f"文件上传失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"文件上传失败: {str(e)}", "success": False}
    
    @staticmethod
    async def get_file_info(params: Dict[str, Any]) -> Dict[str, Any]:
        """获取文件信息"""
        file_id = params.get("file_id")
        if not file_id:
            return {"content": "缺少必要参数: file_id", "success": False}
            
        try:
            result = await adapter_client.send_request("get_file", {"file_id": file_id})
            if result.get("status") == "ok":
                return {
                    "content": "文件信息获取成功",
                    "success": True,
                    "file_info": result.get("data", {})
                }
            else:
                return {
                    "content": f"获取文件信息失败: {result.get('msg', '未知错误')}",
                    "success": False
                }
        except Exception as e:
            return {"content": f"获取文件信息失败: {str(e)}", "success": False}