import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import time
from pathlib import Path

# 导入监控模块
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from gitmonitor.utils import load_config
from gitmonitor.monitor import GitOperationMonitor

class GitCommandMonitorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GitCommandMonitor"
    _svc_display_name_ = "Git Command Monitor"
    _svc_description_ = "监控系统中所有的Git命令行操作"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.running = False
        self.monitor = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        if self.monitor:
            self.monitor.stop()

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                             servicemanager.PYS_SERVICE_STARTED,
                             (self._svc_name_, ''))
        self.running = True
        self.main()

    def main(self):
        # 配置文件路径
        script_dir = Path(__file__).parent
        config_path = script_dir / "config.json"
        
        # 使用增强配置
        try:
            config = load_config(str(config_path))
        except:
            # 默认配置
            config = {
                "monitor_interval": 1,
                "storage_path": str(script_dir / "data"),
                "database_file": "git_history.db",
                "ignored_commands": [],  # 不忽略任何命令
                "monitored_commands": []  # 空列表表示监控所有git命令
            }
        
        # 创建并启动监控器
        self.monitor = GitOperationMonitor(config)
        self.monitor.start()
        
        # 保持服务运行
        while self.running:
            # 检查服务停止信号
            if win32event.WaitForSingleObject(self.hWaitStop, 5000) == win32event.WAIT_OBJECT_0:
                break

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(GitCommandMonitorService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(GitCommandMonitorService) 