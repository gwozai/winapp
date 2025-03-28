import sys
import threading
import uuid
import redis
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QListWidget,
    QLineEdit, QPushButton, QLabel, QHBoxLayout
)

# 用于线程间通信的对象
class SignalBus(QObject):
    new_message = pyqtSignal(str)
    update_users = pyqtSignal()

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()

        # Redis 连接池配置
        self.redis = redis.Redis(
            host='106.12.107.176',
            port=6379,
            password='584257191',
            decode_responses=True,
            max_connections=10
        )

        # 匿名用户名生成
        self.username = f"User_{uuid.uuid4().hex[:6]}"
        self.channel = "chatroom"

        # 信号
        self.signal_bus = SignalBus()
        self.signal_bus.new_message.connect(self.display_message)
        self.signal_bus.update_users.connect(self.update_user_list)

        self.init_ui()
        self.register_user()
        self.start_message_listener()

    def init_ui(self):
        self.setWindowTitle(f"聊天室 - {self.username}")
        self.setGeometry(200, 200, 500, 400)

        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(QLabel("聊天室"))
        layout.addWidget(self.chat_display)

        self.user_list = QListWidget()
        layout.addWidget(QLabel("在线用户"))
        layout.addWidget(self.user_list)

        bottom_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.message_input)
        bottom_layout.addWidget(self.send_button)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        self.update_user_list()

    def register_user(self):
        self.redis.sadd("online_users", self.username)
        self.redis.publish(self.channel, f"📢 {self.username} 加入了聊天室")

    def closeEvent(self, event):
        self.redis.srem("online_users", self.username)
        self.redis.publish(self.channel, f"📢 {self.username} 离开了聊天室")
        event.accept()

    def update_user_list(self):
        self.user_list.clear()
        users = self.redis.smembers("online_users")
        for user in sorted(users):
            self.user_list.addItem(user)

    def display_message(self, msg):
        self.chat_display.append(msg)

    def send_message(self):
        msg = self.message_input.text().strip()
        if msg:
            self.redis.publish(self.channel, f"{self.username}: {msg}")
            self.message_input.clear()

    def start_message_listener(self):
        def listener():
            pubsub = self.redis.pubsub()
            pubsub.subscribe(self.channel)
            for message in pubsub.listen():
                if message['type'] == 'message':
                    text = message['data']
                    self.signal_bus.new_message.emit(text)
                    self.signal_bus.update_users.emit()

        threading.Thread(target=listener, daemon=True).start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec_())
