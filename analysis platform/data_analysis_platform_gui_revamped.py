# -*- coding: utf-8 -*-
"""
数据分析平台GUI界面 - 原子朋克风格
风格参考：原子朋克的复古核能美学、磁带盒未来主义、NASA朋克的航天工业硬核风
主要色调：磁带盒未来主义的橙白配色
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import sys
import json
import re
from io import BytesIO
import math

# 导入数据分析平台核心功能
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_analysis_platform import DataAnalysisPlatform

# 尝试导入PIL的模块用于图片预览
try:
    from PIL import Image, ImageTk
except ImportError:
    print("警告：无法导入PIL模块，图片预览功能可能受限。")
    Image = None
    ImageTk = None

class RetroFuturisticPlatformGUI:
    """数据分析平台GUI类 - 原子朋克风格"""
    
    def __init__(self, root):
        """初始化GUI界面"""
        # 初始化数据分析平台
        self.platform = DataAnalysisPlatform()
        
        # 设置主窗口
        self.root = root
        self.root.title("RHEINLAB DATA ANALYSIS SYSTEM")
        self.root.minsize(1000, 700)
        # 设置默认全屏
        self.root.attributes('-fullscreen', True)
        
        # 设置磁带盒未来主义风格的颜色方案
        self.bg_color = "#E8E5E0"  # 深黑色背景
        self.fg_color = "#000000"  # 黑色前景
        self.accent_color = "#ff7f2a"  # 橙色强调色
        self.secondary_color = "#32cd32"  # 荧光绿次要强调色
        self.panel_color = "#E8E5E0"  # 面板背景色
        self.button_color = "#2a2a2a"  # 按钮背景色
        self.input_bg = "#1a1a1a"  # 输入框背景色
        self.border_color = "#ff7f2a"  # 边框颜色
        self.warning_color = "#ff3e3e"  # 警告颜色
        self.btn_words = "#E8E5E0"  # 按钮文字颜色
        
        # 设置全局样式
        self.style = ttk.Style()
        self.style.theme_use("clam")  # 使用clam主题作为基础
        
        # 配置样式
        self._configure_styles()
        
        # 添加装饰性元素
        self._add_decorative_elements()
        
        # 创建主布局
        self._create_main_layout()
    
    def _configure_styles(self):
        """配置ttk样式"""
        # 配置框架样式 - 使用ttk兼容的选项
        self.style.configure("RetroFrame.TFrame", background=self.panel_color)
        self.style.configure("RetroPanel.TFrame", background=self.bg_color)
        self.style.configure("RetroAccent.TFrame", background=self.accent_color)
        
        # 配置标签样式
        self.style.configure("RetroLabel.TLabel", 
                            background=self.panel_color, 
                            foreground=self.fg_color, 
                            font=("Courier New", 10, "bold"))
        
        # 配置标题标签样式
        self.style.configure("RetroTitle.TLabel", 
                            background=self.bg_color, 
                            foreground=self.accent_color, 
                            font=("Courier New", 30, "bold"),
                            padding=10)
        
        # 配置警告标签样式
        self.style.configure("RetroWarning.TLabel", 
                            background=self.bg_color, 
                            foreground=self.warning_color, 
                            font=("Courier New", 10, "bold"))
        
        # 配置按钮样式 - 移除不兼容的选项
        self.style.configure("RetroButton.TButton", 
                            background=self.button_color, 
                            foreground=self.btn_words if self.btn_words else self.fg_color, 
                            font=("Courier New", 10, "bold"),
                            padding=5)
        # 添加选中和未选中状态的视觉区分
        self.style.map("RetroButton.TButton", 
                      background=[("active", self.accent_color),
                                 ("selected", self.accent_color)],
                      foreground=[("active", self.bg_color),
                                 ("selected", self.bg_color)])
        
        # 配置输入框样式 - 移除不兼容的选项
        self.style.configure("RetroEntry.TEntry", 
                            fieldbackground=self.input_bg, 
                            foreground=self.bg_color, 
                            insertcolor=self.accent_color,
                            font=("Courier New", 10))
        
        # 配置组合框样式 - 移除不兼容的选项
        self.style.configure("RetroCombobox.TCombobox", 
                            fieldbackground=self.input_bg, 
                            foreground=self.btn_words,
                            font=("Courier New", 10))
        
        # 配置标签页样式 - 移除不兼容的选项
        self.style.configure("RetroNotebook.TNotebook", 
                            background=self.bg_color)
        self.style.configure("RetroNotebook.TNotebook.Tab", 
                            background=self.button_color, 
                            foreground=self.btn_words,
                            font=("Courier New", 10, "bold"),
                            padding=(15, 5))
        self.style.map("RetroNotebook.TNotebook.Tab", 
                      background=[("selected", self.accent_color)],
                      foreground=[("selected", self.bg_color)])
        
        # 配置滚动条样式 - 移除不兼容的选项
        self.style.configure("RetroScrollbar.TScrollbar",
                            background=self.button_color,
                            troughcolor=self.bg_color,
                            arrowcolor=self.fg_color)
        self.style.map("RetroScrollbar.TScrollbar",
                      background=[("active", self.accent_color)],
                      arrowcolor=[("active", self.bg_color)])
    
    def _create_main_layout(self):
        """创建主布局"""
        # 设置主窗口背景
        self.root.configure(bg=self.bg_color)
        
        # 添加警告条和退出按钮
        top_bar_frame = ttk.Frame(self.root, height=30)
        top_bar_frame.pack(fill=tk.X)
        top_bar_frame.columnconfigure(0, weight=1)
        top_bar_frame.columnconfigure(1, weight=0)
        
        # 警告条
        warning_bar = ttk.Frame(top_bar_frame, style="RetroAccent.TFrame", height=30)
        warning_bar.grid(row=0, column=0, sticky="ew")
        
        warning_label = ttk.Label(warning_bar, text="// CURRENT PERMISSIONS: Collaborators == RHODES_ISLAND-Doctor >>> Level 4 //", 
                                 style="RetroWarning.TLabel", font=('Courier New', 12, 'bold'))
        warning_label.pack(fill=tk.X, padx=20, pady=5)
        
        # 退出按钮
        exit_frame = ttk.Frame(top_bar_frame, height=30)
        exit_frame.grid(row=0, column=1, sticky="e")
        
        exit_btn = ttk.Button(exit_frame, text="[退出系统]", command=self._exit_application, 
                             style="RetroButton.TButton")
        exit_btn.pack(padx=10, pady=5)
        
        # 创建标题栏
        title_frame = ttk.Frame(self.root, style="RetroFrame.TFrame")
        title_frame.pack(fill=tk.X, padx=20, pady=15)  # 装饰组件稍向右移
        
        # 添加复古装饰元素（磁带盒风格）
        cassette_top = ttk.Frame(title_frame, height=30, style="RetroAccent.TFrame")
        cassette_top.pack(fill=tk.X, padx=100, pady=(10, 0))  # 装饰组件稍向右移
        
        # 添加标题
        title_label = ttk.Label(title_frame, text="RHEIN LAB DATA ANALYSIS SYSTEM", 
                               style="RetroTitle.TLabel")
        title_label.pack(pady=20)
        
        # 添加版本信息
        version_label = ttk.Label(title_frame, text="VERSION 1.0.0 // CLASSIFIED // LEVEL 3 ACCESS REQUIRED", 
                                 style="RetroLabel.TLabel")
        version_label.pack(pady=10)
        
        # 添加复古装饰元素（磁带卷轴）
        self._add_cassette_rolls(title_frame)
        
        # 创建标签页控件 - 重写功能区布局
        notebook_frame = ttk.Frame(self.root, style="RetroFrame.TFrame")
        notebook_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)  # 标准padding，避免出框
        
        self.notebook = ttk.Notebook(notebook_frame, style="RetroNotebook.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # 标准padding，避免出框
        
        # 创建标签页
        self._create_encoding_tab()
        self._create_image_tab()
        self._create_audio_tab()
        self._create_video_tab()
        self._create_text_tab()
        self._create_file_tab()
        self._create_commands_tab()
    
    def _exit_application(self):
        """退出应用程序"""
        self.root.destroy()
        sys.exit(0)
            
    def _create_scrollable_panel(self, parent):
        """创建带有垂直滚动条的面板"""
        # 创建容纳Canvas和Scrollbar的框架
        scrollable_frame = ttk.Frame(parent, style="RetroPanel.TFrame")
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.rowconfigure(0, weight=1)
        
        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(scrollable_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview, style="RetroScrollbar.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.grid(row=0, column=0, sticky="nsew")
        
        # 创建可以滚动的内容框架
        control_frame = ttk.Frame(canvas, style="RetroPanel.TFrame")
        canvas_window = canvas.create_window((0, 0), window=control_frame, anchor="nw")
        
        # 使用lambda函数将canvas和canvas_window作为参数传递给类方法
        control_frame.bind("<Configure>", lambda event, c=canvas: self._on_frame_configure(event, c))
        canvas.bind("<Configure>", lambda event, c=canvas, cw=canvas_window: self._on_canvas_configure(event, c, cw))
        
        # 在Canvas上绑定滚轮事件
        canvas.bind("<MouseWheel>", lambda event, c=canvas: self._on_mousewheel(event, c))  # Windows
        canvas.bind("<Button-4>", lambda event, c=canvas: self._on_mousewheel(event, c))    # Linux
        canvas.bind("<Button-5>", lambda event, c=canvas: self._on_mousewheel(event, c))    # Linux
        
        # 确保Canvas可以聚焦，以便接收滚轮事件
        canvas.focus_set()
        
        return scrollable_frame, canvas, control_frame
    
    def _on_frame_configure(self, event, canvas):
        """当内容框架大小变化时更新Canvas的滚动区域"""
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def _on_canvas_configure(self, event, canvas, canvas_window):
        """当Canvas大小变化时，调整内容框架的宽度"""
        canvas.itemconfig(canvas_window, width=event.width)
        
    def _on_mousewheel(self, event, canvas):
        """处理鼠标滚轮事件"""
        # 处理Windows滚轮事件
        if hasattr(event, 'delta'):
            # 垂直滚动
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        # 处理Linux滚轮事件
        elif event.num == 4:
            canvas.yview_scroll(-1, "units")  # 向上滚动
        elif event.num == 5:
            canvas.yview_scroll(1, "units")   # 向下滚动
        # 防止事件冒泡
        return "break"
    
    def _add_decorative_elements(self):
        """添加装饰性元素"""
        # 在窗口顶部添加装饰线条
        top_decor = tk.Frame(self.root, height=5, background=self.accent_color)
        top_decor.pack(fill=tk.X)
        
        # 在窗口底部添加装饰线条
        bottom_decor = tk.Frame(self.root, height=5, background=self.accent_color)
        bottom_decor.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 添加状态指示器
        status_frame = ttk.Frame(self.root, style="RetroFrame.TFrame", height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)
        
        self.status_var = tk.StringVar(value="SYSTEM ONLINE // ALL SYSTEMS NOMINAL")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                              style="RetroLabel.TLabel", anchor=tk.W, font=("Courier New", 12, "bold"))
        status_bar.pack(fill=tk.X, padx=20, pady=5)
    
    def _add_cassette_rolls(self, parent_frame):
        """添加磁带卷轴装饰元素"""
        # 创建卷轴容器 - 减小左侧padding，使整体更靠左
        rolls_frame = ttk.Frame(parent_frame, style="RetroFrame.TFrame", height=80)
        rolls_frame.pack(fill=tk.X, padx=(30, 50), pady=5)  # 减小pady增加功能区高度
        
        # 左边卷轴 - 减小x坐标，更靠左
        left_roll_frame = ttk.Frame(rolls_frame, style="RetroPanel.TFrame", width=80, height=80)
        left_roll_frame.place(x=20, y=0)
        left_roll_frame.pack_propagate(False)
        
        left_roll = tk.Canvas(left_roll_frame, width=60, height=60, background=self.bg_color, highlightthickness=0)
        left_roll.pack(expand=True)
        
        # 绘制圆形卷轴
        left_roll.create_oval(10, 10, 50, 50, fill=self.button_color, outline=self.accent_color, width=2)
        left_roll.create_oval(25, 25, 35, 35, fill=self.accent_color, outline=self.accent_color)
        
        # 绘制磁带线
        for i in range(8):
            angle = i * 45
            x = 30 + 15 * math.cos(math.radians(angle))
            y = 30 + 15 * math.sin(math.radians(angle))
            left_roll.create_line(30, 30, x, y, fill=self.accent_color, width=1)
        
        # 右边卷轴
        right_roll_frame = ttk.Frame(rolls_frame, style="RetroPanel.TFrame", width=80, height=80)
        right_roll_frame.place(x=parent_frame.winfo_width() - 150, y=0)  # 增加右侧边距，避免出框
        right_roll_frame.pack_propagate(False)
        
        # 绑定事件，当父窗口大小改变时更新右侧卷轴位置
        parent_frame.bind("<Configure>", lambda e, rf=right_roll_frame, pf=parent_frame: 
                          rf.place(x=pf.winfo_width() - 150, y=0))
        
        right_roll = tk.Canvas(right_roll_frame, width=60, height=60, background=self.bg_color, highlightthickness=0)
        right_roll.pack(expand=True)
        
        # 绘制圆形卷轴
        right_roll.create_oval(10, 10, 50, 50, fill=self.button_color, outline=self.accent_color, width=2)
        right_roll.create_oval(25, 25, 35, 35, fill=self.accent_color, outline=self.accent_color)
        
        # 绘制磁带线
        for i in range(8):
            angle = i * 45
            x = 30 + 15 * math.cos(math.radians(angle))
            y = 30 + 15 * math.sin(math.radians(angle))
            right_roll.create_line(30, 30, x, y, fill=self.accent_color, width=1)
        
        # 绘制连接线
        self.tape_line = ttk.Frame(rolls_frame, height=5, style="RetroAccent.TFrame")
        self.tape_line.place(x=130, y=40, width=parent_frame.winfo_width() - 280)  # 调整连接线宽度计算，配合右侧卷轴位置
        
        # 绑定事件，当父窗口大小改变时更新连接线宽度
        parent_frame.bind("<Configure>", lambda e, tl=self.tape_line, pf=parent_frame: 
                          tl.place(x=130, y=40, width=pf.winfo_width() - 280), add="+")
    
    def _create_encoding_tab(self):
        """创建编码解码标签页"""
        encoding_tab = ttk.Frame(self.notebook, style="RetroFrame.TFrame")
        self.notebook.add(encoding_tab, text="编码解码")
        
        # 使用网格布局重写编码解码标签页，避免控件出框
        encoding_tab.columnconfigure(0, weight=1)
        encoding_tab.columnconfigure(1, weight=1)
        encoding_tab.rowconfigure(0, weight=1)
        encoding_tab.rowconfigure(1, weight=0)
        encoding_tab.rowconfigure(2, weight=0)
        
        # 创建左侧输入区域
        left_frame = ttk.Frame(encoding_tab, style="RetroPanel.TFrame")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # 创建右侧输出区域
        right_frame = ttk.Frame(encoding_tab, style="RetroPanel.TFrame")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # 左侧输入区域 - 使用grid布局
        input_label = ttk.Label(left_frame, text="// 输入数据 //", style="RetroLabel.TLabel")
        input_label.grid(row=0, column=0, sticky="w", pady=(5, 0), padx=10)
        
        # 输入文本框 - 设计成终端风格
        input_term_frame = ttk.Frame(left_frame, style="RetroFrame.TFrame")
        input_term_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        input_term_frame.columnconfigure(0, weight=1)
        input_term_frame.rowconfigure(0, weight=1)
        
        self.input_text = scrolledtext.ScrolledText(input_term_frame, wrap=tk.WORD, 
                                                  bg=self.input_bg, fg=self.fg_color, 
                                                  insertbackground=self.accent_color, 
                                                  font=("Courier New", 10))
        self.input_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 添加装饰性提示符
        self.input_text.insert(tk.END, ">>> ")
        
        # 功能选择区域
        function_frame = ttk.Frame(left_frame, style="RetroPanel.TFrame")
        function_frame.grid(row=2, column=0, sticky="ew", pady=5, padx=10)
        function_frame.columnconfigure(0, weight=1)
        
        # 编码类型选择
        self.encoding_type = tk.StringVar(value="base64_encode")
        
        # 添加复古风格的装饰
        ttk.Label(function_frame, text="// 编码选项 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        
        options_container = ttk.Frame(function_frame, style="RetroFrame.TFrame")
        options_container.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # 创建一个内部框架来管理单选按钮的水平布局
        options_inner = ttk.Frame(options_container)
        options_inner.pack(fill="x", expand=True, padx=5, pady=5)
        
        ttk.Radiobutton(options_inner, text="BASE64 编码", variable=self.encoding_type, 
                       value="base64_encode", style="RetroButton.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Radiobutton(options_inner, text="BASE64 解码", variable=self.encoding_type, 
                       value="base64_decode", style="RetroButton.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Radiobutton(options_inner, text="计算哈希", variable=self.encoding_type, 
                       value="calculate_hash", style="RetroButton.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Radiobutton(options_inner, text="HEX 编码", variable=self.encoding_type, 
                       value="hex_encode", style="RetroButton.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Radiobutton(options_inner, text="HEX 解码", variable=self.encoding_type, 
                       value="hex_decode", style="RetroButton.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        
        # 哈希算法选择
        hash_frame = ttk.Frame(function_frame, style="RetroPanel.TFrame")
        hash_frame.grid(row=2, column=0, sticky="ew", pady=5, padx=10)
        
        hash_container = ttk.Frame(hash_frame)
        hash_container.pack(fill="x", expand=True, padx=5, pady=5)
        
        ttk.Label(hash_container, text="算法:", style="RetroLabel.TLabel").pack(side=tk.LEFT, padx=5, pady=5)
        self.hash_algorithm = ttk.Combobox(hash_container, values=["md5", "sha1", "sha224", "sha256", "sha384", "sha512"],
                                          style="RetroCombobox.TCombobox", width=10)
        self.hash_algorithm.current(0)
        self.hash_algorithm.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 执行按钮 - 复古科技风格
        execute_frame = ttk.Frame(encoding_tab, style="RetroAccent.TFrame")
        execute_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5, padx=10)
        
        execute_btn = ttk.Button(execute_frame, text="[执行编码/解码]", command=self._execute_encoding, 
                                style="RetroButton.TButton")
        execute_btn.pack(fill=tk.X, padx=20, pady=5)
        
        # 右侧输出区域 - 使用grid布局
        output_label = ttk.Label(right_frame, text="// 输出结果 //", style="RetroLabel.TLabel")
        output_label.grid(row=0, column=0, sticky="w", pady=(5, 0), padx=10)
        
        # 输出文本框 - 设计成终端风格
        output_term_frame = ttk.Frame(right_frame, style="RetroFrame.TFrame")
        output_term_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        output_term_frame.columnconfigure(0, weight=1)
        output_term_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_term_frame, wrap=tk.WORD, 
                                                   bg=self.input_bg, fg=self.secondary_color, 
                                                   insertbackground=self.accent_color, 
                                                   font=("Courier New", 10))
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 复制按钮 - 复古科技风格
        copy_frame = ttk.Frame(encoding_tab, style="RetroFrame.TFrame")
        copy_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5, padx=10)
        
        copy_btn = ttk.Button(copy_frame, text="[复制结果]", command=self._copy_result, 
                             style="RetroButton.TButton")
        copy_btn.pack(fill=tk.X, padx=20, pady=5)
    
    def _execute_encoding(self):
        """执行编码解码操作"""
        input_data = self.input_text.get(1.0, tk.END).strip()
        # 移除提示符
        if input_data.startswith(">>> "):
            input_data = input_data[4:]
        
        if not input_data:
            messagebox.showerror("ERROR", "请输入数据")
            return
        
        try:
            function = self.encoding_type.get()
            result = ""
            
            if function == "base64_encode":
                result = self.platform.encode_base64(input_data)
            elif function == "base64_decode":
                result = self.platform.decode_base64(input_data)
            elif function == "calculate_hash":
                algorithm = self.hash_algorithm.get()
                result = self.platform.calculate_hash(input_data, algorithm)
            elif function == "hex_encode":
                result = self.platform.encode_hex(input_data)
            elif function == "hex_decode":
                result = self.platform.decode_hex(input_data)
            
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"[操作结果]\n")
            self.output_text.insert(tk.END, f"[模式: {function}]\n")
            self.output_text.insert(tk.END, f"{'-'*40}\n")
            self.output_text.insert(tk.END, result)
            self.status_var.set(f"OPERATION COMPLETE: {function}")
        except Exception as e:
            messagebox.showerror("ERROR", f"操作失败: {str(e)}")
            self.status_var.set(f"OPERATION FAILED: {str(e)}")
    
    def _copy_result(self):
        """复制结果到剪贴板"""
        result = self.output_text.get(1.0, tk.END).strip()
        if result:
            # 移除装饰文本
            result_lines = result.split('\n')
            if len(result_lines) >= 3:
                result = '\n'.join(result_lines[3:])
            
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.status_var.set("RESULT COPIED TO CLIPBOARD")
    
    def _create_image_tab(self):
        """创建图片处理标签页 - 使用grid布局"""
        image_tab = ttk.Frame(self.notebook, style="RetroFrame.TFrame")
        self.notebook.add(image_tab, text="图片处理")
        
        # 核心布局：左侧控制面板和右侧预览区域
        image_tab.columnconfigure(0, weight=1)  # 增加左侧面板权重
        image_tab.columnconfigure(1, weight=1, minsize=300, uniform="area")  # 缩小右侧预览区域权重并限制最小宽度
        image_tab.columnconfigure(2, weight=0, minsize=100)  # 右侧额外空间占位
        image_tab.rowconfigure(0, weight=1)
        
        # 左侧滚动控制面板
        scrollable_frame, canvas, control_frame = self._create_scrollable_panel(image_tab)
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # 设置控制面板内部grid布局
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(0, weight=0)
        control_frame.rowconfigure(1, weight=0)
        control_frame.rowconfigure(2, weight=0)
        control_frame.rowconfigure(3, weight=0)
        control_frame.rowconfigure(4, weight=0)
        control_frame.rowconfigure(5, weight=0)
        control_frame.rowconfigure(6, weight=0)
        control_frame.rowconfigure(7, weight=0)
        
        # 控制面板标题
        ttk.Label(control_frame, text="// 图片控制面板 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=10, padx=10)
        
        # 文件选择区域
        file_select_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        file_select_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        file_select_frame.columnconfigure(0, weight=1)
        file_select_frame.rowconfigure(0, weight=0)
        file_select_frame.rowconfigure(1, weight=0)
        file_select_frame.rowconfigure(2, weight=0)
        
        ttk.Label(file_select_frame, text="文件路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
        
        self.image_path_var = tk.StringVar()
        ttk.Entry(file_select_frame, textvariable=self.image_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        browse_frame = ttk.Frame(file_select_frame, style="RetroAccent.TFrame")
        browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        browse_frame.columnconfigure(0, weight=1)
        
        ttk.Button(browse_frame, text="[浏览...]", command=self._browse_image, style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 处理功能选择区域 - 横向排版
        function_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        function_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        function_frame.columnconfigure(0, weight=1)
        function_frame.columnconfigure(1, weight=1)
        function_frame.rowconfigure(0, weight=0)
        function_frame.rowconfigure(1, weight=0)
        
        ttk.Label(function_frame, text="处理功能:", style="RetroLabel.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(10, 5), padx=10)
        
        self.image_function = tk.StringVar(value="resize")
        
        # 功能选项 - 横向排列
        functions = [
            ("调整大小", "resize"),
            ("转换格式", "convert"),
            ("灰度转换", "grayscale"),
            ("模糊处理", "blur")
        ]
        
        row, col = 1, 0
        for text, value in functions:
            func_btn_frame = ttk.Frame(function_frame, style="RetroButton.TFrame")
            func_btn_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=2)
            func_btn_frame.columnconfigure(0, weight=1)
            
            ttk.Radiobutton(func_btn_frame, text=f"[ {text} ]", variable=self.image_function, 
                           value=value, style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=2, pady=2)
            
            # 每2个按钮换行
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        # 调整大小参数
        self.resize_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        self.resize_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        self.resize_frame.columnconfigure(0, weight=0)
        self.resize_frame.columnconfigure(1, weight=1)
        self.resize_frame.rowconfigure(0, weight=0)
        self.resize_frame.rowconfigure(1, weight=0)
        
        ttk.Label(self.resize_frame, text="宽度:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        self.width_var = tk.StringVar(value="800")
        ttk.Entry(self.resize_frame, textvariable=self.width_var, style="RetroEntry.TEntry").grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.resize_frame, text="高度:", style="RetroLabel.TLabel").grid(row=1, column=0, sticky="w", pady=5, padx=10)
        self.height_var = tk.StringVar(value="600")
        ttk.Entry(self.resize_frame, textvariable=self.height_var, style="RetroEntry.TEntry").grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # 转换格式参数
        self.format_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        self.format_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        self.format_frame.columnconfigure(0, weight=0)
        self.format_frame.columnconfigure(1, weight=1)
        self.format_frame.rowconfigure(0, weight=0)
        
        ttk.Label(self.format_frame, text="目标格式:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        self.format_var = ttk.Combobox(self.format_frame, values=["png", "jpg", "bmp", "gif"],
                                      style="RetroCombobox.TCombobox")
        self.format_var.current(0)
        self.format_var.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 模糊半径参数
        self.blur_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        self.blur_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
        self.blur_frame.columnconfigure(0, weight=0)
        self.blur_frame.columnconfigure(1, weight=1)
        self.blur_frame.rowconfigure(0, weight=0)
        
        ttk.Label(self.blur_frame, text="模糊半径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        self.blur_radius_var = tk.StringVar(value="2")
        ttk.Entry(self.blur_frame, textvariable=self.blur_radius_var, style="RetroEntry.TEntry").grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 输出路径
        output_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        output_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=5)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=0)
        output_frame.rowconfigure(1, weight=0)
        output_frame.rowconfigure(2, weight=0)
        
        ttk.Label(output_frame, text="输出路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
        
        self.image_output_path_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.image_output_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        output_browse_frame = ttk.Frame(output_frame, style="RetroAccent.TFrame")
        output_browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        output_browse_frame.columnconfigure(0, weight=1)
        
        ttk.Button(output_browse_frame, text="[浏览...]", command=self._browse_image_output, style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 执行按钮
        execute_main_frame = ttk.Frame(control_frame, style="RetroAccent.TFrame")
        execute_main_frame.grid(row=7, column=0, sticky="ew", padx=10, pady=(10, 10))
        execute_main_frame.columnconfigure(0, weight=1)
        
        ttk.Button(execute_main_frame, text="[执行图片处理]", command=self._execute_image_processing, 
                  style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # 右侧预览区域
        preview_frame = ttk.Frame(image_tab, style="RetroFrame.TFrame")
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=0)
        preview_frame.rowconfigure(1, weight=1)
        
        # 预览区域标题
        ttk.Label(preview_frame, text="// 图片预览 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10), padx=10)
        
        # 预览显示器框架
        monitor_frame = ttk.Frame(preview_frame, style="RetroPanel.TFrame", relief=tk.RAISED, borderwidth=3)
        monitor_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        monitor_frame.columnconfigure(0, weight=1)
        monitor_frame.rowconfigure(0, weight=0)
        monitor_frame.rowconfigure(1, weight=1)
        
        # 显示器装饰
        monitor_top = ttk.Frame(monitor_frame, height=20, style="RetroFrame.TFrame")
        monitor_top.grid(row=0, column=0, sticky="ew")
        
        # 图片显示Canvas
        self.preview_canvas = tk.Canvas(monitor_frame, bg=self.bg_color, highlightthickness=0)
        self.preview_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # 初始化预览信息文本
        self.preview_info = tk.StringVar(value="// 请选择图片文件以预览")
        self.preview_info_label = ttk.Label(self.preview_canvas, textvariable=self.preview_info, 
                                          style="RetroLabel.TLabel", wraplength=400)
        self.preview_canvas.create_window(200, 100, window=self.preview_info_label)
        
        # 存储当前预览的图片对象（防止被垃圾回收）
        self.preview_image = None
        
        # 绑定Canvas大小变化事件
        self.preview_canvas.bind("<Configure>", self._on_preview_resize)
    
    def _browse_image(self):
        """浏览选择图片文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            self.image_path_var.set(file_path)
            
            # 如果没有设置输出路径，自动生成
            if not self.image_output_path_var.get():
                base_name, ext = os.path.splitext(file_path)
                self.image_output_path_var.set(f"{base_name}_processed{ext}")
            
            # 加载并显示图片
            self._display_preview_image(file_path)
    
    def _browse_image_output(self):
        """浏览选择图片输出路径"""
        # 根据选择的功能确定文件类型
        function = self.image_function.get()
        file_types = [("所有文件", "*.*")]
        
        if function == "convert":
            format_type = self.format_var.get()
            file_types = [(f"{format_type.upper()}文件", f"*.{format_type}")]
        elif function == "resize":
            file_types = [("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        
        file_path = filedialog.asksaveasfilename(filetypes=file_types)
        if file_path:
            self.image_output_path_var.set(file_path)
    
    def _execute_image_processing(self):
        """执行图片处理"""
        image_path = self.image_path_var.get()
        output_path = self.image_output_path_var.get()
        
        if not image_path or not os.path.exists(image_path):
            messagebox.showerror("ERROR", "请选择有效的图片文件")
            return
        
        try:
            function = self.image_function.get()
            result = ""
            
            if function == "resize":
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                result = self.platform.resize_image(image_path, width, height, output_path)
            elif function == "convert":
                format_type = self.format_var.get()
                result = self.platform.convert_image_format(image_path, format_type, output_path)
            elif function == "grayscale":
                result = self.platform.grayscale_image(image_path, output_path)
            elif function == "blur":
                radius = int(self.blur_radius_var.get())
                result = self.platform.blur_image(image_path, radius, output_path)
            
            messagebox.showinfo("SUCCESS", result)
            self.status_var.set(f"IMAGE PROCESSING COMPLETE: {result}")
        except Exception as e:
            messagebox.showerror("ERROR", f"图片处理失败: {str(e)}")
            self.status_var.set(f"IMAGE PROCESSING FAILED: {str(e)}")
    
    def _display_preview_image(self, image_path):
        """显示预览图片"""
        try:
            if Image is None:
                self.preview_info.set(f"// 错误：Pillow库未安装，无法显示图片预览\n// 已选择图片: {image_path}")
                return
            
            # 清除Canvas上的所有内容
            self.preview_canvas.delete("all")
            
            # 使用PIL加载图片
            img = Image.open(image_path)
            
            # 获取图片原始尺寸
            img_width, img_height = img.size
            
            # 获取Canvas尺寸
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # 如果Canvas还没有实际尺寸，使用默认值
            if canvas_width < 10:  # 防止初始宽度为0
                canvas_width = 400
                canvas_height = 300
            
            # 计算缩放比例，保持宽高比
            scale = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # 调整图片大小
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # 将PIL图片转换为Tkinter可用的PhotoImage
            # 对于JPG等格式，需要使用PhotoImage的不同方法
            img_format = img.format.lower()
            
            if img_format == 'png':
                # PNG格式可以直接转换
                self.preview_image = ImageTk.PhotoImage(resized_img)
            else:
                # 对于其他格式，使用临时缓冲区
                buffer = BytesIO()
                resized_img.save(buffer, format="PNG")
                buffer.seek(0)
                self.preview_image = ImageTk.PhotoImage(data=buffer.read())
            
            # 在Canvas上显示图片，居中显示
            x_pos = (canvas_width - new_width) // 2
            y_pos = (canvas_height - new_height) // 2
            self.preview_canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=self.preview_image)
            
            # 添加复古风格的扫描线效果
            for y in range(0, new_height, 4):
                self.preview_canvas.create_line(x_pos, y_pos + y, x_pos + new_width, y_pos + y, 
                                              fill="#ff7f2a", width=1, stipple="gray50")
            
            # 显示图片信息
            info_text = f"// 文件: {os.path.basename(image_path)}\n// 原始尺寸: {img_width}x{img_height}\n// 预览尺寸: {new_width}x{new_height}"
            self.preview_info.set(info_text)
            
            # 创建信息标签，放在左上角
            info_frame = ttk.Frame(self.preview_canvas, style="RetroFrame.TFrame", padding=5)
            self.preview_canvas.create_window(10, 10, window=info_frame, anchor=tk.NW)
            
            ttk.Label(info_frame, textvariable=self.preview_info, style="RetroLabel.TLabel").pack(anchor=tk.W)
            
        except Exception as e:
            self.preview_info.set(f"// 加载图片失败: {str(e)}\n// 文件: {image_path}")
            self.preview_canvas.delete("all")
            
            error_frame = ttk.Frame(self.preview_canvas, style="RetroFrame.TFrame", padding=10)
            self.preview_canvas.create_window(canvas_width//2, canvas_height//2, window=error_frame, anchor=tk.CENTER)
            
            ttk.Label(error_frame, textvariable=self.preview_info, style="RetroWarning.TLabel").pack(anchor=tk.W)
            
    def _on_preview_resize(self, event):
        """预览窗口大小变化时重新调整图片大小"""
        # 获取当前选择的图片路径
        image_path = self.image_path_var.get()
        
        # 如果已有选择的图片，重新显示预览
        if image_path and os.path.exists(image_path):
            self._display_preview_image(image_path)
    
    def _create_audio_tab(self):
        """创建音频处理标签页 - 使用grid布局"""
        audio_tab = ttk.Frame(self.notebook, style="RetroFrame.TFrame")
        self.notebook.add(audio_tab, text="音频处理")
        
        # 核心布局权重配置
        audio_tab.columnconfigure(0, weight=1)  # 增加左侧面板权重
        audio_tab.columnconfigure(1, weight=1, minsize=300, uniform="area")  # 缩小右侧信息区域权重并限制最小宽度
        audio_tab.columnconfigure(2, weight=0, minsize=100)  # 右侧额外空间占位
        audio_tab.rowconfigure(0, weight=1)
        
        # 创建左侧滚动控制面板
        scrollable_frame, canvas, control_frame = self._create_scrollable_panel(audio_tab)
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # 创建右侧信息/输出区域
        info_frame = ttk.Frame(audio_tab, style="RetroFrame.TFrame")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=0)
        info_frame.rowconfigure(1, weight=1)


        
        # 设置控制面板内部grid布局
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(0, weight=0)
        control_frame.rowconfigure(1, weight=0)
        control_frame.rowconfigure(2, weight=0)
        control_frame.rowconfigure(3, weight=0)
        control_frame.rowconfigure(4, weight=0)
        control_frame.rowconfigure(5, weight=0)
        control_frame.rowconfigure(6, weight=0)
        
        # 添加控制面板标题
        ttk.Label(control_frame, text="// 音频控制面板 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=10, padx=10)
        
        # 文件选择区域 - 复古科技风格
        file_select_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        file_select_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        file_select_frame.columnconfigure(0, weight=1)
        file_select_frame.rowconfigure(0, weight=0)
        file_select_frame.rowconfigure(1, weight=0)
        file_select_frame.rowconfigure(2, weight=0)
        
        ttk.Label(file_select_frame, text="文件路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
        
        self.audio_path_var = tk.StringVar()
        ttk.Entry(file_select_frame, textvariable=self.audio_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        browse_frame = ttk.Frame(file_select_frame, style="RetroAccent.TFrame")
        browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        browse_frame.columnconfigure(0, weight=1)
        
        ttk.Button(browse_frame, text="[浏览...]", command=self._browse_audio, style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 获取信息按钮
        info_btn_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        info_btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        info_btn_frame.columnconfigure(0, weight=1)
        
        ttk.Button(info_btn_frame, text="[获取音频信息]", command=self._get_audio_info, 
                  style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # 处理功能选择区域 - 横向排版
        function_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        function_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        function_frame.columnconfigure(0, weight=1)
        function_frame.columnconfigure(1, weight=1)
        function_frame.rowconfigure(0, weight=0)
        function_frame.rowconfigure(1, weight=0)
        
        ttk.Label(function_frame, text="处理功能:", style="RetroLabel.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(10, 5), padx=10)
        
        self.audio_function = tk.StringVar(value="convert")
        
        # 功能选项 - 横向排列
        functions = [
            ("转换格式", "convert"),
            ("改变速度", "speed")
        ]
        
        row, col = 1, 0
        for text, value in functions:
            func_btn_frame = ttk.Frame(function_frame, style="RetroButton.TFrame")
            func_btn_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=2)
            func_btn_frame.columnconfigure(0, weight=1)
            
            ttk.Radiobutton(func_btn_frame, text=f"[ {text} ]", variable=self.audio_function, 
                           value=value, style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=2, pady=2)
            col += 1
        
        # 转换格式参数
        self.audio_format_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        self.audio_format_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        self.audio_format_frame.columnconfigure(0, weight=0)
        self.audio_format_frame.columnconfigure(1, weight=1)
        self.audio_format_frame.rowconfigure(0, weight=0)
        
        ttk.Label(self.audio_format_frame, text="目标格式:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        self.audio_format_var = ttk.Combobox(self.audio_format_frame, values=["wav", "mp3", "flac", "ogg"],
                                           style="RetroCombobox.TCombobox")
        self.audio_format_var.current(0)
        self.audio_format_var.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 速度调整参数
        self.speed_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        self.speed_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
        self.speed_frame.columnconfigure(0, weight=0)
        self.speed_frame.columnconfigure(1, weight=1)
        self.speed_frame.rowconfigure(0, weight=0)
        
        ttk.Label(self.speed_frame, text="速度因子:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        self.speed_factor_var = tk.StringVar(value="1.5")
        ttk.Entry(self.speed_frame, textvariable=self.speed_factor_var, style="RetroEntry.TEntry").grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 输出路径
        output_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        output_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=5)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=0)
        output_frame.rowconfigure(1, weight=0)
        output_frame.rowconfigure(2, weight=0)
        
        ttk.Label(output_frame, text="输出路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
        
        self.audio_output_path_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.audio_output_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        output_browse_frame = ttk.Frame(output_frame, style="RetroAccent.TFrame")
        output_browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        output_browse_frame.columnconfigure(0, weight=1)
        
        ttk.Button(output_browse_frame, text="[浏览...]", command=self._browse_audio_output, style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 执行按钮
        execute_main_frame = ttk.Frame(control_frame, style="RetroAccent.TFrame")
        execute_main_frame.grid(row=7, column=0, sticky="ew", padx=10, pady=(10, 0))
        execute_main_frame.columnconfigure(0, weight=1)
        
        ttk.Button(execute_main_frame, text="[执行音频处理]", command=self._execute_audio_processing, 
                  style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # 设置控制面板内部grid布局
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(0, weight=0)
        control_frame.rowconfigure(1, weight=0)
        control_frame.rowconfigure(2, weight=0)
        control_frame.rowconfigure(3, weight=0)
        control_frame.rowconfigure(4, weight=0)
        control_frame.rowconfigure(5, weight=0)
        control_frame.rowconfigure(6, weight=0)
        control_frame.rowconfigure(7, weight=0)
        
        # 添加底部间距
        ttk.Label(control_frame).grid(row=8, column=0, pady=10)
        
        # 音频信息显示区域
        ttk.Label(info_frame, text="// 音频信息 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10), padx=10)
        
        # 创建信息显示终端
        info_term_frame = ttk.Frame(info_frame, style="RetroPanel.TFrame", relief=tk.SUNKEN)
        info_term_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        info_term_frame.columnconfigure(0, weight=1)
        info_term_frame.rowconfigure(0, weight=1)
        
        self.audio_info_text = scrolledtext.ScrolledText(info_term_frame, wrap=tk.WORD, 
                                                        bg=self.input_bg, fg=self.secondary_color, 
                                                        insertbackground=self.accent_color, 
                                                        font=("Courier New", 10))
        self.audio_info_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.audio_info_text.insert(tk.END, "// 请选择音频文件并点击'获取音频信息'")
        self.audio_info_text.config(state=tk.DISABLED)
    
    def _browse_audio(self):
        """浏览选择音频文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("音频文件", "*.wav;*.mp3;*.flac;*.ogg")]
        )
        if file_path:
            self.audio_path_var.set(file_path)
            
            # 如果没有设置输出路径，自动生成
            if not self.audio_output_path_var.get():
                base_name, ext = os.path.splitext(file_path)
                self.audio_output_path_var.set(f"{base_name}_processed{ext}")
    
    def _browse_audio_output(self):
        """浏览选择音频输出路径"""
        # 根据选择的功能确定文件类型
        function = self.audio_function.get()
        file_types = [("所有文件", "*.*")]
        
        if function == "convert":
            format_type = self.audio_format_var.get()
            file_types = [(f"{format_type.upper()}文件", f"*.{format_type}")]
        elif function == "speed":
            file_types = [("WAV文件", "*.wav")]
        
        file_path = filedialog.asksaveasfilename(filetypes=file_types)
        if file_path:
            self.audio_output_path_var.set(file_path)
    
    def _get_audio_info(self):
        """获取音频信息"""
        audio_path = self.audio_path_var.get()
        
        if not audio_path or not os.path.exists(audio_path):
            messagebox.showerror("ERROR", "请选择有效的音频文件")
            return
        
        try:
            info = self.platform.get_audio_info(audio_path)
            
            self.audio_info_text.config(state=tk.NORMAL)
            self.audio_info_text.delete(1.0, tk.END)
            self.audio_info_text.insert(tk.END, "// 音频文件分析结果\n")
            self.audio_info_text.insert(tk.END, f"// 文件名: {os.path.basename(audio_path)}\n")
            self.audio_info_text.insert(tk.END, f"{'-'*50}\n")
            
            if isinstance(info, dict):
                for key, value in info.items():
                    self.audio_info_text.insert(tk.END, f"// {key}: {value}\n")
            else:
                self.audio_info_text.insert(tk.END, str(info))
            
            self.audio_info_text.config(state=tk.DISABLED)
            self.status_var.set(f"AUDIO INFO RETRIEVED SUCCESSFULLY")
        except Exception as e:
            messagebox.showerror("ERROR", f"获取音频信息失败: {str(e)}")
            self.status_var.set(f"AUDIO INFO RETRIEVAL FAILED: {str(e)}")
    
    def _execute_audio_processing(self):
        """执行音频处理"""
        audio_path = self.audio_path_var.get()
        output_path = self.audio_output_path_var.get()
        
        if not audio_path or not os.path.exists(audio_path):
            messagebox.showerror("ERROR", "请选择有效的音频文件")
            return
        
        if not output_path:
            messagebox.showerror("ERROR", "请设置输出路径")
            return
        
        try:
            function = self.audio_function.get()
            result = ""
            
            if function == "convert":
                format_type = self.audio_format_var.get()
                result = self.platform.convert_audio_format(audio_path, format_type, output_path)
            elif function == "speed":
                speed_factor = float(self.speed_factor_var.get())
                result = self.platform.change_audio_speed(audio_path, speed_factor, output_path)
            
            messagebox.showinfo("SUCCESS", result)
            self.status_var.set(f"AUDIO PROCESSING COMPLETE: {result}")
        except Exception as e:
            messagebox.showerror("ERROR", f"音频处理失败: {str(e)}")
            self.status_var.set(f"AUDIO PROCESSING FAILED: {str(e)}")
    
    def _create_video_tab(self):
        """创建视频处理标签页 - 使用grid布局"""
        video_tab = ttk.Frame(self.notebook, style="RetroFrame.TFrame")
        self.notebook.add(video_tab, text="视频处理")
        
        # 核心布局权重配置
        video_tab.columnconfigure(0, weight=1)  # 增加左侧面板权重
        video_tab.columnconfigure(1, weight=1, minsize=300, uniform="area")  # 缩小右侧信息区域权重并限制最小宽度
        video_tab.columnconfigure(2, weight=0, minsize=100)  # 右侧额外空间占位
        video_tab.rowconfigure(0, weight=1)
        
        # 创建左侧滚动控制面板
        scrollable_frame, canvas, control_frame = self._create_scrollable_panel(video_tab)
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # 创建右侧信息/输出区域
        info_frame = ttk.Frame(video_tab, style="RetroFrame.TFrame")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=0)
        info_frame.rowconfigure(1, weight=1)
        
        # 设置控制面板内部grid布局
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(0, weight=0)
        control_frame.rowconfigure(1, weight=0)
        control_frame.rowconfigure(2, weight=0)
        control_frame.rowconfigure(3, weight=0)
        control_frame.rowconfigure(4, weight=0)
        control_frame.rowconfigure(5, weight=0)
        control_frame.rowconfigure(6, weight=0)
        
        # 添加控制面板标题
        ttk.Label(control_frame, text="// 视频控制面板 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=10, padx=10)
        
        # 文件选择区域 - 复古科技风格
        file_select_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        file_select_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        file_select_frame.columnconfigure(0, weight=1)
        file_select_frame.rowconfigure(0, weight=0)
        file_select_frame.rowconfigure(1, weight=0)
        file_select_frame.rowconfigure(2, weight=0)
        
        ttk.Label(file_select_frame, text="文件路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
        
        self.video_path_var = tk.StringVar()
        ttk.Entry(file_select_frame, textvariable=self.video_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        browse_frame = ttk.Frame(file_select_frame, style="RetroAccent.TFrame")
        browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        browse_frame.columnconfigure(0, weight=1)
        
        ttk.Button(browse_frame, text="[浏览...]", command=self._browse_video, style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 获取信息按钮
        info_btn_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        info_btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        info_btn_frame.columnconfigure(0, weight=1)
        
        ttk.Button(info_btn_frame, text="[获取视频信息]", command=self._get_video_info, 
                  style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # 处理功能选择区域 - 横向排版
        function_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        function_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        function_frame.columnconfigure(0, weight=1)
        function_frame.columnconfigure(1, weight=1)
        function_frame.rowconfigure(0, weight=0)
        function_frame.rowconfigure(1, weight=0)
        
        ttk.Label(function_frame, text="处理功能:", style="RetroLabel.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(10, 5), padx=10)
        
        self.video_function = tk.StringVar(value="extract_audio")
        
        # 功能选项 - 横向排列
        functions = [
            ("提取音频", "extract_audio"),
            ("裁剪视频", "trim")
        ]
        
        row, col = 1, 0
        for text, value in functions:
            func_btn_frame = ttk.Frame(function_frame, style="RetroButton.TFrame")
            func_btn_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=2)
            func_btn_frame.columnconfigure(0, weight=1)
            
            ttk.Radiobutton(func_btn_frame, text=f"[ {text} ]", variable=self.video_function, 
                           value=value, style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=2, pady=2)
            col += 1
            
        # 裁剪参数
        self.trim_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        self.trim_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        self.trim_frame.columnconfigure(0, weight=0)
        self.trim_frame.columnconfigure(1, weight=1)
        self.trim_frame.rowconfigure(0, weight=0)
        self.trim_frame.rowconfigure(1, weight=0)
        
        ttk.Label(self.trim_frame, text="开始时间(秒):", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        self.start_time_var = tk.StringVar(value="0")
        ttk.Entry(self.trim_frame, textvariable=self.start_time_var, style="RetroEntry.TEntry").grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.trim_frame, text="结束时间(秒):", style="RetroLabel.TLabel").grid(row=1, column=0, sticky="w", pady=5, padx=10)
        self.end_time_var = tk.StringVar(value="10")
        ttk.Entry(self.trim_frame, textvariable=self.end_time_var, style="RetroEntry.TEntry").grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # 输出路径
        output_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        output_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=0)
        output_frame.rowconfigure(1, weight=0)
        output_frame.rowconfigure(2, weight=0)
        
        ttk.Label(output_frame, text="输出路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
        
        self.video_output_path_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.video_output_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        output_browse_frame = ttk.Frame(output_frame, style="RetroAccent.TFrame")
        output_browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        output_browse_frame.columnconfigure(0, weight=1)
        
        ttk.Button(output_browse_frame, text="[浏览...]", command=self._browse_video_output, style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 执行按钮
        execute_main_frame = ttk.Frame(control_frame, style="RetroAccent.TFrame")
        execute_main_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=(10, 0))
        execute_main_frame.columnconfigure(0, weight=1)
        
        ttk.Button(execute_main_frame, text="[执行视频处理]", command=self._execute_video_processing, 
                  style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # 确保Canvas可以聚焦，以便接收滚轮事件
        canvas.focus_set()
        
        # 设置控制面板内部grid布局
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(0, weight=0)
        control_frame.rowconfigure(1, weight=0)
        control_frame.rowconfigure(2, weight=0)
        control_frame.rowconfigure(3, weight=0)
        control_frame.rowconfigure(4, weight=0)
        control_frame.rowconfigure(5, weight=0)
        control_frame.rowconfigure(6, weight=0)
        control_frame.rowconfigure(7, weight=0)
        
        # 添加底部间距
        ttk.Label(control_frame).grid(row=8, column=0, pady=10)
        control_frame.grid_propagate(True)
        
        # 视频信息显示区域
        ttk.Label(info_frame, text="// 视频信息 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10), padx=10)
        
        # 创建信息显示终端
        info_term_frame = ttk.Frame(info_frame, style="RetroPanel.TFrame", relief=tk.SUNKEN)
        info_term_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        info_term_frame.columnconfigure(0, weight=1)
        info_term_frame.rowconfigure(0, weight=1)
        
        self.video_info_text = scrolledtext.ScrolledText(info_term_frame, wrap=tk.WORD, 
                                                        bg=self.input_bg, fg=self.secondary_color, 
                                                        insertbackground=self.accent_color, 
                                                        font=("Courier New", 10))
        self.video_info_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.video_info_text.insert(tk.END, "// 请选择视频文件并点击'获取视频信息'")
        self.video_info_text.config(state=tk.DISABLED)
    
    def _browse_video(self):
        """浏览选择视频文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("视频文件", "*.mp4;*.avi;*.mov;*.mkv")]
        )
        if file_path:
            self.video_path_var.set(file_path)
            
            # 如果没有设置输出路径，自动生成
            if not self.video_output_path_var.get():
                base_name, ext = os.path.splitext(file_path)
                self.video_output_path_var.set(f"{base_name}_processed.mp3")  # 默认提取音频为mp3
    
    def _browse_video_output(self):
        """浏览选择视频输出路径"""
        # 根据选择的功能确定文件类型
        function = self.video_function.get()
        file_types = [("所有文件", "*.*")]
        
        if function == "extract_audio":
            file_types = [("MP3文件", "*.mp3")]
        elif function == "trim":
            file_types = [("MP4文件", "*.mp4")]
        
        file_path = filedialog.asksaveasfilename(filetypes=file_types)
        if file_path:
            self.video_output_path_var.set(file_path)
    
    def _get_video_info(self):
        """获取视频信息"""
        video_path = self.video_path_var.get()
        
        if not video_path or not os.path.exists(video_path):
            messagebox.showerror("ERROR", "请选择有效的视频文件")
            return
        
        try:
            info = self.platform.get_video_info(video_path)
            
            self.video_info_text.config(state=tk.NORMAL)
            self.video_info_text.delete(1.0, tk.END)
            self.video_info_text.insert(tk.END, "// 视频文件分析结果\n")
            self.video_info_text.insert(tk.END, f"// 文件名: {os.path.basename(video_path)}\n")
            self.video_info_text.insert(tk.END, f"{'-'*50}\n")
            
            if isinstance(info, dict):
                for key, value in info.items():
                    self.video_info_text.insert(tk.END, f"// {key}: {value}\n")
            else:
                self.video_info_text.insert(tk.END, str(info))
            
            self.video_info_text.config(state=tk.DISABLED)
            self.status_var.set(f"VIDEO INFO RETRIEVED SUCCESSFULLY")
        except Exception as e:
            messagebox.showerror("ERROR", f"获取视频信息失败: {str(e)}")
            self.status_var.set(f"VIDEO INFO RETRIEVAL FAILED: {str(e)}")
    
    def _execute_video_processing(self):
        """执行视频处理"""
        video_path = self.video_path_var.get()
        output_path = self.video_output_path_var.get()
        
        if not video_path or not os.path.exists(video_path):
            messagebox.showerror("ERROR", "请选择有效的视频文件")
            return
        
        if not output_path:
            messagebox.showerror("ERROR", "请设置输出路径")
            return
        
        try:
            function = self.video_function.get()
            result = ""
            
            if function == "extract_audio":
                result = self.platform.extract_audio_from_video(video_path, output_path)
            elif function == "trim":
                start_time = float(self.start_time_var.get())
                end_time = float(self.end_time_var.get())
                result = self.platform.trim_video(video_path, start_time, end_time, output_path)
            
            messagebox.showinfo("SUCCESS", result)
            self.status_var.set(f"VIDEO PROCESSING COMPLETE: {result}")
        except Exception as e:
            messagebox.showerror("ERROR", f"视频处理失败: {str(e)}")
            self.status_var.set(f"VIDEO PROCESSING FAILED: {str(e)}")
    
    def _create_text_tab(self):
        """创建文本处理标签页 - 使用grid布局"""
        text_tab = ttk.Frame(self.notebook, style="RetroFrame.TFrame")
        self.notebook.add(text_tab, text="文本处理")
        
        # 设置grid权重以适应窗口大小变化
        text_tab.columnconfigure(0, weight=1)
        text_tab.columnconfigure(1, weight=1)
        text_tab.rowconfigure(0, weight=1)
        
        # 创建左侧输入区域
        left_frame = ttk.Frame(text_tab, style="RetroPanel.TFrame")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=0)
        left_frame.rowconfigure(1, weight=1)
        left_frame.rowconfigure(2, weight=0)
        left_frame.rowconfigure(3, weight=0)
        
        # 创建右侧输出区域
        right_frame = ttk.Frame(text_tab, style="RetroPanel.TFrame")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=0)
        right_frame.rowconfigure(1, weight=1)
        right_frame.rowconfigure(2, weight=0)
        
        # 左侧输入区域
        input_label = ttk.Label(left_frame, text="// 输入文本 //", style="RetroLabel.TLabel")
        input_label.grid(row=0, column=0, sticky="w", pady=(0, 5), padx=10)
        
        # 输入文本框 - 设计成终端风格
        input_term_frame = ttk.Frame(left_frame, style="RetroFrame.TFrame")
        input_term_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        input_term_frame.columnconfigure(0, weight=1)
        input_term_frame.rowconfigure(0, weight=1)
        
        self.text_input = scrolledtext.ScrolledText(input_term_frame, wrap=tk.WORD, 
                                                  bg=self.input_bg, fg=self.fg_color, 
                                                  insertbackground=self.accent_color, 
                                                  font=("Courier New", 10),
                                                  borderwidth=2, relief=tk.SUNKEN, 
                                                  highlightbackground=self.border_color)
        self.text_input.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 文本处理选项
        options_frame = ttk.Frame(left_frame, style="RetroPanel.TFrame")
        options_frame.grid(row=2, column=0, sticky="ew", pady=10, padx=10)
        options_frame.columnconfigure(0, weight=1)
        options_frame.rowconfigure(0, weight=0)
        options_frame.rowconfigure(1, weight=0)
        options_frame.rowconfigure(2, weight=0)
        
        # 统计功能
        stats_frame = ttk.Frame(options_frame, style="RetroFrame.TFrame")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=0)
        stats_frame.rowconfigure(1, weight=0)
        
        ttk.Label(stats_frame, text="// 统计功能 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        
        stats_check_frame = ttk.Frame(stats_frame, style="RetroPanel.TFrame")
        stats_check_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        stats_check_frame.columnconfigure(0, weight=1)
        stats_check_frame.columnconfigure(1, weight=1)
        stats_check_frame.columnconfigure(2, weight=1)
        
        self.count_words_var = tk.BooleanVar(value=False)
        self.count_chars_var = tk.BooleanVar(value=False)
        self.count_lines_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(stats_check_frame, text="[单词数]", variable=self.count_words_var, style="RetroButton.TButton").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(stats_check_frame, text="[字符数]", variable=self.count_chars_var, style="RetroButton.TButton").grid(row=0, column=1, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(stats_check_frame, text="[行数]", variable=self.count_lines_var, style="RetroButton.TButton").grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        # 提取功能
        extract_frame = ttk.Frame(options_frame, style="RetroFrame.TFrame")
        extract_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        extract_frame.columnconfigure(0, weight=1)
        extract_frame.rowconfigure(0, weight=0)
        extract_frame.rowconfigure(1, weight=0)
        
        ttk.Label(extract_frame, text="// 提取功能 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        
        extract_check_frame = ttk.Frame(extract_frame, style="RetroPanel.TFrame")
        extract_check_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        extract_check_frame.columnconfigure(0, weight=1)
        extract_check_frame.columnconfigure(1, weight=1)
        
        self.extract_emails_var = tk.BooleanVar(value=False)
        self.extract_urls_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(extract_check_frame, text="[邮箱]", variable=self.extract_emails_var, style="RetroButton.TButton").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(extract_check_frame, text="[URL]", variable=self.extract_urls_var, style="RetroButton.TButton").grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # JSON转换功能
        json_frame = ttk.Frame(options_frame, style="RetroFrame.TFrame")
        json_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        json_frame.columnconfigure(0, weight=1)
        json_frame.rowconfigure(0, weight=0)
        json_frame.rowconfigure(1, weight=0)
        
        ttk.Label(json_frame, text="// 转换功能 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        
        json_check_frame = ttk.Frame(json_frame, style="RetroPanel.TFrame")
        json_check_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        json_check_frame.columnconfigure(0, weight=1)
        json_check_frame.columnconfigure(1, weight=0)
        json_check_frame.columnconfigure(2, weight=0)
        
        self.convert_json_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(json_check_frame, text="[转JSON]", variable=self.convert_json_var, style="RetroButton.TButton").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(json_check_frame, text="键名:", style="RetroLabel.TLabel").grid(row=0, column=1, sticky="w", padx=10, pady=5)
        self.json_key_var = tk.StringVar(value="text")
        ttk.Entry(json_check_frame, textvariable=self.json_key_var, style="RetroEntry.TEntry", width=10).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # 执行按钮 - 复古科技风格
        execute_frame = ttk.Frame(left_frame, style="RetroAccent.TFrame")
        execute_frame.grid(row=3, column=0, sticky="ew", pady=10, padx=10)
        execute_frame.columnconfigure(0, weight=1)
        
        execute_btn = ttk.Button(execute_frame, text="[执行文本处理]", command=self._execute_text_processing, 
                                style="RetroButton.TButton")
        execute_btn.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 右侧输出区域
        output_label = ttk.Label(right_frame, text="// 处理结果 //", style="RetroLabel.TLabel")
        output_label.grid(row=0, column=0, sticky="w", pady=(0, 5), padx=10)
        
        # 输出文本框 - 设计成终端风格
        output_term_frame = ttk.Frame(right_frame, style="RetroFrame.TFrame")
        output_term_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        output_term_frame.columnconfigure(0, weight=1)
        output_term_frame.rowconfigure(0, weight=1)
        
        self.text_output = scrolledtext.ScrolledText(output_term_frame, wrap=tk.WORD, 
                                                   bg=self.input_bg, fg=self.secondary_color, 
                                                   insertbackground=self.accent_color, 
                                                   font=("Courier New", 10),
                                                   borderwidth=2, relief=tk.SUNKEN, 
                                                   highlightbackground=self.border_color)
        self.text_output.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 复制按钮 - 复古科技风格
        copy_frame = ttk.Frame(right_frame, style="RetroFrame.TFrame")
        copy_frame.grid(row=2, column=0, sticky="ew", pady=10, padx=10)
        
        copy_btn = ttk.Button(copy_frame, text="[复制结果]", command=self._copy_text_result, 
                             style="RetroButton.TButton")
        copy_btn.pack(fill=tk.X, padx=5, pady=5)
    
    def _execute_text_processing(self):
        """执行文本处理"""
        input_text = self.text_input.get(1.0, tk.END).strip()
        
        if not input_text:
            messagebox.showerror("ERROR", "请输入文本")
            return
        
        try:
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, "// 文本处理结果\n")
            self.text_output.insert(tk.END, f"{'-'*50}\n")
            
            # 统计功能
            if self.count_words_var.get():
                word_count = self.platform.count_words(input_text)
                self.text_output.insert(tk.END, f"// 单词数: {word_count}\n")
            
            if self.count_chars_var.get():
                char_count = self.platform.count_chars(input_text)
                self.text_output.insert(tk.END, f"// 字符数: {char_count}\n")
            
            if self.count_lines_var.get():
                line_count = self.platform.count_lines(input_text)
                self.text_output.insert(tk.END, f"// 行数: {line_count}\n")
            
            # 添加分隔线
            if self.count_words_var.get() or self.count_chars_var.get() or self.count_lines_var.get():
                self.text_output.insert(tk.END, f"{'-'*50}\n")
            
            # 提取功能
            if self.extract_emails_var.get():
                emails = self.platform.extract_emails(input_text)
                if emails:
                    self.text_output.insert(tk.END, "// 提取的邮箱地址:\n")
                    for email in emails:
                        self.text_output.insert(tk.END, f"// - {email}\n")
                else:
                    self.text_output.insert(tk.END, "// 未找到邮箱地址\n")
            
            if self.extract_urls_var.get():
                urls = self.platform.extract_urls(input_text)
                if urls:
                    self.text_output.insert(tk.END, "// 提取的URL:\n")
                    # 处理URL格式，移除可能的额外信息
                    unique_urls = set()
                    for url_parts in urls:
                        if url_parts and isinstance(url_parts, tuple) and url_parts[0]:
                            base_url = url_parts[0]
                            # 尝试重建完整URL
                            if 'http' not in base_url:
                                base_url = 'https://' + base_url
                            unique_urls.add(base_url)
                    
                    for url in unique_urls:
                        self.text_output.insert(tk.END, f"// - {url}\n")
                else:
                    self.text_output.insert(tk.END, "// 未找到URL\n")
            
            # 添加分隔线
            if self.extract_emails_var.get() or self.extract_urls_var.get():
                self.text_output.insert(tk.END, f"{'-'*50}\n")
            
            # JSON转换功能
            if self.convert_json_var.get():
                key_name = self.json_key_var.get() or "text"
                json_result = self.platform.text_to_json(input_text, key_name)
                self.text_output.insert(tk.END, "// JSON格式:\n")
                self.text_output.insert(tk.END, f"{json_result}\n")
            
            self.text_output.insert(tk.END, f"{'-'*50}\n")
            self.text_output.insert(tk.END, "// 处理完成\n")
            self.status_var.set(f"TEXT PROCESSING COMPLETE")
        except Exception as e:
            messagebox.showerror("ERROR", f"文本处理失败: {str(e)}")
            self.status_var.set(f"TEXT PROCESSING FAILED: {str(e)}")
    
    def _copy_text_result(self):
        """复制文本处理结果到剪贴板"""
        result = self.text_output.get(1.0, tk.END).strip()
        if result:
            # 移除装饰文本
            result_lines = result.split('\n')
            clean_result = []
            for line in result_lines:
                if line.startswith("// "):
                    clean_result.append(line[3:])
                elif line.startswith("-"):
                    continue
                else:
                    clean_result.append(line)
            
            clean_result = '\n'.join(clean_result)
            
            self.root.clipboard_clear()
            self.root.clipboard_append(clean_result)
            self.status_var.set("TEXT RESULT COPIED TO CLIPBOARD")
    
    def _create_file_tab(self):
        """创建文件处理标签页 - 使用grid布局"""
        file_tab = ttk.Frame(self.notebook, style="RetroFrame.TFrame")
        self.notebook.add(file_tab, text="文件处理")

        # 核心布局权重配置
        file_tab.columnconfigure(0, weight=1)  # 增加左侧面板权重
        file_tab.columnconfigure(1, weight=1, minsize=300, uniform="area")  # 缩小右侧信息区域权重并限制最小宽度
        file_tab.columnconfigure(2, weight=0, minsize=100)  # 右侧额外空间占位
        file_tab.rowconfigure(0, weight=1)

        # 创建左侧滚动控制面板
        scrollable_frame, canvas, control_frame = self._create_scrollable_panel(file_tab)
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # 创建右侧信息/输出区域
        info_frame = ttk.Frame(file_tab, style="RetroFrame.TFrame")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=0)
        info_frame.rowconfigure(1, weight=1)

        # 设置控制面板内部grid布局
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(0, weight=0)
        control_frame.rowconfigure(1, weight=0)
        control_frame.rowconfigure(2, weight=1)
        control_frame.rowconfigure(3, weight=0)
        
        # 文件操作所需变量定义
        self.file_path_var = tk.StringVar()
        self.file_path_var2 = tk.StringVar()
        self.output_path_var = tk.StringVar()
        self.offset_var = tk.StringVar(value="0")
        self.hex_data_var = tk.StringVar()
        self.max_bytes_var = tk.StringVar(value="1024")
        self.hash_algorithm_var = tk.StringVar(value="md5")
        self.bytes_per_line_var = tk.StringVar(value="16")
        # 添加读取全部选项
        self.read_all_var = tk.BooleanVar(value=True)
        # 添加读取到写入区选项
        self.read_to_write_var = tk.BooleanVar(value=False)
        
        # 添加控制面板标题
        ttk.Label(control_frame, text="// 文件功能控制面板 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=10, padx=10)

        # 处理功能选择 - 横向排版
        function_frame = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        function_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        function_frame.columnconfigure(0, weight=1)
        function_frame.columnconfigure(1, weight=1)
        function_frame.rowconfigure(0, weight=0)
        function_frame.rowconfigure(1, weight=0)
        function_frame.rowconfigure(2, weight=0)
        function_frame.rowconfigure(3, weight=0)

        ttk.Label(function_frame, text="选择功能:", style="RetroLabel.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(10, 5), padx=10)

        self.file_function = tk.StringVar(value="read")

        functions = [
            ("读取二进制文件", "read"),
            ("写入二进制文件", "write"),
            ("编辑二进制文件", "edit"),
            ("比较文件", "compare"),
            ("计算文件哈希", "hash"),
            ("分析文件结构", "analyze")
        ]

        row, col = 1, 0
        for text, value in functions:
            func_btn_frame = ttk.Frame(function_frame, style="RetroButton.TFrame")
            func_btn_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=1)
            func_btn_frame.columnconfigure(0, weight=1)
            
            ttk.Radiobutton(func_btn_frame, text=f"[ {text} ]", variable=self.file_function, 
                           value=value, style="RetroButton.TButton", 
                           command=lambda: self._update_file_ui()).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
            
            # 每2个按钮换行
            col += 1
            if col >= 2:
                col = 0
                row += 1
            
        # 创建一个容器来放置动态UI元素
        self.file_ui_container = ttk.Frame(control_frame, style="RetroFrame.TFrame")
        self.file_ui_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.file_ui_container.columnconfigure(0, weight=1)
        self.file_ui_container.rowconfigure(0, weight=1)
        
        # 初始更新UI
        self._update_file_ui()

        # 执行按钮
        execute_main_frame = ttk.Frame(control_frame, style="RetroAccent.TFrame")
        execute_main_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        execute_main_frame.columnconfigure(0, weight=1)
        
        ttk.Button(execute_main_frame, text="[执行]", command=self._execute_file_operation, 
                  style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # 设置控制面板内部grid布局
        control_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(0, weight=0)
        control_frame.rowconfigure(1, weight=0)
        control_frame.rowconfigure(2, weight=1)
        control_frame.rowconfigure(3, weight=0)
        control_frame.rowconfigure(4, weight=0)
        
        # 添加底部间距
        ttk.Label(control_frame).grid(row=5, column=0, pady=10)

        # 创建文件操作结果显示区域
        ttk.Label(info_frame, text="// 文件操作结果 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10), padx=10)
        
        # 创建结果显示终端
        result_term_frame = ttk.Frame(info_frame, style="RetroPanel.TFrame", relief=tk.SUNKEN)
        result_term_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        result_term_frame.columnconfigure(0, weight=1)
        result_term_frame.rowconfigure(0, weight=1)
        
        self.file_result_text = scrolledtext.ScrolledText(result_term_frame, wrap=tk.WORD, 
                                                        bg=self.input_bg, fg=self.secondary_color, 
                                                        insertbackground=self.accent_color, 
                                                        font=("Courier New", 10))
        self.file_result_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.file_result_text.insert(tk.END, "// 文件操作结果将显示在这里\n// 请选择文件功能并设置相应参数")
        self.file_result_text.config(state=tk.DISABLED)
    
    def _update_file_ui(self):
        """根据选择的功能更新文件操作UI - 使用grid布局"""
        # 清除容器中的所有小部件
        for widget in self.file_ui_container.winfo_children():
            widget.destroy()

        function = self.file_function.get()

        if function == "read":
            # 读取二进制文件UI - 使用grid布局
            read_frame = ttk.Frame(self.file_ui_container, style="RetroFrame.TFrame")
            read_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
            read_frame.columnconfigure(0, weight=1)
            read_frame.rowconfigure(0, weight=0)
            read_frame.rowconfigure(1, weight=0)
            read_frame.rowconfigure(2, weight=0)
            read_frame.rowconfigure(3, weight=0)
            read_frame.rowconfigure(4, weight=0)
            
            ttk.Label(read_frame, text="文件路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
            ttk.Entry(read_frame, textvariable=self.file_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
            
            browse_frame = ttk.Frame(read_frame, style="RetroAccent.TFrame")
            browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
            browse_frame.columnconfigure(0, weight=1)
            
            ttk.Button(browse_frame, text="[浏览...]", command=lambda: self._browse_file(self.file_path_var), 
                      style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            
            ttk.Label(read_frame, text="最大读取字节数:", style="RetroLabel.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 5), padx=10)
            
            # 创建一个框架来放置输入框和复选框
            read_option_frame = ttk.Frame(read_frame)
            read_option_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
            read_option_frame.columnconfigure(0, weight=1)
            read_option_frame.columnconfigure(1, weight=0)
            
            ttk.Entry(read_option_frame, textvariable=self.max_bytes_var, style="RetroEntry.TEntry").grid(row=0, column=0, sticky="ew", padx=(0, 5))
            
            # 添加读取全部复选框
            ttk.Checkbutton(read_option_frame, text="读取全部", variable=self.read_all_var, style="RetroCheckbutton.TCheckbutton").grid(row=0, column=1, sticky="w")
            
            # 添加读取到写入区复选框
            read_to_write_frame = ttk.Frame(read_frame)
            read_to_write_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
            read_to_write_frame.columnconfigure(0, weight=0)
            read_to_write_frame.columnconfigure(1, weight=1)
            
            ttk.Checkbutton(read_to_write_frame, text="读取到写入区", variable=self.read_to_write_var, style="RetroCheckbutton.TCheckbutton").grid(row=0, column=0, sticky="w")

        elif function == "write":
            # 写入二进制文件UI - 使用grid布局
            write_frame = ttk.Frame(self.file_ui_container, style="RetroFrame.TFrame")
            write_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
            write_frame.columnconfigure(0, weight=1)
            write_frame.rowconfigure(0, weight=0)
            write_frame.rowconfigure(1, weight=0)
            write_frame.rowconfigure(2, weight=0)
            write_frame.rowconfigure(3, weight=0)
            write_frame.rowconfigure(4, weight=0)
            write_frame.rowconfigure(5, weight=0)
            
            ttk.Label(write_frame, text="输出路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
            ttk.Entry(write_frame, textvariable=self.output_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
            
            browse_frame = ttk.Frame(write_frame, style="RetroAccent.TFrame")
            browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
            browse_frame.columnconfigure(0, weight=1)
            
            ttk.Button(browse_frame, text="[浏览...]", command=lambda: self._browse_file_save(self.output_path_var), 
                      style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            
            ttk.Label(write_frame, text="十六进制数据:", style="RetroLabel.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 5), padx=10)
            
            # 创建一个更大的文本框用于输入十六进制数据
            hex_text_frame = ttk.LabelFrame(write_frame, style="RetroFrame.TFrame", padding="5")
            hex_text_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
            hex_text_frame.columnconfigure(0, weight=1)
            hex_text_frame.rowconfigure(0, weight=1)
            
            # 创建一个ScrolledText作为十六进制数据输入框
            self.hex_text_widget = scrolledtext.ScrolledText(hex_text_frame, wrap=tk.WORD, 
                                                           bg=self.input_bg, fg=self.secondary_color, 
                                                           insertbackground=self.accent_color, 
                                                           font=(("Courier New", 10)), height=10)
            self.hex_text_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            
            # 确保hex_text_widget与hex_data_var保持同步
            def update_hex_var(event=None):
                self.hex_data_var.set(self.hex_text_widget.get("1.0", tk.END).strip())
            
            def update_hex_widget(*args):
                current_text = self.hex_text_widget.get("1.0", tk.END).strip()
                if current_text != self.hex_data_var.get():
                    self.hex_text_widget.delete("1.0", tk.END)
                    self.hex_text_widget.insert(tk.END, self.hex_data_var.get())
            
            self.hex_text_widget.bind("<KeyRelease>", update_hex_var)
            self.hex_data_var.trace_add("write", update_hex_widget)
            
            ttk.Label(write_frame, text="(例如: 48656c6c6f20576f726c64)", style="RetroLabel.TLabel").grid(row=5, column=0, sticky="w", padx=10)
            
            # 确保write_frame的行4有足够的权重
            write_frame.rowconfigure(4, weight=1)

        elif function == "edit":
            # 编辑二进制文件UI - 使用grid布局
            edit_frame = ttk.Frame(self.file_ui_container, style="RetroFrame.TFrame")
            edit_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
            edit_frame.columnconfigure(0, weight=1)
            edit_frame.rowconfigure(0, weight=0)
            edit_frame.rowconfigure(1, weight=0)
            edit_frame.rowconfigure(2, weight=0)
            edit_frame.rowconfigure(3, weight=0)
            edit_frame.rowconfigure(4, weight=0)
            edit_frame.rowconfigure(5, weight=0)
            edit_frame.rowconfigure(6, weight=0)
            
            ttk.Label(edit_frame, text="文件路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
            ttk.Entry(edit_frame, textvariable=self.file_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
            
            browse_frame = ttk.Frame(edit_frame, style="RetroAccent.TFrame")
            browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
            browse_frame.columnconfigure(0, weight=1)
            
            ttk.Button(browse_frame, text="[浏览...]", command=lambda: self._browse_file(self.file_path_var), 
                      style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            
            ttk.Label(edit_frame, text="偏移量:", style="RetroLabel.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 5), padx=10)
            ttk.Entry(edit_frame, textvariable=self.offset_var, style="RetroEntry.TEntry").grid(row=4, column=0, sticky="ew", padx=10, pady=5)
            
            ttk.Label(edit_frame, text="十六进制数据:", style="RetroLabel.TLabel").grid(row=5, column=0, sticky="w", pady=(10, 5), padx=10)
            ttk.Entry(edit_frame, textvariable=self.hex_data_var, style="RetroEntry.TEntry").grid(row=6, column=0, sticky="ew", padx=10, pady=5)

        elif function == "compare":
            # 比较文件UI - 使用grid布局
            compare_frame = ttk.Frame(self.file_ui_container, style="RetroFrame.TFrame")
            compare_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
            compare_frame.columnconfigure(0, weight=1)
            compare_frame.rowconfigure(0, weight=0)
            compare_frame.rowconfigure(1, weight=0)
            compare_frame.rowconfigure(2, weight=0)
            compare_frame.rowconfigure(3, weight=0)
            compare_frame.rowconfigure(4, weight=0)
            compare_frame.rowconfigure(5, weight=0)
            
            ttk.Label(compare_frame, text="文件1路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
            ttk.Entry(compare_frame, textvariable=self.file_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
            
            browse_frame = ttk.Frame(compare_frame, style="RetroAccent.TFrame")
            browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
            browse_frame.columnconfigure(0, weight=1)
            
            ttk.Button(browse_frame, text="[浏览...]", command=lambda: self._browse_file(self.file_path_var), 
                      style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            
            ttk.Label(compare_frame, text="文件2路径:", style="RetroLabel.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 5), padx=10)
            ttk.Entry(compare_frame, textvariable=self.file_path_var2, style="RetroEntry.TEntry").grid(row=4, column=0, sticky="ew", padx=10, pady=5)
            
            browse_frame2 = ttk.Frame(compare_frame, style="RetroAccent.TFrame")
            browse_frame2.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
            browse_frame2.columnconfigure(0, weight=1)
            
            ttk.Button(browse_frame2, text="[浏览...]", command=lambda: self._browse_file(self.file_path_var2), 
                      style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        elif function == "hash":
            # 计算文件哈希UI - 使用grid布局
            hash_frame = ttk.Frame(self.file_ui_container, style="RetroFrame.TFrame")
            hash_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
            hash_frame.columnconfigure(0, weight=1)
            hash_frame.rowconfigure(0, weight=0)
            hash_frame.rowconfigure(1, weight=0)
            hash_frame.rowconfigure(2, weight=0)
            hash_frame.rowconfigure(3, weight=0)
            hash_frame.rowconfigure(4, weight=0)
            
            ttk.Label(hash_frame, text="文件路径:", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
            ttk.Entry(hash_frame, textvariable=self.file_path_var, style="RetroEntry.TEntry").grid(row=1, column=0, sticky="ew", padx=10, pady=5)
            
            browse_frame = ttk.Frame(hash_frame, style="RetroAccent.TFrame")
            browse_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
            browse_frame.columnconfigure(0, weight=1)
            
            ttk.Button(browse_frame, text="[浏览...]", command=lambda: self._browse_file(self.file_path_var), 
                      style="RetroButton.TButton").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            
            ttk.Label(hash_frame, text="哈希算法:", style="RetroLabel.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 5), padx=10)
            hash_algorithms = ttk.Combobox(hash_frame, textvariable=self.hash_algorithm_var, style="RetroCombobox.TCombobox", state="readonly")
            hash_algorithms['values'] = ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512')
            hash_algorithms.current(0)
            hash_algorithms.grid(row=4, column=0, sticky="ew", padx=10, pady=5)

        elif function == "analyze":
            # 分析文件结构UI - 使用grid布局
            analyze_frame = ttk.Frame(self.file_ui_container, style="RetroFrame.TFrame")
            analyze_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
            
            ttk.Label(analyze_frame, text="文件路径:", style="RetroLabel.TLabel").pack(anchor=tk.W, pady=(10, 5), padx=10)
            ttk.Entry(analyze_frame, textvariable=self.file_path_var, style="RetroEntry.TEntry").pack(fill=tk.X, padx=10, pady=5)
            
            browse_frame = ttk.Frame(analyze_frame, style="RetroAccent.TFrame")
            browse_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Button(browse_frame, text="[浏览...]", command=lambda: self._browse_file(self.file_path_var), 
                      style="RetroButton.TButton").pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(analyze_frame, text="每行显示字节数:", style="RetroLabel.TLabel").pack(anchor=tk.W, pady=(10, 5), padx=10)
            ttk.Entry(analyze_frame, textvariable=self.bytes_per_line_var, style="RetroEntry.TEntry").pack(fill=tk.X, padx=10, pady=5)
    
    def _browse_file(self, var):
        """浏览选择文件"""
        file_path = filedialog.askopenfilename()
        if file_path:
            var.set(file_path)

    def _browse_file_save(self, var):
        """浏览选择保存文件路径"""
        file_path = filedialog.asksaveasfilename()
        if file_path:
            var.set(file_path)

    def _execute_file_operation(self):
        """执行文件操作"""
        function = self.file_function.get()
        try:
            self.file_result_text.config(state=tk.NORMAL)
            self.file_result_text.delete(1.0, tk.END)
            self.file_result_text.insert(tk.END, f"// 执行文件操作: {function}\n")
            self.file_result_text.insert(tk.END, f"{'-'*50}\n")

            if function == "read":
                file_path = self.file_path_var.get()
                if not file_path or not os.path.exists(file_path):
                    messagebox.showerror("ERROR", "请选择有效的文件路径")
                    return

                max_bytes = int(self.max_bytes_var.get()) if self.max_bytes_var.get().isdigit() else None
                result = self.platform.read_binary_file(file_path, max_bytes)

                if result["success"]:
                    self.file_result_text.insert(tk.END, f"// 读取文件: {file_path}\n")
                    self.file_result_text.insert(tk.END, f"// 读取大小: {result['size']} 字节\n\n")
                    
                    # 检查是否选择了读取全部
                    if self.read_all_var.get():
                        # 显示所有读取的数据
                        display_data = result["data"]
                        
                        # 按每行16字节分割数据
                        bytes_per_line = 16
                        
                        self.file_result_text.insert(tk.END, "// 十六进制表示:\n")
                        
                        # 分段显示十六进制数据
                        for i in range(0, len(display_data), bytes_per_line):
                            chunk = display_data[i:i+bytes_per_line]
                            hex_str = chunk.hex()
                            # 格式化十六进制字符串，每两个字符一组
                            formatted_hex = ' '.join([hex_str[j:j+2] for j in range(0, len(hex_str), 2)])
                            # 左对齐并固定宽度
                            formatted_hex = formatted_hex.ljust(bytes_per_line * 3 - 1)
                            
                            # 显示ASCII表示
                            ascii_str = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in chunk])
                            
                            # 显示偏移量
                            offset_str = f"0x{i:08x}"
                            self.file_result_text.insert(tk.END, f"// {offset_str}: {formatted_hex}  |  {ascii_str}\n")
                    else:
                        # 只显示前100字节
                        display_data = result["data"][:100]
                        hex_str = display_data.hex()
                        # 格式化十六进制字符串，每两个字符一组
                        formatted_hex = ' '.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)])
                        self.file_result_text.insert(tk.END, f"// {formatted_hex}\n\n")
                        
                        # 显示ASCII表示
                        ascii_str = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in display_data])
                        self.file_result_text.insert(tk.END, f"// ASCII: {ascii_str}\n\n")
                        
                        if len(result["data"]) > 100:
                            self.file_result_text.insert(tk.END, f"// ... 还有 {len(result['data']) - 100} 字节未显示\n\n")
                            self.file_result_text.insert(tk.END, "// 勾选'读取全部'复选框可显示完整内容\n")
                    
                    # 检查是否选择了读取到写入区
                    if self.read_to_write_var.get():
                        # 为了读取完整文件，我们需要重新读取一次文件但不限制大小
                        try:
                            with open(file_path, 'rb') as f:
                                full_data = f.read()
                            hex_data = full_data.hex()
                            
                            # 先自动切换到写入功能
                            self.file_function.set("write")
                            self._update_file_ui()
                            
                            # 在UI更新后，再设置数据到写入框
                            self.hex_data_var.set(hex_data)
                            
                            # 如果hex_text_widget已经创建，直接设置其内容
                            if hasattr(self, 'hex_text_widget'):
                                self.hex_text_widget.delete("1.0", tk.END)
                                self.hex_text_widget.insert(tk.END, hex_data)
                            
                            self.file_result_text.insert(tk.END, f"// \n// 完整数据已添加到写入区域 (共{len(full_data)}字节)\n")
                        except Exception as e:
                            self.file_result_text.insert(tk.END, f"// \n// 读取完整文件失败: {str(e)}\n")
                            # 如果出错，至少使用之前读取的数据
                            hex_data = result["data"].hex()
                            self.hex_data_var.set(hex_data)
                            if hasattr(self, 'hex_text_widget'):
                                self.hex_text_widget.delete("1.0", tk.END)
                                self.hex_text_widget.insert(tk.END, hex_data)
                            self.file_result_text.insert(tk.END, f"// 已添加部分数据到写入区域\n")
                    
                    self.status_var.set(f"FILE READ COMPLETE: {file_path}")
                else:
                    self.file_result_text.insert(tk.END, f"// 错误: {result['error']}")
                    self.status_var.set(f"FILE READ FAILED: {result['error']}")

            elif function == "write":
                output_path = self.output_path_var.get()
                hex_data = self.hex_data_var.get()
                
                if not output_path:
                    messagebox.showerror("ERROR", "请选择输出文件路径")
                    return
                
                # 验证十六进制数据
                try:
                    data = bytes.fromhex(hex_data)
                except ValueError:
                    messagebox.showerror("ERROR", "无效的十六进制数据")
                    return
                
                result = self.platform.write_binary_file(output_path, data)
                self.file_result_text.insert(tk.END, f"// {result}\n")
                self.status_var.set(f"FILE WRITE COMPLETE: {output_path}")

            elif function == "edit":
                file_path = self.file_path_var.get()
                if not file_path or not os.path.exists(file_path):
                    messagebox.showerror("ERROR", "请选择有效的文件路径")
                    return
                
                offset = int(self.offset_var.get()) if self.offset_var.get().isdigit() else 0
                hex_data = self.hex_data_var.get()
                
                # 验证十六进制数据
                try:
                    data = bytes.fromhex(hex_data)
                except ValueError:
                    messagebox.showerror("ERROR", "无效的十六进制数据")
                    return
                
                result = self.platform.edit_binary_file(file_path, offset, data)
                self.file_result_text.insert(tk.END, f"// {result}\n")
                self.status_var.set(f"FILE EDIT COMPLETE: {file_path}")

            elif function == "compare":
                file_path1 = self.file_path_var.get()
                file_path2 = self.file_path_var2.get()
                
                if not file_path1 or not os.path.exists(file_path1) or not file_path2 or not os.path.exists(file_path2):
                    messagebox.showerror("ERROR", "请选择有效的文件路径")
                    return
                
                result = self.platform.compare_files(file_path1, file_path2)
                
                if result.get("success", True):  # 假设成功除非有明确的success:False
                    if result["are_identical"]:
                        self.file_result_text.insert(tk.END, f"// 文件比较结果: 两个文件完全相同\n")
                        self.file_result_text.insert(tk.END, f"// 文件大小: {result['size']} 字节\n")
                        self.status_var.set(f"FILE COMPARE COMPLETE: FILES IDENTICAL")
                    else:
                        self.file_result_text.insert(tk.END, f"// 文件比较结果: 两个文件不同\n")
                        self.file_result_text.insert(tk.END, f"// 原因: {result['reason']}\n")
                        if "first_diff_position" in result:
                            self.file_result_text.insert(tk.END, f"// 第一个不同位置: 偏移量 {result['first_diff_position']}\n")
                        self.file_result_text.insert(tk.END, f"// 文件1大小: {result['size1']} 字节\n")
                        self.file_result_text.insert(tk.END, f"// 文件2大小: {result['size2']} 字节\n")
                        self.status_var.set(f"FILE COMPARE COMPLETE: FILES DIFFERENT")
                else:
                    self.file_result_text.insert(tk.END, f"// 错误: {result['error']}")
                    self.status_var.set(f"FILE COMPARE FAILED: {result['error']}")

            elif function == "hash":
                file_path = self.file_path_var.get()
                if not file_path or not os.path.exists(file_path):
                    messagebox.showerror("ERROR", "请选择有效的文件路径")
                    return
                
                algorithm = self.hash_algorithm_var.get()
                result = self.platform.calculate_file_hash(file_path, algorithm)
                
                if result["success"]:
                    self.file_result_text.insert(tk.END, f"// 文件: {result['file_path']}\n")
                    self.file_result_text.insert(tk.END, f"// 算法: {result['algorithm'].upper()}\n")
                    self.file_result_text.insert(tk.END, f"// 哈希值: {result['hash']}\n")
                    self.status_var.set(f"FILE HASH COMPLETE: {algorithm.upper()} {file_path}")
                else:
                    self.file_result_text.insert(tk.END, f"// 错误: {result['error']}")
                    self.status_var.set(f"FILE HASH FAILED: {result['error']}")

            elif function == "analyze":
                file_path = self.file_path_var.get()
                if not file_path or not os.path.exists(file_path):
                    messagebox.showerror("ERROR", "请选择有效的文件路径")
                    return
                
                bytes_per_line = int(self.bytes_per_line_var.get()) if self.bytes_per_line_var.get().isdigit() else 16
                result = self.platform.analyze_file_structure(file_path, bytes_per_line)
                
                if result["success"]:
                    self.file_result_text.insert(tk.END, f"// 文件分析: {result['file_path']}\n")
                    self.file_result_text.insert(tk.END, f"// 文件大小: {result['file_size']} 字节\n\n")
                    
                    # 显示文件的十六进制视图，限制显示行数
                    hex_view = result["hex_view"]
                    lines = hex_view.split('\n')
                    
                    # 显示前100行和后50行
                    if len(lines) > 150:
                        display_lines = lines[:100] + ["// ...", "// ..."] + lines[-50:]
                    else:
                        display_lines = lines
                    
                    for line in display_lines:
                        self.file_result_text.insert(tk.END, f"// {line}\n")
                    
                    if len(lines) > 150:
                        self.file_result_text.insert(tk.END, f"\n// ... 共 {len(lines)} 行，显示了 152 行\n")
                    
                    self.status_var.set(f"FILE ANALYSIS COMPLETE: {file_path}")
                else:
                    self.file_result_text.insert(tk.END, f"// 错误: {result['error']}")
                    self.status_var.set(f"FILE ANALYSIS FAILED: {result['error']}")

            self.file_result_text.insert(tk.END, f"{'-'*50}\n")
            self.file_result_text.insert(tk.END, "// 操作完成\n")
            self.file_result_text.config(state=tk.DISABLED)
        except Exception as e:
            self.file_result_text.insert(tk.END, f"// 执行操作时出错: {str(e)}")
            self.file_result_text.config(state=tk.DISABLED)
            messagebox.showerror("ERROR", f"执行操作时出错: {str(e)}")
            self.status_var.set(f"FILE OPERATION FAILED: {str(e)}")
    
    def _create_commands_tab(self):
        """创建命令表标签页 - 使用grid布局"""
        commands_tab = ttk.Frame(self.notebook, style="RetroFrame.TFrame")
        self.notebook.add(commands_tab, text="命令表")
        
        # 设置grid权重以适应窗口大小变化
        commands_tab.columnconfigure(0, weight=1)
        commands_tab.rowconfigure(0, weight=0)
        commands_tab.rowconfigure(1, weight=1)
        
        # 创建命令类型选择区域
        top_frame = ttk.Frame(commands_tab, style="RetroPanel.TFrame")
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=0)
        top_frame.rowconfigure(0, weight=0)
        top_frame.rowconfigure(1, weight=0)
        
        # 添加标题
        ttk.Label(top_frame, text="// 终端命令参考表 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        
        # 命令类型选择
        type_frame = ttk.Frame(top_frame, style="RetroFrame.TFrame")
        type_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self.command_type = tk.StringVar(value="windows")
        
        ttk.Radiobutton(type_frame, text="[ Windows PowerShell ]", variable=self.command_type, 
                       value="windows", style="RetroButton.TButton").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Radiobutton(type_frame, text="[ Linux ]", variable=self.command_type, 
                       value="linux", style="RetroButton.TButton").grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # 加载命令按钮
        load_btn_frame = ttk.Frame(top_frame, style="RetroAccent.TFrame")
        load_btn_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        load_btn = ttk.Button(load_btn_frame, text="[加载命令表]", command=self._load_commands, 
                             style="RetroButton.TButton")
        load_btn.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 创建左侧类别列表和右侧命令详情区域
        content_frame = ttk.Frame(commands_tab, style="RetroFrame.TFrame")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=0, minsize=200)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # 左侧类别列表
        categories_frame = ttk.Frame(content_frame, style="RetroPanel.TFrame")
        categories_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        categories_frame.columnconfigure(0, weight=1)
        categories_frame.rowconfigure(0, weight=0)
        categories_frame.rowconfigure(1, weight=1)
        
        ttk.Label(categories_frame, text="// 命令类别 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 5), padx=10)
        
        # 创建类别列表 - 设计成复古终端风格
        listbox_frame = ttk.Frame(categories_frame, style="RetroFrame.TFrame")
        listbox_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        self.categories_listbox = tk.Listbox(listbox_frame, bg=self.input_bg, fg=self.fg_color, 
                                          font=("Courier New", 10, "bold"), selectbackground=self.accent_color, 
                                          selectforeground=self.bg_color, relief=tk.SUNKEN, borderwidth=2)
        self.categories_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.categories_listbox.bind('<<ListboxSelect>>', self._on_category_select)
        
        # 右侧命令详情区域
        commands_frame = ttk.Frame(content_frame, style="RetroPanel.TFrame")
        commands_frame.grid(row=0, column=1, sticky="nsew")
        commands_frame.columnconfigure(0, weight=1)
        commands_frame.rowconfigure(0, weight=0)
        commands_frame.rowconfigure(1, weight=1)
        
        ttk.Label(commands_frame, text="// 命令详情 //", style="RetroLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 5), padx=10)
        
        # 创建命令详情显示终端
        commands_term_frame = ttk.Frame(commands_frame, style="RetroFrame.TFrame")
        commands_term_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        commands_term_frame.columnconfigure(0, weight=1)
        commands_term_frame.rowconfigure(0, weight=1)
        
        self.commands_text = scrolledtext.ScrolledText(commands_term_frame, wrap=tk.WORD, 
                                                     bg=self.input_bg, fg=self.secondary_color, 
                                                     insertbackground=self.accent_color, 
                                                     font=("Courier New", 10),
                                                     borderwidth=2, relief=tk.SUNKEN)
        self.commands_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.commands_text.config(state=tk.DISABLED)
        
        # 存储当前命令数据
        self.current_commands = {}
        
        # 初始化加载Windows命令
        self._load_commands()
    
    def _load_commands(self):
        """加载命令表"""
        try:
            command_type = self.command_type.get()
            
            if command_type == "windows":
                self.current_commands = self.platform.get_windows_commands()
            else:
                self.current_commands = self.platform.get_linux_commands()
            
            # 更新类别列表
            self.categories_listbox.delete(0, tk.END)
            for category in self.current_commands.keys():
                self.categories_listbox.insert(tk.END, f"[ {category} ]")
            
            # 自动选择第一个类别
            if self.current_commands:
                self.categories_listbox.selection_set(0)
                self._display_commands(list(self.current_commands.keys())[0])
            
            self.status_var.set(f"{command_type.upper()} COMMANDS LOADED SUCCESSFULLY")
        except Exception as e:
            messagebox.showerror("ERROR", f"加载命令表失败: {str(e)}")
            self.status_var.set(f"COMMANDS LOADING FAILED: {str(e)}")
    
    def _on_category_select(self, event):
        """处理类别选择事件"""
        selection = self.categories_listbox.curselection()
        if selection:
            # 移除方括号获取实际类别名
            category_text = self.categories_listbox.get(selection[0])
            if category_text.startswith('[ ') and category_text.endswith(' ]'):
                category = category_text[2:-2]
                self._display_commands(category)
    
    def _display_commands(self, category):
        """显示选定类别的命令"""
        if category in self.current_commands:
            commands = self.current_commands[category]
            
            self.commands_text.config(state=tk.NORMAL)
            self.commands_text.delete(1.0, tk.END)
            
            self.commands_text.insert(tk.END, f"// ===== {category} =====\n\n")
            for cmd, description in commands.items():
                self.commands_text.insert(tk.END, f"[ COMMAND ]> {cmd}\n")
                self.commands_text.insert(tk.END, f"[ DESCRIPTION ]> {description}\n\n")
            
            self.commands_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    
    # 设置窗口图标（如果有）
    # root.iconbitmap("logo.ico")
    
    # 创建并启动GUI应用
    app = RetroFuturisticPlatformGUI(root)
    
    # 添加复古风格的窗口关闭确认
    def on_closing():
        if messagebox.askyesno("确认退出", "确定要退出数据分析平台吗？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 运行主循环
    root.mainloop()