import os
import re
import importlib.util
import inspect
import sys
from plugin_registry import registry

# 定义平台URL模式字典
PLATFORM_PATTERNS = {
    'huya': r'https?://(?:www\.)?huya\.com/[A-Za-z0-9]+',
    'bilibili': r'https?://live\.bilibili\.com/\d+',
    '17live': r'https?://17\.live/live/\d+',
    'douyu': r'https?://(?:www\.)?douyu\.com/[A-Za-z0-9]+',
    'kuaishou': r'https?://(?:www\.)?kuaishou\.com/[A-Za-z0-9]+',
    'yy': r'https?://(?:www\.)?yy\.com/[A-Za-z0-9]+',
    'twitch': r'https?://(?:www\.)?twitch\.tv/[A-Za-z0-9_]+',
    'tiktok': r'https?://(?:www\.)?tiktok\.com/@[A-Za-z0-9_.]+',
    'iqiyi': r'https?://(?:www\.)?iqiyi\.com/[A-Za-z0-9]+',
    'zhanqi': r'https?://(?:www\.)?zhanqi\.tv/[A-Za-z0-9]+',
    # 更多平台可以按需添加
}

def load_platform_module(file_path, module_name):
    """加载平台模块并返回其中的get_real_url函数"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # 查找get_real_url函数
    if hasattr(module, 'get_real_url'):
        return module.get_real_url
    
    # 如果没有找到，查找其他可能的函数名
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and 'url' in name.lower():
            return obj
    
    return None

def auto_register_platforms(plugins_dir="real-url"):
    """自动注册插件目录中的所有平台"""
    # 确保目录存在
    if not os.path.exists(plugins_dir):
        print(f"错误: 找不到插件目录 {plugins_dir}")
        return False
        
    # 遍历目录中的所有Python文件
    registered = 0
    for filename in os.listdir(plugins_dir):
        if not filename.endswith('.py') or filename == '__init__.py':
            continue
            
        module_name = filename[:-3]  # 移除.py后缀
        file_path = os.path.join(plugins_dir, filename)
        
        # 尝试加载模块和获取函数
        get_real_url_func = load_platform_module(file_path, module_name)
        if not get_real_url_func:
            print(f"警告: 在 {filename} 中找不到合适的函数")
            continue
            
        # 确定平台名称和URL模式
        platform_name = module_name
        
        # 查找预定义的URL模式
        url_pattern = None
        for name, pattern in PLATFORM_PATTERNS.items():
            if name.lower() in module_name.lower():
                url_pattern = pattern
                break
                
        # 如果没有预定义模式，使用通用模式
        if not url_pattern:
            print(f"注意: 使用通用URL模式 {platform_name}")
            url_pattern = fr'https?://(?:www\.)?{platform_name}\.com/\d+'
            
        # 注册插件
        registry.register(platform_name, url_pattern, get_real_url_func)
        registered += 1
        print(f"已注册: {platform_name}")
            
    print(f"共注册了 {registered} 个平台插件")
    return True 