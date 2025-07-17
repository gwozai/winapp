from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTreeWidget, QTreeWidgetItem, QHeaderView,
                             QLineEdit, QComboBox, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
import os
from datetime import datetime

class FileSelectPage(QWidget):
    """文件选择页面，支持多文件选择、搜索和过滤"""
    
    # 定义信号
    files_selected = pyqtSignal(list)  # 当文件被选中时发出信号
    
    def __init__(self, minio_service):
        super().__init__()
        self.minio_service = minio_service
        self.selected_files = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文件名...")
        self.search_input.textChanged.connect(self.filter_files)
        toolbar.addWidget(QLabel("搜索:"))
        toolbar.addWidget(self.search_input)
        
        # 文件类型过滤
        self.type_combo = QComboBox()
        self.type_combo.addItems(["全部文件", "文本文件", "图片文件", "压缩文件", "其他文件"])
        self.type_combo.currentTextChanged.connect(self.filter_files)
        toolbar.addWidget(QLabel("文件类型:"))
        toolbar.addWidget(self.type_combo)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新列表")
        self.refresh_btn.clicked.connect(self.refresh_files)
        toolbar.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 文件列表
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["文件名", "大小", "修改时间", "类型"])
        self.file_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.file_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.file_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.file_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.file_tree.itemSelectionChanged.connect(self.update_selection)
        layout.addWidget(self.file_tree)
        
        # 底部状态栏
        status_bar = QHBoxLayout()
        
        # 选择计数
        self.selection_label = QLabel("已选择: 0 个文件")
        status_bar.addWidget(self.selection_label)
        
        # 全选/取消全选
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setCheckable(True)
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        status_bar.addWidget(self.select_all_btn)
        
        # 确认选择按钮
        self.confirm_btn = QPushButton("确认选择")
        self.confirm_btn.clicked.connect(self.confirm_selection)
        status_bar.addWidget(self.confirm_btn)
        
        layout.addLayout(status_bar)
        
        self.setLayout(layout)
        
        # 初始加载文件
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
                item.setSelected(checked)
                
    def update_selection(self):
        """更新选择状态"""
        self.selected_files = [item.text(0) for item in self.file_tree.selectedItems()]
        count = len(self.selected_files)
        self.selection_label.setText(f"已选择: {count} 个文件")
        
    def confirm_selection(self):
        """确认选择并发出信号"""
        if self.selected_files:
            self.files_selected.emit(self.selected_files)
        else:
            QMessageBox.warning(self, "提示", "请至少选择一个文件")
            
    def get_selected_files(self):
        """获取选中的文件列表"""
        return self.selected_files 