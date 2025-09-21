"""
AutoMod 安装脚本

用于安装AutoMod支持库及其所有依赖包。
"""

import os
import sys
import subprocess
import platform
import time

def check_python_version():
    """检查Python版本是否符合要求"""
    required_major = 3
    required_minor = 8
    
    major, minor, _, _, _ = sys.version_info
    
    if major < required_major or (major == required_major and minor < required_minor):
        print(f"错误: 需要Python {required_major}.{required_minor} 或更高版本。当前版本: {major}.{minor}")
        sys.exit(1)
    
    print(f"Python版本检查通过: {major}.{minor}")


def install_packages():
    """安装所有依赖包"""
    print("\n=== 开始安装依赖包 ===")
    
    # 首先确保pip是最新的
    print("更新pip...")
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # 安装核心依赖
    core_packages = [
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "pyautogui>=0.9.54",
        "requests>=2.31.0",
        "Pillow>=9.5.0"
    ]
    
    print("\n安装核心依赖...")
    for package in core_packages:
        print(f"安装 {package}...")
        subprocess.call([sys.executable, "-m", "pip", "install", package])
    
    # 安装OCR引擎
    print("\n安装OCR引擎 (Tesseract)...")
    subprocess.call([sys.executable, "-m", "pip", "install", "pytesseract>=0.3.10"])
    
    # 根据操作系统提供不同的提示
    current_os = platform.system()
    
    if current_os == "Windows":
        print("\n=== Windows系统额外配置 ===")
        print("1. 请下载并安装Tesseract OCR引擎:")
        print("   - 下载地址: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   - 安装时请记住安装路径，稍后可能需要配置")
        print("\n2. 安装后，您可能需要在代码中设置tesseract_cmd路径，例如:")
        print("   import pytesseract")
        print("   pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        
    elif current_os == "Darwin":  # macOS
        print("\n=== macOS系统额外配置 ===")
        print("1. 请使用Homebrew安装Tesseract OCR引擎:")
        print("   brew install tesseract")
        print("   brew install tesseract-lang  # 安装额外语言包")
        
    elif current_os == "Linux":
        print("\n=== Linux系统额外配置 ===")
        print("1. 请使用包管理器安装Tesseract OCR引擎:")
        print("   Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim")
        print("   CentOS/RHEL: sudo yum install tesseract tesseract-langpack-chi_sim")
        print("   Arch Linux: sudo pacman -S tesseract tesseract-data-chi_sim")
    
    # 可选：PaddleOCR引擎
    print("\n=== 可选: PaddleOCR引擎 ===")
    print("如果您想使用PaddleOCR引擎，可以取消下面的注释")
    print("注意：PaddleOCR安装可能需要较长时间并占用较多资源")
    print("\n是否安装PaddleOCR引擎？(y/n): ")
    install_paddle = input().strip().lower()
    
    if install_paddle == 'y':
        print("\n安装PaddleOCR引擎...")
        subprocess.call([sys.executable, "-m", "pip", "install", "paddleocr>=2.6.1"])
        print("\nPaddleOCR安装完成")
    
    print("\n=== 依赖包安装完成 ===")


def setup_environment():
    """设置环境变量"""
    print("\n=== 设置环境变量 ===")
    
    # 检查是否需要设置PYTHONPATH
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # 检查当前目录是否在PYTHONPATH中
    python_path = os.environ.get("PYTHONPATH", "")
    if current_dir not in python_path and parent_dir not in python_path:
        print(f"检测到AutoMod目录不在PYTHONPATH中")
        print(f"AutoMod目录: {current_dir}")
        print("\n建议将AutoMod目录添加到PYTHONPATH中，以便在任何位置导入")
        print("\nWindows系统可以通过以下方式设置:")
        print(f"set PYTHONPATH=%PYTHONPATH%;{current_dir}")
        print("\nLinux/macOS系统可以通过以下方式设置:")
        print(f"export PYTHONPATH=$PYTHONPATH:{current_dir}")
        print("\n或者在您的Python脚本中添加:")
        print(f"import sys")
        print(f"sys.path.append('{current_dir}')")
    else:
        print("AutoMod目录已在PYTHONPATH中，无需额外设置")


def create_config_file():
    """创建示例配置文件"""
    print("\n=== 创建示例配置文件 ===")
    
    config_content = '''{
  "ocr_config": {
    "engine": "pytesseract",
    "lang": "chi_sim+eng",
    "data_path": null,
    "confidence_threshold": 0.7
  },
  "mouse_config": {
    "move_speed": 1.0,
    "click_delay": 0.1,
    "smooth_move": true,
    "human_like": true
  },
  "translation_config": {
    "service": "google",
    "api_key": null,
    "api_secret": null,
    "timeout": 10,
    "proxy": null
  }
}
'''
    
    config_file = "automod_config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print(f"已创建示例配置文件: {config_file}")
    print("您可以根据需要修改此配置文件，然后通过load_config方法加载")


def run_simple_test():
    """运行简单测试以验证安装"""
    print("\n=== 运行安装验证测试 ===")
    
    try:
        # 尝试导入AutoMod模块
        from automod import AutoMod
        print("✓ AutoMod模块导入成功")
        
        # 创建AutoMod实例
        auto = AutoMod()
        print("✓ AutoMod实例创建成功")
        print(f"当前配置: {auto}")
        
        # 测试基本功能
        print("\n测试基本翻译功能...")
        test_text = "Hello, AutoMod!"
        result = auto.translate_text(test_text)
        print(f"原文: {test_text}")
        print(f"翻译: {result.get('translated_text', '翻译失败')}")
        
        print("\n✓ 安装验证测试通过！")
        return True
    except Exception as e:
        print(f"✗ 安装验证测试失败: {str(e)}")
        print("请检查安装过程中的错误信息")
        return False


def main():
    """主函数"""
    print("======= AutoMod 安装脚本 =======")
    print("这个脚本将帮助您安装AutoMod支持库及其所有依赖")
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖包
    install_packages()
    
    # 设置环境
    setup_environment()
    
    # 创建配置文件
    create_config_file()
    
    # 运行验证测试
    success = run_simple_test()
    
    print("\n===============================")
    print("\n安装完成！")
    
    if success:
        print("您现在可以通过以下方式开始使用AutoMod:")
        print("1. 运行示例: python example.py")
        print("2. 查看综合示例: python comprehensive_example.py")
        print("3. 在您的代码中导入: from automod import AutoMod")
    else:
        print("安装过程中可能存在问题，请检查上面的错误信息")
        print("如有需要，请手动安装缺失的依赖")
    
    print("\n祝您使用愉快！")

if __name__ == "__main__":
    main()