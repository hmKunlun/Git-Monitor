#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git命令监控 - 系统托盘应用
可在后台运行，显示系统托盘图标，并提供快捷生成报告功能
"""

import os
import sys
import datetime
import json
import threading
import tempfile
from pathlib import Path

# 导入PyQt5库
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, 
                            QAction, QMessageBox, QDialog, QVBoxLayout, 
                            QLabel, QComboBox, QCalendarWidget, QDialogButtonBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDate

# 导入监控器和报告生成器
from gitmonitor.utils import pretty_print, load_config, ensure_dir_exists
from gitmonitor.monitor import GitOperationMonitor
from gitmonitor.report import GitReportGenerator

# 设置资源路径
def get_resource_path(relative_path):
    """获取资源文件的路径，兼容打包后的情况"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的路径
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

# 创建或获取图标
def get_app_icon():
    """获取应用图标，如果不存在则创建一个临时图标"""
    icon_path = get_resource_path("app_icon.png")
    if not os.path.exists(icon_path):
        # 如果图标不存在，使用一个简单的文本来创建临时图标
        from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
        pixmap = QPixmap(128, 128)
        pixmap.fill(QColor(52, 152, 219))  # 蓝色背景
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Arial', 36, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "G")
        painter.end()
        # 保存到临时文件
        temp_dir = tempfile.gettempdir()
        icon_path = os.path.join(temp_dir, "git_monitor_icon.png")
        pixmap.save(icon_path)
    return icon_path

class ReportDialog(QDialog):
    """报告生成对话框"""
    def __init__(self, parent=None, report_type="daily"):
        super().__init__(parent)
        self.report_type = report_type
        self.setWindowTitle(f"生成{self.get_report_name()}报告")
        self.resize(300, 200)
        
        # 布局
        layout = QVBoxLayout()
        
        # 日期选择（对于每日报告，只显示日期；对于周报，显示日期并说明会计算整周；对于月报，同理）
        self.date_label = QLabel(f"选择{self.get_report_name()}报告日期:")
        layout.addWidget(self.date_label)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())
        layout.addWidget(self.calendar)
        
        # 格式选择
        self.format_label = QLabel("选择报告格式:")
        layout.addWidget(self.format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["HTML和Markdown", "仅HTML", "仅Markdown"])
        layout.addWidget(self.format_combo)
        
        # 确定和取消按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        self.setLayout(layout)
    
    def get_report_name(self):
        """获取报告类型的中文名称"""
        report_names = {
            "daily": "日",
            "weekly": "周",
            "monthly": "月"
        }
        return report_names.get(self.report_type, "")
    
    def get_selected_date(self):
        """获取选中的日期"""
        return self.calendar.selectedDate().toPyDate()
    
    def get_format_type(self):
        """获取选中的格式类型"""
        format_text = self.format_combo.currentText()
        if format_text == "仅HTML":
            return "html"
        elif format_text == "仅Markdown":
            return "markdown"
        else:
            return "both"

class GitMonitorTrayApp:
    """Git命令监控系统托盘应用"""
    
    def __init__(self):
        """初始化应用"""
        # 加载配置
        self.config_path = "config.json"
        self.config = load_config(self.config_path)
        
        # 创建应用
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # 初始化监控器
        self.start_monitor()
        
        # 设置图标
        self.icon_path = get_app_icon()
        self.tray_icon = QSystemTrayIcon(QIcon(self.icon_path), self.app)
        self.tray_icon.setToolTip("Git命令监控")
        
        # 创建托盘菜单
        self.create_tray_menu()
        
        # 显示图标
        self.tray_icon.show()
        
        # 显示启动通知
        self.tray_icon.showMessage(
            "Git命令监控已启动",
            "应用现在正在后台运行，监控Git命令操作。",
            QSystemTrayIcon.Information,
            3000
        )
    
    def start_monitor(self):
        """启动监控器"""
        self.monitor = GitOperationMonitor(self.config)
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_thread_func, daemon=True)
        self.monitor_thread.start()
        
        # 初始化报告生成器（用于生成报告）
        self.report_generator = GitReportGenerator(self.config)
    
    def _monitor_thread_func(self):
        """监控线程函数"""
        self.monitor.start()
    
    def create_tray_menu(self):
        """创建托盘菜单"""
        # 创建菜单
        self.tray_menu = QMenu()
        
        # 状态标签（不可点击）
        status_action = QAction("Git命令监控运行中", self.tray_menu)
        status_action.setEnabled(False)
        self.tray_menu.addAction(status_action)
        
        self.tray_menu.addSeparator()
        
        # 报告生成子菜单
        report_menu = QMenu("生成报告", self.tray_menu)
        
        # 日报
        daily_action = QAction("生成日报...", report_menu)
        daily_action.triggered.connect(lambda: self.show_report_dialog("daily"))
        report_menu.addAction(daily_action)
        
        # 周报
        weekly_action = QAction("生成周报...", report_menu)
        weekly_action.triggered.connect(lambda: self.show_report_dialog("weekly"))
        report_menu.addAction(weekly_action)
        
        # 月报
        monthly_action = QAction("生成月报...", report_menu)
        monthly_action.triggered.connect(lambda: self.show_report_dialog("monthly"))
        report_menu.addAction(monthly_action)
        
        self.tray_menu.addMenu(report_menu)
        
        self.tray_menu.addSeparator()
        
        # 打开报告目录
        open_reports_action = QAction("打开报告目录", self.tray_menu)
        open_reports_action.triggered.connect(self.open_reports_directory)
        self.tray_menu.addAction(open_reports_action)
        
        # 打开配置文件
        open_config_action = QAction("编辑配置文件", self.tray_menu)
        open_config_action.triggered.connect(self.open_config_file)
        self.tray_menu.addAction(open_config_action)
        
        self.tray_menu.addSeparator()
        
        # 开机启动设置
        startup_action = QAction("设置开机启动", self.tray_menu)
        startup_action.triggered.connect(self.configure_startup)
        self.tray_menu.addAction(startup_action)
        
        # 关于
        about_action = QAction("关于", self.tray_menu)
        about_action.triggered.connect(self.show_about)
        self.tray_menu.addAction(about_action)
        
        self.tray_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self.tray_menu)
        exit_action.triggered.connect(self.exit_app)
        self.tray_menu.addAction(exit_action)
        
        # 设置托盘图标菜单
        self.tray_icon.setContextMenu(self.tray_menu)
    
    def show_report_dialog(self, report_type):
        """显示报告生成对话框"""
        dialog = ReportDialog(None, report_type)
        if dialog.exec_() == QDialog.Accepted:
            selected_date = dialog.get_selected_date()
            format_type = dialog.get_format_type()
            self.generate_report(report_type, selected_date, format_type)
    
    def generate_report(self, report_type, target_date, format_type):
        """生成报告"""
        try:
            report_paths = []
            
            if report_type == "daily":
                html_path, md_path = self.report_generator.generate_daily_report(target_date, format_type)
                if html_path: report_paths.append(html_path)
                if md_path: report_paths.append(md_path)
            elif report_type == "weekly":
                html_path, md_path = self.report_generator.generate_weekly_report(target_date, format_type)
                if html_path: report_paths.append(html_path)
                if md_path: report_paths.append(md_path)
            elif report_type == "monthly":
                html_path, md_path = self.report_generator.generate_monthly_report(target_date, format_type)
                if html_path: report_paths.append(html_path)
                if md_path: report_paths.append(md_path)
            
            # 显示成功通知
            if report_paths:
                report_name = {"daily": "日报", "weekly": "周报", "monthly": "月报"}.get(report_type, "报告")
                self.tray_icon.showMessage(
                    f"生成{report_name}成功",
                    f"报告已保存至：\n{os.path.dirname(report_paths[0])}",
                    QSystemTrayIcon.Information,
                    5000
                )
            
        except Exception as e:
            self.tray_icon.showMessage(
                "生成报告失败",
                f"错误信息：{str(e)}",
                QSystemTrayIcon.Critical,
                5000
            )
    
    def open_reports_directory(self):
        """打开报告目录"""
        report_path = self.config.get("report_path", "./reports")
        ensure_dir_exists(report_path)
        # 使用系统默认程序打开目录
        os.startfile(os.path.abspath(report_path))
    
    def open_config_file(self):
        """打开配置文件"""
        try:
            # 使用系统默认程序打开配置文件
            os.startfile(os.path.abspath(self.config_path))
        except Exception as e:
            self.tray_icon.showMessage(
                "打开配置文件失败",
                f"错误信息：{str(e)}",
                QSystemTrayIcon.Critical,
                3000
            )
    
    def configure_startup(self):
        """配置开机启动"""
        try:
            from startup_helper import configure_startup
            
            if configure_startup():
                self.tray_icon.showMessage(
                    "设置开机启动成功",
                    "Git命令监控将在系统启动时自动运行。",
                    QSystemTrayIcon.Information,
                    3000
                )
            else:
                self.tray_icon.showMessage(
                    "取消开机启动",
                    "Git命令监控将不会在系统启动时自动运行。",
                    QSystemTrayIcon.Information,
                    3000
                )
        except Exception as e:
            self.tray_icon.showMessage(
                "设置开机启动失败",
                f"错误信息：{str(e)}",
                QSystemTrayIcon.Critical,
                3000
            )
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            None,
            "关于 Git命令监控",
            """<h3>Git命令监控 v0.3.3</h3>
            <p>一个为开发团队设计的Git命令系统级监控工具<br>
            可记录所有执行的Git操作，支持Windows系统</p>
            <p>© 2023 Your Name</p>"""
        )
    
    def exit_app(self):
        """退出应用"""
        # 停止监控
        if hasattr(self, 'monitor'):
            self.monitor.stop()
        
        # 退出应用
        self.app.quit()
    
    def run(self):
        """运行应用"""
        # 进入应用事件循环
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = GitMonitorTrayApp()
    app.run() 