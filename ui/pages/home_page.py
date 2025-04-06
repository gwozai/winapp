from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📄 欢迎使用 MinIO 命令生成器"))
        layout.addWidget(QPushButton("开始生成命令"))
        self.setLayout(layout)