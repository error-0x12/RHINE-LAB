"""
文字匹配自动化程序

功能：
1. 点击文字：01
2. 重复执行：
   - 识别指定坐标(175,285)和(565,355)处的文字
   - 如果内容是中文，则点击它的英文翻译（全屏范围）
   - 如果是英文，则点击它的中文翻译（全屏范围）
   - 等待2秒
"""

import sys
import os
import time
import re

# 确保可以导入AutoMod
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automod import AutoMod

class TextMatchingAutomation:
    """文字匹配自动化类"""
    
    def __init__(self):
        """初始化自动化对象"""
        # 创建AutoMod实例
        self.auto = AutoMod()
        # 设置识别区域坐标
        self.coordinates = self._load_coordinates()
        # 设置配置
        self._setup_config()
        
        print("=== 文字匹配自动化程序初始化完成 ===")
        print(f"识别坐标: {self.coordinates}")
    
    def _load_coordinates(self):
        """从文件加载坐标信息"""
        try:
            # 从1.txt文件加载坐标
            with open("d:\code\python\RHINE-LAB\1.txt", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            coordinates = []
            for line in lines:
                # 提取坐标值，处理中文逗号
                coords = line.strip().replace('，', ',').split(',')
                if len(coords) >= 2:
                    try:
                        x = int(coords[0].strip())
                        y = int(coords[1].strip())
                        coordinates.append((x, y))
                    except ValueError:
                        print(f"警告: 无法解析坐标行 '{line.strip()}'")
            
            # 如果文件中没有坐标，使用默认值
            if not coordinates:
                print("警告: 未找到有效坐标，使用默认值")
                coordinates = [(175, 285), (565, 355)]
            
            return coordinates
        except Exception as e:
            print(f"加载坐标文件失败: {str(e)}")
            # 返回默认坐标
            return [(175, 285), (565, 355)]
    
    def _setup_config(self):
        """设置自动化配置"""
        # 配置OCR识别精度
        self.auto.set_ocr_engine("pytesseract")
        # 配置类人鼠标操作
        self.auto.set_human_like_mouse(True)
        # 设置翻译服务
        self.auto.set_translation_service("google")
    
    def is_chinese_text(self, text):
        """判断文本是否包含中文"""
        # 使用正则表达式检测中文字符
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        return bool(chinese_pattern.search(text))
    
    def click_text(self, text_to_find, max_search_time=5):
        """在屏幕上查找并点击指定文字"""
        print(f"正在查找文字: '{text_to_find}'")
        
        start_time = time.time()
        
        while time.time() - start_time < max_search_time:
            try:
                # 截取全屏并识别文字
                ocr_result = self.auto.screenshot_and_recognize()
                
                if not ocr_result.get('text'):
                    time.sleep(0.5)
                    continue
                
                # 在识别结果中查找目标文字
                for box in ocr_result.get('boxes', []):
                    if text_to_find in box['text'] and box['confidence'] > 0.6:
                        # 计算文本框中心位置
                        center_x = box['x'] + box['width'] // 2
                        center_y = box['y'] + box['height'] // 2
                        
                        print(f"找到文字 '{text_to_find}'，位置: ({center_x}, {center_y})")
                        
                        # 移动鼠标并点击
                        self.auto.move_mouse(center_x, center_y)
                        time.sleep(0.2)
                        self.auto.click_mouse()
                        return True
                        
            except Exception as e:
                print(f"查找文字时发生错误: {str(e)}")
                
            time.sleep(0.5)
            
        print(f"在{max_search_time}秒内未找到文字: '{text_to_find}'")
        return False
    
    def recognize_text_at_position(self, x, y, region_size=30):
        """识别指定位置附近的文字"""
        # 定义识别区域（以指定坐标为中心）
        region = (x - region_size, y - region_size, region_size * 2, region_size * 2)
        
        try:
            # 截取区域并识别文字
            ocr_result = self.auto.screenshot_and_recognize(region=region)
            
            # 如果识别结果为空，尝试扩大区域再次识别
            if not ocr_result.get('text'):
                larger_region = (x - region_size * 2, y - region_size * 2, region_size * 4, region_size * 4)
                ocr_result = self.auto.screenshot_and_recognize(region=larger_region)
            
            text = ocr_result.get('text', '').strip()
            print(f"在位置({x}, {y})识别到文字: '{text}'")
            
            return text
        except Exception as e:
            print(f"在位置({x}, {y})识别文字失败: {str(e)}")
            return ""
    
    def click_translation(self, text, is_chinese):
        """根据文本语言类型查找并点击对应的翻译"""
        if not text:
            return False
            
        try:
            # 根据语言类型确定目标语言
            target_lang = 'en' if is_chinese else 'zh'
            
            # 翻译文本
            translation_result = self.auto.translate_text(text, dest_lang=target_lang)
            translated_text = translation_result.get('translated_text', '').strip()
            
            if not translated_text:
                print(f"翻译失败: '{text}'")
                return False
            
            print(f"翻译结果: '{text}' -> '{translated_text}'")
            
            # 查找并点击翻译后的文字
            return self.click_text(translated_text)
            
        except Exception as e:
            print(f"翻译过程中发生错误: {str(e)}")
            return False
    
    def run_initial_step(self):
        """执行初始步骤：点击文字01"""
        print("\n=== 开始执行初始步骤 ===")
        success = self.click_text("01")
        
        if success:
            print("初始步骤执行成功")
        else:
            print("警告: 初始步骤执行失败")
            
        return success
    
    def run_repeat_step(self):
        """执行重复步骤：识别文字并点击翻译"""
        print("\n=== 开始执行重复步骤 ===")
        
        all_success = True
        
        # 遍历所有坐标
        for i, (x, y) in enumerate(self.coordinates):
            print(f"\n处理坐标 {i+1}: ({x}, {y})")
            
            # 识别指定位置的文字
            text = self.recognize_text_at_position(x, y)
            
            if text:
                # 判断是否为中文
                is_chinese = self.is_chinese_text(text)
                print(f"识别到的文字{'是' if is_chinese else '不是'}中文")
                
                # 点击对应的翻译
                success = self.click_translation(text, is_chinese)
                
                if not success:
                    all_success = False
                    print(f"警告: 点击翻译失败")
            else:
                all_success = False
                print(f"警告: 未能识别到文字")
                
        return all_success
    
    def main_loop(self):
        """主循环"""
        print("\n=== 文字匹配自动化程序开始运行 ===")
        
        # 执行初始步骤
        initial_success = self.run_initial_step()
        
        if not initial_success:
            print("初始步骤失败，程序将继续尝试...")
        
        # 主循环
        try:
            while True:
                # 执行重复步骤
                self.run_repeat_step()
                
                # 等待2秒
                print("\n等待2秒...")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"\n程序发生错误: {str(e)}")
        finally:
            print("\n=== 文字匹配自动化程序结束 ===")

if __name__ == "__main__":
    # 创建并运行自动化程序
    automation = TextMatchingAutomation()
    automation.main_loop()