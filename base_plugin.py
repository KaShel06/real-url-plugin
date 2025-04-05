from abc import ABC, abstractmethod

class BasePlugin(ABC):
    @abstractmethod
    def match_url(self, url: str) -> bool:
        """检查是否可以处理给定URL"""
        pass
    
    @abstractmethod
    def get_real_url(self, url: str) -> str:
        """获取真实流媒体URL"""
        pass 