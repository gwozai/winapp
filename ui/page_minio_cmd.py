
import os
import json
from datetime import timedelta
from urllib.parse import unquote
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QLabel, QMessageBox, QListView, QApplication
)
from PyQt5.QtCore import Qt, QThreadPool
from minio import Minio

from core.worker import Worker

class MinioCmdPage(QWidget):
    def __init__(self):
        super().__init__()

        self.client = Minio("106.12.107.176:19000",
                            access_key="minio",
                            secret_key="ei2BEHZYLaR8eGtT",
                            secure=False)
        self.bucket = "album"
        self.objects = []
        self.pool = QThreadPool()

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListView.MultiSelection)
        self.generate_button = QPushButton("生成命令")
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        layout.addWidget(QLabel("文件列表："))
        layout.addWidget(self.list_widget)
        layout.addWidget(self.generate_button)
        layout.addWidget(QLabel("合并命令："))
        layout.addWidget(self.output_box)
        self.setLayout(layout)

        self.generate_button.clicked.connect(self.generate_commands)

        self.load_files_async()

    def load_files_async(self):
        worker = Worker(self.fetch_objects)
        worker.signals.result.connect(self.populate_list)
        worker.signals.error.connect(self.show_error)
        self.pool.start(worker)

    def fetch_objects(self):
        return list(self.client.list_objects(self.bucket, recursive=True))

    def populate_list(self, objects):
        self.objects = objects
        self.list_widget.clear()
        for obj in objects:
            filename = os.path.basename(unquote(obj.object_name))
            item = QListWidgetItem(f"{filename} ({obj.object_name})")
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

    def show_error(self, message):
        QMessageBox.critical(self, "错误", message)

    def extract_filename_and_type(self, object_path):
        filename = os.path.basename(unquote(object_path))
        _, ext = os.path.splitext(filename)
        return filename, ext.lower()

    def is_archive(self, ext):
        return ext in {'.zip', '.rar', '.7z'}

    def is_text_file(self, ext):
        return ext in {'.txt', '.md', '.json', '.log', '.csv'}

    def generate_commands(self):
        selected_indexes = [i for i in range(self.list_widget.count())
                            if self.list_widget.item(i).checkState() == Qt.Checked]

        if not selected_indexes:
            QMessageBox.warning(self, "提示", "请至少选择一个文件。")
            return

        commands = []

        for i in selected_indexes:
            obj = self.objects[i]
            url = self.client.presigned_get_object(
                self.bucket, obj.object_name, expires=timedelta(hours=1)
            )
            filename, ext = self.extract_filename_and_type(obj.object_name)

            if self.is_archive(ext):
                foldername = os.path.splitext(filename)[0]
                cmd = (
                    f'mkdir "{foldername}" 2>nul && curl -o "{filename}" "{url}" && '
                    f'powershell -command "Expand-Archive -Path \"{filename}\" -DestinationPath .\{foldername} -Force" && del "{filename}"'
                )
            elif self.is_text_file(ext):
                cmd = f"powershell -Command \"Set-Clipboard -Value (Invoke-WebRequest -Uri '{url}').Content\""
            else:
                cmd = f'curl -O "{url}"'

            commands.append(cmd)

        merged_cmd = " && \
".join(commands)
        self.output_box.setText(merged_cmd)

        QApplication.clipboard().setText(merged_cmd)
        QMessageBox.information(self, "完成", "命令已生成并复制到剪贴板。")
