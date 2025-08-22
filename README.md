# NapCat QQ协议插件

基于OneBot 11协议的NapCat QQ协议插件，为MaiBot提供完整的QQ机器人API接口，**使用WebSocket协议**与NapCat通信。

## 🚀 功能特性

- **消息管理**: 发送和接收私聊/群聊消息
- **群管理**: 获取群列表、群成员信息、群签到、戳一戳
- **好友管理**: 获取好友列表、分类好友、戳一戳
- **文件操作**: 文件上传、获取文件信息
- **消息操作**: 获取消息详情、转发消息
- **WebSocket协议**: 使用WebSocket协议与NapCat通信，无需HTTP API

## 📁 项目结构

```
plugins/napcat_plugin/
├── ws_client.py             # WebSocket客户端管理器
├── server_manager.py        # 统一服务器管理器
├── utils/                   # 工具模块目录
│   ├── __init__.py
│   ├── message_utils.py     # 消息发送工具 (WebSocket)
│   ├── group_utils.py       # 群管理工具 (WebSocket)
│   ├── friend_utils.py      # 好友管理工具 (WebSocket)
│   ├── file_utils.py        # 文件操作工具 (WebSocket)
│   └── message_ops_utils.py # 消息操作工具 (WebSocket)
├── plugin.py (重构)         # 主插件文件
├── _manifest.json (更新)    # 插件清单
├── README.md (更新)        # 完整文档
└── template/template_config.toml (更新) # 配置模板
```

## ⚙️ 配置说明

### 基本配置
在 `config.toml` 中配置：

```toml
[napcat]
# NapCat WebSocket配置
api_base_url = "ws://localhost:3000"  # 使用WebSocket协议
access_token = ""                     # 访问令牌（可选）

[napcat.server]
host = "127.0.0.1"  # 监听地址
port = 3001         # 监听端口

[napcat.connection]
timeout = 30        # 请求超时时间（秒）
max_retries = 3     # 最大重试次数
retry_delay = 1.0   # 重试延迟（秒）
```

## 🛠️ 使用方法

### 1. 启动插件
插件会在MaiBot启动时自动启动NapCat服务器，并建立WebSocket连接。

### 2. 使用工具
通过NapCatTool使用各项功能，所有操作都通过WebSocket协议：

```python
# 发送消息
await napcat_tool.execute({
    "action": "send_message",
    "params": {
        "type": "group",
        "target_id": 123456789,
        "message": "Hello, World!"
    }
})

# 获取群列表
await napcat_tool.execute({
    "action": "get_groups",
    "params": {}
})

# 获取群成员
await napcat_tool.execute({
    "action": "get_group_members",
    "params": {"group_id": 123456789}
})
```

### 3. 直接调用工具模块
也可以直接使用工具模块的独立方法：

```python
from plugins.napcat_plugin.utils import MessageUtils, GroupUtils

# 使用消息工具
await MessageUtils.send_message({
    "type": "private",
    "target_id": 123456789,
    "message": "Hello!"
})

# 使用群管理工具
await GroupUtils.get_groups({})
```

## 📋 支持的操作

### 消息操作
- `send_message`: 发送消息
- `get_message`: 获取消息详情
- `forward_message`: 转发消息

### 群管理
- `get_groups`: 获取群列表
- `get_group_members`: 获取群成员列表
- `group_sign`: 群签到
- `group_poke`: 群戳一戳

### 好友管理
- `get_friends`: 获取好友列表
- `get_friends_with_category`: 获取分类好友列表
- `friend_poke`: 好友戳一戳

### 文件操作
- `upload_file`: 上传文件
- `get_file_info`: 获取文件信息

## 🔧 技术架构

### WebSocket通信
- **协议**: WebSocket (ws://)
- **消息格式**: JSON
- **通信模式**: 请求-响应模式
- **连接管理**: 自动重连和错误处理

### 消息格式
```json
{
  "action": "send_group_msg",
  "params": {
    "group_id": 123456789,
    "message": "Hello"
  },
  "echo": "unique_id"
}
```

## 🔄 从HTTP迁移到WebSocket

### 主要变化
- ✅ **移除HTTP API依赖**: 不再使用aiohttp和HTTP请求
- ✅ **WebSocket协议**: 所有通信通过WebSocket进行
- ✅ **实时通信**: 更低的延迟和更好的实时性
- ✅ **统一连接**: 所有工具共享同一个WebSocket连接

### 向后兼容
- ✅ **API接口不变**: 保持原有的NapCatTool接口
- ✅ **参数格式不变**: 保持原有的参数格式
- ✅ **响应格式不变**: 保持原有的响应格式

## 🐛 故障排除

### 常见问题
1. **连接失败**: 检查NapCat服务是否运行，WebSocket地址是否正确
2. **权限错误**: 检查access_token是否正确配置
3. **消息发送失败**: 检查目标ID是否正确，机器人是否有权限

### 日志查看
查看 `logs/napcat.log` 获取详细日志信息。

## 📄 更新日志

### v2.2.0
- ✅ **重大更新**: 从HTTP API迁移到WebSocket协议
- ✅ **移除HTTP依赖**: 完全移除aiohttp和HTTP API
- ✅ **WebSocket支持**: 所有工具模块使用WebSocket协议
- ✅ **性能优化**: 更低的延迟和更好的实时性
- ✅ **代码重构**: 更清晰的架构和更好的可维护性

### v2.1.0
- ✅ 重构为模块化架构
- ✅ 创建统一的服务器管理器
- ✅ 拆分功能到独立工具模块

### v2.0.0
- ✅ 集成NapcatAdapter到插件
- ✅ 提供完整的QQ协议API

## 🤝 贡献
欢迎提交Issue和Pull Request！

## 📄 许可证
MIT License