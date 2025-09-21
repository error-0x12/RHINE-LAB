# AutoMod - 自动化支持库

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AutoMod 是一个集成了 OCR（光学字符识别）、鼠标模拟和翻译功能的 Python 支持库，旨在为自动化脚本和应用程序提供便捷的接口。

## 功能特点

- **OCR 文字识别**
  - 支持 Tesseract 和 PaddleOCR 两种引擎
  - 支持中英文等多语言识别
  - 可识别全屏或指定区域的文字
  - 提供文字位置和置信度信息

- **鼠标模拟控制**
  - 支持鼠标移动、点击、双击、右键点击等操作
  - 实现类人鼠标移动算法（贝塞尔曲线、加速度控制）
  - 支持平滑移动和随机延迟
  - 支持鼠标拖拽和滚轮操作

- **多语言翻译**
  - 支持 Google、百度、有道等多种翻译服务
  - 自动语言检测
  - 支持文本和批量翻译
  - 支持文件翻译

- **集成工作流**
  - 提供统一的接口，便于集成多个功能
  - 灵活的配置系统
  - 支持配置保存和加载
  - 丰富的示例代码

## 安装指南

### 快速安装

1. 克隆或下载本仓库
2. 运行安装脚本：
   
   ```bash
   cd automod
   python install.py
   ```

   安装脚本会自动安装所有依赖包，并提供必要的配置指导。

### 手动安装

1. 安装 Python 3.8 或更高版本
2. 安装依赖包：
   
   ```bash
   pip install -r requirements.txt
   ```

3. 安装 OCR 引擎（Tesseract）：
   - **Windows**: 从 [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) 下载并安装
   - **macOS**: `brew install tesseract tesseract-lang`
   - **Linux**: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim` (Ubuntu/Debian)

## 快速开始

以下是一个简单的使用示例：

```python
from automod import AutoMod

# 创建AutoMod实例
auto = AutoMod()

# 截取屏幕并识别文字
ocr_result = auto.screenshot_and_recognize()
print(f"识别结果: {ocr_result.get('text', '')}")

# 翻译识别到的文字
if ocr_result.get('text'):
    translate_result = auto.translate_text(ocr_result['text'], dest_lang='zh')
    print(f"翻译结果: {translate_result.get('translated_text', '')}")

# 移动鼠标到屏幕中央
import pyautogui
width, height = pyautogui.size()
auto.move_mouse(width // 2, height // 2)
```

## 详细文档

### 1. 配置管理

AutoMod 提供了灵活的配置系统，您可以根据需要自定义各种参数：

```python
from automod import AutoModConfig, AutoMod

# 创建并自定义配置
config = AutoModConfig()
config.update_ocr_config(
    engine="pytesseract",  # 可选: pytesseract, paddleocr
    lang="chi_sim+eng",    # 识别语言
    confidence_threshold=0.7  # 置信度阈值
)
config.update_mouse_config(
    move_speed=1.5,        # 鼠标移动速度
    smooth_move=True,      # 是否使用平滑移动
    human_like=True        # 是否模拟人类行为
)

# 使用自定义配置创建AutoMod实例
auto = AutoMod(config)

# 保存配置到文件
auto.save_config("my_config.json")

# 从文件加载配置
auto.load_config("my_config.json")
```

### 2. OCR 功能

```python
# 识别图像文件中的文字
result = auto.recognize_text("image.jpg")

# 识别指定区域的文字
region_result = auto.recognize_text("image.jpg", region=(100, 100, 400, 300))

# 截取屏幕指定区域并识别
ss_result = auto.screenshot_and_recognize(region=(0, 0, 800, 600))

# 获取识别到的文字和文本框信息
text = ss_result.get('text', '')
boxes = ss_result.get('boxes', [])
for box in boxes:
    print(f"文本: {box['text']}, 位置: ({box['x']}, {box['y']}), 置信度: {box['confidence']}")
```

### 3. 鼠标控制

```python
# 移动鼠标
auto.move_mouse(500, 300, duration=1.0)  # 1秒内移动到(500, 300)

# 点击鼠标
auto.click_mouse()  # 点击当前位置
auto.click_mouse(500, 300, button='left')  # 点击指定位置

# 右键点击
auto.right_click_mouse()

# 双击
auto.double_click_mouse()

# 拖拽操作
auto.move_mouse(100, 100).drag_mouse(300, 300, duration=1.5)

# 滚动鼠标滚轮
auto.scroll_mouse(5)  # 向上滚动5格
auto.scroll_mouse(-5)  # 向下滚动5格

# 获取当前鼠标位置
x, y = auto.get_mouse_position()
print(f"当前鼠标位置: ({x}, {y})")
```

### 4. 翻译功能

```python
# 翻译文本
result = auto.translate_text("Hello, world!", dest_lang='zh')
print(f"翻译结果: {result.get('translated_text', '')}")

# 检测语言
detected_lang = auto.detect_language("你好，世界！")
print(f"检测到的语言: {detected_lang}")

# 批量翻译
batch_texts = ["Hello", "How are you?", "Goodbye"]
batch_results = auto.batch_translate(batch_texts, dest_lang='zh')
for i, res in enumerate(batch_results):
    print(f"{i+1}. {res['text']} -> {res['translated_text']}")

# 文件翻译
auto.translator.translate_file("input.txt", "output_zh.txt", dest_lang='zh')
```

### 5. 组合功能

```python
# 识别并翻译屏幕文字
combined_result = auto.screenshot_recognize_and_translate(
    region=(0, 0, 800, 600),  # 截取区域
    dest_lang='zh'             # 目标语言
)
print(f"组合结果: {combined_result.get('combined_text', '')}")
```

## 示例代码

本库提供了两个示例文件：

1. `example.py` - 基础功能示例，展示各模块的基本使用方法
2. `comprehensive_example.py` - 综合示例，展示更复杂的功能组合和工作流

您可以通过以下命令运行示例：

```bash
python example.py
python comprehensive_example.py
```

## 注意事项

1. **Tesseract 配置**：使用前请确保已正确安装 Tesseract OCR 引擎，并在需要时配置正确的路径

2. **权限问题**：鼠标模拟功能可能需要特定权限才能在某些操作系统或应用程序中正常工作

3. **API 密钥**：使用百度或有道翻译服务时，需要提供有效的 API 密钥

4. **资源消耗**：PaddleOCR 引擎相比 Tesseract 消耗更多系统资源，但在某些场景下识别效果更好

5. **网络连接**：翻译功能需要稳定的网络连接才能正常工作

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交问题和改进建议！如果您有任何问题，请在 GitHub 仓库中创建 issue。

## 更新日志

### v1.0.0
- 初始版本，包含 OCR、鼠标模拟和翻译功能
- 支持 Tesseract 和 PaddleOCR 引擎
- 实现类人鼠标移动算法
- 支持 Google、百度、有道翻译服务
- 提供丰富的配置选项和示例代码