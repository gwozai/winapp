from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFrame, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QFileDialog, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from core.utils.logger import LogManager
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import matplotlib as mpl
import platform
from matplotlib.font_manager import FontProperties
import matplotlib.font_manager as fm

class StatsPage(QWidget):
    def __init__(self, log_manager):
        super().__init__()
        
        # 设置matplotlib中文字体
        self.setup_matplotlib_fonts()
        
        self.logger = log_manager
        self.init_ui()
        
        # 设置自动刷新定时器
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.start(5000)  # 每5秒刷新一次

    def setup_matplotlib_fonts(self):
        """设置matplotlib的中文字体"""
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            # 尝试多个常见的中文字体
            chinese_fonts = [
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',
                '/System/Library/Fonts/STHeiti Medium.ttc',
                '/System/Library/Fonts/Hiragino Sans GB.ttc'
            ]
            
            # 查找第一个存在的字体
            font_path = None
            for font in chinese_fonts:
                if os.path.exists(font):
                    font_path = font
                    break
            
            if font_path:
                self.font_prop = FontProperties(fname=font_path)
                plt.rcParams['font.family'] = self.font_prop.get_name()
            else:
                print("警告：未找到合适的中文字体")
                
        elif system == 'Windows':
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        else:  # Linux
            plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']
            
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['figure.dpi'] = 100

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 概览页
        overview_tab = QWidget()
        self.setup_overview_tab(overview_tab)
        self.tab_widget.addTab(overview_tab, "概览")
        
        # 详细统计页
        stats_tab = QWidget()
        self.setup_stats_tab(stats_tab)
        self.tab_widget.addTab(stats_tab, "详细统计")
        
        # 日志查看页
        logs_tab = QWidget()
        self.setup_logs_tab(logs_tab)
        self.tab_widget.addTab(logs_tab, "日志查看")
        
        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新统计数据")
        export_btn = QPushButton("导出统计")
        
        refresh_btn.clicked.connect(self.refresh_stats)
        export_btn.clicked.connect(self.export_stats)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)

    def setup_overview_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # 基本信息框
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.StyledPanel)
        info_layout = QGridLayout(info_frame)
        
        # 获取统计数据
        stats = self.logger.get_stats()
        
        # 显示基本统计信息
        self.command_count_label = QLabel(f"命令生成总次数: {stats.get('command_generated_count', 0)}")
        self.last_command_label = QLabel(f"最后生成时间: {stats.get('last_command_time', '无')}")
        
        info_layout.addWidget(self.command_count_label, 0, 0)
        info_layout.addWidget(self.last_command_label, 1, 0)
        
        layout.addWidget(info_frame)
        
        # 创建图表
        self.file_type_figure = plt.figure(figsize=(6, 4))
        self.file_type_canvas = FigureCanvas(self.file_type_figure)
        layout.addWidget(self.file_type_canvas)
        
        self.update_file_type_chart(stats.get('file_types_stats', {}))

    def setup_stats_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # 文件类型统计表格
        type_group = QFrame()
        type_group.setFrameStyle(QFrame.StyledPanel)
        type_layout = QVBoxLayout(type_group)
        
        type_layout.addWidget(QLabel("文件类型统计"))
        self.type_table = QTableWidget(4, 2)
        self.type_table.setHorizontalHeaderLabels(["类型", "数量"])
        self.type_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        type_layout.addWidget(self.type_table)
        
        layout.addWidget(type_group)
        
        # 月度统计表格
        monthly_group = QFrame()
        monthly_group.setFrameStyle(QFrame.StyledPanel)
        monthly_layout = QVBoxLayout(monthly_group)
        
        monthly_layout.addWidget(QLabel("月度统计"))
        self.monthly_figure = plt.figure(figsize=(8, 4))
        self.monthly_canvas = FigureCanvas(self.monthly_figure)
        monthly_layout.addWidget(self.monthly_canvas)
        
        layout.addWidget(monthly_group)
        
        self.update_tables()

    def setup_logs_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # 日志文件选择
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("选择日志文件:"))
        self.log_combo = QComboBox()
        self.update_log_files()
        select_layout.addWidget(self.log_combo)
        
        layout.addLayout(select_layout)
        
        # 日志内容显示
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 连接信号
        self.log_combo.currentTextChanged.connect(self.load_log_file)

    def refresh_stats(self):
        """刷新统计数据"""
        try:
            stats = self.logger.get_stats()
            
            # 更新基本统计信息
            total_commands = stats["command_generated_count"]
            last_time = stats.get("last_command_time")
            if last_time:
                last_time = datetime.fromisoformat(last_time).strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_time = "从未"
                
            stats_text = f"总共生成命令次数: {total_commands}\n最后一次生成时间: {last_time}"
            self.command_count_label.setText(f"命令生成总次数: {total_commands}")
            self.last_command_label.setText(f"最后生成时间: {last_time}")
            
            # 更新文件类型分布图
            self.update_file_type_chart(stats["file_types_stats"])
            
            # 更新月度统计图
            self.update_monthly_chart(stats["monthly_stats"])
            
            # 更新表格
            self.update_tables()
            
            # 更新日志文件列表
            self.update_log_files()
            
        except Exception as e:
            print(f"刷新统计数据失败: {e}")
            self.command_count_label.setText("命令生成总次数: 获取失败")
            self.last_command_label.setText("最后生成时间: 获取失败")

    def update_file_type_chart(self, type_stats):
        """更新文件类型分布图"""
        self.file_type_figure.clear()
        ax = self.file_type_figure.add_subplot(111)
        
        # 准备数据
        labels = []
        sizes = []
        for type_name, count in type_stats.items():
            if count > 0:  # 只显示有数据的类型
                labels.append(type_name)
                sizes.append(count)
                
        if not sizes:  # 没有数据时显示提示
            ax.text(0.5, 0.5, '暂无数据', ha='center', va='center')
            ax.axis('off')
        else:
            # 设置中文字体
            self.set_chinese_font(ax)
            
            # 绘制饼图
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            
        self.file_type_canvas.draw()

    def update_monthly_chart(self, monthly_stats):
        """更新月度统计图"""
        self.monthly_figure.clear()
        ax = self.monthly_figure.add_subplot(111)
        
        if not monthly_stats:  # 没有数据时显示提示
            ax.text(0.5, 0.5, '暂无数据', ha='center', va='center')
            ax.axis('off')
        else:
            # 设置中文字体
            self.set_chinese_font(ax)
            
            # 准备数据
            months = list(monthly_stats.keys())
            counts = list(monthly_stats.values())
            
            # 绘制柱状图
            ax.bar(months, counts)
            ax.set_xlabel('月份')
            ax.set_ylabel('命令生成次数')
            ax.set_title('月度命令生成统计')
            
            # 旋转x轴标签以防重叠
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
        self.monthly_figure.tight_layout()
        self.monthly_canvas.draw()

    def set_chinese_font(self, ax):
        """设置中文字体"""
        system = platform.system()
        if system == 'Windows':
            font_path = 'C:/Windows/Fonts/msyh.ttc'  # 微软雅黑
        elif system == 'Darwin':  # macOS
            # macOS 字体路径
            font_paths = [
                '/System/Library/Fonts/PingFang.ttc',  # PingFang
                '/System/Library/Fonts/STHeiti Light.ttc',  # Heiti
                '/System/Library/Fonts/Hiragino Sans GB.ttc'  # Hiragino
            ]
            # 使用第一个存在的字体
            font_path = next((path for path in font_paths if os.path.exists(path)), None)
        else:  # Linux
            font_path = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
            
        if font_path and os.path.exists(font_path):
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            
    def update_tables(self):
        """更新统计表格"""
        try:
            stats = self.logger.get_stats()
            
            # 更新文件类型表格
            type_stats = stats.get('file_types_stats', {})
            valid_type_stats = {k: v for k, v in type_stats.items() 
                              if isinstance(v, (int, float)) and v >= 0}
            
            self.type_table.setRowCount(max(len(valid_type_stats), 1))
            
            if valid_type_stats:
                for i, (type_name, count) in enumerate(valid_type_stats.items()):
                    self.type_table.setItem(i, 0, QTableWidgetItem(str(type_name)))
                    self.type_table.setItem(i, 1, QTableWidgetItem(str(int(count))))
            else:
                self.type_table.setItem(0, 0, QTableWidgetItem("暂无数据"))
                self.type_table.setItem(0, 1, QTableWidgetItem("0"))
            
            # 更新月度统计表格
            monthly_stats = stats.get('monthly_stats', {})
            valid_monthly_stats = {k: v for k, v in monthly_stats.items() 
                                 if isinstance(v, (int, float)) and v >= 0}
            
            self.monthly_figure.clear()
            ax = self.monthly_figure.add_subplot(111)
            
            if not valid_monthly_stats:
                ax.text(0.5, 0.5, '暂无数据', ha='center', va='center')
                ax.axis('off')
            else:
                # 设置中文字体
                self.set_chinese_font(ax)
                
                # 准备数据
                months = list(valid_monthly_stats.keys())
                counts = list(valid_monthly_stats.values())
                
                # 绘制柱状图
                ax.bar(months, counts)
                ax.set_xlabel('月份')
                ax.set_ylabel('命令生成次数')
                ax.set_title('月度命令生成统计')
                
                # 旋转x轴标签以防重叠
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            self.monthly_figure.tight_layout()
            self.monthly_canvas.draw()
            
        except Exception as e:
            print(f"更新表格时出错: {str(e)}")
            # 显示错误信息在表格中
            self.type_table.setRowCount(1)
            self.type_table.setItem(0, 0, QTableWidgetItem("更新失败"))
            self.type_table.setItem(0, 1, QTableWidgetItem("--"))
            
            self.monthly_figure.clear()
            ax = self.monthly_figure.add_subplot(111)
            ax.text(0.5, 0.5, '更新失败', ha='center', va='center')
            ax.axis('off')
            self.monthly_canvas.draw()

    def update_log_files(self):
        """更新日志文件列表"""
        current_file = self.log_combo.currentText()
        self.log_combo.clear()
        
        log_dir = "logs"
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            self.log_combo.addItems(sorted(log_files, reverse=True))
            
            # 恢复之前选择的文件
            if current_file and current_file in log_files:
                self.log_combo.setCurrentText(current_file)
            elif log_files:
                self.log_combo.setCurrentText(log_files[0])

    def load_log_file(self, filename):
        """加载选中的日志文件"""
        if not filename:
            return
            
        try:
            log_path = os.path.join("logs", filename)
            with open(log_path, 'r', encoding='utf-8') as f:
                self.log_text.setText(f.read())
        except Exception as e:
            self.log_text.setText(f"加载日志文件失败: {str(e)}")

    def export_stats(self):
        """导出统计数据"""
        try:
            # 获取保存路径
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "导出统计数据",
                f"minio_stats_{datetime.now().strftime('%Y%m%d')}.txt",
                "Text Files (*.txt)"
            )
            
            if not filename:
                return
                
            # 获取统计数据
            stats = self.logger.get_stats()
            
            # 生成报告内容
            content = [
                "MinIO 命令生成器统计报告",
                f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "\n基本信息:",
                f"命令生成总次数: {stats.get('command_generated_count', 0)}",
                f"最后生成时间: {stats.get('last_command_time', '无')}",
                "\n文件类型统计:",
            ]
            
            type_stats = stats.get('file_types_stats', {})
            if type_stats:
                for type_name, count in type_stats.items():
                    content.append(f"{type_name}: {count}")
            else:
                content.append("暂无数据")
                
            content.append("\n月度使用统计:")
            monthly_stats = stats.get('monthly_stats', {})
            if monthly_stats:
                for month, count in sorted(monthly_stats.items()):
                    content.append(f"{month}: {count}")
            else:
                content.append("暂无数据")
                
            # 写入文件
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
                
            QMessageBox.information(self, "成功", "统计数据导出成功！")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出统计数据失败: {str(e)}")

    def connect_command_page(self, command_page):
        """连接到命令页面的信号"""
        command_page.command_generated.connect(self.refresh_stats) 