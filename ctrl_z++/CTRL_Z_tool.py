import os
import time
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading
import difflib
import codecs

class CodeArchiver:
    def __init__(self, root):
        self.root = root
        self.root.title("CTRL_Z_tool")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 配置
        self.config = {
            "watch_path": "",
            "archive_dir": "",
            "interval": 300,  # 默认5分钟自动保存
            "history": [],
            "include_extensions": [".py", ".java", ".cpp", ".h", ".c", ".js", ".html", ".css", ".php", ".go", ".rb", ".ts"],
            "watch_changes": True  # 是否监测文件变化
        }
        
        # 状态
        self.watching = False
        self.watch_thread = None
        self.last_archive_time = 0
        self.file_modified_times = {}  # 存储文件的最后修改时间
        self.current_archive = None  # 当前选中的存档
        self.compare_archive1 = None  # 用于比较的第一个存档
        self.compare_archive2 = None  # 用于比较的第二个存档
        
        # 加载配置
        self.load_config()
        
        # 创建UI
        self.create_widgets()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部控制区域
        control_frame = ttk.LabelFrame(main_frame, text="控制中心", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 选择目录按钮
        ttk.Button(control_frame, text="选择监控目录", command=self.select_watch_dir).pack(side=tk.LEFT, padx=5)
        
        # 监控目录显示
        self.watch_dir_var = tk.StringVar(value=self.config["watch_path"] or "未选择目录")
        ttk.Label(control_frame, textvariable=self.watch_dir_var, width=50).pack(side=tk.LEFT, padx=5)
        
        # 间隔设置
        ttk.Label(control_frame, text="自动保存间隔(分钟):").pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.StringVar(value=str(self.config["interval"] // 60))
        interval_entry = ttk.Entry(control_frame, textvariable=self.interval_var, width=5)
        interval_entry.pack(side=tk.LEFT, padx=5)
        
        # 监测变化复选框
        self.watch_changes_var = tk.BooleanVar(value=self.config["watch_changes"])
        self.watch_changes_checkbox = ttk.Checkbutton(control_frame, text="监测文件变化自动保存", variable=self.watch_changes_var, command=self.update_watch_changes_config)
        self.watch_changes_checkbox.pack(side=tk.LEFT, padx=5)
        
        # 开始/停止按钮
        self.start_stop_btn = ttk.Button(control_frame, text="开始监控", command=self.toggle_watch)
        self.start_stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 立即保存按钮
        ttk.Button(control_frame, text="立即保存", command=self.archive_now).pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建历史记录和文件预览的分割窗口
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 历史记录列表
        history_frame = ttk.LabelFrame(paned_window, text="版本历史", padding="10")
        paned_window.add(history_frame, weight=1)
        
        # 创建历史记录列表
        columns = ("timestamp", "description")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=15)
        self.history_tree.heading("timestamp", text="时间戳")
        self.history_tree.heading("description", text="描述")
        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("description", width=200)
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定历史记录选择事件
        self.history_tree.bind("<<TreeviewSelect>>", self.on_history_select)
        
        # 操作按钮
        action_frame = ttk.Frame(history_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="回档到选定版本", command=self.restore_version).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="刷新历史", command=self.refresh_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="删除选定版本", command=self.delete_version).pack(side=tk.LEFT, padx=5)
        
        # 文件预览区域
        preview_frame = ttk.LabelFrame(paned_window, text="文件预览", padding="10")
        paned_window.add(preview_frame, weight=2)
        
        # 创建标签页
        self.notebook = ttk.Notebook(preview_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 当前文件标签页
        self.current_files_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.current_files_tab, text="当前文件")
        
        # 创建文件列表视图
        self.file_list = ttk.Treeview(self.current_files_tab, columns=("name"), show="headings", height=10)
        self.file_list.heading("name", text="文件名")
        self.file_list.column("name", width=300)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 文件列表滚动条
        file_scrollbar = ttk.Scrollbar(self.current_files_tab, orient=tk.VERTICAL, command=self.file_list.yview)
        self.file_list.configure(yscroll=file_scrollbar.set)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定文件双击事件
        self.file_list.bind("<Double-1>", self.on_file_double_click)
        
        # 创建文件内容显示区域
        self.file_content_text = tk.Text(self.current_files_tab, wrap=tk.WORD, width=80, height=20)
        self.file_content_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 添加文本滚动条
        text_scrollbar = ttk.Scrollbar(self.file_content_text, orient=tk.VERTICAL, command=self.file_content_text.yview)
        self.file_content_text.configure(yscroll=text_scrollbar.set)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 版本比较标签页
        self.compare_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.compare_tab, text="版本比较")
        
        # 比较选择区域
        compare_select_frame = ttk.Frame(self.compare_tab)
        compare_select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(compare_select_frame, text="版本1: ").pack(side=tk.LEFT, padx=5)
        self.compare_version1_var = tk.StringVar()
        self.compare_version1_combo = ttk.Combobox(compare_select_frame, textvariable=self.compare_version1_var, width=20, state="readonly")
        self.compare_version1_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(compare_select_frame, text="版本2: ").pack(side=tk.LEFT, padx=5)
        self.compare_version2_var = tk.StringVar()
        self.compare_version2_combo = ttk.Combobox(compare_select_frame, textvariable=self.compare_version2_var, width=20, state="readonly")
        self.compare_version2_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(compare_select_frame, text="开始比较", command=self.start_compare).pack(side=tk.LEFT, padx=5)
        
        # 比较结果显示区域
        self.compare_result_text = tk.Text(self.compare_tab, wrap=tk.WORD, width=80, height=20)
        self.compare_result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 比较结果滚动条
        compare_scrollbar = ttk.Scrollbar(self.compare_result_text, orient=tk.VERTICAL, command=self.compare_result_text.yview)
        self.compare_result_text.configure(yscroll=compare_scrollbar.set)
        compare_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 加载历史记录
        self.refresh_history()
    
    def update_watch_changes_config(self):
        self.config["watch_changes"] = self.watch_changes_var.get()
        self.save_config()
    
    def select_watch_dir(self):
        dir_path = filedialog.askdirectory(title="选择要监控的代码目录")
        if dir_path:
            self.config["watch_path"] = dir_path
            # 默认将存档目录设置为监控目录下的 .code_archives 文件夹
            self.config["archive_dir"] = os.path.join(dir_path, ".code_archives")
            self.watch_dir_var.set(dir_path)
            self.save_config()
            self.refresh_history()
            # 初始化文件修改时间记录
            if self.watching:
                self.initialize_file_modified_times()
            messagebox.showinfo("成功", f"已选择监控目录: {dir_path}")
    
    def toggle_watch(self):
        if not self.config["watch_path"] or not os.path.exists(self.config["watch_path"]):
            messagebox.showerror("错误", "请先选择有效的监控目录")
            return
        
        # 更新间隔设置
        try:
            minutes = int(self.interval_var.get())
            if minutes <= 0:
                raise ValueError("间隔必须大于0")
            self.config["interval"] = minutes * 60  # 转换为秒
            self.save_config()
        except ValueError as e:
            messagebox.showerror("错误", f"无效的间隔设置: {str(e)}")
            return
        
        if self.watching:
            self.stop_watch()
        else:
            self.start_watch()
    
    def start_watch(self):
        self.watching = True
        self.start_stop_btn.config(text="停止监控")
        
        # 更新状态显示
        if self.config["watch_changes"]:
            self.status_var.set(f"监控中... 自动保存间隔: {self.config['interval']//60}分钟 (检测变化)")
        else:
            self.status_var.set(f"监控中... 自动保存间隔: {self.config['interval']//60}分钟")
        
        # 创建存档目录
        if not os.path.exists(self.config["archive_dir"]):
            os.makedirs(self.config["archive_dir"])
        
        # 初始化文件修改时间记录
        self.initialize_file_modified_times()
        
        # 立即保存一次
        self.archive_now(description="手动保存")
        
        # 启动监控线程
        self.watch_thread = threading.Thread(target=self.watch_loop, daemon=True)
        self.watch_thread.start()
    
    def stop_watch(self):
        self.watching = False
        if self.watch_thread:
            self.watch_thread.join(1.0)  # 等待线程结束，最多1秒
        self.start_stop_btn.config(text="开始监控")
        self.status_var.set("已停止监控")
    
    def initialize_file_modified_times(self):
        """初始化文件修改时间记录"""
        self.file_modified_times = {}
        self._update_file_modified_times()
    
    def _update_file_modified_times(self):
        """更新文件修改时间记录"""
        if not self.config["watch_path"] or not os.path.exists(self.config["watch_path"]):
            return
        
        try:
            for root, dirs, files in os.walk(self.config["watch_path"]):
                # 排除存档目录本身
                if self.config["archive_dir"] and root.startswith(self.config["archive_dir"]):
                    continue
                
                # 排除隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                
                # 记录符合条件的文件的修改时间
                for file in files:
                    if any(file.endswith(ext) for ext in self.config["include_extensions"]):
                        file_path = os.path.join(root, file)
                        try:
                            # 使用文件的修改时间和大小作为判断变化的依据
                            mtime = os.path.getmtime(file_path)
                            size = os.path.getsize(file_path)
                            self.file_modified_times[file_path] = (mtime, size)
                        except OSError:
                            # 忽略无法访问的文件
                            pass
        except Exception as e:
            print(f"初始化文件修改时间失败: {str(e)}")
    
    def has_files_changed(self):
        """检查文件是否发生变化"""
        if not self.config["watch_path"] or not os.path.exists(self.config["watch_path"]):
            return False
        
        try:
            changes_detected = False
            
            # 检查现有文件是否有变化
            for file_path, (old_mtime, old_size) in list(self.file_modified_times.items()):
                if not os.path.exists(file_path):
                    # 文件被删除
                    self.file_modified_times.pop(file_path)
                    changes_detected = True
                    continue
                
                try:
                    new_mtime = os.path.getmtime(file_path)
                    new_size = os.path.getsize(file_path)
                    if new_mtime != old_mtime or new_size != old_size:
                        # 文件被修改
                        self.file_modified_times[file_path] = (new_mtime, new_size)
                        changes_detected = True
                except OSError:
                    # 忽略无法访问的文件
                    self.file_modified_times.pop(file_path)
            
            # 检查是否有新文件添加
            for root, dirs, files in os.walk(self.config["watch_path"]):
                # 排除存档目录本身
                if self.config["archive_dir"] and root.startswith(self.config["archive_dir"]):
                    continue
                
                # 排除隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                
                for file in files:
                    if any(file.endswith(ext) for ext in self.config["include_extensions"]):
                        file_path = os.path.join(root, file)
                        if file_path not in self.file_modified_times:
                            # 新文件被添加
                            try:
                                mtime = os.path.getmtime(file_path)
                                size = os.path.getsize(file_path)
                                self.file_modified_times[file_path] = (mtime, size)
                                changes_detected = True
                            except OSError:
                                # 忽略无法访问的文件
                                pass
            
            return changes_detected
        except Exception as e:
            print(f"检查文件变化失败: {str(e)}")
            return False
    
    def watch_loop(self):
        while self.watching:
            current_time = time.time()
            time_based_save = current_time - self.last_archive_time >= self.config["interval"]
            
            # 检查是否需要保存
            if time_based_save:
                self.archive_now(description="定时自动保存")
            elif self.config["watch_changes"] and self.has_files_changed():
                self.archive_now(description="文件变化自动保存")
            
            # 更新状态显示
            if self.watching:  # 再次检查，因为archive_now可能会修改watching状态
                if self.config["watch_changes"]:
                    self.status_var.set(f"监控中... 自动保存间隔: {self.config['interval']//60}分钟 (检测变化)")
                else:
                    self.status_var.set(f"监控中... 自动保存间隔: {self.config['interval']//60}分钟")
            
            time.sleep(10)  # 每10秒检查一次
    
    def archive_now(self, description=None):
        if not self.config["watch_path"] or not os.path.exists(self.config["watch_path"]):
            return
        
        # 创建存档目录
        if not os.path.exists(self.config["archive_dir"]):
            os.makedirs(self.config["archive_dir"])
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(self.config["archive_dir"], timestamp)
        
        try:
            # 复制所有符合条件的文件
            self.copy_project_files(self.config["watch_path"], archive_path)
            
            # 记录存档信息
            archive_info = {
                "timestamp": timestamp,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "description": description or "自动保存"
            }
            self.config["history"].append(archive_info)
            self.save_config()
            
            self.last_archive_time = time.time()
            self.status_var.set(f"已自动保存 ({archive_info['datetime']})")
            self.refresh_history()
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def copy_project_files(self, source_dir, dest_dir):
        # 确保目标目录存在
        os.makedirs(dest_dir, exist_ok=True)
        
        # 复制文件
        for root, dirs, files in os.walk(source_dir):
            # 排除存档目录本身
            if self.config["archive_dir"] and root.startswith(self.config["archive_dir"]):
                continue
            
            # 排除隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            
            # 创建目标子目录
            rel_path = os.path.relpath(root, source_dir)
            target_dir = os.path.join(dest_dir, rel_path)
            os.makedirs(target_dir, exist_ok=True)
            
            # 复制符合条件的文件
            for file in files:
                if any(file.endswith(ext) for ext in self.config["include_extensions"]):
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)
                    shutil.copy2(source_file, target_file)
    
    def refresh_history(self):
        # 清空历史记录树
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # 重新加载历史记录
        self.load_config()
        
        # 添加到历史记录树
        combo_values = []
        for item in reversed(self.config["history"]):
            self.history_tree.insert("", tk.END, values=(item["datetime"], item["description"]))
            combo_values.append(item["datetime"])
        
        # 更新比较版本下拉框
        self.compare_version1_combo['values'] = combo_values
        self.compare_version2_combo['values'] = combo_values
        if combo_values:
            self.compare_version1_combo.current(0)
            if len(combo_values) > 1:
                self.compare_version2_combo.current(1)
            else:
                self.compare_version2_combo.current(0)
    
    def on_history_select(self, event):
        selected_items = self.history_tree.selection()
        if not selected_items:
            return
        
        # 获取选中的时间戳
        item = selected_items[0]
        datetime_str = self.history_tree.item(item, "values")[0]
        
        # 查找对应的存档信息
        selected_archive = None
        for archive in self.config["history"]:
            if archive["datetime"] == datetime_str:
                selected_archive = archive
                break
        
        if selected_archive:
            self.current_archive = selected_archive
            self.status_var.set(f"已选择版本: {selected_archive['datetime']}")
            self.load_archive_files(selected_archive)
    
    def load_archive_files(self, archive):
        # 清空文件列表
        for item in self.file_list.get_children():
            self.file_list.delete(item)
        
        # 清空文件内容
        self.file_content_text.delete("1.0", tk.END)
        
        # 加载存档中的文件
        archive_path = os.path.join(self.config["archive_dir"], archive["timestamp"])
        if not os.path.exists(archive_path):
            return
        
        try:
            for root, dirs, files in os.walk(archive_path):
                for file in files:
                    if any(file.endswith(ext) for ext in self.config["include_extensions"]):
                        # 获取相对路径
                        rel_path = os.path.relpath(os.path.join(root, file), archive_path)
                        self.file_list.insert("", tk.END, values=(rel_path,), tags=(os.path.join(root, file),))
        except Exception as e:
            print(f"加载存档文件失败: {str(e)}")
    
    def on_file_double_click(self, event):
        selected_items = self.file_list.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        file_path = self.file_list.item(item, "tags")[0]  # 获取实际文件路径
        
        try:
            # 读取文件内容
            with codecs.open(file_path, 'r', 'utf-8', errors='replace') as f:
                content = f.read()
            
            # 显示文件内容
            self.file_content_text.delete("1.0", tk.END)
            self.file_content_text.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {str(e)}")
    
    def start_compare(self):
        # 获取选择的两个版本
        datetime1 = self.compare_version1_var.get()
        datetime2 = self.compare_version2_var.get()
        
        if not datetime1 or not datetime2:
            messagebox.showinfo("提示", "请选择要比较的两个版本")
            return
        
        # 查找对应的存档信息
        archive1 = None
        archive2 = None
        for archive in self.config["history"]:
            if archive["datetime"] == datetime1:
                archive1 = archive
            if archive["datetime"] == datetime2:
                archive2 = archive
        
        if not archive1 or not archive2:
            messagebox.showerror("错误", "找不到选中的版本信息")
            return
        
        # 清空比较结果
        self.compare_result_text.delete("1.0", tk.END)
        
        # 比较两个版本
        archive_path1 = os.path.join(self.config["archive_dir"], archive1["timestamp"])
        archive_path2 = os.path.join(self.config["archive_dir"], archive2["timestamp"])
        
        # 获取所有文件
        files1 = self.get_archive_files(archive_path1)
        files2 = self.get_archive_files(archive_path2)
        
        # 合并文件列表
        all_files = set(files1.keys()).union(set(files2.keys()))
        
        # 比较每个文件
        for rel_path in sorted(all_files):
            if rel_path not in files1:
                self.compare_result_text.insert(tk.END, f"+ 新增文件: {rel_path}\n")
            elif rel_path not in files2:
                self.compare_result_text.insert(tk.END, f"- 删除文件: {rel_path}\n")
            else:
                # 读取两个文件内容并比较
                try:
                    with codecs.open(files1[rel_path], 'r', 'utf-8', errors='replace') as f1, \
                         codecs.open(files2[rel_path], 'r', 'utf-8', errors='replace') as f2:
                        content1 = f1.readlines()
                        content2 = f2.readlines()
                    
                    # 使用difflib比较文件内容
                    diff = difflib.unified_diff(content1, content2, fromfile=f"版本1: {rel_path}", tofile=f"版本2: {rel_path}", lineterm='')
                    diff_lines = list(diff)
                    
                    if diff_lines:
                        self.compare_result_text.insert(tk.END, f"* 修改文件: {rel_path}\n")
                        for line in diff_lines[:50]:  # 只显示前50行差异
                            self.compare_result_text.insert(tk.END, line + '\n')
                        if len(diff_lines) > 50:
                            self.compare_result_text.insert(tk.END, f"... 还有{len(diff_lines) - 50}行差异未显示\n")
                        self.compare_result_text.insert(tk.END, '\n')
                except Exception as e:
                    self.compare_result_text.insert(tk.END, f"! 比较文件失败: {rel_path} - {str(e)}\n")
    
    def get_archive_files(self, archive_path):
        """获取存档中的所有文件，返回相对路径到绝对路径的映射"""
        files = {}
        
        if not os.path.exists(archive_path):
            return files
        
        try:
            for root, dirs, files_list in os.walk(archive_path):
                for file in files_list:
                    if any(file.endswith(ext) for ext in self.config["include_extensions"]):
                        # 获取相对路径
                        rel_path = os.path.relpath(os.path.join(root, file), archive_path)
                        files[rel_path] = os.path.join(root, file)
        except Exception as e:
            print(f"获取存档文件失败: {str(e)}")
        
        return files
    
    def restore_version(self):
        selected_items = self.history_tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择要回档的版本")
            return
        
        # 获取选中的时间戳
        item = selected_items[0]
        datetime_str = self.history_tree.item(item, "values")[0]
        
        # 查找对应的存档信息
        selected_archive = None
        for archive in self.config["history"]:
            if archive["datetime"] == datetime_str:
                selected_archive = archive
                break
        
        if not selected_archive:
            messagebox.showerror("错误", "找不到选中的版本信息")
            return
        
        # 确认回档
        if not messagebox.askyesno("确认回档", f"确定要回档到 {selected_archive['datetime']} 的版本吗？\n当前文件将会被覆盖！"):
            return
        
        try:
            # 停止监控
            was_watching = self.watching
            if was_watching:
                self.stop_watch()
            
            # 获取存档路径
            archive_path = os.path.join(self.config["archive_dir"], selected_archive["timestamp"])
            
            # 备份当前文件
            backup_path = os.path.join(self.config["archive_dir"], f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            self.copy_project_files(self.config["watch_path"], backup_path)
            
            # 清空当前目录下的所有代码文件
            for root, dirs, files in os.walk(self.config["watch_path"]):
                if self.config["archive_dir"] and root.startswith(self.config["archive_dir"]):
                    continue
                for file in files:
                    if any(file.endswith(ext) for ext in self.config["include_extensions"]):
                        os.remove(os.path.join(root, file))
            
            # 从存档恢复文件
            for root, dirs, files in os.walk(archive_path):
                rel_path = os.path.relpath(root, archive_path)
                target_dir = os.path.join(self.config["watch_path"], rel_path)
                os.makedirs(target_dir, exist_ok=True)
                
                for file in files:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)
                    shutil.copy2(source_file, target_file)
            
            # 记录回档操作
            restore_info = {
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "description": f"回档到 {selected_archive['datetime']}"
            }
            self.config["history"].append(restore_info)
            self.save_config()
            
            # 重新初始化文件修改时间记录
            self.initialize_file_modified_times()
            
            # 重新开始监控
            if was_watching:
                self.start_watch()
            
            self.refresh_history()
            messagebox.showinfo("成功", f"已成功回档到 {selected_archive['datetime']} 的版本")
        except Exception as e:
            messagebox.showerror("错误", f"回档失败: {str(e)}")
            # 尝试恢复到回档前的状态
            try:
                if os.path.exists(backup_path):
                    for root, dirs, files in os.walk(self.config["watch_path"]):
                        if self.config["archive_dir"] and root.startswith(self.config["archive_dir"]):
                            continue
                        for file in files:
                            if any(file.endswith(ext) for ext in self.config["include_extensions"]):
                                os.remove(os.path.join(root, file))
                    for root, dirs, files in os.walk(backup_path):
                        rel_path = os.path.relpath(root, backup_path)
                        target_dir = os.path.join(self.config["watch_path"], rel_path)
                        os.makedirs(target_dir, exist_ok=True)
                        for file in files:
                            source_file = os.path.join(root, file)
                            target_file = os.path.join(target_dir, file)
                            shutil.copy2(source_file, target_file)
            except:
                pass
    
    def delete_version(self):
        selected_items = self.history_tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择要删除的版本")
            return
        
        # 获取选中的时间戳
        item = selected_items[0]
        datetime_str = self.history_tree.item(item, "values")[0]
        
        # 查找对应的存档信息
        selected_archive = None
        index = -1
        for i, archive in enumerate(self.config["history"]):
            if archive["datetime"] == datetime_str:
                selected_archive = archive
                index = i
                break
        
        if not selected_archive:
            messagebox.showerror("错误", "找不到选中的版本信息")
            return
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除 {selected_archive['datetime']} 的版本吗？\n此操作不可恢复！"):
            return
        
        try:
            # 删除存档文件
            archive_path = os.path.join(self.config["archive_dir"], selected_archive["timestamp"])
            if os.path.exists(archive_path):
                shutil.rmtree(archive_path)
            
            # 从历史记录中移除
            self.config["history"].pop(index)
            self.save_config()
            
            self.refresh_history()
            messagebox.showinfo("成功", f"已成功删除 {selected_archive['datetime']} 的版本")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {str(e)}")
    
    def save_config(self):
        if not self.config["archive_dir"]:
            return
        
        config_path = os.path.join(self.config["archive_dir"], "config.json")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
    
    def load_config(self):
        if not self.config["archive_dir"] or not os.path.exists(self.config["archive_dir"]):
            return
        
        config_path = os.path.join(self.config["archive_dir"], "config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # 更新配置，但保留当前的监控状态
                    watching = self.watching
                    self.config.update(loaded_config)
                    self.watching = watching
                    # 更新UI状态
                    if hasattr(self, 'watch_changes_var'):
                        self.watch_changes_var.set(self.config.get("watch_changes", True))
        except Exception as e:
            print(f"加载配置失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeArchiver(root)
    root.mainloop()