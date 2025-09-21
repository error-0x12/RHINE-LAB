# -*- coding: utf-8 -*-
"""
启动原子朋克风格的数据分析平台GUI
"""

import sys
import os

# 设置工作目录到脚本所在目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("===== 莱茵生命数据分析平台 =====")
print("正在启动界面...")

try:
    # 运行原子朋克风格的GUI
    from data_analysis_platform_gui_revamped import RetroFuturisticPlatformGUI
    import tkinter as tk
    
    # 创建主窗口
    root = tk.Tk()
    
    # 创建并启动GUI应用
    app = RetroFuturisticPlatformGUI(root)
    
    # 运行主循环
    root.mainloop()
    
    print("程序已正常退出")
except ImportError as e:
    print(f"错误: 无法导入必要的模块 - {str(e)}")
    print("请确保所有依赖已正确安装")
except Exception as e:
    print(f"错误: 程序运行时发生异常 - {str(e)}")
finally:
    print("===== 程序结束 =====")