"""
AutoMod 综合示例文件

展示如何更复杂地使用AutoMod支持库的各种功能组合。
"""

from automod import AutoMod, AutoModConfig
import time
import cv2
import numpy as np
import os

# 创建一个带配置的AutoMod实例
config = AutoModConfig()
config.update_ocr_config(
    engine="pytesseract",  # 可以切换为"paddleocr"
    lang="chi_sim+eng",
    confidence_threshold=0.6
)
config.update_mouse_config(
    move_speed=1.5,
    smooth_move=True,
    human_like=True
)
config.update_translation_config(
    service="google",  # 可以切换为"baidu"或"youdao"（需要API密钥）
    timeout=15
)

auto = AutoMod(config)

print("=== AutoMod 综合示例 ===")
print("这个示例展示了如何更高级地使用AutoMod的各项功能")
print("当前配置:")
print(auto)
print("\n按Enter键继续...")
input()

# 功能1: 高级OCR识别
print("\n=== 功能1: 高级OCR识别 ===")
print("1.1 屏幕区域OCR识别")
print("3秒后将截取屏幕右上角区域并识别文字")
time.sleep(3)

# 截取屏幕右上角区域
import pyautogui
width, height = pyautogui.size()
region = (width - 500, 0, 500, 300)  # 右上角区域
ocr_result = auto.screenshot_and_recognize(region=region)

print(f"识别到的文字: {ocr_result.get('text', '')}")
print(f"识别到的文本框数量: {len(ocr_result.get('boxes', []))}")

# 1.2 保存识别结果为图像（带文本框标记）
if ocr_result.get('boxes'):
    print("\n1.2 保存带文本框标记的截图...")
    # 重新截取屏幕
    screenshot = pyautogui.screenshot(region=region)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # 在图像上标记文本框
    for box in ocr_result['boxes']:
        x, y, w, h = box['x'], box['y'], box['width'], box['height']
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # 在文本框上方显示识别的文字
        cv2.putText(
            img, box['text'], (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2
        )
    
    # 保存图像
    output_path = "ocr_result_with_boxes.png"
    cv2.imwrite(output_path, img)
    print(f"已保存带文本框标记的截图到: {output_path}")

print("\n按Enter键继续...")
input()

# 功能2: 智能翻译工作流
print("\n=== 功能2: 智能翻译工作流 ===")
print("2.1 检测语言并翻译")

# 准备测试文本（混合语言）
mixed_text = "Python is a powerful programming language. Python是一种强大的编程语言。"
print(f"原始文本: {mixed_text}")

# 检测语言
detected_lang = auto.detect_language(mixed_text)
print(f"检测到的语言: {detected_lang}")

# 根据检测结果选择目标语言
if detected_lang == 'zh':
    target_lang = 'en'
else:
    target_lang = 'zh'

# 翻译文本
translate_result = auto.translate_text(mixed_text, dest_lang=target_lang)
print(f"翻译结果: {translate_result.get('translated_text', '')}")

print("\n按Enter键继续...")
input()

# 功能3: 高级鼠标控制
print("\n=== 功能3: 高级鼠标控制 ===")
print("3.1 类人鼠标移动")
print("3秒后将演示类人鼠标移动模式")
time.sleep(3)

# 获取当前位置
current_x, current_y = auto.get_mouse_position()
print(f"当前鼠标位置: ({current_x}, {current_y})")

# 演示类人移动到几个随机位置
for i in range(3):
    # 生成随机目标位置（在当前位置附近）
    target_x = current_x + np.random.randint(-200, 200)
    target_y = current_y + np.random.randint(-200, 200)
    
    # 限制在屏幕范围内
    target_x = max(0, min(target_x, width - 1))
    target_y = max(0, min(target_y, height - 1))
    
    print(f"移动鼠标到: ({target_x}, {target_y})...")
    auto.move_mouse(target_x, target_y)
    
    # 更新当前位置
    current_x, current_y = target_x, target_y
    time.sleep(1)

print("\n3.2 模拟拖拽操作")
print("3秒后将模拟拖拽操作")
time.sleep(3)

# 创建一个临时文件用于演示拖拽（不实际执行）
print("提示: 在实际应用中，您可以使用drag_mouse来模拟文件拖拽等操作")
print("示例代码: auto.drag_mouse(start_x, start_y).drag_to(end_x, end_y, duration=1.5)")

print("\n按Enter键继续...")
input()

# 功能4: 完整的工作流集成
print("\n=== 功能4: 完整的工作流集成 ===")
print("4.1 OCR + 翻译 + 鼠标操作组合示例")
print("这个示例展示了如何创建一个完整的自动化工作流")

# 定义一个简单的自动化工作流函数
def automate_workflow():
    print("\n开始自动化工作流...")
    
    # 1. 截取屏幕并识别文字
    print("1. 截取屏幕并识别文字...")
    screen_center = (width // 2, height // 2)
    workflow_region = (screen_center[0] - 300, screen_center[1] - 200, 600, 400)
    workflow_ocr = auto.screenshot_and_recognize(region=workflow_region)
    
    if not workflow_ocr.get('text'):
        print("未识别到文字，使用演示文本...")
        workflow_ocr['text'] = "This is a sample text for the automated workflow demonstration."
        
    print(f"识别到的文字: {workflow_ocr['text']}")
    
    # 2. 翻译文字
    print("2. 翻译识别到的文字...")
    workflow_translate = auto.translate_text(workflow_ocr['text'], dest_lang='zh')
    print(f"翻译结果: {workflow_translate['translated_text']}")
    
    # 3. 模拟鼠标操作（移动到屏幕右下角）
    print("3. 模拟鼠标操作...")
    auto.move_mouse(width - 100, height - 100, duration=1.0)
    print("已移动鼠标到屏幕右下角")
    
    # 注意：为了安全，这里不实际执行点击操作
    # auto.click_mouse()
    
    print("\n自动化工作流完成！")

# 执行自动化工作流
automate_workflow()

print("\n按Enter键继续...")
input()

# 功能5: 配置管理
print("\n=== 功能5: 配置管理 ===")
print("5.1 保存和加载配置")

# 保存当前配置到文件
config_file = "automod_config.json"
print(f"保存配置到文件: {config_file}")
auto.save_config(config_file)

# 加载配置
print(f"加载配置文件: {config_file}")
new_auto = AutoMod().load_config(config_file)
print("加载后的配置:")
print(new_auto)

print("\n=== 示例结束 ===")
print("感谢使用AutoMod支持库！")
print("您可以基于这些示例创建自己的自动化脚本和应用程序。")

# 清理临时文件
try:
    if os.path.exists(config_file):
        os.remove(config_file)
    if os.path.exists("ocr_result_with_boxes.png"):
        os.remove("ocr_result_with_boxes.png")
    print("\n临时文件已清理")
except:
    pass