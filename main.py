import re
import sys
import os
from plugin_registry import registry
from plugin_loader import auto_register_platforms

def extract_url(input_text):
    """从输入文本中提取URL"""
    url_match = re.search(r'https?://[^\s]+', input_text)
    if url_match:
        return url_match.group(0)
    return input_text

def main():
    # 自动注册所有平台插件
    if not auto_register_platforms():
        print("插件加载失败，程序退出")
        return
        
    # 显示已加载的平台列表
    platforms = registry.list_platforms()
    print(f"已支持的直播平台: {', '.join(platforms)}")
    
    # 获取用户输入
    user_input = input('请输入直播间链接：\n')
    url = extract_url(user_input)
    
    # 查找处理该URL的插件
    plugin = registry.get_plugin_for_url(url)
    
    if plugin:
        try:
            real_url = plugin.get_real_url(url)
            if real_url:
                print("获取到的真实流媒体地址:")
                if isinstance(real_url, list):
                    for idx, u in enumerate(real_url, 1):
                        print(f"{idx}. {u}")
                else:
                    print(real_url)
            else:
                print("获取地址失败")
        except Exception as e:
            print(f"处理链接时出错: {e}")
    else:
        print(f"未找到可以处理该链接的插件: {url}")
        print("尝试输入完整的直播间链接，例如:")
        print("- https://17.live/live/276480")
        print("- https://www.douyu.com/xxx")

if __name__ == '__main__':
    main() 