from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFrame, QComboBox,
    QCheckBox, QScrollArea, QMessageBox, QLineEdit,
    QGridLayout, QSpinBox, QApplication, QFileDialog,
    QListWidget, QListWidgetItem, QDialog,
    QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import os
import platform
from core.command_builder import CommandBuilder
from core.services.minio_service import MinioService
from core.utils.config_manager import ConfigManager
from core.utils.logger import LogManager
import pyperclip
from datetime import timedelta

class FileSelectDialog(QDialog):
    def __init__(self, minio_service):
        super().__init__()
        self.minio_service = minio_service
        self.selected_files = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("选择文件")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        layout = QVBoxLayout()
        
        # 搜索和过滤区域
        filter_layout = QHBoxLayout()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文件名...")
        self.search_input.textChanged.connect(self.filter_files)
        filter_layout.addWidget(QLabel("搜索:"))
        filter_layout.addWidget(self.search_input)
        
        # 文件类型过滤
        self.type_combo = QComboBox()
        self.type_combo.addItems(["全部文件", "文本文件", "图片文件", "压缩文件", "其他文件"])
        self.type_combo.currentTextChanged.connect(self.filter_files)
        filter_layout.addWidget(QLabel("文件类型:"))
        filter_layout.addWidget(self.type_combo)
        
        layout.addLayout(filter_layout)
        
        # 文件列表（使用带复选框的树形视图）
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["文件名", "大小", "修改时间", "类型"])
        self.file_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.file_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.file_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        # 启用复选框
        self.file_tree.setSelectionMode(QTreeWidget.NoSelection)  # 禁用选择高亮
        self.file_tree.itemChanged.connect(self.update_selection_count)  # 当复选框状态改变时更新计数
        
        layout.addWidget(self.file_tree)
        
        # 选择计数
        self.selection_label = QLabel("已选择: 0 个文件")
        layout.addWidget(self.selection_label)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        # 全选/取消全选
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setCheckable(True)
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新列表")
        self.refresh_btn.clicked.connect(self.refresh_files)
        
        # 确定和取消按钮
        self.select_btn = QPushButton("选择")
        self.select_btn.setDefault(True)
        self.cancel_btn = QPushButton("取消")
        
        btn_layout.addWidget(self.select_all_btn)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # 连接信号
        self.select_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        # 加载文件列表
        self.refresh_files()
        
    def get_file_type(self, filename):
        """获取文件类型"""
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.txt', '.log', '.md', '.json', '.xml', '.csv']:
            return "文本文件"
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            return "图片文件"
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return "压缩文件"
        return "其他文件"
        
    def format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
        
    def refresh_files(self):
        """刷新文件列表"""
        try:
            self.file_tree.clear()
            files = self.minio_service.list_files()
            for file in files:
                item = QTreeWidgetItem(self.file_tree)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # 启用复选框
                item.setCheckState(0, Qt.Unchecked)  # 设置复选框初始状态
                item.setText(0, file["name"])
                item.setText(1, self.format_size(file["size"]))
                item.setText(2, file["last_modified"].strftime("%Y-%m-%d %H:%M"))
                item.setText(3, self.get_file_type(file["name"]))
            self.filter_files()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取文件列表失败: {str(e)}")
            
    def filter_files(self):
        """根据搜索文本和文件类型过滤文件"""
        search_text = self.search_input.text().lower()
        file_type = self.type_combo.currentText()
        
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            filename = item.text(0).lower()
            type_text = item.text(3)
            
            # 检查是否匹配搜索条件
            matches_search = not search_text or search_text in filename
            matches_type = file_type == "全部文件" or file_type == type_text
            
            # 显示或隐藏项目
            item.setHidden(not (matches_search and matches_type))
            
    def toggle_select_all(self, checked):
        """全选/取消全选"""
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            if not item.isHidden():
                item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
                
    def update_selection_count(self):
        """更新选择计数"""
        count = 0
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked and not item.isHidden():
                count += 1
        self.selection_label.setText(f"已选择: {count} 个文件")
            
    def get_selected_files(self):
        """获取选中的文件"""
        selected = []
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                selected.append(item.text(0))
        return selected

class FileListWidget(QListWidget):
    """自定义的文件列表控件，支持复选框"""
    def __init__(self):
        super().__init__()
        self.setSelectionMode(QListWidget.NoSelection)  # 禁用默认选择模式
        
    def add_file(self, filename):
        """添加一个带复选框的文件项"""
        item = QListWidgetItem()
        self.addItem(item)
        
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        
        checkbox = QCheckBox()
        checkbox.setText(filename)
        checkbox.setChecked(True)  # 默认选中
        
        layout.addWidget(checkbox)
        layout.addStretch()
        
        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        self.setItemWidget(item, widget)
        
    def get_selected_files(self):
        """获取所有选中的文件"""
        selected_files = []
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget:  # 确保widget存在
                checkbox = widget.layout().itemAt(0).widget()
                if checkbox and checkbox.isChecked():  # 确保checkbox存在且被选中
                    selected_files.append(checkbox.text())
        return selected_files
        
    def clear_selection(self):
        """清除所有选择"""
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget:  # 确保widget存在
                checkbox = widget.layout().itemAt(0).widget()
                if checkbox:  # 确保checkbox存在
                    checkbox.setChecked(False)
            
    def select_all(self):
        """选择所有文件"""
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget:  # 确保widget存在
                checkbox = widget.layout().itemAt(0).widget()
                if checkbox:  # 确保checkbox存在
                    checkbox.setChecked(True)

class CommandPage(QWidget):
    # 添加命令生成完成的信号
    command_generated = pyqtSignal()
    
    def __init__(self, minio_service: MinioService):
        super().__init__()
        self.minio_service = minio_service
        self.command_builder = CommandBuilder()
        self.logger = LogManager()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 当前MinIO配置显示
        config_info = self.minio_service.config_manager.get_minio_config()
        config_label = QLabel(f"当前MinIO服务器: {config_info['endpoint']} (存储桶: {config_info['bucket']})")
        config_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(config_label)
        
        # 文件列表区域
        files_frame = QFrame()
        files_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        files_layout = QVBoxLayout(files_frame)
        
        # 文件列表标题和操作按钮
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("已选择的文件:"))
        header_layout.addStretch()
        
        # 添加和移除按钮
        self.add_btn = QPushButton("添加文件")
        self.remove_btn = QPushButton("移除选中")
        self.clear_btn = QPushButton("清空列表")
        
        header_layout.addWidget(self.add_btn)
        header_layout.addWidget(self.remove_btn)
        header_layout.addWidget(self.clear_btn)
        files_layout.addLayout(header_layout)
        
        # 已选文件列表
        self.file_list = FileListWidget()
        files_layout.addWidget(self.file_list)
        
        files_frame.setLayout(files_layout)
        layout.addWidget(files_frame)
        
        # 链接有效期
        expiry_layout = QHBoxLayout()
        expiry_layout.addWidget(QLabel("链接有效期:"))
        self.expiry_combo = QComboBox()
        self.expiry_combo.addItems(["1小时", "6小时", "12小时", "1天", "7天"])
        self.expiry_combo.setCurrentText("1天")
        expiry_layout.addWidget(self.expiry_combo)
        expiry_layout.addStretch()
        layout.addLayout(expiry_layout)
        
        # 下载选项
        options_layout = QVBoxLayout()
        self.auto_extract_cb = QCheckBox("自动解压ZIP文件")
        self.auto_extract_cb.setChecked(True)
        self.copy_text_cb = QCheckBox("自动复制文本文件内容到剪贴板")
        self.copy_text_cb.setChecked(True)
        self.create_folder_cb = QCheckBox("为多个文件创建文件夹")
        self.create_folder_cb.setChecked(True)
        
        options_layout.addWidget(self.auto_extract_cb)
        options_layout.addWidget(self.copy_text_cb)
        options_layout.addWidget(self.create_folder_cb)
        layout.addLayout(options_layout)
        
        # 生成的命令显示
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.command_output.setMinimumHeight(150)
        layout.addWidget(QLabel("生成的PowerShell命令:"))
        layout.addWidget(self.command_output)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.generate_btn = QPushButton("生成命令")
        self.copy_btn = QPushButton("复制命令")
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.copy_btn)
        layout.addLayout(button_layout)
        
        # 使用说明
        help_text = """
        使用说明：
        1. 点击"添加文件"选择要分享的文件
        2. 设置链接有效期
        3. 选择需要的自动处理选项
        4. 点击"生成命令"生成PowerShell命令
        5. 复制命令到PowerShell中执行
        
        功能特点：
        - 自动解压ZIP文件
        - 自动复制文本文件内容到剪贴板
        - 多文件自动创建文件夹
        - 支持批量处理多个文件
        """
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 12px; padding: 10px;")
        layout.addWidget(help_label)
        
        self.setLayout(layout)
        
        # 连接信号
        self.add_btn.clicked.connect(self.add_files)
        self.remove_btn.clicked.connect(self.remove_files)
        self.clear_btn.clicked.connect(self.clear_files)
        self.generate_btn.clicked.connect(self.generate_command)
        self.copy_btn.clicked.connect(self.copy_command)
        
    def add_files(self):
        """添加文件"""
        dialog = FileSelectDialog(self.minio_service)
        if dialog.exec_() == QDialog.Accepted:
            selected_files = dialog.get_selected_files()
            for file in selected_files:
                # 检查是否已经添加
                items = self.file_list.findItems(file, Qt.MatchExactly)
                if not items:
                    self.file_list.add_file(file)
            
    def remove_files(self):
        """移除选中的文件"""
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
            
    def clear_files(self):
        """清空文件列表"""
        self.file_list.clear()
        
    def get_expiry_hours(self):
        """获取过期时间（小时）"""
        expiry_text = self.expiry_combo.currentText()
        if "天" in expiry_text:
            return int(expiry_text.replace("天", "")) * 24
        return int(expiry_text.replace("小时", ""))
        
    def get_file_type(self, filename):
        """获取文件类型"""
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.txt', '.log', '.md', '.json', '.xml', '.csv']:
            return "text"
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            return "image"
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return "archive"
        return "other"
        
    def generate_command(self):
        try:
            # 获取选中的文件
            selected_files = self.file_list.get_selected_files()
            if not selected_files:
                QMessageBox.warning(self, "警告", "请先选择文件")
                return
            
            # 统计文件类型
            file_types = set()
            for file in selected_files:
                file_types.add(self.get_file_type(file))
            
            # 生成命令
            command = self.command_builder.build_command(selected_files)
            if command:
                self.command_output.setPlainText(command)
                
                # 记录命令生成信息
                self.logger.log_command_generation(
                    file_count=len(selected_files),
                    file_types=list(file_types),
                    command_type="PowerShell"
                )
                
                # 发出命令生成完成的信号
                self.command_generated.emit()
            else:
                QMessageBox.warning(self, "错误", "没有生成任何命令")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成命令失败: {str(e)}")
            self.logger.log_error("命令生成错误", str(e))
            
    def copy_command(self):
        """复制命令到剪贴板"""
        cmd = self.command_output.toPlainText()
        if cmd:
            pyperclip.copy(cmd)
            QMessageBox.information(self, "成功", "命令已复制到剪贴板")
        else:
            QMessageBox.warning(self, "错误", "请先生成命令")