from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget
from ui.page_minio_cmd import MinioCmdPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MinIO 命令工具箱")
        self.setGeometry(200, 100, 1000, 700)

        central = QWidget()
        layout = QHBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.menu = QListWidget()
        self.menu.addItem("📥 命令生成")
        self.menu.currentRowChanged.connect(self.change_page)
        layout.addWidget(self.menu, 1)

        self.stack = QStackedWidget()
        self.page_minio = MinioCmdPage()
        self.stack.addWidget(self.page_minio)
        layout.addWidget(self.stack, 4)

    def change_page(self, index):
        self.stack.setCurrentIndex(index)
