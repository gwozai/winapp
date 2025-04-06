from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QMessageBox

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.endpoint = QLineEdit("106.12.107.176:19000")
        self.access_key = QLineEdit("minio")
        self.secret_key = QLineEdit("ei2BEHZYLaR8eGtT")
        self.bucket = QLineEdit("album")

        layout = QFormLayout()
        layout.addRow("Endpoint:", self.endpoint)
        layout.addRow("Access Key:", self.access_key)
        layout.addRow("Secret Key:", self.secret_key)
        layout.addRow("Bucket:", self.bucket)

        save_button = QPushButton("保存配置")
        save_button.clicked.connect(self.save_config)
        layout.addRow(save_button)

        self.setLayout(layout)

    def save_config(self):
        QMessageBox.information(self, "提示", "配置已保存！（开发中）")