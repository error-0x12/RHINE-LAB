import sys
import os
import subprocess

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 构建应用程序路径
app_path = os.path.join(script_dir, 'code_archiver_gui.py')

# 检查应用程序文件是否存在
if not os.path.exists(app_path):
    print(f"错误：找不到应用程序文件 {app_path}")
    input("按回车键退出...")
    sys.exit(1)

# 启动应用程序
print(f"正在启动CTRL_Z_tool...")
try:
    # 使用Python启动应用程序
    subprocess.run([sys.executable, app_path], check=True)
except subprocess.CalledProcessError as e:
    print(f"应用程序启动失败：{e}")
    input("按回车键退出...")
    sys.exit(1)
except KeyboardInterrupt:
    print("应用程序已被用户中断")
    sys.exit(0)