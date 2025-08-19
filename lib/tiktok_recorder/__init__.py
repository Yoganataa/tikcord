# lib/tiktok_recorder/__init__.py  
from .bridge import start_recording  
from .core.tiktok_recorder import TikTokRecorder  
  
__all__ = ['start_recording', 'TikTokRecorder']