"""
AutoMod 测试文件

用于快速验证AutoMod支持库的基本功能是否正常工作。
"""

import sys
import os
import time

# 确保可以导入AutoMod
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestResult:
    """测试结果类"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = []
        
    def add_result(self, test_name: str, success: bool, message: str = ""):
        """添加测试结果"""
        self.total += 1
        if success:
            self.passed += 1
            status = "✓ PASSED"
        else:
            self.failed += 1
            status = "✗ FAILED"
        
        self.results.append((test_name, status, message))
        print(f"{test_name}: {status}")
        if message:
            print(f"  {message}")
    
    def summary(self):
        """打印测试摘要"""
        print("\n=== 测试摘要 ===")
        print(f"总测试数: {self.total}")
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        
        if self.failed > 0:
            print("\n失败的测试:")
            for name, status, msg in self.results:
                if status == "✗ FAILED":
                    print(f"- {name}: {msg}")
        
        return self.failed == 0


def test_import():
    """测试模块导入"""
    try:
        from automod import AutoMod, AutoModConfig
        return True, "模块导入成功"
    except ImportError as e:
        return False, f"模块导入失败: {str(e)}"


def test_config():
    """测试配置功能"""
    try:
        from automod import AutoModConfig
        config = AutoModConfig()
        
        # 测试更新配置
        config.update_ocr_config(lang="eng")
        config.update_mouse_config(move_speed=2.0)
        config.update_translation_config(timeout=5)
        
        # 测试获取配置
        assert config.get('ocr', 'lang') == "eng"
        assert config.get('mouse', 'move_speed') == 2.0
        assert config.get('translation', 'timeout') == 5
        
        # 测试默认值
        assert config.get('nonexistent', 'key', 'default') == 'default'
        
        return True, "配置功能测试通过"
    except Exception as e:
        return False, f"配置功能测试失败: {str(e)}"


def test_translation():
    """测试翻译功能"""
    try:
        from automod import AutoMod
        auto = AutoMod()
        
        # 测试基本翻译
        result = auto.translate_text("Hello, world!")
        assert result.get('translated_text') and result.get('translated_text') != ""
        
        # 测试语言检测
        detected_lang = auto.detect_language("你好，世界！")
        assert detected_lang == "zh" or detected_lang == "auto"
        
        return True, f"翻译功能测试通过 (翻译结果: {result['translated_text'][:20]}..."
    except Exception as e:
        return False, f"翻译功能测试失败: {str(e)}"


def test_mouse_position():
    """测试鼠标位置获取功能"""
    try:
        from automod import AutoMod
        auto = AutoMod()
        
        # 获取鼠标位置
        x, y = auto.get_mouse_position()
        assert isinstance(x, int) and isinstance(y, int)
        assert x >= 0 and y >= 0
        
        return True, f"鼠标位置获取成功: ({x}, {y})"
    except Exception as e:
        return False, f"鼠标位置获取失败: {str(e)}"


def test_ocr_preparation():
    """测试OCR准备工作"""
    try:
        from automod import AutoMod
        auto = AutoMod()
        
        # 检查OCR引擎是否可用（不实际执行识别）
        # 这里只是验证模块可以正常初始化
        assert hasattr(auto.ocr, 'recognize')
        assert hasattr(auto.ocr, 'screenshot_and_recognize')
        
        return True, "OCR模块初始化成功"
    except Exception as e:
        return False, f"OCR模块初始化失败: {str(e)}"


def run_tests():
    """运行所有测试"""
    print("======= AutoMod 功能测试 =======")
    print(f"Python版本: {sys.version}")
    print(f"当前目录: {os.getcwd()}")
    print(f"AutoMod目录: {os.path.dirname(os.path.abspath(__file__))}")
    print("\n开始测试...\n")
    
    # 创建测试结果对象
    result = TestResult()
    
    # 运行测试
    result.add_result("模块导入测试", *test_import())
    result.add_result("配置功能测试", *test_config())
    result.add_result("翻译功能测试", *test_translation())
    result.add_result("鼠标位置测试", *test_mouse_position())
    result.add_result("OCR准备测试", *test_ocr_preparation())
    
    # 打印摘要
    success = result.summary()
    
    print("\n===============================")
    
    if success:
        print("\n🎉 所有测试通过！AutoMod支持库基本功能正常。")
        print("您可以通过运行 example.py 来查看更多示例。")
    else:
        print("\n❌ 部分测试失败。请检查错误信息并修复问题。")
        print("建议运行 install.py 重新安装依赖。")
    
    print("\n测试完成。")

if __name__ == "__main__":
    run_tests()