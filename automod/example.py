"""
AutoMod 示例文件

展示如何使用AutoMod支持库的各种功能。
"""

from automod import AutoMod, AutoModConfig
import time

# 创建AutoMod实例
auto = AutoMod()

# 打印当前配置
print("=== AutoMod配置信息 ===")
print(auto)
print()

# 示例1: 基本OCR识别
print("=== 示例1: 基本OCR识别 ===")
# 注意：这里假设您有一个测试图像文件
# 如果没有，可以使用屏幕截图识别代替
# result = auto.recognize_text("test_image.png")
# 或者使用屏幕截图识别
print("3秒后将截取屏幕左上角并识别文字...")
time.sleep(3)
ocr_result = auto.screenshot_and_recognize(region=(0, 0, 800, 600))
print(f"识别结果: {ocr_result.get('text', '')}")
print(f"识别到的文本框数量: {len(ocr_result.get('boxes', []))}")
print()

# 示例2: 识别并翻译
print("=== 示例2: 识别并翻译 ===")
# 创建一些测试文本用于演示
# 注意：在实际使用中，您可以使用屏幕截图识别的文本
# 这里我们模拟一些文本进行演示
if not ocr_result.get('text', ''):
    # 如果屏幕截图没有识别到文字，使用示例文本
    test_text = "This is a test text for translation. 这是一段用于翻译测试的文本。"
    translate_result = auto.translate_text(test_text, dest_lang='zh')
    print(f"原文: {test_text}")
    print(f"翻译: {translate_result.get('translated_text', '')}")
else:
    # 使用屏幕截图识别的文字进行翻译
    print("识别并翻译屏幕文字...")
    combined_result = auto.recognize_and_translate(
        image=None,  # 使用屏幕截图
        region=(0, 0, 800, 600),
        dest_lang='zh'
    )
    print(f"组合结果: {combined_result.get('combined_text', '')}")
print()

# 示例3: 鼠标控制
print("=== 示例3: 鼠标控制 ===")
print("当前鼠标位置:", auto.get_mouse_position())

# 移动鼠标到屏幕中央附近
print("移动鼠标到屏幕中央...")
# 获取屏幕尺寸
import pyautogui
width, height = pyautogui.size()
center_x, center_y = width // 2, height // 2

# 移动鼠标到中央
auto.move_mouse(center_x, center_y, duration=1.0)
print("移动后的鼠标位置:", auto.get_mouse_position())

# 模拟鼠标点击
print("3秒后将点击鼠标（请确保鼠标位置安全）...")
time.sleep(3)
# 注意：为了安全，这里不实际执行点击操作
# auto.click_mouse()
print("点击操作已模拟（在实际使用中会执行真实点击）")
print()

# 示例4: 配置自定义
print("=== 示例4: 配置自定义 ===")
# 创建自定义配置
custom_config = AutoModConfig()
custom_config.update_ocr_config(lang="eng")  # 设置OCR语言为英文
custom_config.update_mouse_config(move_speed=2.0, human_like=False)  # 更快的鼠标移动

# 使用自定义配置创建AutoMod实例
custom_auto = AutoMod(custom_config)
print("自定义配置后的AutoMod:")
print(custom_auto)
print()

# 示例5: 批量翻译
print("=== 示例5: 批量翻译 ===")
batch_texts = [
    "Hello, world!",
    "How are you?",
    "This is a test."
]
print(f"批量翻译文本: {batch_texts}")
batch_results = auto.batch_translate(batch_texts, dest_lang='zh')
for i, result in enumerate(batch_results):
    print(f"{i+1}. 原文: {result['text']}")
    print(f"   翻译: {result['translated_text']}")
print()

# 示例6: 组合操作
print("=== 示例6: 组合操作 ===")
# 这个示例展示了如何组合使用多个功能
print("5秒后将执行以下操作:")
print("1. 截取屏幕中央区域")
print("2. 识别其中的文字")
print("3. 将文字翻译为中文")
time.sleep(5)

# 执行组合操作
combo_result = auto.screenshot_recognize_and_translate(
    region=(center_x - 400, center_y - 300, 800, 600),
    dest_lang='zh'
)

if combo_result.get('ocr_result') and combo_result['ocr_result'].get('text'):
    print(f"组合操作结果:")
    print(f"识别原文: {combo_result['ocr_result']['text']}")
    print(f"翻译结果: {combo_result['translation_result']['translated_text']}")
else:
    print("组合操作未能识别到文字")
print()

print("=== 示例结束 ===")
print("感谢使用AutoMod支持库！")
print("更多高级功能请参考API文档或查看源码。")