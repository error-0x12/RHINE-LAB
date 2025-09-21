"""
AutoMod 配置模块

负责管理OCR、鼠标模拟和翻译功能的配置参数。
"""

import os
from typing import Dict, Optional, Any

class AutoModConfig:
    """AutoMod 配置类，管理所有功能模块的配置参数"""
    
    def __init__(self):
        # OCR 配置
        self.ocr_config = {
            "engine": "pytesseract",  # 可选: pytesseract, paddleocr
            "lang": "chi_sim+eng",    # OCR识别语言
            "data_path": None,        # 自定义OCR数据路径
            "confidence_threshold": 0.7  # 置信度阈值
        }
        
        # 鼠标模拟配置
        self.mouse_config = {
            "move_speed": 1.0,        # 鼠标移动速度
            "click_delay": 0.1,       # 点击延迟（秒）
            "smooth_move": True,      # 是否使用平滑移动
            "human_like": True        # 是否模拟人类行为
        }
        
        # 翻译配置
        self.translation_config = {
            "service": "google",     # 可选: google, baidu, youdao
            "api_key": None,          # API密钥
            "api_secret": None,       # API密钥
            "timeout": 10,            # 超时时间（秒）
            "proxy": None             # 代理设置
        }
        
    def update_ocr_config(self, **kwargs) -> "AutoModConfig":
        """更新OCR配置"""
        self.ocr_config.update(kwargs)
        return self
        
    def update_mouse_config(self, **kwargs) -> "AutoModConfig":
        """更新鼠标模拟配置"""
        self.mouse_config.update(kwargs)
        return self
        
    def update_translation_config(self, **kwargs) -> "AutoModConfig":
        """更新翻译配置"""
        self.translation_config.update(kwargs)
        return self
        
    def load_from_json(self, json_path: str) -> "AutoModConfig":
        """从JSON文件加载配置"""
        import json
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'ocr_config' in config:
                    self.ocr_config.update(config['ocr_config'])
                if 'mouse_config' in config:
                    self.mouse_config.update(config['mouse_config'])
                if 'translation_config' in config:
                    self.translation_config.update(config['translation_config'])
        return self
        
    def save_to_json(self, json_path: str) -> None:
        """将配置保存到JSON文件"""
        import json
        config = {
            'ocr_config': self.ocr_config,
            'mouse_config': self.mouse_config,
            'translation_config': self.translation_config
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """获取指定配置项"""
        config_map = {
            'ocr': self.ocr_config,
            'mouse': self.mouse_config,
            'translation': self.translation_config
        }
        
        if section in config_map and key in config_map[section]:
            return config_map[section][key]
        return default