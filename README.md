# Git操作监控工具 (Git Command Monitor)

一个为开发团队设计的Git命令系统级监控工具，可记录所有执行的Git操作，支持Windows系统。
可以一键导出日报周报记录，轻松解决工作周报。

## 功能特点

- 📝 完整记录系统中执行的所有Git命令
- 🔄 深入分析Git命令内容，详细展示提交和变更的文件
- 🔄 将数据存储为结构化JSON格式，便于后续分析
- 🖥️ 支持作为Windows服务在后台持续运行
- 📊 可进行日志分析和团队Git使用模式研究
- ⚙️ 灵活配置，可自定义监控行为
- 🔍 智能进程缓存，避免重复记录相同的命令
- 📈 自动生成日报、周报和月报（HTML和Markdown格式）
- 🛡️ 增强的错误处理和容错机制，适应各种复杂环境
- 🌐 全面支持中文和多语言环境
- 🔗 自动关联GitHub仓库，记录项目修改历史
- 🔤 智能中文字体处理，解决报告图表中文显示问题
- 🖼️ 系统托盘应用，支持后台运行和快速操作
- 🚀 开机自启动功能，无需手动启动

## 最新更新 (v0.4.0)

- 🖼️ 新增系统托盘应用，支持后台运行和托盘图标
- 🚀 添加开机自启动功能，可自动随系统启动
- 🖱️ 托盘右键菜单，快速生成日报、周报和月报
- 📅 可视化日期选择和报告格式选择
- 📂 快速访问报告目录和配置文件
- 🔄 监控引擎改为多线程模式，提高性能
- 🛠️ 用户界面与后台监控分离，增强稳定性
- 🔤 修复报告图表中文字符显示为"口口口"的乱码问题
- 🎨 智能检测操作系统，自动选择合适的中文字体
- 🖼️ 提高图表质量和分辨率，优化图表样式
- 🔗 新增GitHub仓库关联功能，自动记录项目修改历史
- 🔄 自动关联commit与push操作，追踪完整工作流
- 📝 输出格式化GitHub操作记录（时间+仓库+提交信息）
- 💾 独立存储GitHub记录，便于查询和分析
- 🔄 修复Git命令分析中文字符编码问题
- 📦 增加对二进制文件和特殊文件的智能处理
- 🔒 添加更健壮的异常处理机制
- ➕ 新增对`git remote`命令的支持
- ⚡ 优化Git命令分析器的错误处理和性能
- 📈 提高系统对非UTF-8编码的适应性

#### 赞赏
  如果对你有帮助，可以给扫描下面的二维码，请我喝杯咖啡 非常感谢！
![image](https://github.com/user-attachments/assets/065cc15e-1f1f-48c5-9845-49943506a818)





## 演示
![6cdd35ecab3f4a778e8785782764a4c](https://github.com/user-attachments/assets/d09142d5-5959-4179-8a0e-0b4646f883ea)
![6b4ba9cc49be8190776b0992f5bf81d](https://github.com/user-attachments/assets/132c47b9-3618-4f25-a00c-79c60ce68bed)
![3054f7ce5a9dca3f05c941e9ff016f9](https://github.com/user-attachments/assets/4b0bda66-be1f-448a-9f1c-014a4abc1ae9)
![a1abcab629721da7a5fd9a91d7ea74d](https://github.com/user-attachments/assets/b2faabe3-8b82-4ec7-9ab6-26341137f078)


## 系统要求

- Windows 10/11
- Python 3.7+
- Git (已安装并添加到PATH)
- PyQt5 (系统托盘应用所需)

## 如何安装

### 方法1：从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/git-command-monitor.git
cd git-command-monitor

# 安装依赖
pip install -r requirements.txt

# 运行系统托盘应用（推荐）
python run_tray_hidden.py
```

### 方法2：下载预构建版本

您也可以从[Releases页面](https://github.com/yourusername/git-command-monitor/releases)下载最新的预构建版本。

## 配置

编辑`config.json`文件配置监控行为：

```json
{
  "storage_path": "./data",
  "log_file": "./logs/monitor.log",
  "report_path": "./reports",
  "ignored_commands": ["git diff", "git log"],
  "system_level_monitoring": true,
  "monitor_interval": 1,
  "pid_cache_ttl": 300,
  "github_records": {
    "enabled": true,
    "separate_storage": true,
    "highlight_output": true
  },
  "report": {
    "auto_generate": {
      "enabled": false,
      "daily": true,
      "weekly": true,
      "monthly": true,
      "time": "23:50"
    }
  }
}
```

### 配置选项说明

| 选项 | 说明 |
|------|------|
| storage_path | 存储记录数据的目录 |
| log_file | 日志文件路径 |
| report_path | 报告文件存储目录 |
| ignored_commands | 不需要记录的Git命令列表 |
| system_level_monitoring | 是否启用系统级监控 |
| monitor_interval | 监控时间间隔(秒) |
| pid_cache_ttl | 进程ID缓存的生存时间(秒) |
| github_records.enabled | 是否启用GitHub仓库关联功能 |
| github_records.separate_storage | 是否单独存储GitHub记录 |
| github_records.highlight_output | 是否在控制台高亮显示GitHub记录 |
| report.auto_generate.enabled | 是否启用自动报告生成 |
| report.auto_generate.daily | 是否生成日报 |
| report.auto_generate.weekly | 是否生成周报 |
| report.auto_generate.monthly | 是否生成月报 |
| report.auto_generate.time | 自动生成报告的时间(HH:MM) |

## 运行方式

### 1. 系统托盘应用（推荐）

系统托盘应用是最友好的使用方式，会在系统托盘显示一个图标，并提供右键菜单。

#### 普通模式（有控制台窗口）

```bash
python tray_app.py
```

注意：直接运行此命令会显示一个命令行窗口，关闭窗口后应用也会退出。

#### 无窗口模式（推荐）

要在后台运行应用而不显示命令行窗口，使用以下命令：

```bash
python run_tray_hidden.py
```

这将使用pythonw启动托盘应用，无命令行窗口显示。应用将在系统托盘显示图标，即使关闭启动窗口后也会继续运行。

### 2. 纯后台监控服务（无界面）

如果只需要监控功能，不需要系统托盘界面：

#### 有窗口模式

```bash
python background_monitor.py
```

#### 无窗口模式（推荐）

```bash
python run_background.py
```

这将使用pythonw在后台启动监控服务，无任何窗口显示。服务将持续运行，即使关闭启动窗口。

### 3. 命令行工具

Git命令监控工具也提供了命令行接口：

```bash
# 启动监控
python main.py monitor

# 生成报告
python main.py report daily
python main.py report weekly -d 2023-05-15
python main.py report monthly -f html
```

> **注意**：命令行模式下，关闭命令行窗口后服务也会停止运行。如需持续运行，请使用上述的无窗口模式。

## 打包与分发

应用可以打包为独立的可执行文件，便于分发和使用。

### 创建可执行文件

```bash
# 安装打包工具（如果尚未安装）
pip install pyinstaller

# 使用打包脚本创建可执行文件
python build_exe.py
```

打包过程：
1. 自动创建应用图标
2. 生成PyInstaller配置文件
3. 打包应用为可执行文件
4. 配置默认设置和目录结构
5. 生成使用说明文档

### 分发与安装

打包完成后，`dist/GitCommandMonitor`目录包含完整的应用：
- GitCommandMonitor.exe：主程序
- 配置文件和默认目录结构
- 必要的依赖库和资源

将此目录复制到任意位置即可运行，无需安装Python环境和依赖包。

### 应用自定义

可执行文件支持以下自定义：
- 编辑`config.json`配置监控行为
- 使用应用提供的"设置开机启动"功能实现自启动
- 通过右键菜单管理所有功能

## 数据格式

记录的Git操作将以JSON格式存储在配置的`storage_path`目录中，包含以下信息：

```json
{
  "timestamp": "2023-07-15T14:32:45",
  "command": "git commit -m \"Fix login bug\"",
  "working_directory": "C:\\Projects\\my-app",
  "username": "developer",
  "hostname": "DESKTOP-ABC123",
  "pid": 1234,
  "status": 0,
  "analysis": {
    "type": "commit",
    "commit_hash": "a1b2c3d4e5f6...",
    "author": "Developer Name <dev@example.com>",
    "message": "Fix login bug",
    "files": [
      {
        "filename": "login.js",
        "change_type": "modified",
        "diff": "function login() { ... }"
      },
      {
        "filename": "auth.js",
        "change_type": "modified"
      }
    ],
    "stats": {
      "files_changed": 2,
      "insertions": 15,
      "deletions": 5
    }
  },
  "description": "提交了 2 个文件 (+15/-5): Fix login bug"
}
```

## 报告内容

生成的报告包含以下内容：

- 命令执行总数统计
- Git命令类型分布图表
- 命令执行时间分布图表
- 每日活动趋势图表
- 用户活跃度统计
- 仓库活跃度统计
- 最近提交的详细内容：
  - 提交信息和作者
  - 变更文件列表和变更类型
  - 文件内容预览（对于新增或修改的文件）
  - 变更统计（添加/删除的行数）

报告同时提供HTML和Markdown两种格式：
- **HTML格式**：美观的网页格式，包含交互式图表，适合通过浏览器查看
- **Markdown格式**：纯文本格式，适合集成到GitHub、GitLab或其它支持Markdown的平台

## 开发

### 项目结构

```
git-command-monitor/
├── gitmonitor/              # 核心模块
│   ├── __init__.py
│   ├── monitor.py           # 监控逻辑
│   ├── git_analyzer.py      # Git命令内容分析
│   ├── report.py            # 报告生成
│   └── utils.py             # 工具函数
├── data/                    # 数据存储(默认)
├── logs/                    # 日志存储
├── reports/                 # 报告存储
│   └── charts/              # 图表文件
├── icons/                   # 应用图标
├── config.json              # 配置文件
├── main.py                  # 主入口脚本
├── background_monitor.py    # 控制台运行脚本
├── service_installer.py     # Windows服务安装
├── generate_report.py       # 报告生成工具
├── auto_report.py           # 自动报告脚本
├── tray_app.py              # 系统托盘应用
├── startup_helper.py        # 开机自启动辅助脚本
├── create_icon.py           # 应用图标生成
├── build_exe.py             # 应用打包脚本
└── README.md                # 项目说明
```

### 技术架构

- **监控引擎**：使用psutil库监控系统进程，筛选Git命令
- **命令分析**：利用git命令行工具分析提交内容和变更
- **报告生成**：基于matplotlib和jinja2生成图表和报告
- **系统托盘**：使用PyQt5实现系统托盘应用
- **开机自启动**：通过Windows注册表或启动文件夹实现
- **打包分发**：使用PyInstaller创建独立可执行文件

## 兼容性与稳定性

该工具经过优化，可在各种复杂环境中稳定运行：

- **多语言支持**: 完全支持中文和其他非ASCII字符的命令和输出
- **编码适应**: 智能处理UTF-8、GBK等不同编码
- **错误容忍**: 即使Git命令分析出错，也能继续记录基本命令信息
- **二进制文件处理**: 智能检测并跳过二进制文件内容分析
- **优雅降级**: 在复杂情况下提供基本功能，确保监控不中断
- **资源管理**: 多线程设计与守护进程模式，确保稳定运行和优雅退出

## GitHub仓库关联功能

该工具能够自动关联Git操作与GitHub仓库，并生成格式化的操作记录：

```
2023-05-16 14:25:30 修改了@https://github.com/hmKunlun/deepulse，修改 test.html 文件，添加支付接口
```

### 工作流程

1. 当你执行`git commit`时，系统记录提交信息和变更文件
2. 当你执行`git push`时，系统自动关联最近的提交，并提取GitHub仓库链接
3. 生成格式化记录，包含时间、仓库链接和提交信息
4. 将记录保存到单独的文件中（按月组织），便于查询和统计

### 使用方法

此功能默认启用，无需额外配置。你可以在配置文件中调整：

```json
"github_records": {
  "enabled": true,          // 是否启用GitHub仓库关联功能
  "separate_storage": true, // 是否单独存储GitHub记录
  "highlight_output": true  // 是否在控制台高亮显示GitHub记录
}
```

### 记录查看

GitHub操作记录保存在`data/github_records/`目录下，文件名格式为`github_records_YYYYMM.txt`。

你可以使用任何文本编辑器查看这些记录，也可以将其集成到你的工作报告中。

## 常见问题解答

### Q: 系统托盘图标没有显示？
A: 确保已安装PyQt5库 (`pip install PyQt5`)，并且系统允许应用在通知区域显示图标。

### Q: 如何查看监控是否正常工作？
A: 查看日志文件 (`logs/monitor.log`) 或通过托盘菜单打开报告目录查看记录。

### Q: 开机自启动设置失败？
A: 尝试以管理员权限运行命令 `python startup_helper.py add`，或通过托盘菜单设置。

### Q: 报告图表中文乱码？
A: 确保系统已安装中文字体，或更新到最新版本，已添加自动字体检测功能。

### Q: 如何打包为可执行文件？
A: 运行 `python build_exe.py`，打包后的文件位于 `dist/GitCommandMonitor` 目录。

## 贡献

欢迎提交问题和拉取请求！可以通过以下方式贡献：

1. Fork项目并创建分支
2. 提交改进和Bug修复
3. 提交新功能或建议
4. 完善文档和示例

## 许可

MIT 

## 未来计划

- 添加Web界面，支持远程访问
- 提供更多数据分析功能
- 支持更多Git操作类型的详细分析
- 增加团队协作功能
- 支持Linux和macOS平台 

## 目录结构

```
git-command-monitor/
├── gitmonitor/              # 核心模块
│   ├── __init__.py
│   ├── monitor.py           # 监控逻辑
│   ├── git_analyzer.py      # Git命令分析
│   ├── report.py            # 报告生成
│   └── utils.py             # 工具函数
├── tray_app.py              # 系统托盘应用
├── background_monitor.py    # 后台监控服务
├── run_tray_hidden.py       # 无窗口托盘启动脚本
├── run_background.py        # 无窗口后台服务脚本
├── main.py                  # 命令行入口
├── config.example.json      # 配置文件示例
└── requirements.txt         # 依赖列表
```

## 问题反馈与贡献

如果您遇到任何问题或有改进建议，请[提交Issue](https://github.com/yourusername/git-command-monitor/issues)。

欢迎贡献代码！请参阅[贡献指南](CONTRIBUTING.md)了解更多信息。

## 开发者名单

感谢所有为本项目做出贡献的开发者！

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件 
