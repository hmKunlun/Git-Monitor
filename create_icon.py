#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建Git命令监控工具的应用图标
"""

import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QIcon
from PyQt5.QtCore import Qt, QSize

def create_icon():
    """创建应用图标并保存到文件"""
    # 创建QApplication实例（必须在创建QPixmap前）
    app = QApplication(sys.argv)
    
    # 创建基本图标
    pixmap = QPixmap(256, 256)
    pixmap.fill(QColor(52, 152, 219))  # 蓝色背景
    
    # 创建画笔
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)
    
    # 绘制外圆
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(41, 128, 185))  # 深蓝色
    painter.drawEllipse(10, 10, 236, 236)
    
    # 绘制内圆
    painter.setBrush(QColor(236, 240, 241))  # 近白色
    painter.drawEllipse(30, 30, 196, 196)
    
    # 设置字体
    font = QFont('Arial', 120, QFont.Bold)
    painter.setFont(font)
    
    # 绘制文字
    painter.setPen(QColor(52, 73, 94))  # 深灰色
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "G")
    
    # 结束绘制
    painter.end()
    
    # 确保目录存在
    if not os.path.exists('icons'):
        os.makedirs('icons')
    
    # 保存图标
    pixmap.save('icons/app_icon.png')
    
    # 创建并保存不同尺寸的图标（适用于Windows任务栏和系统托盘）
    icon = QIcon(pixmap)
    for size in [16, 32, 48, 64, 128]:
        small_pixmap = icon.pixmap(QSize(size, size))
        small_pixmap.save(f'icons/app_icon_{size}x{size}.png')
    
    # 复制一份到根目录作为应用默认图标
    pixmap.save('app_icon.png')
    
    print(f"图标已创建并保存到 icons/app_icon.png 和 app_icon.png")

if __name__ == "__main__":
    create_icon() 