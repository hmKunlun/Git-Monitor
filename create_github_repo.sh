#!/bin/bash

# 设置终端颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}           Git命令监控工具 - GitHub仓库创建脚本            ${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 检查Git是否安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}[错误] 未检测到Git。请先安装Git。${NC}"
    echo "Ubuntu/Debian: sudo apt install git"
    echo "Fedora/RHEL: sudo dnf install git"
    echo "macOS: brew install git"
    exit 1
fi

# 询问GitHub用户名和仓库名
read -p "请输入GitHub用户名: " GITHUB_USER
if [ -z "$GITHUB_USER" ]; then
    echo -e "${RED}[错误] 用户名不能为空。${NC}"
    exit 1
fi

read -p "请输入仓库名 (例如: git-command-monitor): " REPO_NAME
if [ -z "$REPO_NAME" ]; then
    echo -e "${RED}[错误] 仓库名不能为空。${NC}"
    exit 1
fi

# 构建仓库URL
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo -e "${YELLOW}[信息] 将使用仓库URL: $REPO_URL${NC}"
read -p "是否正确？(y/n): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo -e "${YELLOW}[信息] 请重新运行脚本并提供正确的信息。${NC}"
    exit 0
fi

# 询问是否先在GitHub上创建仓库
echo ""
read -p "是否需要先在GitHub上创建仓库？(y/n): " CREATE_REPO
if [ "$CREATE_REPO" = "y" ] || [ "$CREATE_REPO" = "Y" ]; then
    echo -e "${YELLOW}[信息] 请按照以下步骤在GitHub上创建仓库：${NC}"
    echo "1. 访问 https://github.com/new"
    echo "2. 仓库名设置为: $REPO_NAME"
    echo "3. 选择公开或私有"
    echo "4. 不要初始化README、.gitignore或许可证"
    echo "5. 点击'创建仓库'"
    echo ""
    read -p "完成后按Enter继续..." CONTINUE
fi

# 创建必要的空目录和.gitkeep文件
echo -e "${YELLOW}[信息] 创建必要的目录结构...${NC}"
mkdir -p data logs reports
touch data/.gitkeep logs/.gitkeep reports/.gitkeep
echo -e "${GREEN}[成功] 目录结构创建完成。${NC}"

# 确保config.json存在，如果不存在，则从example复制
if [ ! -f "config.json" ]; then
    if [ -f "config.example.json" ]; then
        echo -e "${YELLOW}[信息] 复制配置文件模板...${NC}"
        cp config.example.json config.json
        echo -e "${GREEN}[成功] 已创建配置文件。${NC}"
    else
        echo -e "${YELLOW}[警告] 未找到config.example.json，请确保创建一个config.json配置文件。${NC}"
    fi
fi

# 初始化Git仓库
echo ""
echo -e "${YELLOW}[信息] 正在初始化Git仓库...${NC}"
git init
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 初始化Git仓库失败。${NC}"
    exit 1
fi
echo -e "${GREEN}[成功] Git仓库初始化完成。${NC}"

# 添加所有文件
echo ""
echo -e "${YELLOW}[信息] 添加文件到Git仓库...${NC}"
git add .
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 添加文件失败。${NC}"
    exit 1
fi
echo -e "${GREEN}[成功] 文件已添加到仓库。${NC}"

# 提交所有文件
echo ""
echo -e "${YELLOW}[信息] 提交文件...${NC}"
git commit -m "Initial commit: Git Command Monitor Tool"
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 提交文件失败。请确保已配置Git用户名和邮箱。${NC}"
    echo "提示: 使用以下命令配置"
    echo "  git config --global user.name \"你的名字\""
    echo "  git config --global user.email \"你的邮箱\""
    exit 1
fi
echo -e "${GREEN}[成功] 文件已提交。${NC}"

# 添加远程仓库
echo ""
echo -e "${YELLOW}[信息] 添加远程仓库...${NC}"
git remote add origin "$REPO_URL"
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 添加远程仓库失败。请检查仓库URL是否正确。${NC}"
    exit 1
fi
echo -e "${GREEN}[成功] 远程仓库已添加。${NC}"

# 询问默认分支名称
echo ""
read -p "请输入要使用的默认分支名称 (通常是main或master): " BRANCH_NAME
if [ -z "$BRANCH_NAME" ]; then
    BRANCH_NAME="main"
    echo -e "${YELLOW}[信息] 使用默认分支名: $BRANCH_NAME${NC}"
fi

# 重命名当前分支
git branch -M "$BRANCH_NAME"

# 询问是否推送到远程仓库
echo ""
read -p "是否立即推送到远程仓库？(y/n): " PUSH_NOW
if [ "$PUSH_NOW" = "y" ] || [ "$PUSH_NOW" = "Y" ]; then
    echo ""
    echo -e "${YELLOW}[信息] 推送到远程仓库...${NC}"
    git push -u origin "$BRANCH_NAME"
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 推送失败。请检查仓库权限和网络连接。${NC}"
        echo "你可能需要通过浏览器授权GitHub访问。"
        exit 1
    fi
    echo -e "${GREEN}[成功] 代码已成功推送到远程仓库。${NC}"
else
    echo ""
    echo -e "${YELLOW}[信息] 跳过推送。你可以稍后使用以下命令手动推送:${NC}"
    echo "  git push -u origin $BRANCH_NAME"
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}                      操作完成！                          ${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo "下一步："
echo "1. 在GitHub上查看你的仓库: https://github.com/$GITHUB_USER/$REPO_NAME"
echo "2. 添加详细的README.md描述"
echo "3. 邀请贡献者并分享你的项目"
echo ""
echo -e "${GREEN}祝你的开源项目成功！${NC}"
echo "" 