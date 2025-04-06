import sys
import redis
import random
import requests
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QDialog, QLabel, QLineEdit
from PyQt5.QtGui import QPixmap, QImage
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO


# 自定义弹窗类
class CustomPopup(QDialog):
    def __init__(self, message):
        super().__init__()

        self.setWindowTitle('通知')  # 弹窗标题
        self.setFixedSize(250, 100)  # 设置弹窗大小

        # 设置弹窗样式
        self.setStyleSheet("""
            background-color: #333;
            color: white;
            border-radius: 10px;
            font-size: 14px;
            padding: 10px;
        """)

        # 显示的内容
        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # 设置窗口置顶
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # 设置透明度
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 计算右下角的位置并设置窗口位置
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 10, screen.height() - self.height() - 10)

        # 设置定时器，3秒后自动关闭弹窗
        QTimer.singleShot(3000, self.close)

    def show_popup(self):
        # 延迟显示弹窗，避免阻塞主线程
        QTimer.singleShot(0, self.show)


# Redis消息接收线程
class RedisReceiverThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, redis_host, redis_port, redis_password, channel, thread_pool):
        super().__init__()
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.channel = channel
        self.thread_pool = thread_pool
        self.client = redis.StrictRedis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        self.pubsub = self.client.pubsub()
        self.pubsub.subscribe(self.channel)

    def run(self):
        # 使用线程池来管理 Redis 消息的接收
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                self.thread_pool.submit(self.message_received.emit, message['data'].decode('utf-8'))


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('图片随机播放')
        self.setFixedSize(800, 600)

        # 创建布局
        self.layout = QVBoxLayout()

        # 输入框用于添加多个图片URL
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("输入图片 URL（多个 URL 用逗号分隔）")

        # 按钮，点击后添加URL并显示图片
        self.add_button = QPushButton('添加 URL', self)
        self.add_button.clicked.connect(self.add_url)

        # 图片显示标签
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        # 在线人数显示标签
        self.online_label = QLabel(self)
        self.online_label.setAlignment(Qt.AlignCenter)

        # 布局
        self.layout.addWidget(self.url_input)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.online_label)

        self.setLayout(self.layout)

        # 用于存储图片URL的列表
        self.image_urls = []

        # 创建线程池，最大线程数为 5
        self.thread_pool = ThreadPoolExecutor(max_workers=5)  # Initialize ThreadPoolExecutor

        # 初始化Redis接收线程
        self.redis_thread = RedisReceiverThread(
            redis_host='106.12.107.176',
            redis_port=6379,
            redis_password='584257191',
            channel='notifications_channel',  # 频道名称
            thread_pool=self.thread_pool
        )
        self.redis_thread.message_received.connect(self.show_notification)
        self.redis_thread.start()

        # 定时器，随机显示图片
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_random_image)
        self.timer.start(5000)  # 每 5 秒钟随机选择并显示图片

        # 定时器，更新在线人数
        self.online_timer = QTimer(self)
        self.online_timer.timeout.connect(self.update_online_count)
        self.online_timer.start(10000)  # 每 10 秒钟更新一次在线人数

    def add_url(self):
        # 获取输入框中的图片URL并添加到列表
        urls = self.url_input.text().split(',')
        self.image_urls.extend([url.strip() for url in urls if url.strip()])
        self.url_input.clear()

        # 打印当前URL列表
        print("当前图片URL列表：", self.image_urls)

    def show_random_image(self):
        # 如果URL列表非空，则随机选择一个URL并显示图片
        if self.image_urls:
            random_url = random.choice(self.image_urls)
            pixmap = self.load_image_from_url(random_url)
            if pixmap:
                self.image_label.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatio))

    def load_image_from_url(self, url):
        try:
            # 下载图片
            response = requests.get(url)
            if response.status_code == 200:
                image_data = response.content
                image = QImage()
                image.loadFromData(image_data)
                pixmap = QPixmap(image)
                return pixmap
            else:
                print(f"无法下载图片: {url}")
                return None
        except Exception as e:
            print(f"加载图片失败: {url}, 错误: {e}")
            return None

    def update_online_count(self):
        # 从Redis获取在线人数
        try:
            online_count = self.client.get('online_users_count')  # 这个key是用来存储在线人数的
            if online_count:
                self.online_label.setText(f"当前在线人数: {online_count.decode('utf-8')}")
            else:
                self.online_label.setText("当前在线人数: 0")
        except Exception as e:
            print(f"获取在线人数失败: {e}")
            self.online_label.setText("当前在线人数: 无法获取")

    def show_popup(self):
        # 获取输入框内容
        input_text = self.input_line.text()

        # 如果输入框为空，则显示默认消息
        if not input_text:
            input_text = '请输入一些消息'

        # 创建弹窗并显示
        self.popup = CustomPopup(input_text)
        self.popup.show_popup()

    def show_notification(self, message):
        # 当接收到Redis消息时创建通知弹窗
        self.popup = CustomPopup(message)
        self.popup.show_popup()


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
