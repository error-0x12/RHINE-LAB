#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分析平台
功能包括：编码解码、图片处理、音频处理、视频处理、文本处理、命令表等
"""

import base64
import hashlib
import os
import re
import json
import struct
from io import BytesIO

# 尝试导入常用的多媒体处理库
try:
    import cv2
    import numpy as np
    import PIL.Image as Image
    import PIL.ImageFilter as ImageFilter
    import PIL.ImageOps as ImageOps
except ImportError:
    print("警告：图像处理库未安装，某些图片处理功能将不可用。请安装opencv-python和Pillow。")
    Image = None
    ImageFilter = None
    ImageOps = None
    cv2 = None
    np = None

try:
    import librosa
    import soundfile as sf
except ImportError:
    print("警告：音频处理库未安装，某些音频处理功能将不可用。请安装librosa和soundfile。")
    librosa = None
    sf = None

# 尝试导入video处理库
try:
    # moviepy 2.2.1版本不再使用moviepy.editor模块
    from moviepy.video.io.VideoFileClip import VideoFileClip
    # 创建一个与旧版兼容的mp对象
    class MoviePyWrapper:
        VideoFileClip = VideoFileClip
    mp = MoviePyWrapper()
except ImportError:
    print("警告：视频处理库未安装或版本不兼容，某些视频处理功能将不可用。请安装moviepy 2.0+版本。")
    mp = None


class DataAnalysisPlatform:
    """数据分析平台主类"""

    def __init__(self):
        """初始化数据分析平台"""
        pass

    # ===== 编码解码功能 =====
    def encode_base64(self, data):
        """对数据进行Base64编码"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.b64encode(data).decode('utf-8')

    def decode_base64(self, encoded_data):
        """对Base64编码的数据进行解码"""
        try:
            return base64.b64decode(encoded_data).decode('utf-8')
        except Exception as e:
            return f"解码失败: {str(e)}"

    def calculate_hash(self, data, algorithm='md5'):
        """计算数据的哈希值"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha224': hashlib.sha224,
            'sha256': hashlib.sha256,
            'sha384': hashlib.sha384,
            'sha512': hashlib.sha512
        }
        
        if algorithm not in algorithms:
            return f"不支持的哈希算法: {algorithm}"
        
        hash_obj = algorithms[algorithm]()
        hash_obj.update(data)
        return hash_obj.hexdigest()

    def encode_hex(self, data):
        """将数据编码为十六进制字符串"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return data.hex()

    def decode_hex(self, hex_str):
        """将十六进制字符串解码为原始数据"""
        try:
            return bytes.fromhex(hex_str).decode('utf-8')
        except Exception as e:
            return f"解码失败: {str(e)}"

    # ===== 图片处理功能 =====
    def resize_image(self, image_path, width, height, output_path=None):
        """调整图片大小"""
        if Image is None:
            return "错误：Pillow库未安装"
        
        try:
            img = Image.open(image_path)
            resized_img = img.resize((width, height))
            
            if output_path:
                resized_img.save(output_path)
            return "图片调整大小成功"
        except Exception as e:
            return f"处理失败: {str(e)}"

    def convert_image_format(self, image_path, format_type, output_path=None):
        """转换图片格式"""
        if Image is None:
            return "错误：Pillow库未安装"
        
        try:
            img = Image.open(image_path)
            
            if not output_path:
                base_name = os.path.splitext(image_path)[0]
                output_path = f"{base_name}.{format_type.lower()}"
            
            img.save(output_path, format=format_type.upper())
            return f"图片已转换为{format_type}格式"
        except Exception as e:
            return f"处理失败: {str(e)}"

    def grayscale_image(self, image_path, output_path=None):
        """将图片转换为灰度图"""
        if Image is None:
            return "错误：Pillow库未安装"
        
        try:
            img = Image.open(image_path)
            gray_img = ImageOps.grayscale(img)
            
            if output_path:
                gray_img.save(output_path)
            else:
                gray_img.save(image_path)
            return "图片已转换为灰度图"
        except Exception as e:
            return f"处理失败: {str(e)}"

    def blur_image(self, image_path, radius=2, output_path=None):
        """模糊图片"""
        if Image is None:
            return "错误：Pillow库未安装"
        
        try:
            img = Image.open(image_path)
            blurred_img = img.filter(ImageFilter.GaussianBlur(radius))
            
            if output_path:
                blurred_img.save(output_path)
            else:
                blurred_img.save(image_path)
            return "图片已模糊处理"
        except Exception as e:
            return f"处理失败: {str(e)}"

    # ===== 音频处理功能 =====
    def get_audio_info(self, audio_path):
        """获取音频文件信息"""
        if librosa is None:
            return "错误：librosa库未安装"
        
        try:
            y, sr = librosa.load(audio_path)
            duration = librosa.get_duration(y=y, sr=sr)
            
            info = {
                "采样率": sr,
                "时长(秒)": duration,
                "帧数": len(y),
                "通道数": 1 if len(y.shape) == 1 else y.shape[1]
            }
            
            return info
        except Exception as e:
            return f"处理失败: {str(e)}"

    def convert_audio_format(self, audio_path, format_type, output_path=None):
        """转换音频格式"""
        if sf is None:
            return "错误：soundfile库未安装"
        
        try:
            data, samplerate = sf.read(audio_path)
            
            if not output_path:
                base_name = os.path.splitext(audio_path)[0]
                output_path = f"{base_name}.{format_type.lower()}"
            
            sf.write(output_path, data, samplerate)
            return f"音频已转换为{format_type}格式"
        except Exception as e:
            return f"处理失败: {str(e)}"

    def change_audio_speed(self, audio_path, speed_factor, output_path=None):
        """改变音频速度"""
        if librosa is None or sf is None:
            return "错误：librosa或soundfile库未安装"
        
        try:
            y, sr = librosa.load(audio_path)
            
            # 使用time_stretch改变速度
            y_stretched = librosa.effects.time_stretch(y, rate=speed_factor)
            
            if not output_path:
                base_name = os.path.splitext(audio_path)[0]
                output_path = f"{base_name}_speed_{speed_factor}.wav"
            
            sf.write(output_path, y_stretched, sr)
            return f"音频速度已调整为原来的{speed_factor}倍"
        except Exception as e:
            return f"处理失败: {str(e)}"

    # ===== 视频处理功能 =====
    def get_video_info(self, video_path):
        """获取视频文件信息"""
        if mp is None:
            return "错误：moviepy库未安装"
        
        try:
            video = mp.VideoFileClip(video_path)
            
            info = {
                "时长(秒)": video.duration,
                "分辨率": f"{video.w}x{video.h}",
                "帧率": video.fps,
                "音频采样率": video.audio.fps if video.audio else "无音频"
            }
            
            video.close()
            return info
        except Exception as e:
            return f"处理失败: {str(e)}"

    def extract_audio_from_video(self, video_path, output_path=None):
        """从视频中提取音频"""
        if mp is None:
            return "错误：moviepy库未安装"
        
        try:
            video = mp.VideoFileClip(video_path)
            
            if not output_path:
                base_name = os.path.splitext(video_path)[0]
                output_path = f"{base_name}.mp3"
            
            video.audio.write_audiofile(output_path)
            video.close()
            return f"音频已从视频中提取到{output_path}"
        except Exception as e:
            return f"处理失败: {str(e)}"

    def trim_video(self, video_path, start_time, end_time, output_path=None):
        """裁剪视频"""
        if mp is None:
            return "错误：moviepy库未安装"
        
        try:
            video = mp.VideoFileClip(video_path).subclip(start_time, end_time)
            
            if not output_path:
                base_name = os.path.splitext(video_path)[0]
                output_path = f"{base_name}_trimmed.mp4"
            
            video.write_videofile(output_path)
            video.close()
            return f"视频已裁剪并保存到{output_path}"
        except Exception as e:
            return f"处理失败: {str(e)}"

    # ===== 文本处理功能 =====
    def count_words(self, text):
        """统计文本中的单词数量"""
        words = re.findall(r'\b\w+\b', text)
        return len(words)

    def count_chars(self, text):
        """统计文本中的字符数量"""
        return len(text)

    def count_lines(self, text):
        """统计文本中的行数"""
        return len(text.split('\n'))

    def extract_emails(self, text):
        """从文本中提取邮箱地址"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(pattern, text)

    def extract_urls(self, text):
        """从文本中提取URL"""
        pattern = r'https?://[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?'
        return re.findall(pattern, text)

    def text_to_json(self, text, key_name="text"):
        """将文本转换为JSON格式"""
        try:
            return json.dumps({key_name: text}, ensure_ascii=False)
        except Exception as e:
            return f"转换失败: {str(e)}"

    # ===== 文件处理功能 =====
    def read_binary_file(self, file_path, max_bytes=None):
        """读取二进制文件内容"""
        try:
            with open(file_path, 'rb') as f:
                if max_bytes:
                    data = f.read(max_bytes)
                else:
                    data = f.read()
            return {
                "success": True,
                "data": data,
                "size": len(data),
                "file_path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def write_binary_file(self, file_path, data):
        """写入二进制数据到文件"""
        try:
            with open(file_path, 'wb') as f:
                f.write(data)
            return f"成功写入{len(data)}字节到{file_path}"
        except Exception as e:
            return f"写入失败: {str(e)}"

    def edit_binary_file(self, file_path, offset, new_data):
        """编辑二进制文件的特定位置"""
        try:
            # 读取整个文件
            with open(file_path, 'rb+') as f:
                # 获取文件大小
                f.seek(0, 2)
                file_size = f.tell()
                
                # 检查偏移量是否有效
                if offset < 0 or offset > file_size:
                    return f"无效的偏移量: {offset}"
                
                # 移动到指定偏移量
                f.seek(offset)
                
                # 写入新数据
                bytes_written = f.write(new_data)
                
            return f"成功在偏移量{offset}处写入{bytes_written}字节"
        except Exception as e:
            return f"编辑失败: {str(e)}"

    def compare_files(self, file_path1, file_path2, block_size=4096):
        """比较两个文件的内容"""
        try:
            with open(file_path1, 'rb') as f1, open(file_path2, 'rb') as f2:
                # 比较文件大小
                f1.seek(0, 2)
                f2.seek(0, 2)
                size1 = f1.tell()
                size2 = f2.tell()
                
                if size1 != size2:
                    return {
                        "are_identical": False,
                        "reason": f"文件大小不同: {size1} vs {size2}",
                        "size1": size1,
                        "size2": size2
                    }
                
                # 重置文件指针
                f1.seek(0)
                f2.seek(0)
                
                # 分块比较内容
                block_num = 0
                while True:
                    block1 = f1.read(block_size)
                    block2 = f2.read(block_size)
                    
                    if not block1 and not block2:
                        break
                    
                    if block1 != block2:
                        # 找到不同的位置
                        diff_pos = 0
                        while diff_pos < len(block1) and diff_pos < len(block2):
                            if block1[diff_pos] != block2[diff_pos]:
                                absolute_pos = block_num * block_size + diff_pos
                                return {
                                    "are_identical": False,
                                    "reason": "文件内容不同",
                                    "first_diff_position": absolute_pos,
                                    "size1": size1,
                                    "size2": size2
                                }
                            diff_pos += 1
                    
                    block_num += 1
                
            return {
                "are_identical": True,
                "size": size1
            }
        except Exception as e:
            return {
                "are_identical": False,
                "error": str(e)
            }

    def calculate_file_hash(self, file_path, algorithm='md5', block_size=8192):
        """计算文件的哈希值"""
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha224': hashlib.sha224,
            'sha256': hashlib.sha256,
            'sha384': hashlib.sha384,
            'sha512': hashlib.sha512
        }
        
        if algorithm not in algorithms:
            return f"不支持的哈希算法: {algorithm}"
        
        try:
            hash_obj = algorithms[algorithm]()
            with open(file_path, 'rb') as f:
                while chunk := f.read(block_size):
                    hash_obj.update(chunk)
            
            return {
                "success": True,
                "file_path": file_path,
                "algorithm": algorithm,
                "hash": hash_obj.hexdigest()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_file_structure(self, file_path, bytes_per_line=16):
        """分析并返回文件的二进制结构"""
        try:
            result = self.read_binary_file(file_path)
            if not result["success"]:
                return result
            
            data = result["data"]
            hex_lines = []
            
            for i in range(0, len(data), bytes_per_line):
                chunk = data[i:i+bytes_per_line]
                
                # 十六进制部分
                hex_part = ' '.join([f'{byte:02x}' for byte in chunk])
                
                # 字符部分（可打印字符显示，不可打印字符显示为.）
                char_part = ''.join([chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk])
                
                # 格式化行
                line = f'{i:08x}: {hex_part:<{bytes_per_line*3-1}} | {char_part}'
                hex_lines.append(line)
            
            return {
                "success": True,
                "file_path": file_path,
                "file_size": len(data),
                "hex_view": '\n'.join(hex_lines)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# ===== 命令表功能 =====
    def get_windows_commands(self):
        """获取常用Windows PowerShell命令"""
        commands = {
            "文件操作": {
                "ls": "列出目录内容",
                "cd": "更改目录",
                "mkdir": "创建新目录",
                "rm": "删除文件或目录",
                "cp": "复制文件或目录",
                "mv": "移动或重命名文件或目录"
            },
            "系统信息": {
                "systeminfo": "显示系统信息",
                "tasklist": "显示运行中的进程列表",
                "ipconfig": "显示网络配置信息"
            },
            "网络工具": {
                "ping": "测试网络连接",
                "tracert": "跟踪数据包路径",
                "nslookup": "查询DNS信息"
            }
        }
        return commands

    def get_linux_commands(self):
        """获取常用Linux命令"""
        commands = {
            "文件操作": {
                "ls": "列出目录内容",
                "cd": "更改目录",
                "mkdir": "创建新目录",
                "rm": "删除文件或目录",
                "cp": "复制文件或目录",
                "mv": "移动或重命名文件或目录"
            },
            "系统信息": {
                "uname": "显示系统信息",
                "ps": "显示进程状态",
                "top": "显示进程信息并实时更新",
                "df": "显示磁盘使用情况"
            },
            "网络工具": {
                "ping": "测试网络连接",
                "traceroute": "跟踪数据包路径",
                "ifconfig": "显示或配置网络接口"
            }
        }
        return commands


# 主程序入口（仅用于测试）
