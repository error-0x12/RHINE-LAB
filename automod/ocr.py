"""
OCR 模块

提供图像文字识别功能，支持多种OCR引擎。
"""

import cv2
import numpy as np
from typing import Dict, Optional, Tuple, Union
from .config import AutoModConfig

class OCRProcessor:
    """OCR处理器，用于图像文字识别"""
    
    def __init__(self, config: Optional[AutoModConfig] = None):
        """初始化OCR处理器"""
        self.config = config or AutoModConfig()
        self.engine = None
        self._init_engine()
        
    def _init_engine(self):
        """初始化OCR引擎"""
        engine_type = self.config.get('ocr', 'engine', 'pytesseract')
        
        if engine_type == 'pytesseract':
            try:
                import pytesseract
                self.engine = pytesseract
                # 检查tesseract命令路径配置
                if hasattr(self.config, 'tesseract_cmd') and self.config.tesseract_cmd:
                    pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_cmd
            except ImportError:
                raise ImportError("请安装pytesseract: pip install pytesseract")
        elif engine_type == 'paddleocr':
            try:
                from paddleocr import PaddleOCR
                self.engine = PaddleOCR(
                    use_angle_cls=True,
                    lang=self.config.get('ocr', 'lang', 'ch').replace('+', '_'),
                    use_gpu=False
                )
            except ImportError:
                raise ImportError("请安装paddleocr: pip install paddleocr")
        else:
            raise ValueError(f"不支持的OCR引擎: {engine_type}")
            
    def recognize(self, image: Union[str, np.ndarray]) -> Dict:
        """
        识别图像中的文字
        
        参数:
            image: 图像路径或numpy数组
        
        返回:
            包含识别结果的字典
        """
        # 加载图像
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise FileNotFoundError(f"无法加载图像: {image}")
        else:
            img = image.copy()
            
        # 图像预处理
        img = self._preprocess_image(img)
        
        # 使用不同引擎进行识别
        engine_type = self.config.get('ocr', 'engine', 'pytesseract')
        confidence_threshold = self.config.get('ocr', 'confidence_threshold', 0.7)
        
        if engine_type == 'pytesseract':
            return self._recognize_with_pytesseract(img, confidence_threshold)
        elif engine_type == 'paddleocr':
            return self._recognize_with_paddleocr(img, confidence_threshold)
            
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """图像预处理"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 自适应阈值处理
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        return thresh
        
    def _recognize_with_pytesseract(self, image: np.ndarray, confidence_threshold: float) -> Dict:
        """使用pytesseract进行OCR识别"""
        try:
            # 获取详细数据
            data = self.engine.image_to_data(
                image, 
                lang=self.config.get('ocr', 'lang', 'chi_sim+eng'),
                output_type=self.engine.Output.DICT
            )
            
            # 提取有效结果
            text = ""
            boxes = []
            
            for i in range(len(data['text'])):
                confidence = float(data['conf'][i])
                if confidence > confidence_threshold and data['text'][i].strip():
                    text += data['text'][i] + " "
                    # 获取边界框
                    x, y, w, h = (
                        data['left'][i], 
                        data['top'][i], 
                        data['width'][i], 
                        data['height'][i]
                    )
                    boxes.append({
                        'x': x, 'y': y, 'width': w, 'height': h,
                        'text': data['text'][i],
                        'confidence': confidence
                    })
                    
            return {
                'text': text.strip(),
                'boxes': boxes,
                'engine': 'pytesseract'
            }
        except Exception as e:
            raise RuntimeError(f"pytesseract OCR识别失败: {str(e)}")
            
    def _recognize_with_paddleocr(self, image: np.ndarray, confidence_threshold: float) -> Dict:
        """使用paddleocr进行OCR识别"""
        try:
            # PaddleOCR需要RGB图像
            img_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            # 执行识别
            result = self.engine.ocr(img_rgb, cls=True)
            
            # 处理结果
            text = ""
            boxes = []
            
            for line in result:
                if line is None:
                    continue
                for box_info in line:
                    box, (txt, confidence) = box_info
                    if confidence > confidence_threshold and txt.strip():
                        text += txt + " "
                        # 转换边界框格式
                        x1, y1 = box[0]
                        x3, y3 = box[2]
                        boxes.append({
                            'x': int(x1), 
                            'y': int(y1), 
                            'width': int(x3 - x1), 
                            'height': int(y3 - y1),
                            'text': txt,
                            'confidence': confidence
                        })
                        
            return {
                'text': text.strip(),
                'boxes': boxes,
                'engine': 'paddleocr'
            }
        except Exception as e:
            raise RuntimeError(f"paddleocr OCR识别失败: {str(e)}")
            
    def recognize_region(self, image: Union[str, np.ndarray], region: Tuple[int, int, int, int]) -> Dict:
        """
        识别图像中指定区域的文字
        
        参数:
            image: 图像路径或numpy数组
            region: (x, y, width, height) 区域坐标
        
        返回:
            包含识别结果的字典
        """
        # 加载图像
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise FileNotFoundError(f"无法加载图像: {image}")
        else:
            img = image.copy()
            
        # 裁剪区域
        x, y, w, h = region
        region_img = img[y:y+h, x:x+w]
        
        # 识别区域文字
        return self.recognize(region_img)
        
    def screenshot_and_recognize(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """
        截取屏幕并识别文字
        
        参数:
            region: 可选的区域坐标 (x, y, width, height)
        
        返回:
            包含识别结果的字典
        """
        try:
            import pyautogui
            
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
                
            # 转换为OpenCV格式
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            return self.recognize(img)
        except ImportError:
            raise ImportError("请安装pyautogui: pip install pyautogui")
        except Exception as e:
            raise RuntimeError(f"截图识别失败: {str(e)}")