@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo                Git命令监控工具 - 仓库创建脚本
echo ============================================================
echo.

REM 检查Git是否安装
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Git。请先安装Git并确保其在PATH环境变量中。
    echo 下载地址: https://git-scm.com/download/win
    goto :EOF
)

REM 询问GitHub仓库URL
set /p REPO_URL=请输入GitHub仓库URL（例如: https://github.com/yourusername/git-command-monitor.git）: 
if "!REPO_URL!"=="" (
    echo [错误] 仓库URL不能为空。
    goto :EOF
)

REM 创建必要的空目录和.gitkeep文件
echo [信息] 创建必要的目录结构...
if not exist "data\" mkdir data
if not exist "logs\" mkdir logs
if not exist "reports\" mkdir reports
type nul > data\.gitkeep
type nul > logs\.gitkeep
type nul > reports\.gitkeep
echo [成功] 目录结构创建完成。

REM 确保config.json存在，如果不存在，则从example复制
if not exist "config.json" (
    if exist "config.example.json" (
        echo [信息] 复制配置文件模板...
        copy "config.example.json" "config.json"
        echo [成功] 已创建配置文件。
    ) else (
        echo [警告] 未找到config.example.json，请确保创建一个config.json配置文件。
    )
)

REM 初始化Git仓库
echo.
echo [信息] 正在初始化Git仓库...
git init
if %errorlevel% neq 0 (
    echo [错误] 初始化Git仓库失败。
    goto :EOF
)
echo [成功] Git仓库初始化完成。

REM 添加所有文件
echo.
echo [信息] 添加文件到Git仓库...
git add .
if %errorlevel% neq 0 (
    echo [错误] 添加文件失败。
    goto :EOF
)
echo [成功] 文件已添加到仓库。

REM 提交所有文件
echo.
echo [信息] 提交文件...
git commit -m "Initial commit: Git Command Monitor Tool"
if %errorlevel% neq 0 (
    echo [错误] 提交文件失败。请确保已配置Git用户名和邮箱。
    echo 提示: 使用以下命令配置
    echo   git config --global user.name "你的名字"
    echo   git config --global user.email "你的邮箱"
    goto :EOF
)
echo [成功] 文件已提交。

REM 添加远程仓库
echo.
echo [信息] 添加远程仓库...
git remote add origin !REPO_URL!
if %errorlevel% neq 0 (
    echo [错误] 添加远程仓库失败。请检查仓库URL是否正确。
    goto :EOF
)
echo [成功] 远程仓库已添加。

REM 询问默认分支名称
echo.
set /p BRANCH_NAME=请输入要使用的默认分支名称 (通常是main或master，默认为main): 
if "!BRANCH_NAME!"=="" set BRANCH_NAME=main
echo [信息] 使用分支名: !BRANCH_NAME!

REM 重命名分支
git branch -M !BRANCH_NAME!

REM 询问是否推送到远程仓库
echo.
set /p PUSH_NOW=是否立即推送到远程仓库？(Y/N): 
if /i "!PUSH_NOW!"=="Y" (
    echo.
    echo [信息] 推送到远程仓库...
    git push -u origin !BRANCH_NAME!
    if %errorlevel% neq 0 (
        echo [错误] 推送失败。请检查仓库权限和网络连接。
        goto :EOF
    )
    echo [成功] 代码已成功推送到远程仓库。
) else (
    echo.
    echo [信息] 跳过推送。你可以稍后使用以下命令手动推送:
    echo   git push -u origin !BRANCH_NAME!
)

echo.
echo ============================================================
echo                      操作完成！
echo ============================================================
echo.
echo 下一步：
echo 1. 在GitHub上查看你的仓库
echo 2. 添加详细的README.md描述
echo 3. 邀请贡献者并分享你的项目
echo.
echo 祝你的开源项目成功！
echo.

pause 