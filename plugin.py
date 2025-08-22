"""
NapCat QQ协议插件 - 提供完整的QQ机器人API接口

基于OneBot 11协议和NapCat扩展接口，为其他插件提供标准化的QQ协议操作能力。
使用现有adapter的WebSocket连接进行通信。
"""

from typing import List, Tuple, Type, Any, Dict
import asyncio
import json
import sys
import websockets as Server
from src.common.logger import get_logger
from src.plugin_system import (
    BasePlugin, BaseTool, register_plugin,
    ComponentInfo, ConfigField, ToolParamType, 
    BaseEventHandler, EventType
)

from plugins.napcat_plugin.utils import (
    MessageUtils, GroupUtils,
    FriendUtils, FileUtils, MessageOpsUtils
)
from plugins.napcat_plugin.server_manager import server_manager

from plugins.napcat_plugin.ada.recv_handler.message_handler import message_handler
from plugins.napcat_plugin.ada.recv_handler.meta_event_handler import meta_event_handler
from plugins.napcat_plugin.ada.recv_handler.notice_handler import notice_handler
from plugins.napcat_plugin.ada.recv_handler.message_sending import message_send_instance
from plugins.napcat_plugin.ada.send_handler import send_handler
from plugins.napcat_plugin.ada.mmc_com_layer import mmc_start_com, mmc_stop_com, router
from plugins.napcat_plugin.ada.response_pool import put_response, check_timeout_response

logger = get_logger("napcat_plugin")

class NapcatAdapter:
    """NapCat适配器 - 处理WebSocket连接和消息分发"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.port = port
        self.host = host
        self.message_queue = asyncio.Queue()

    async def message_recv(self, server_connection: Server.ServerConnection):
        await message_handler.set_server_connection(server_connection)
        asyncio.create_task(notice_handler.set_server_connection(server_connection))
        await send_handler.set_server_connection(server_connection)
        async for raw_message in server_connection:
            logger.debug(f"{raw_message[:1500]}..." if (len(raw_message) > 1500) else raw_message)
            decoded_raw_message: dict = json.loads(raw_message)
            post_type = decoded_raw_message.get("post_type")
            if post_type in ["meta_event", "message", "notice"]:
                await self.message_queue.put(decoded_raw_message)
            elif post_type is None:
                await put_response(decoded_raw_message)


    async def message_process(self):
        while True:
            message = await self.message_queue.get()
            post_type = message.get("post_type")
            if post_type == "message":
                await message_handler.handle_raw_message(message)
            elif post_type == "meta_event":
                await meta_event_handler.handle_meta_event(message)
            elif post_type == "notice":
                await notice_handler.handle_notice(message)
            else:
                logger.warning(f"未知的post_type: {post_type}")
            self.message_queue.task_done()
            await asyncio.sleep(0.05)


    async def main(self):
        message_send_instance.maibot_router = router
        _ = await asyncio.gather(self.napcat_server(), mmc_start_com(), self.message_process(), check_timeout_response())


    async def napcat_server(self):
        logger.info("正在启动adapter...")
        async with Server.serve(self.message_recv, self.host, self.port, max_size=2**26) as server:
            logger.info(
                f"Adapter已启动，监听地址: ws://{self.host}:{self.port}"
            )
            await server.serve_forever()


    async def graceful_shutdown(self):
        try:
            logger.info("正在关闭adapter...")
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), 15)
            await mmc_stop_com()  # 后置避免神秘exception
            logger.info("Adapter已成功关闭")
        except Exception as e:
            logger.error(f"Adapter关闭中出现错误: {e}")

    def start(self):
        """启动NapCat适配器"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.main())
        except Exception as e:
            logger.exception(f"主程序异常: {str(e)}")
            sys.exit(1)
        finally:
            if loop and not loop.is_closed():
                loop.close()
            sys.exit(0)


class NapCatTool(BaseTool):
    """NapCat综合工具类 - 使用现有adapter连接"""
    
    name = "napcat_tool"
    description = "NapCat QQ协议综合工具，提供消息发送、群管理、好友管理、文件操作等完整功能"
    parameters = [
        ("action", ToolParamType.STRING, 
         "操作类型: send_message, get_groups, get_group_members, get_friends, upload_file, "
         "group_sign, group_poke, friend_poke, get_file_info, get_friends_with_category, "
         "get_message, forward_message", True, None),
        ("params", ToolParamType.DICT, "操作参数，根据action类型提供不同参数", True, None),
    ]
    available_for_llm = False
    
    async def execute(self, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """执行NapCat操作"""
        try:
            action = function_args.get("action")
            params = function_args.get("params", {})
            
            if not action:
                return {"name": self.name, "content": "必须指定操作类型", "success": False}
            
            # 委托给对应工具类
            tool_map = {
                "send_message": MessageUtils.send_message,
                "get_groups": GroupUtils.get_groups,
                "get_group_members": GroupUtils.get_group_members,
                "get_friends": FriendUtils.get_friends,
                "upload_file": FileUtils.upload_file,
                "group_sign": GroupUtils.group_sign,
                "group_poke": GroupUtils.group_poke,
                "friend_poke": FriendUtils.friend_poke,
                "get_file_info": FileUtils.get_file_info,
                "get_friends_with_category": FriendUtils.get_friends_with_category,
                "get_message": MessageOpsUtils.get_message,
                "forward_message": MessageOpsUtils.forward_message,
            }
            
            handler = tool_map.get(action)
            if handler:
                result = await handler(params)
                result["name"] = self.name
                return result
            else:
                return {"name": self.name, "content": f"不支持的操作类型: {action}", "success": False}
                
        except Exception as e:
            logger.error(f"NapCat操作失败: {e}")
            return {"name": self.name, "content": f"操作失败: {str(e)}", "success": False}

class NapcatPluginStartHandler(BaseEventHandler):
    """NapCat插件启动处理器"""
    
    event_type = EventType.ON_START
    handler_name = "napcat_plugin_laucher"
    handler_description = "自启动Napcat插件，提供QQ协议支持"
    weight = 0
    intercept_message = False

    async def execute(self):
        """执行启动逻辑"""
        try:
            logger.info("正在启动NapCat插件...")
            await server_manager.start(host=self.get_config("napcat_server.host","127.0.0.1"),port=self.get_config("napcat_server.port",8000))
            return True, True, "NapCat插件启动成功"
        except Exception as e:
            logger.error(f"NapCat插件启动失败: {e}")
            return False, False, f"NapCat插件启动失败: {str(e)}"

@register_plugin
class NapCatPlugin(BasePlugin):
    """NapCat QQ协议插件"""
    
    plugin_name = "napcat_plugin"
    enable_plugin = True
    config_file_name = "config.toml"
    python_dependencies: List[str] = ["openai", "tenacity"]  # 添加新依赖
    dependencies = []

    config_section_descriptions = {
        "plugin": "插件基本信息",
        "napcat": "NapCat API配置",
        "napcat.server": "NapCat服务器设置",
        "napcat.connection": "连接配置",
        "napcat.logging": "日志配置",
    }

    config_schema: dict = {
        "plugin": {
            "name": ConfigField(
                type=str, default="napcat_plugin", description="插件名称"
            ),
            "version": ConfigField(type=str, default="2.4.0", description="插件版本"),
            "config_version": ConfigField(type=str, default="2.4.0", description="配置文件版本"),
            "enabled": ConfigField(
                type=bool, default=True, description="是否启用插件"
            ),
        },
        "napcat": {
            "api_base_url": ConfigField(
                type=str, default="http://localhost:3000", description="NapCat API基础URL，用于WebSocket连接"
            ),
            "access_token": ConfigField(
                type=str, default="", description="访问令牌，用于身份验证（可选）"
            ),
        },
        "napcat.server": {
            "host": ConfigField(
                type=str, default="127.0.0.1", description="监听地址，默认为127.0.0.1"
            ),
            "port": ConfigField(
                type=int, default=3001, description="监听端口，默认为3001"
            ),
        },
        "napcat.connection": {
            "timeout": ConfigField(
                type=int, default=30, description="请求超时时间（秒）"
            ),
            "max_retries": ConfigField(
                type=int, default=3, description="最大重试次数"
            ),
            "retry_delay": ConfigField(
                type=float, default=1.0, description="重试延迟时间（秒）"
            ),
        },
        "napcat.logging": {
            "level": ConfigField(
                type=str, default="INFO", description="日志级别（DEBUG, INFO, WARNING, ERROR）"
            ),
            "file_path": ConfigField(
                type=str, default="logs/napcat.log", description="日志文件路径"
            ),
            "max_size": ConfigField(
                type=str, default="10MB", description="日志文件最大大小"
            ),
            "backup_count": ConfigField(
                type=int, default=5, description="日志备份文件数量"
            ),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            (NapCatTool.get_tool_info(), NapCatTool),
            (NapcatPluginStartHandler.get_handler_info(), NapcatPluginStartHandler),
        ]