# 更新日志

所有项目的显著变化都将记录在此文件中。

## [0.4.0] - 2023-05-20

### 添加
- 系统托盘应用功能，支持后台运行
- 开机自启动支持，可配置Windows启动项
- 托盘右键菜单，快速生成日报、周报和月报
- 可视化日期和报告格式选择

### 优化
- 监控引擎改为多线程模式，提高性能
- 用户界面与后台监控分离，增强稳定性
- 增强错误处理和异常捕获
- 配置界面优化

## [0.3.0] - 2023-05-12

### 添加

- Git命令内容深度分析功能
- 详细提取提交和推送的文件变更内容
- 命令执行内容的人性化描述
- 报告中显示详细的提交内容和文件变更
- 统一的主入口脚本(main.py)，支持监控和报告生成

### 优化

- 重构监控引擎，整合命令分析功能
- 增强报告内容，添加提交详情部分
- 改进输出信息，显示更详细的操作内容
- 优化命令行工具结构，统一参数处理

## [0.3.1] - 2023-05-15

### 修复
- 修复了Git命令分析中文字符编码问题
- 增加了对二进制文件和特殊文件处理的支持
- 添加了更健壮的异常处理机制
- 修复了push命令分析中可能出现的问题
- 添加了对git remote命令的支持

### 优化
- 优化了Git命令分析器的错误处理机制
- 改进了监控引擎的异常捕获逻辑
- 提高了系统对非UTF-8编码的适应性
- 添加了更详细的日志记录

## [0.3.2] - 2023-05-16

### 添加
- GitHub仓库关联功能
- 自动关联commit与push操作
- 格式化输出GitHub操作记录
- GitHub记录独立存储，便于查询和分析

### 优化
- 改进仓库URL解析，支持更多格式
- 增强命令行输出，高亮显示GitHub操作
- 优化对提交信息的处理和关联

## [0.3.3] - 2023-05-18

### 修复
- 修复了报告图表中的中文字符显示为"口口口"的乱码问题
- 增强了matplotlib字体配置，支持多种中文字体
- 提高了图表质量和分辨率

### 优化
- 根据操作系统自动选择合适的中文字体
- 优化图表样式和美观度
- 增强了图表导出设置

## [0.2.0] - 2023-05-10

### 添加

- 报告生成功能，支持日报、周报和月报
- HTML和Markdown两种报告格式
- 数据可视化图表（命令类型分布、时间分布、每日活动）
- 命令行报告生成工具
- 自动报告生成脚本

### 优化

- 更新项目结构，添加报告模块
- 优化配置系统，添加报告相关配置
- 扩展依赖，支持数据分析和可视化

## [0.1.1] - 2023-05-09

### 修复

- 修复Git命令重复记录问题
- 添加进程ID缓存系统，避免记录长时间运行的相同进程
- 优化定期清理不活跃进程的机制

### 优化

- 改进状态报告，显示当前缓存的进程数量
- 添加`pid_cache_ttl`配置选项，控制进程缓存生命周期

## [0.1.0] - 2023-05-09

### 添加

- 初始项目结构和基础框架
- 系统级Git命令监控功能
- Windows服务支持
- 进程和命令监控
- 基于JSON的数据存储
- 配置系统
- 日志系统
- 控制台运行模式

### 技术特性

- 使用psutil进行进程监控
- 使用pywin32实现Windows服务
- 基于JSON的数据存储格式
- 多线程异步监控

## [计划中的功能]

- 用户界面用于数据可视化
- 更详细的Git命令分析
- 团队Git使用情况报告
- 多操作系统支持（Linux、macOS）
- 远程数据收集和集中管理
- API接口用于第三方集成 