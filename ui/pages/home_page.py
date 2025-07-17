from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # 欢迎标题
        title = QLabel("欢迎使用 MinIO 命令生成器")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Bold))
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("一个简单、高效的 MinIO 文件管理工具")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)

        # 功能说明
        features = [
            "✨ 快速生成 MinIO 命令",
            "📁 便捷的文件管理功能",
            "🔍 文件快速选择工具",
            "📊 使用统计和分析",
            "⚙️ 灵活的配置选项"
        ]

        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setAlignment(Qt.AlignCenter)
            feature_label.setFont(QFont("Arial", 14))
            feature_label.setStyleSheet("color: #333333; margin: 10px;")
            layout.addWidget(feature_label)

        # 添加弹性空间
        layout.addStretch()

        # 提示文本
        hint = QLabel("使用左侧菜单开始使用各项功能")
        hint.setAlignment(Qt.AlignCenter)
        hint.setFont(QFont("Arial", 12))
        hint.setStyleSheet("color: #999999;")
        layout.addWidget(hint)