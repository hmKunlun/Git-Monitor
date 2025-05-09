# 贡献指南

感谢您对Git命令监控工具项目的兴趣！我们欢迎各种形式的贡献，包括功能开发、错误修复、文档改进或使用反馈。

## 如何贡献

### 报告问题

如果您发现了问题或有改进建议，请按以下步骤操作：

1. 检查现有 Issues，避免重复报告
2. 使用 Issue 模板（如有），提供尽可能多的细节
3. 包括操作系统、Python版本、Git版本等环境信息
4. 如果可能，添加截图或者复现步骤

### 提交代码

1. Fork 此仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m '添加了某某功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建新的 Pull Request

### 开发规范

请遵循以下规范进行开发：

- 使用清晰的注释说明代码功能
- 保持代码风格一致（建议使用PEP 8标准）
- 新功能需要添加相应的文档说明
- 在提交前测试您的代码

### 分支命名规范

- `feature/*`: 新功能开发
- `bugfix/*`: 错误修复
- `docs/*`: 文档更新
- `refactor/*`: 代码重构（不改变功能）
- `test/*`: 添加或修改测试

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/yourusername/git-command-monitor.git
cd git-command-monitor

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt  # 如果存在
```

## 目录结构

```
gitmonitor/              # 核心模块
├── __init__.py
├── monitor.py           # 监控逻辑
├── git_analyzer.py      # Git命令分析
├── report.py            # 报告生成
└── utils.py             # 工具函数
```

## 未来计划

我们正在考虑的功能和改进包括：

- 添加更多的Git操作分析
- 提供更丰富的报告视图
- 支持Linux和macOS平台
- 添加网页界面

如果您对这些方向有兴趣，欢迎联系我们讨论具体的实现方案。

## 行为准则

请尊重所有项目参与者，保持良好的交流氛围。不接受任何形式的骚扰或冒犯性言论。 