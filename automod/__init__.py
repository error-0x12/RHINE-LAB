"""
RHINE-LAB AutoMod - 自动化支持库

包含OCR、鼠标模拟和翻译功能的综合支持库，用于自动化任务处理。
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "RHINE-LAB"
__license__ = "MIT"

# 导出主要模块
from .ocr import OCRProcessor
from .mouse import MouseSimulator
from .translation import Translator
from .core import AutoMod
from .config import AutoModConfig