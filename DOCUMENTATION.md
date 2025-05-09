# Git命令监控工具 - 技术文档

## 项目概述

Git命令监控工具是一个系统级监控解决方案，专为Windows环境设计，用于记录系统中执行的所有Git命令。该工具可以在后台持续运行，或作为Windows服务自动启动，无需用户干预。此外，它还能深入分析Git命令的内容，提取提交的文件变更等详细信息，提供强大的报告生成功能，用于分析和展示Git命令的使用情况。

## 系统架构

### 模块结构

```
git-command-monitor/
├── gitmonitor/              # 核心模块
│   ├── __init__.py          # 模块初始化
│   ├── monitor.py           # 监控逻辑
│   ├── git_analyzer.py      # Git命令内容分析
│   ├── report.py            # 报告生成
│   └── utils.py             # 实用工具函数
├── data/                    # 数据存储目录
├── logs/                    # 日志存储目录
├── reports/                 # 报告存储目录
│   └── charts/              # 图表文件目录
├── config.json              # 配置文件
├── main.py                  # 主入口脚本
├── background_monitor.py    # 控制台模式启动脚本
├── service_installer.py     # Windows服务安装脚本
├── generate_report.py       # 报告生成命令行工具
├── auto_report.py           # 自动报告生成脚本
├── requirements.txt         # 项目依赖
└── README.md                # 项目说明
```

### 核心组件

1. **监控引擎 (monitor.py)**
   - `GitOperationMonitor`: 核心监控类，负责检测和记录Git命令
   - 集成`GitCommandAnalyzer`进行命令内容分析
   - 智能进程缓存，避免重复记录同一进程

2. **Git命令分析器 (git_analyzer.py)**
   - `GitCommandAnalyzer`: 命令分析类，深入分析Git命令内容
   - 支持分析commit、push、add、checkout等命令
   - 提取提交信息、文件变更、统计数据等

3. **报告生成器 (report.py)**
   - `GitReportGenerator`: 报告生成类，支持生成日报、周报和月报
   - 支持HTML和Markdown两种输出格式
   - 生成数据可视化图表和统计分析
   - 展示详细的提交内容和文件变更

4. **工具函数 (utils.py)**
   - 日志记录
   - 配置管理
   - 数据存储
   - 错误处理

5. **运行模式**
   - 主入口模式 (main.py)：支持监控和报告生成
   - 控制台模式 (background_monitor.py)
   - Windows服务模式 (service_installer.py)
   - 报告生成模式 (generate_report.py, auto_report.py)

## 技术实现

### 监控原理

工具使用`psutil`库持续扫描操作系统中运行的进程，筛选出所有Git命令进程，并记录其命令行参数、工作目录、用户名等信息。监控周期由配置文件中的`monitor_interval`参数控制。

系统采用智能进程缓存机制，避免重复记录同一个Git进程：
1. 维护已处理进程ID集合
2. 对每个检测到的Git进程，先检查是否已经记录过
3. 定期清理不再活跃的进程ID，释放内存

### Git命令内容分析

当检测到Git命令时，系统会调用`GitCommandAnalyzer`分析器进行深入分析：

1. **命令分类和解析**：
   - 识别Git子命令（commit、push、add等）
   - 解析命令参数和选项

2. **提交分析(commit)**：
   - 提取提交消息和作者信息
   - 获取所有变更的文件列表
   - 分析文件变更类型（添加、修改、删除）
   - 获取文件内容的差异（对于添加和修改的文件）
   - 统计变更行数（添加/删除）

3. **推送分析(push)**：
   - 识别远程仓库和分支
   - 获取推送的提交列表
   - 分析每个提交的内容和变更

4. **其他命令分析**：
   - 分析add命令添加的文件
   - 分析checkout命令切换的分支
   - 分析merge和pull命令的操作

5. **结果整合**：
   - 将分析结果添加到记录中
   - 生成人性化描述，便于理解命令行为

### 数据存储

监控数据以JSON格式存储，按日期分文件组织：
- 文件名格式：`YYYYMMDD.json`
- 位置：配置的`storage_path`目录

数据记录包含标准信息和分析结果：
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
      }
    ],
    "stats": {
      "files_changed": 1,
      "insertions": 10,
      "deletions": 5
    }
  },
  "description": "提交了 1 个文件 (+10/-5): Fix login bug"
}
```

### 报告生成

报告生成基于收集的Git命令数据，分析并生成可视化报告：

1. **数据加载和分析**
   - 根据报告类型（日报、周报、月报）确定时间范围
   - 加载对应时间范围内的所有数据
   - 分析命令类型、使用频率、时间分布等
   - 统计用户和仓库活跃度
   - 提取提交详情和文件变更信息

2. **图表生成**
   - 使用`matplotlib`库生成数据可视化图表
   - 命令类型分布图
   - 每小时命令执行分布图
   - 每日活动趋势图

3. **提交内容展示**
   - 展示最近提交的详细信息
   - 显示每个提交的文件变更列表
   - 对于添加或修改的文件，显示部分内容
   - 展示每个提交的统计信息（文件数、添加行数、删除行数）

4. **报告格式**
   - HTML格式：使用`jinja2`模板引擎生成美观的HTML报告
   - Markdown格式：生成可在GitHub、GitLab等平台直接显示的MD文件
   - 两种格式包含相同的数据、图表和详细提交信息

5. **自动生成**
   - 支持通过计划任务自动生成报告
   - 可配置生成频率（每日、每周、每月）
   - 易于集成到现有的团队工作流中

### Windows服务

Windows服务实现基于`pywin32`库，提供以下功能：
- 自动启动：系统启动时自动运行
- 后台运行：无需登录即可工作
- 服务管理：通过Windows服务管理器或命令行控制

服务配置：
- 服务名称：GitCommandMonitorService
- 显示名称：Git Command Monitor
- 描述：监控所有系统Git命令执行

## 配置选项

配置文件(`config.json`)支持以下选项：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| storage_path | 字符串 | "./data" | 数据存储目录 |
| log_file | 字符串 | "./logs/monitor.log" | 日志文件路径 |
| report_path | 字符串 | "./reports" | 报告存储目录 |
| system_level_monitoring | 布尔值 | true | 是否启用系统级监控 |
| monitor_interval | 整数 | 1 | 监控间隔（秒） |
| ignored_commands | 数组 | ["git status", "git diff", "git log"] | 忽略的Git命令列表 |
| log_level | 字符串 | "INFO" | 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL） |
| max_history_size | 整数 | 10000 | 历史记录最大条数 |
| file_rotation_size | 整数 | 5242880 | 日志文件轮转大小（字节） |
| pid_cache_ttl | 整数 | 300 | 进程ID缓存的生存时间（秒） |
| report.auto_generate.enabled | 布尔值 | false | 是否启用自动报告生成 |
| report.auto_generate.daily | 布尔值 | true | 是否生成日报 |
| report.auto_generate.weekly | 布尔值 | true | 是否生成周报 |
| report.auto_generate.monthly | 布尔值 | true | 是否生成月报 |
| report.auto_generate.time | 字符串 | "23:50" | 自动生成报告的时间 |
| report.chart_theme | 字符串 | "default" | 图表主题 |
| report.include_repos | 数组 | [] | 仅包含指定仓库（空为全部） |
| github_records | 对象 | {} | GitHub仓库关联功能配置 |

## 日志管理

工具使用Python标准日志库进行日志记录：
- 日志位置：由`log_file`配置指定
- 日志级别：由`log_level`配置指定
- 控制台输出：日志同时输出到控制台和文件

## 命令行工具

系统提供以下命令行工具：

### 主入口脚本 (main.py)

```
usage: main.py [-h] [-c CONFIG] {monitor,report} ...

Git命令监控工具

positional arguments:
  {monitor,report}      子命令
    monitor             启动Git命令监控
    report              生成Git命令报告

optional arguments:
  -h, --help            显示帮助信息
  -c CONFIG, --config CONFIG 配置文件路径，默认为config.json
```

### 报告生成 (main.py report)

```
usage: main.py report [-h] [-d DATE] [-f {html,markdown,both}] {daily,weekly,monthly}

Git命令监控报告生成工具

positional arguments:
  {daily,weekly,monthly}     报告类型：daily(日报)、weekly(周报)、monthly(月报)

optional arguments:
  -h, --help                 显示帮助信息
  -d DATE, --date DATE       报告日期，格式为YYYY-MM-DD或YYYYMMDD，默认为今天
  -f {html,markdown,both}, --format {html,markdown,both}
                             报告输出格式，默认同时生成HTML和Markdown
```

## Git命令分析器的内部实现

`GitCommandAnalyzer`类实现了多种Git命令的分析：

1. **提交分析流程**：
   - 提取提交消息：使用正则表达式从命令中提取
   - 获取最近提交：执行`git log -1 --name-status --pretty=format:%H|%an|%ae|%at|%s`
   - 解析提交信息：获取提交哈希、作者、时间、消息
   - 解析文件变更：获取变更类型和文件名
   - 获取文件差异：对于添加或修改的文件，执行`git show --format= <commit>:<file>`
   - 获取统计信息：执行`git show --stat --format= <commit>`解析变更统计

2. **推送分析流程**：
   - 识别远程仓库和分支：从命令参数中提取
   - 获取远程仓库URL：执行`git remote get-url <remote>`
   - 获取推送的提交：执行`git log <remote>/<branch>..<branch> --pretty=format:%H|%an|%ae|%at|%s`
   - 对每个提交进行分析：获取变更文件和统计信息

3. **其他命令分析**：
   - add命令：解析添加的文件列表，执行`git status --porcelain`查看状态
   - checkout命令：判断是切换分支还是恢复文件
   - merge命令：获取源分支和目标分支，检查冲突
   - pull命令：分析远程仓库和分支，获取当前状态

4. **结果整合**：
   - 将分析结果添加到记录中
   - 生成人性化描述，便于理解命令行为

## 性能考虑

- **CPU使用率**: 监控进程使用的CPU资源非常小，通常低于1%
- **内存占用**: 典型安装下内存占用约为20-30MB
- **磁盘使用**: 取决于Git命令使用频率，每1000条记录约占用2-3MB磁盘空间
- **进程缓存**: 定期清理不活跃的进程ID，确保内存使用合理
- **报告生成**: 报告生成时可能会短暂占用较多CPU和内存（生成图表和分析详细提交内容时）

## 限制和已知问题

1. 只能监控通过标准Git可执行文件执行的命令
2. 无法监控Git GUI客户端内部操作
3. 提交内容分析需要Git仓库存在且可访问
4. 对于非常大的提交或大型二进制文件，只显示有限的内容
5. 内容分析依赖Git命令行工具，需确保系统PATH中存在git命令
6. 报告生成依赖`matplotlib`，在某些环境下可能需要额外配置

## 开发扩展

### 添加新功能

要添加新功能，建议遵循以下模式：
1. 在适当的模块中添加新类或函数
2. 更新配置文件格式
3. 添加相应的文档
4. 更新README.md

### 代码风格

本项目遵循PEP 8编码规范，主要风格指南：
- 使用4空格缩进
- 每行最多120个字符
- 使用文档字符串注释所有公共函数和类
- 使用类型注释辅助代码理解 

## 异常处理与容错机制

系统设计了完善的异常处理与容错机制，确保在各种复杂环境下稳定运行：

1. **编码问题处理**
   - 支持UTF-8和其他编码（如GBK）
   - 使用`errors='replace'`策略处理无法解码的字符
   - 解决Windows环境下多语言命令输出的兼容性问题

2. **二进制文件处理**
   - 智能检测二进制文件（使用`git check-attr -a`）
   - 对二进制文件提供特殊处理，不尝试获取内容差异
   - 防止大型二进制文件导致内存占用过高

3. **多层错误捕获**
   - 监控引擎层错误捕获：确保即使命令分析失败，基本监控功能仍能继续
   - 命令分析层错误捕获：单个命令分析异常不影响其他命令处理
   - 文件操作错误处理：防止文件读写异常导致系统崩溃

4. **优雅降级**
   - 当无法获取详细分析时，仍记录基本命令信息
   - 当遇到过大文件时，限制获取内容的行数
   - 提供清晰的错误日志，便于问题诊断和修复

## 近期优化

### 命令分析增强
- 新增对`git remote`命令的支持，能够分析remote添加、修改和删除操作
- 优化`push`命令分析，增加对新创建的远程分支和无远程分支情况的处理
- 改进了`commit`内容分析的性能和准确性

### 性能与稳定性提升
- 优化了进程扫描机制，减少CPU使用
- 改进了文件差异获取逻辑，降低对大文件的处理负担
- 增强了日志记录详细程度，便于问题诊断
- 提升了异常情况下的自动恢复能力

## GitHub仓库关联功能

系统新增了对GitHub仓库的智能关联功能，将开发活动与代码库直接链接：

### 工作原理

1. **提交信息缓存**
   - 系统会缓存最近的`commit`命令信息
   - 包括提交哈希、提交消息、变更文件列表和统计数据
   - 使用工作目录作为键，关联同一仓库的操作

2. **仓库链接提取**
   - 从`git push`命令分析远程仓库URL
   - 自动识别并格式化GitHub仓库链接
   - 支持多种URL格式（HTTPS和SSH）

3. **操作关联**
   - 将`push`操作自动关联到最近的`commit`
   - 生成包含时间、仓库链接和提交信息的格式化记录
   - 例如：`2023-05-16 14:25:30 修改了@https://github.com/hmKunlun/deepulse，修改 test.html 文件，添加支付接口`

4. **独立存储**
   - GitHub操作记录被单独保存到特定文件中
   - 使用月度格式文件名：`github_records_YYYYMM.txt`
   - 便于查询和统计分析

### 配置选项

配置文件中新增了GitHub记录相关选项：

```json
"github_records": {
  "enabled": true,          // 是否启用GitHub仓库关联功能
  "separate_storage": true, // 是否单独存储GitHub记录
  "highlight_output": true  // 是否在控制台高亮显示GitHub记录
}
```

### 输出示例

控制台输出示例：
```
[2023-05-16 14:25:30] 已记录命令: git push origin master
[2023-05-16 14:25:30] GitHub操作: 2023-05-16 14:25:30 修改了@https://github.com/hmKunlun/deepulse，修改 test.html 文件，添加支付接口
```

记录文件格式：
```
2023-05-16 14:25:30 修改了@https://github.com/hmKunlun/deepulse，修改 test.html 文件，添加支付接口
2023-05-16 15:42:12 修改了@https://github.com/hmKunlun/deepulse，修复登录页面验证问题
...
```

### 用途与应用

- **工作记录追踪**：自动记录开发人员的GitHub贡献
- **项目时间线**：建立项目修改历史的时间线
- **工作量统计**：便于统计特定仓库的工作量和提交频率
- **活动报告**：为周报/月报提供详细的GitHub活动记录 

## 系统托盘应用

系统托盘应用是Git命令监控工具的图形化界面入口，使用PyQt5库实现，支持在Windows系统托盘区域显示图标并提供快捷菜单操作。

### 核心组件

#### GitMonitorTrayApp类

系统托盘应用的主类，负责创建托盘图标、菜单和处理用户交互。主要功能：

- 初始化应用和创建系统托盘图标
- 在后台线程中启动Git操作监控
- 创建右键菜单，包括生成报告、设置开机自启动等选项
- 处理用户交互，如日期选择和报告生成

#### ReportDialog类

报告生成对话框，用于选择报告日期和格式。主要功能：

- 提供日期选择器，用于选择报告日期
- 提供格式选择器，可选择生成HTML、Markdown或两种格式
- 返回用户选择的日期和格式信息

### 技术实现

1. **多线程设计**：
   ```python
   # 启动监控线程
   self.monitor_thread = threading.Thread(target=self._monitor_thread_func, daemon=True)
   self.monitor_thread.start()
   ```
   监控功能在单独的守护线程中运行，确保UI线程响应性和应用退出时线程自动结束。

2. **托盘图标和菜单**：
   ```python
   self.tray_icon = QSystemTrayIcon(QIcon(self.icon_path), self.app)
   self.tray_menu = QMenu()
   # 添加菜单项...
   self.tray_icon.setContextMenu(self.tray_menu)
   ```
   使用QSystemTrayIcon创建托盘图标，并设置右键菜单。

3. **报告生成**：
   ```python
   def generate_report(self, report_type, target_date, format_type):
       # 根据报告类型调用相应的报告生成方法
       if report_type == "daily":
           html_path, md_path = self.report_generator.generate_daily_report(
               target_date, format_type)
       # ...
   ```
   根据用户选择的报告类型、日期和格式，调用相应的报告生成方法。

4. **通知用户**：
   ```python
   self.tray_icon.showMessage(
       f"生成{report_name}成功",
       f"报告已保存至：\n{os.path.dirname(report_paths[0])}",
       QSystemTrayIcon.Information,
       5000
   )
   ```
   使用系统通知向用户提供反馈信息。

## 开机自启动功能

开机自启动功能使Git命令监控工具可以随系统启动，无需手动运行。该功能通过Windows注册表和启动文件夹两种方式实现。

### 核心组件

#### startup_helper模块

提供开机自启动设置的功能，包括添加、移除和检查开机自启动状态。主要功能：

- 使用注册表方式配置开机自启动（主要方法）
- 使用启动文件夹方式配置开机自启动（备选方法）
- 提供命令行接口和API接口

### 技术实现

1. **注册表方式**：
   ```python
   def add_to_registry():
       # 打开注册表键
       key = winreg.OpenKey(
           winreg.HKEY_CURRENT_USER,
           r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
           0,
           winreg.KEY_SET_VALUE
       )
       # 设置注册表值
       winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
       winreg.CloseKey(key)
   ```
   向Windows注册表的启动项中添加应用路径。

2. **启动文件夹方式**：
   ```python
   def add_to_startup_folder():
       # 获取启动文件夹路径
       startup_folder = os.path.join(
           os.environ["APPDATA"],
           r"Microsoft\Windows\Start Menu\Programs\Startup"
       )
       # 创建快捷方式
       create_shortcut(exe_path, shortcut_path, working_dir, "Git命令监控工具")
   ```
   在Windows启动文件夹中创建应用的快捷方式。

3. **快捷方式创建**：
   ```python
   def create_shortcut(target_path, shortcut_path, working_dir, description):
       # 使用PowerShell创建快捷方式
       ps_command = f"""
       $WshShell = New-Object -ComObject WScript.Shell
       $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
       $Shortcut.TargetPath = "{target_path}"
       # ...
       """
       subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
   ```
   使用PowerShell COM接口创建Windows快捷方式。

4. **状态切换**：
   ```python
   def configure_startup():
       current_status = is_in_startup()
       if current_status:
           # 如果已设置开机启动，则移除
           remove_from_registry()
           remove_from_startup_folder()
           return False
       else:
           # 如果未设置开机启动，则添加
           if not add_to_registry():
               add_to_startup_folder()
           return True
   ```
   检查当前状态并进行切换，优先使用注册表方法，失败则使用启动文件夹方法。

## 打包和分发

### PyInstaller打包

使用PyInstaller将应用打包为独立可执行文件，便于分发和使用。

```python
# 使用spec文件定义打包配置
a = Analysis(
    ['tray_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app_icon.png', '.'),
        ('icons/*.png', 'icons'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'matplotlib',
        'pandas',
        'jinja2',
        'markdown',
    ],
    # ...
)
```

#### 打包步骤

1. 创建应用图标
2. 生成PyInstaller spec文件
3. 运行PyInstaller构建可执行文件
4. 创建默认配置和必要目录
5. 添加README.txt文件

执行build_exe.py脚本可以自动完成整个打包流程，生成dist/GitCommandMonitor目录，其中包含可独立运行的应用程序。 