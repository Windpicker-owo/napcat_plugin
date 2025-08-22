"""
NapCat适配器客户端
提供与现有NapcatAdapter的WebSocket连接
"""

import asyncio
import json
import websockets
from src.common.logger import get_logger

logger = get_logger("napcat_plugin")

class AdapterClient:
    """适配器客户端，用于与NapCat WebSocket服务器通信"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port
        self.websocket = None
        self.connected = False
        
    async def connect(self):
        """连接到NapCat WebSocket服务器"""
        try:
            uri = f"ws://{self.host}:{self.port}"
            logger.info(f"连接到NapCat服务器: {uri}")
            self.websocket = await websockets.connect(uri)
            self.connected = True
            logger.info("成功连接到NapCat服务器")
        except Exception as e:
            logger.error(f"连接NapCat服务器失败: {e}")
            self.connected = False
            raise
            
    async def disconnect(self):
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("已断开与NapCat服务器的连接")
            
    async def send_request(self, action: str, params: dict) -> dict:
        """发送请求到NapCat服务器"""
        if not self.connected or not self.websocket:
            raise RuntimeError("未连接到NapCat服务器")
            
        request = {
            "action": action,
            "params": params
        }
        
        try:
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            logger.error(f"发送请求失败: {e}")
            raise
            
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

# 全局适配器客户端实例
adapter_client = AdapterClient()