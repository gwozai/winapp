import logging
import os
from datetime import datetime
import json
from typing import Dict, Any

class LogManager:
    def __init__(self):
        # 确保日志目录存在
        self.log_dir = "logs"
        self.stats_file = os.path.join(self.log_dir, "command_stats.json")
        os.makedirs(self.log_dir, exist_ok=True)

        # 配置主日志记录器
        self.logger = logging.getLogger('minio_manager')
        self.logger.setLevel(logging.INFO)

        # 创建日志文件处理器
        log_file = os.path.join(self.log_dir, f"minio_manager_{datetime.now().strftime('%Y%m')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器到日志记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 初始化统计数据
        self.init_stats()

    def init_stats(self):
        """初始化或加载统计数据"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except:
                self.stats = self._create_default_stats()
        else:
            self.stats = self._create_default_stats()
        self.save_stats()

    def _create_default_stats(self) -> Dict[str, Any]:
        """创建默认的统计数据结构"""
        return {
            "command_generated_count": 0,
            "last_command_time": None,
            "file_types_stats": {
                "text": 0,
                "image": 0,
                "archive": 0,
                "other": 0
            },
            "monthly_stats": {}
        }

    def save_stats(self):
        """保存统计数据到文件"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存统计数据失败: {e}")

    def log_minio_connection(self, endpoint: str, bucket: str, success: bool, error_msg: str = None):
        """记录MinIO连接信息"""
        if success:
            self.logger.info(f"成功连接到MinIO服务器 - 端点: {endpoint}, 存储桶: {bucket}")
        else:
            self.logger.error(f"连接MinIO服务器失败 - 端点: {endpoint}, 存储桶: {bucket}, 错误: {error_msg}")

    def log_command_generation(self, file_count: int, file_types: list, command_type: str):
        """记录命令生成信息"""
        # 更新基本统计信息
        self.stats["command_generated_count"] += 1
        self.stats["last_command_time"] = datetime.now().isoformat()

        # 更新月度统计
        current_month = datetime.now().strftime("%Y-%m")
        if current_month not in self.stats["monthly_stats"]:
            self.stats["monthly_stats"][current_month] = 0
        self.stats["monthly_stats"][current_month] += 1

        # 更新文件类型统计
        for file_type in file_types:
            if file_type in self.stats["file_types_stats"]:
                self.stats["file_types_stats"][file_type] += 1

        # 保存统计数据
        self.save_stats()

        # 记录日志
        self.logger.info(
            f"生成命令 - 文件数量: {file_count}, "
            f"文件类型: {', '.join(file_types)}, "
            f"命令类型: {command_type}"
        )

    def log_error(self, error_type: str, error_msg: str):
        """记录错误信息"""
        self.logger.error(f"{error_type}: {error_msg}")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats

    def get_monthly_stats(self) -> Dict[str, int]:
        """获取月度统计信息"""
        return self.stats["monthly_stats"]

    def get_file_type_stats(self) -> Dict[str, int]:
        """获取文件类型统计信息"""
        return self.stats["file_types_stats"] 