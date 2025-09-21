"""
AutoMod 核心模块

整合OCR、鼠标模拟和翻译功能，提供统一的接口。
"""

from typing import Dict, Optional, Tuple, Union
from .config import AutoModConfig
from .ocr import OCRProcessor
from .mouse import MouseSimulator
from .translation import Translator

class AutoMod:
    """AutoMod主类，整合所有功能模块"""
    
    def __init__(self, config: Optional[AutoModConfig] = None):
        """初始化AutoMod"""
        self.config = config or AutoModConfig()
        
        # 初始化各功能模块
        self.ocr = OCRProcessor(self.config)
        self.mouse = MouseSimulator(self.config)
        self.translator = Translator(self.config)
        
    def update_config(self, **kwargs) -> "AutoMod":
        """更新配置参数"""
        # 处理不同模块的配置更新
        if 'ocr' in kwargs:
            self.config.update_ocr_config(**kwargs['ocr'])
        if 'mouse' in kwargs:
            self.config.update_mouse_config(**kwargs['mouse'])
        if 'translation' in kwargs:
            self.config.update_translation_config(**kwargs['translation'])
        
        # 重新初始化模块以应用新配置
        self.ocr = OCRProcessor(self.config)
        self.mouse = MouseSimulator(self.config)
        self.translator = Translator(self.config)
        
        return self
        
    def load_config(self, json_path: str) -> "AutoMod":
        """从JSON文件加载配置"""
        self.config.load_from_json(json_path)
        
        # 重新初始化模块
        self.ocr = OCRProcessor(self.config)
        self.mouse = MouseSimulator(self.config)
        self.translator = Translator(self.config)
        
        return self
        
    def save_config(self, json_path: str) -> None:
        """将配置保存到JSON文件"""
        self.config.save_to_json(json_path)
        
    # OCR功能封装
    def recognize_text(self, image: Union[str, object], region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """
        识别图像中的文字
        
        参数:
            image: 图像路径或numpy数组
            region: 可选的识别区域 (x, y, width, height)
        
        返回:
            识别结果字典
        """
        if region:
            return self.ocr.recognize_region(image, region)
        return self.ocr.recognize(image)
        
    def screenshot_and_recognize(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """
        截取屏幕并识别文字
        
        参数:
            region: 可选的截取区域 (x, y, width, height)
        
        返回:
            识别结果字典
        """
        return self.ocr.screenshot_and_recognize(region)
        
    # 鼠标模拟功能封装
    def move_mouse(self, x: int, y: int, duration: Optional[float] = None) -> "AutoMod":
        """移动鼠标到指定位置"""
        self.mouse.move_to(x, y, duration)
        return self
        
    def click_mouse(self, x: Optional[int] = None, y: Optional[int] = None, button: str = 'left', clicks: int = 1) -> "AutoMod":
        """点击鼠标"""
        self.mouse.click(x, y, button, clicks)
        return self
        
    def double_click_mouse(self, x: Optional[int] = None, y: Optional[int] = None, button: str = 'left') -> "AutoMod":
        """双击鼠标"""
        self.mouse.double_click(x, y, button)
        return self
        
    def right_click_mouse(self, x: Optional[int] = None, y: Optional[int] = None) -> "AutoMod":
        """右键点击鼠标"""
        self.mouse.right_click(x, y)
        return self
        
    def drag_mouse(self, x: int, y: int, duration: Optional[float] = None, button: str = 'left') -> "AutoMod":
        """拖拽鼠标"""
        self.mouse.drag_to(x, y, duration, button)
        return self
        
    def scroll_mouse(self, clicks: int) -> "AutoMod":
        """滚动鼠标滚轮"""
        self.mouse.scroll(clicks)
        return self
        
    # 翻译功能封装
    def translate_text(self, text: str, src_lang: str = 'auto', dest_lang: str = 'zh') -> Dict:
        """翻译文本"""
        return self.translator.translate(text, src_lang, dest_lang)
        
    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        return self.translator.detect_language(text)
        
    def batch_translate(self, texts: list, src_lang: str = 'auto', dest_lang: str = 'zh') -> list:
        """批量翻译文本列表"""
        return self.translator.batch_translate(texts, src_lang, dest_lang)
        
    # 组合功能
    def recognize_and_translate(self, image: Union[str, object], region: Optional[Tuple[int, int, int, int]] = None, dest_lang: str = 'zh') -> Dict:
        """
        识别图像中的文字并翻译
        
        参数:
            image: 图像路径或numpy数组
            region: 可选的识别区域
            dest_lang: 目标语言
        
        返回:
            包含识别和翻译结果的字典
        """
        # 识别文字
        ocr_result = self.recognize_text(image, region)
        
        if not ocr_result.get('text', '').strip():
            return {
                'ocr_result': ocr_result,
                'translation_result': None,
                'error': 'No text recognized'
            }
            
        # 翻译文字
        translation_result = self.translate_text(ocr_result['text'], dest_lang=dest_lang)
        
        return {
            'ocr_result': ocr_result,
            'translation_result': translation_result,
            'combined_text': f"{ocr_result['text']}\n\n翻译: {translation_result['translated_text']}"
        }
        
    def screenshot_recognize_and_translate(self, region: Optional[Tuple[int, int, int, int]] = None, dest_lang: str = 'zh') -> Dict:
        """
        截取屏幕、识别文字并翻译
        
        参数:
            region: 可选的截取区域
            dest_lang: 目标语言
        
        返回:
            包含截图、识别和翻译结果的字典
        """
        # 截取屏幕并识别文字
        ocr_result = self.screenshot_and_recognize(region)
        
        if not ocr_result.get('text', '').strip():
            return {
                'ocr_result': ocr_result,
                'translation_result': None,
                'error': 'No text recognized'
            }
            
        # 翻译文字
        translation_result = self.translate_text(ocr_result['text'], dest_lang=dest_lang)
        
        return {
            'ocr_result': ocr_result,
            'translation_result': translation_result,
            'combined_text': f"{ocr_result['text']}\n\n翻译: {translation_result['translated_text']}"
        }
        
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        return self.mouse.get_position()
        
    def set_ocr_engine(self, engine: str) -> "AutoMod":
        """设置OCR引擎"""
        self.config.update_ocr_config(engine=engine)
        self.ocr = OCRProcessor(self.config)
        return self
        
    def set_translation_service(self, service: str) -> "AutoMod":
        """设置翻译服务"""
        self.config.update_translation_config(service=service)
        self.translator = Translator(self.config)
        return self
        
    def set_human_like_mouse(self, enable: bool) -> "AutoMod":
        """设置是否启用类人鼠标操作"""
        self.config.update_mouse_config(human_like=enable)
        self.mouse = MouseSimulator(self.config)
        return self
        
    def __str__(self) -> str:
        """返回AutoMod实例的字符串表示"""
        return (
            f"AutoMod(v{__import__(__name__.split('.')[0]).__version__})\n"
            f"- OCR Engine: {self.config.get('ocr', 'engine')}\n" 
            f"- Translation Service: {self.config.get('translation', 'service')}\n" 
            f"- Human-like Mouse: {self.config.get('mouse', 'human_like')}"
        )