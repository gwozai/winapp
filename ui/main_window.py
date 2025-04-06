from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget
from ui.pages.home_page import HomePage
from ui.pages.settings_page import SettingsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MinIO 命令生成器")
        self.setGeometry(200, 100, 900, 650)

        self.stack = QStackedWidget()
        self.home_page = HomePage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.settings_page)

        self.btn_home = QPushButton("🏠 首页")
        self.btn_settings = QPushButton("⚙️ 设置")
        self.btn_home.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_settings.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.stack)
        container.setLayout(layout)
        self.setCentralWidget(container)