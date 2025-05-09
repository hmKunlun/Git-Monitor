@echo off
echo ======================================================
echo  开始使用PyInstaller打包Git命令监控应用
echo ======================================================

REM 安装PyInstaller（如果尚未安装）
pip install pyinstaller

REM 使用最简单的命令打包
pyinstaller --onedir --windowed --name=GitCommandMonitor^
 --add-data "config.json;."^
 --hidden-import=PyQt5^
 --hidden-import=PyQt5.QtCore^
 --hidden-import=PyQt5.QtGui^
 --hidden-import=PyQt5.QtWidgets^
 --hidden-import=matplotlib^
 --hidden-import=pandas^
 --hidden-import=jinja2^
 --hidden-import=markdown^
 tray_app.py

REM 检查构建结果
if %ERRORLEVEL% NEQ 0 (
    echo 构建失败。尝试使用更简单的命令...
    pyinstaller --onedir --windowed --name=GitCommandMonitor tray_app.py
)

REM 创建必要的目录
mkdir "dist\GitCommandMonitor\data" 2>nul
mkdir "dist\GitCommandMonitor\logs" 2>nul
mkdir "dist\GitCommandMonitor\reports" 2>nul

REM 复制运行脚本到dist目录
copy "run_tray_hidden.py" "dist\GitCommandMonitor\" /Y
copy "run_background.py" "dist\GitCommandMonitor\" /Y
copy "background_monitor.py" "dist\GitCommandMonitor\" /Y

echo.
echo 打包完成！
echo 程序位于: %CD%\dist\GitCommandMonitor\GitCommandMonitor.exe
echo 可以使用 run_tray_hidden.py 来在无窗口模式下运行应用
echo.

pause 