from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QComboBox, QProgressBar, QFrame, QMenu,
    QMessageBox, QFileDialog, QInputDialog, QApplication
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QClipboard
import os
import humanize
from datetime import datetime, timedelta
from core.services.minio_service import MinioService
from core.utils.config_manager import ConfigManager

class FileUploadThread(QThread):
    progress = pyqtSignal(str, int)  # 文件名, 进度
    finished = pyqtSignal(bool, str)  # 成功/失败, 消息

    def __init__(self, minio_service, file_path):
        super().__init__()
        self.minio_service = minio_service
        self.file_path = file_path

    def run(self):
        try:
            filename = os.path.basename(self.file_path)
            self.progress.emit(filename, 50)
            success = self.minio_service.upload_file(self.file_path)
            self.progress.emit(filename, 100)
            if success:
                self.finished.emit(True, f"文件 {filename} 上传成功")
            else:
                self.finished.emit(False, f"文件 {filename} 上传失败")
        except Exception as e:
            self.finished.emit(False, f"上传错误: {str(e)}")

class FileManagerPage(QWidget):
    def __init__(self, minio_service: MinioService):
        super().__init__()
        self.minio_service = minio_service
        self.upload_threads = []
        self.setup_ui()
        self.refresh_files()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # 顶部工具栏
        self.create_toolbar(layout)
        
        # 文件表格
        self.create_file_table(layout)
        
        # 底部状态栏
        self.create_status_bar(layout)

    def create_toolbar(self, parent_layout):
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文件...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #007bff;
            }
        """)
        self.search_input.textChanged.connect(self.filter_files)
        
        # 过滤器
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["所有文件", "图片", "文档", "压缩包", "其他"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                min-width: 120px;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.filter_files)

        # 上传按钮
        self.upload_btn = QPushButton("上传文件")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_files)

        # 新建文件夹按钮
        self.new_folder_btn = QPushButton("新建文件夹")
        self.new_folder_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.new_folder_btn.clicked.connect(self.create_folder)

        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_files)

        toolbar_layout.addWidget(self.search_input, 2)
        toolbar_layout.addWidget(self.filter_combo, 1)
        toolbar_layout.addWidget(self.upload_btn)
        toolbar_layout.addWidget(self.new_folder_btn)
        toolbar_layout.addWidget(self.refresh_btn)
        
        parent_layout.addWidget(toolbar)

    def create_file_table(self, parent_layout):
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(["名称", "大小", "修改日期", "类型"])
        
        # 设置表格样式
        self.file_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #ddd;
            }
        """)

        # 设置列宽
        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        
        self.file_table.setColumnWidth(1, 100)
        self.file_table.setColumnWidth(2, 150)
        self.file_table.setColumnWidth(3, 100)

        # 启用右键菜单
        self.file_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_table.customContextMenuRequested.connect(self.show_context_menu)

        parent_layout.addWidget(self.file_table)

    def create_status_bar(self, parent_layout):
        status_bar = QFrame()
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        status_layout = QHBoxLayout(status_bar)
        
        # 存储使用情况
        storage_label = QLabel("存储使用情况：")
        self.storage_progress = QProgressBar()
        self.storage_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 3px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #007bff;
            }
        """)
        
        # 文件统计
        self.stats_label = QLabel("总文件数：0")
        
        status_layout.addWidget(storage_label)
        status_layout.addWidget(self.storage_progress)
        status_layout.addStretch()
        status_layout.addWidget(self.stats_label)
        
        parent_layout.addWidget(status_bar)

    def refresh_files(self):
        """刷新文件列表"""
        try:
            # 获取文件列表
            files = self.minio_service.list_files()
            
            # 清空表格
            self.file_table.setRowCount(0)
            
            # 添加文件到表格
            for file in files:
                row = self.file_table.rowCount()
                self.file_table.insertRow(row)
                
                # 文件名
                name_item = QTableWidgetItem(file["name"])
                self.file_table.setItem(row, 0, name_item)
                
                # 文件大小
                size = humanize.naturalsize(file["size"])
                size_item = QTableWidgetItem(size)
                size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.file_table.setItem(row, 1, size_item)
                
                # 修改日期
                date = datetime.strftime(file["last_modified"], "%Y-%m-%d %H:%M")
                date_item = QTableWidgetItem(date)
                self.file_table.setItem(row, 2, date_item)
                
                # 文件类型
                ext = os.path.splitext(file["name"])[1].lower()
                type_item = QTableWidgetItem(self.get_file_type(ext))
                self.file_table.setItem(row, 3, type_item)
            
            # 更新状态栏
            self.update_status_bar()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新文件列表失败: {str(e)}")

    def get_file_type(self, ext: str) -> str:
        """根据扩展名获取文件类型"""
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        doc_exts = {'.txt', '.doc', '.docx', '.pdf', '.md', '.csv'}
        archive_exts = {'.zip', '.rar', '.7z', '.tar', '.gz'}
        
        if ext in image_exts:
            return "图片"
        elif ext in doc_exts:
            return "文档"
        elif ext in archive_exts:
            return "压缩包"
        else:
            return "其他"

    def filter_files(self):
        """根据搜索文本和类型过滤文件"""
        search_text = self.search_input.text().lower()
        file_type = self.filter_combo.currentText()
        
        for row in range(self.file_table.rowCount()):
            filename = self.file_table.item(row, 0).text().lower()
            type_item = self.file_table.item(row, 3).text()
            
            # 检查是否匹配搜索文本和文件类型
            match_search = search_text in filename
            match_type = file_type == "所有文件" or file_type == type_item
            
            # 显示或隐藏行
            self.file_table.setRowHidden(row, not (match_search and match_type))

    def update_status_bar(self):
        """更新状态栏信息"""
        try:
            # 获取存储桶大小
            total_size = self.minio_service.get_bucket_size()
            used_percent = min(total_size / (1024 * 1024 * 1024) * 100, 100)  # 假设有1GB限制
            
            self.storage_progress.setValue(int(used_percent))
            self.storage_progress.setFormat(f"{humanize.naturalsize(total_size)} / 1 GB")
            
            # 更新文件统计
            visible_count = sum(1 for row in range(self.file_table.rowCount())
                              if not self.file_table.isRowHidden(row))
            total_count = self.file_table.rowCount()
            
            self.stats_label.setText(f"显示: {visible_count} / 总数: {total_count}")
            
        except Exception as e:
            print(f"更新状态栏失败: {e}")

    def upload_files(self):
        """上传文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择要上传的文件",
            "",
            "所有文件 (*.*)"
        )
        
        if not files:
            return
            
        for file_path in files:
            # 创建上传线程
            thread = FileUploadThread(self.minio_service, file_path)
            thread.progress.connect(self.update_upload_progress)
            thread.finished.connect(self.handle_upload_finished)
            
            self.upload_threads.append(thread)
            thread.start()

    def update_upload_progress(self, filename: str, progress: int):
        """更新上传进度"""
        # TODO: 添加进度显示UI

    def handle_upload_finished(self, success: bool, message: str):
        """处理上传完成事件"""
        if success:
            self.refresh_files()
        QMessageBox.information(self, "上传完成", message)

    def create_folder(self):
        """创建新文件夹"""
        folder_name, ok = QInputDialog.getText(
            self,
            "新建文件夹",
            "请输入文件夹名称："
        )
        
        if ok and folder_name:
            try:
                if self.minio_service.create_folder(folder_name):
                    self.refresh_files()
                    QMessageBox.information(self, "成功", "文件夹创建成功")
                else:
                    QMessageBox.warning(self, "警告", "文件夹创建失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建文件夹失败: {str(e)}")

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
            }
        """)
        
        # 获取选中的项
        items = self.file_table.selectedItems()
        if not items:
            return
            
        row = items[0].row()
        filename = self.file_table.item(row, 0).text()
        
        # 添加菜单项
        download = menu.addAction("下载")
        preview = menu.addAction("预览")
        share = menu.addAction("生成分享链接")
        menu.addSeparator()
        rename = menu.addAction("重命名")
        delete = menu.addAction("删除")
        
        # 显示菜单并处理选择
        action = menu.exec_(self.file_table.mapToGlobal(position))
        
        if action == download:
            self.download_file(filename)
        elif action == preview:
            self.preview_file(filename)
        elif action == share:
            self.share_file(filename)
        elif action == rename:
            self.rename_file(filename)
        elif action == delete:
            self.delete_file(filename)

    def download_file(self, filename: str):
        """下载文件"""
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存文件",
            filename,
            "所有文件 (*.*)"
        )
        
        if save_path:
            try:
                if self.minio_service.download_file(filename, save_path):
                    QMessageBox.information(self, "成功", "文件下载成功")
                else:
                    QMessageBox.warning(self, "警告", "文件下载失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"下载文件失败: {str(e)}")

    def preview_file(self, filename: str):
        """预览文件"""
        # TODO: 实现文件预览功能
        QMessageBox.information(self, "提示", "文件预览功能开发中")

    def rename_file(self, filename: str):
        """重命名文件"""
        new_name, ok = QInputDialog.getText(
            self,
            "重命名",
            "请输入新的文件名：",
            text=filename
        )
        
        if ok and new_name and new_name != filename:
            try:
                if self.minio_service.rename_file(filename, new_name):
                    self.refresh_files()
                    QMessageBox.information(self, "成功", "文件重命名成功")
                else:
                    QMessageBox.warning(self, "警告", "文件重命名失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"重命名失败: {str(e)}")

    def delete_file(self, filename: str):
        """删除文件"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除 {filename} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.minio_service.delete_file(filename):
                    self.refresh_files()
                    QMessageBox.information(self, "成功", "文件删除成功")
                else:
                    QMessageBox.warning(self, "警告", "文件删除失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除文件失败: {str(e)}")

    def share_file(self, filename: str):
        """生成文件分享链接"""
        try:
            # 生成24小时有效的预签名URL
            url = self.minio_service.get_presigned_url(
                filename,
                expires=timedelta(hours=24)
            )
            
            if url:
                # 复制链接到剪贴板
                clipboard = QApplication.clipboard()
                clipboard.setText(url)
                
                QMessageBox.information(
                    self,
                    "分享成功",
                    "分享链接已复制到剪贴板\n链接有效期：24小时"
                )
            else:
                QMessageBox.warning(self, "警告", "生成分享链接失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成分享链接失败: {str(e)}") 