from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QFrame,
    QCheckBox, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt
from core.utils.config_manager import ConfigManager

class SettingsPage(QWidget):
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # MinIO设置
        self.create_minio_settings(layout)
        
        # 命令生成设置
        self.create_command_settings(layout)
        
        # 保存按钮
        self.create_save_button(layout)

    def create_minio_settings(self, parent_layout):
        group = QGroupBox("MinIO 设置")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)

        # 创建输入框
        self.endpoint = QLineEdit()
        self.access_key = QLineEdit()
        self.secret_key = QLineEdit()
        self.bucket = QLineEdit()
        self.secure = QCheckBox("使用HTTPS")

        # 设置样式
        input_style = """
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #007bff;
            }
        """
        self.endpoint.setStyleSheet(input_style)
        self.access_key.setStyleSheet(input_style)
        self.secret_key.setStyleSheet(input_style)
        self.bucket.setStyleSheet(input_style)

        # 添加到布局
        layout.addRow("服务器地址:", self.endpoint)
        layout.addRow("Access Key:", self.access_key)
        layout.addRow("Secret Key:", self.secret_key)
        layout.addRow("存储桶:", self.bucket)
        layout.addRow("", self.secure)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_command_settings(self, parent_layout):
        group = QGroupBox("命令生成设置")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)

        # 创建选项
        self.show_progress = QCheckBox("显示下载进度")
        self.use_powershell = QCheckBox("优先使用PowerShell命令")
        self.auto_delete = QCheckBox("下载后自动删除")

        # 设置样式
        checkbox_style = """
            QCheckBox {
                padding: 5px;
                color: #333;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """
        self.show_progress.setStyleSheet(checkbox_style)
        self.use_powershell.setStyleSheet(checkbox_style)
        self.auto_delete.setStyleSheet(checkbox_style)

        # 添加到布局
        layout.addWidget(self.show_progress)
        layout.addWidget(self.use_powershell)
        layout.addWidget(self.auto_delete)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_save_button(self, parent_layout):
        # 创建按钮容器
        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # 创建保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        save_btn.clicked.connect(self.save_settings)

        # 创建测试连接按钮
        test_btn = QPushButton("测试连接")
        test_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        test_btn.clicked.connect(self.test_connection)

        button_layout.addWidget(test_btn)
        button_layout.addWidget(save_btn)
        
        parent_layout.addStretch()
        parent_layout.addWidget(button_container)

    def load_settings(self):
        """从配置管理器加载设置"""
        # 加载MinIO设置
        minio_config = self.config_manager.get_minio_config()
        self.endpoint.setText(minio_config["endpoint"])
        self.access_key.setText(minio_config["access_key"])
        self.secret_key.setText(minio_config["secret_key"])
        self.bucket.setText(minio_config["bucket"])
        self.secure.setChecked(minio_config["secure"])

        # 加载命令生成设置
        cmd_config = self.config_manager.get_commands_config()
        self.show_progress.setChecked(cmd_config["show_progress"])
        self.use_powershell.setChecked(cmd_config["use_powershell"])
        self.auto_delete.setChecked(cmd_config["auto_delete"])

    def save_settings(self):
        """保存设置到配置管理器"""
        try:
            # 保存MinIO设置
            minio_config = {
                "endpoint": self.endpoint.text(),
                "access_key": self.access_key.text(),
                "secret_key": self.secret_key.text(),
                "bucket": self.bucket.text(),
                "secure": self.secure.isChecked()
            }
            self.config_manager.update_minio_config(minio_config)

            # 保存命令生成设置
            cmd_config = {
                "show_progress": self.show_progress.isChecked(),
                "use_powershell": self.use_powershell.isChecked(),
                "auto_delete": self.auto_delete.isChecked()
            }
            self.config_manager.update_commands_config(cmd_config)

            QMessageBox.information(self, "成功", "设置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")

    def test_connection(self):
        """测试MinIO连接"""
        try:
            from minio import Minio
            client = Minio(
                endpoint=self.endpoint.text(),
                access_key=self.access_key.text(),
                secret_key=self.secret_key.text(),
                secure=self.secure.isChecked()
            )
            
            # 尝试列出文件
            list(client.list_objects(self.bucket.text(), prefix="", recursive=True))
            
            QMessageBox.information(self, "成功", "连接测试成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接测试失败: {str(e)}")