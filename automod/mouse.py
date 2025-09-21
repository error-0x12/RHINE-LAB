"""
鼠标模拟模块

提供鼠标控制功能，支持模拟人类操作。
"""

import time
import random
import math
from typing import Tuple, Optional, Union
from .config import AutoModConfig

class MouseSimulator:
    """鼠标模拟器，用于控制鼠标移动、点击等操作"""
    
    def __init__(self, config: Optional[AutoModConfig] = None):
        """初始化鼠标模拟器"""
        self.config = config or AutoModConfig()
        self._init_mouse()
        
    def _init_mouse(self):
        """初始化鼠标控制库"""
        try:
            import pyautogui
            # 设置PyAutoGUI的安全功能
            pyautogui.FAILSAFE = True
            # 设置延迟，使操作更可靠
            pyautogui.PAUSE = self.config.get('mouse', 'click_delay', 0.1)
            self.mouse = pyautogui
        except ImportError:
            raise ImportError("请安装pyautogui: pip install pyautogui")
            
    def get_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        return self.mouse.position()
        
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> "MouseSimulator":
        """
        移动鼠标到指定位置
        
        参数:
            x: 目标x坐标
            y: 目标y坐标
            duration: 移动持续时间（秒），为None时使用配置的速度
        """
        if duration is None:
            speed = self.config.get('mouse', 'move_speed', 1.0)
            # 根据距离计算持续时间，使速度更自然
            current_x, current_y = self.get_position()
            distance = math.sqrt((x - current_x) **2 + (y - current_y)** 2)
            duration = distance / (1000 * speed)
            # 限制最短和最长持续时间
            duration = max(0.05, min(duration, 2.0))
        
        smooth_move = self.config.get('mouse', 'smooth_move', True)
        human_like = self.config.get('mouse', 'human_like', True)
        
        if smooth_move and human_like:
            # 模拟人类移动路径（带加速度和微小抖动）
            self._human_like_move(x, y, duration)
        else:
            # 直接移动
            self.mouse.moveTo(x, y, duration=duration)
            
        return self
        
    def _human_like_move(self, x: int, y: int, duration: float) -> None:
        """模拟人类风格的鼠标移动"""
        current_x, current_y = self.get_position()
        start_time = time.time()
        
        # 计算总距离
        total_distance = math.sqrt((x - current_x) ** 2 + (y - current_y) ** 2)
        
        # 生成贝塞尔曲线控制点，创建更自然的路径
        control_points = self._generate_bezier_control_points(current_x, current_y, x, y)
        
        # 移动过程
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            progress = elapsed / duration
            
            # 应用加速度曲线（人类通常开始慢，中间快，结束慢）
            progress = self._apply_acceleration_curve(progress)
            
            # 计算当前位置
            px, py = self._calculate_bezier_point(progress, current_x, current_y, *control_points, x, y)
            
            # 添加微小抖动，使移动更自然
            jitter_x = random.uniform(-2, 2) if progress > 0.1 and progress < 0.9 else 0
            jitter_y = random.uniform(-2, 2) if progress > 0.1 and progress < 0.9 else 0
            
            # 移动到当前计算的位置
            self.mouse.moveTo(px + jitter_x, py + jitter_y, duration=0)
            
            # 短暂暂停，控制移动平滑度
            time.sleep(0.005)
        
        # 确保最终位置准确
        self.mouse.moveTo(x, y, duration=0)
        
    def _generate_bezier_control_points(self, x1: int, y1: int, x4: int, y4: int) -> Tuple[int, int, int, int]:
        """生成贝塞尔曲线的控制点"""
        # 随机偏移，使路径不那么直线
        offset_range = max(50, int(math.sqrt((x4 - x1)**2 + (y4 - y1)** 2) * 0.2))
        
        # 第一个控制点
        cx2 = x1 + random.randint(-offset_range, offset_range)
        cy2 = y1 + random.randint(-offset_range, offset_range)
        
        # 第二个控制点
        cx3 = x4 + random.randint(-offset_range, offset_range)
        cy3 = y4 + random.randint(-offset_range, offset_range)
        
        return cx2, cy2, cx3, cy3
        
    def _apply_acceleration_curve(self, progress: float) -> float:
        """应用加速度曲线，使移动更自然"""
        # S型曲线，开始和结束较慢，中间较快
        if progress < 0.5:
            return 2 * progress * progress
        else:
            return -1 + (4 - 2 * progress) * progress
        
    def _calculate_bezier_point(self, t: float, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, x4: int, y4: int) -> Tuple[float, float]:
        """计算贝塞尔曲线上的点"""
        cx = 3 * (x2 - x1)
        bx = 3 * (x3 - x2) - cx
        ax = x4 - x1 - cx - bx
        
        cy = 3 * (y2 - y1)
        by = 3 * (y3 - y2) - cy
        ay = y4 - y1 - cy - by
        
        px = ax * (t**3) + bx * (t**2) + cx * t + x1
        py = ay * (t**3) + by * (t**2) + cy * t + y1
        
        return px, py
        
    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = 'left', clicks: int = 1) -> "MouseSimulator":
        """
        点击鼠标
        
        参数:
            x: 点击位置x坐标，为None时使用当前位置
            y: 点击位置y坐标，为None时使用当前位置
            button: 按钮类型 ('left', 'right', 'middle')
            clicks: 点击次数
        """
        if x is not None and y is not None:
            self.move_to(x, y)
            
        # 添加随机延迟，使点击更自然
        delay = self.config.get('mouse', 'click_delay', 0.1)
        time.sleep(delay + random.uniform(-0.03, 0.03))
        
        # 执行点击
        self.mouse.click(button=button, clicks=clicks)
        
        # 点击后添加延迟
        time.sleep(delay + random.uniform(-0.02, 0.02))
        
        return self
        
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = 'left') -> "MouseSimulator":
        """
        双击鼠标
        
        参数:
            x: 点击位置x坐标，为None时使用当前位置
            y: 点击位置y坐标，为None时使用当前位置
            button: 按钮类型 ('left', 'right', 'middle')
        """
        return self.click(x, y, button, clicks=2)
        
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> "MouseSimulator":
        """
        右键点击
        
        参数:
            x: 点击位置x坐标，为None时使用当前位置
            y: 点击位置y坐标，为None时使用当前位置
        """
        return self.click(x, y, button='right')
        
    def drag_to(self, x: int, y: int, duration: Optional[float] = None, button: str = 'left') -> "MouseSimulator":
        """
        拖拽鼠标
        
        参数:
            x: 目标x坐标
            y: 目标y坐标
            duration: 拖拽持续时间（秒）
            button: 按钮类型 ('left', 'right', 'middle')
        """
        # 按下鼠标按钮
        self.mouse.mouseDown(button=button)
        
        # 添加小延迟
        time.sleep(0.05 + random.uniform(0, 0.05))
        
        # 移动鼠标
        self.move_to(x, y, duration)
        
        # 添加小延迟
        time.sleep(0.05 + random.uniform(0, 0.05))
        
        # 释放鼠标按钮
        self.mouse.mouseUp(button=button)
        
        return self
        
    def scroll(self, clicks: int) -> "MouseSimulator":
        """
        滚动鼠标滚轮
        
        参数:
            clicks: 滚动的格数，正数向上，负数向下
        """
        self.mouse.scroll(clicks=clicks)
        return self
        
    def move_relative(self, dx: int, dy: int, duration: Optional[float] = None) -> "MouseSimulator":
        """
        相对当前位置移动鼠标
        
        参数:
            dx: x方向移动距离
            dy: y方向移动距离
            duration: 移动持续时间（秒）
        """
        current_x, current_y = self.get_position()
        return self.move_to(current_x + dx, current_y + dy, duration)
        
    def click_region(self, region: Tuple[int, int, int, int], button: str = 'left') -> "MouseSimulator":
        """
        在指定区域内随机位置点击
        
        参数:
            region: (x, y, width, height) 区域坐标
            button: 按钮类型 ('left', 'right', 'middle')
        """
        rx, ry, rw, rh = region
        # 在区域内随机选择一个点，但不选择边缘
        x = rx + 5 + random.randint(0, rw - 10)
        y = ry + 5 + random.randint(0, rh - 10)
        
        return self.click(x, y, button)
        
    def wait_for_position(self, x: int, y: int, tolerance: int = 5, timeout: float = 10) -> bool:
        """
        等待鼠标移动到指定位置
        
        参数:
            x: 目标x坐标
            y: 目标y坐标
            tolerance: 容差范围
            timeout: 超时时间（秒）
        
        返回:
            是否在超时前达到目标位置
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_x, current_y = self.get_position()
            if abs(current_x - x) <= tolerance and abs(current_y - y) <= tolerance:
                return True
            time.sleep(0.05)
        return False