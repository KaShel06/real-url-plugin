import re
import os
import importlib
import sys
from typing import Dict, Optional, List
from base_plugin import BasePlugin

class PluginRegistry:
    """插件注册管理器"""
    
    def __init__(self):
        self.plugins = {}
        
    def register(self, platform_name, url_pattern, get_real_url_func):
        """
        注册一个直播平台插件
        
        Args:
            platform_name: 平台名称
            url_pattern: URL匹配模式
            get_real_url_func: 获取真实URL的函数
        """
        class PlatformPlugin(BasePlugin):
            def match_url(self, url):
                return bool(re.match(url_pattern, url))
            
            def get_real_url(self, url):
                try:
                    # 从URL中提取房间号
                    rid = url.split('/')[-1]
                    return get_real_url_func(rid)
                except Exception as e:
                    print(f"处理错误: {e}")
                    return None
        
        PlatformPlugin.__name__ = f"{platform_name}Plugin"
        self.plugins[platform_name] = PlatformPlugin()
        
    def get_plugin_for_url(self, url: str) -> Optional[BasePlugin]:
        """根据URL找到对应的插件"""
        for name, plugin in self.plugins.items():
            if plugin.match_url(url):
                return plugin
        return None
        
    def list_platforms(self) -> List[str]:
        """获取所有已注册平台的名称"""
        return list(self.plugins.keys())

# 创建全局注册表实例
registry = PluginRegistry() 