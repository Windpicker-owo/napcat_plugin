"""
NapCat插件工具模块

提供模块化的QQ协议操作工具，通过现有adapter连接
"""

from plugins.napcat_plugin.adapter_client import adapter_client
from plugins.napcat_plugin.utils.message_utils import MessageUtils
from plugins.napcat_plugin.utils.group_utils import GroupUtils
from plugins.napcat_plugin.utils.friend_utils import FriendUtils
from plugins.napcat_plugin.utils.file_utils import FileUtils
from plugins.napcat_plugin.utils.message_ops_utils import MessageOpsUtils

__all__ = [
    'adapter_client',
    'MessageUtils',
    'GroupUtils',
    'FriendUtils',
    'FileUtils',
    'MessageOpsUtils'
]