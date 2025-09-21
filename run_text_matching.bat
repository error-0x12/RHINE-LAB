@echo off

REM 检查Python是否安装
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到Python。请先安装Python。
    pause
    exit /b 1
)

REM 检查AutoMod库是否存在
if not exist "%~dp0\automod" (
    echo 警告: 未找到AutoMod库。请确保AutoMod库已正确安装在当前目录。
    pause
)

REM 运行文字匹配自动化程序
echo 正在启动文字匹配自动化程序...
echo 按Ctrl+C可以随时终止程序。
echo.
python "%~dp0\text_matching_automation.py"

REM 如果程序异常退出，显示错误信息
if %errorlevel% neq 0 (
    echo.
    echo 程序执行出错，请检查错误信息。
    pause
    exit /b %errorlevel%
)

pause