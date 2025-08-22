import asyncio
import sys
from typing import Optional
from src.common.logger import get_logger

logger = get_logger("napcat_server_manager")

class NapcatServerManager:
    """NapCat服务器统一管理器"""
    
    _instance: Optional['NapcatServerManager'] = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._adapter = None
        self._is_running = False
        self._task = None
        self._initialized = True
    
    async def start(self, host: str = "127.0.0.1", port: int = 8000):
        """启动NapCat服务器"""
        async with self._lock:
            if self._is_running:
                logger.warning("NapCat服务器已在运行")
                return
                
            try:
                from plugins.napcat_plugin.plugin import NapcatAdapter
                self._adapter = NapcatAdapter(host=host, port=port)
                
                # 创建新的事件循环
                loop = asyncio.get_event_loop()
                self._task = loop.create_task(self._adapter.main())
                
                self._is_running = True
                logger.info("NapCat服务器启动成功")
                
            except Exception as e:
                logger.error(f"启动NapCat服务器失败: {e}")
                raise
    
    async def stop(self):
        """停止NapCat服务器"""
        async with self._lock:
            if not self._is_running:
                return
                
            try:
                if self._task and not self._task.done():
                    self._task.cancel()
                    try:
                        await self._task
                    except asyncio.CancelledError:
                        pass
                        
                self._is_running = False
                logger.info("NapCat服务器已停止")
                
            except Exception as e:
                logger.error(f"停止NapCat服务器失败: {e}")
    
    @property
    def is_running(self) -> bool:
        """检查服务器是否正在运行"""
        return self._is_running
    
    def get_adapter(self):
        """获取adapter实例"""
        return self._adapter

# 全局实例
server_manager = NapcatServerManager()