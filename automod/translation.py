"""
翻译模块

提供文本翻译功能，支持多种翻译服务。
"""

import time
import json
import requests
from typing import Dict, Optional, Tuple, Union
from .config import AutoModConfig

class Translator:
    """翻译器，用于文本翻译"""
    
    def __init__(self, config: Optional[AutoModConfig] = None):
        """初始化翻译器"""
        self.config = config or AutoModConfig()
        self._session = requests.Session()
        # 设置代理（如果有）
        proxy = self.config.get('translation', 'proxy', None)
        if proxy:
            self._session.proxies = {
                'http': proxy,
                'https': proxy
            }
        
    def translate(self, text: str, src_lang: str = 'auto', dest_lang: str = 'zh') -> Dict:
        """
        翻译文本
        
        参数:
            text: 要翻译的文本
            src_lang: 源语言，'auto'表示自动检测
            dest_lang: 目标语言
        
        返回:
            包含翻译结果的字典
        """
        if not text.strip():
            return {
                'text': text,
                'translated_text': '',
                'src_lang': src_lang,
                'dest_lang': dest_lang,
                'service': None,
                'error': 'Empty text'
            }
            
        service = self.config.get('translation', 'service', 'google')
        
        try:
            if service == 'google':
                return self._translate_with_google(text, src_lang, dest_lang)
            elif service == 'baidu':
                return self._translate_with_baidu(text, src_lang, dest_lang)
            elif service == 'youdao':
                return self._translate_with_youdao(text, src_lang, dest_lang)
            else:
                raise ValueError(f"不支持的翻译服务: {service}")
        except Exception as e:
            # 如果首选服务失败，尝试使用谷歌翻译作为备选
            try:
                if service != 'google':
                    return self._translate_with_google(text, src_lang, dest_lang)
                else:
                    raise
            except:
                return {
                    'text': text,
                    'translated_text': '',
                    'src_lang': src_lang,
                    'dest_lang': dest_lang,
                    'service': service,
                    'error': str(e)
                }
                
    def _translate_with_google(self, text: str, src_lang: str, dest_lang: str) -> Dict:
        """使用谷歌翻译API翻译文本"""
        # 使用无API密钥的方式访问谷歌翻译（适用于小规模使用）
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": src_lang,
            "tl": dest_lang,
            "dt": "t",
            "q": text
        }
        
        try:
            timeout = self.config.get('translation', 'timeout', 10)
            response = self._session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            translated_text = ''.join([sentence[0] for sentence in data[0]])
            
            # 获取检测到的源语言
            detected_lang = data[2] if len(data) > 2 else src_lang
            
            return {
                'text': text,
                'translated_text': translated_text,
                'src_lang': detected_lang,
                'dest_lang': dest_lang,
                'service': 'google',
                'error': None
            }
        except Exception as e:
            raise RuntimeError(f"谷歌翻译失败: {str(e)}")
            
    def _translate_with_baidu(self, text: str, src_lang: str, dest_lang: str) -> Dict:
        """使用百度翻译API翻译文本"""
        # 百度翻译API配置
        appid = self.config.get('translation', 'api_key', None)
        secret_key = self.config.get('translation', 'api_secret', None)
        
        if not appid or not secret_key:
            raise ValueError("百度翻译需要提供api_key和api_secret")
            
        # 百度翻译语言代码映射
        lang_map = {
            'auto': 'auto',
            'zh': 'zh', 'en': 'en', 'ja': 'jp', 'ko': 'kor',
            'fr': 'fra', 'de': 'de', 'ru': 'ru', 'es': 'spa'
        }
        
        # 转换语言代码
        from_lang = lang_map.get(src_lang, src_lang)
        to_lang = lang_map.get(dest_lang, dest_lang)
        
        # 生成签名
        import hashlib
        salt = str(int(time.time()))
        sign = appid + text + salt + secret_key
        sign = hashlib.md5(sign.encode('utf-8')).hexdigest()
        
        # 发送请求
        url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': appid,
            'salt': salt,
            'sign': sign
        }
        
        try:
            timeout = self.config.get('translation', 'timeout', 10)
            response = self._session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            if 'error_code' in data:
                raise RuntimeError(f"百度翻译API错误: {data.get('error_msg', '未知错误')}")
                
            translated_text = ''.join([item['dst'] for item in data['trans_result']])
            
            return {
                'text': text,
                'translated_text': translated_text,
                'src_lang': from_lang,
                'dest_lang': to_lang,
                'service': 'baidu',
                'error': None
            }
        except Exception as e:
            raise RuntimeError(f"百度翻译失败: {str(e)}")
            
    def _translate_with_youdao(self, text: str, src_lang: str, dest_lang: str) -> Dict:
        """使用有道翻译API翻译文本"""
        # 有道翻译API配置
        app_key = self.config.get('translation', 'api_key', None)
        app_secret = self.config.get('translation', 'api_secret', None)
        
        if not app_key or not app_secret:
            raise ValueError("有道翻译需要提供api_key和api_secret")
            
        # 有道翻译语言代码映射
        lang_map = {
            'auto': 'auto',
            'zh': 'zh-CHS', 'en': 'en', 'ja': 'ja', 'ko': 'ko',
            'fr': 'fr', 'de': 'de', 'ru': 'ru', 'es': 'es'
        }
        
        # 转换语言代码
        from_lang = lang_map.get(src_lang, src_lang)
        to_lang = lang_map.get(dest_lang, dest_lang)
        
        # 生成签名
        import hashlib
        import time
        curtime = str(int(time.time()))
        sign_str = app_key + self._truncate(text) + curtime + app_secret
        sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
        
        # 发送请求
        url = "https://openapi.youdao.com/api"
        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appKey': app_key,
            'salt': curtime,
            'sign': sign,
            'signType': 'v3',
            'curtime': curtime
        }
        
        try:
            timeout = self.config.get('translation', 'timeout', 10)
            response = self._session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            if data.get('errorCode') != '0':
                raise RuntimeError(f"有道翻译API错误: {data.get('errorMsg', '未知错误')}")
                
            translated_text = data.get('translation', [''])[0]
            
            return {
                'text': text,
                'translated_text': translated_text,
                'src_lang': from_lang,
                'dest_lang': to_lang,
                'service': 'youdao',
                'error': None
            }
        except Exception as e:
            raise RuntimeError(f"有道翻译失败: {str(e)}")
            
    def _truncate(self, text: str) -> str:
        """截断文本以符合API限制"""
        if len(text) <= 20:
            return text
        return text[:10] + str(len(text)) + text[-10:]
        
    def detect_language(self, text: str) -> str:
        """
        检测文本语言
        
        参数:
            text: 要检测的文本
        
        返回:
            检测到的语言代码
        """
        result = self.translate(text, src_lang='auto', dest_lang='en')
        return result.get('src_lang', 'unknown')
        
    def batch_translate(self, texts: list, src_lang: str = 'auto', dest_lang: str = 'zh') -> list:
        """
        批量翻译文本列表
        
        参数:
            texts: 要翻译的文本列表
            src_lang: 源语言
            dest_lang: 目标语言
        
        返回:
            翻译结果列表
        """
        results = []
        
        for text in texts:
            result = self.translate(text, src_lang, dest_lang)
            results.append(result)
            
            # 添加延迟，避免触发API频率限制
            time.sleep(0.1)
            
        return results
        
    def translate_file(self, file_path: str, output_path: str, src_lang: str = 'auto', dest_lang: str = 'zh') -> Dict:
        """
        翻译文件内容
        
        参数:
            file_path: 源文件路径
            output_path: 输出文件路径
            src_lang: 源语言
            dest_lang: 目标语言
        
        返回:
            翻译结果信息
        """
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 翻译内容
            result = self.translate(content, src_lang, dest_lang)
            
            # 写入结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['translated_text'])
                
            return {
                'file_path': file_path,
                'output_path': output_path,
                'original_size': len(content),
                'translated_size': len(result['translated_text']),
                'src_lang': result['src_lang'],
                'dest_lang': result['dest_lang'],
                'success': True,
                'error': None
            }
        except Exception as e:
            return {
                'file_path': file_path,
                'output_path': output_path,
                'success': False,
                'error': str(e)
            }