from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame,
    QSizePolicy, QTabWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from ui.pages.home_page import HomePage
from ui.pages.command_page import CommandPage
from ui.pages.file_manager_page import FileManagerPage
from ui.pages.file_select_page import FileSelectPage
from ui.pages.settings_page import SettingsPage
from ui.pages.stats_page import StatsPage
from core.utils.config_manager import ConfigManager
from core.services.minio_service import MinioService
from core.utils.logger import LogManager

class ModernSidebarButton(QPushButton):
    def __init__(self, text="", icon=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(50)
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 5px;
                text-align: left;
                padding: 5px 10px;
                color: #ffffff;
                background: transparent;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            QPushButton:checked {
                background: rgba(255, 255, 255, 0.2);
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MinIO文件管理器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化服务和管理器
        self.config_manager = ConfigManager()
        self.minio_service = MinioService(self.config_manager)
        self.log_manager = LogManager()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 创建标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 创建各个页面
        self.command_page = CommandPage(self.minio_service)
        self.stats_page = StatsPage(self.log_manager)
        self.settings_page = SettingsPage(self.config_manager)
        self.file_manager_page = FileManagerPage(self.minio_service)
        
        # 连接命令页面和统计页面
        self.stats_page.connect_command_page(self.command_page)
        
        # 添加标签页
        tab_widget.addTab(self.command_page, "命令生成")
        tab_widget.addTab(self.file_manager_page, "文件管理")
        tab_widget.addTab(self.stats_page, "统计信息")
        tab_widget.addTab(self.settings_page, "设置")
    
    def switch_page(self, index):
        """切换页面并更新按钮状态"""
        self.stack.setCurrentIndex(index)
        buttons = [self.btn_home, self.btn_commands, self.btn_files, 
                  self.btn_file_select, self.btn_stats, self.btn_settings]
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index) 