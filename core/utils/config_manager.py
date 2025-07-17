import json
import os
from typing import Dict, Any

class ConfigManager:
    DEFAULT_CONFIG = {
        "minio": {
            "endpoint": "106.12.107.176:19000",
            "access_key": "minio",
            "secret_key": "ei2BEHZYLaR8eGtT",
            "bucket": "album",
            "secure": False
        },
        "ui": {
            "theme": "light",
            "language": "zh_CN",
            "window_size": {
                "width": 1200,
                "height": 800
            }
        },
        "commands": {
            "default_type": "download",
            "show_progress": True,
            "use_powershell": False,
            "auto_delete": False
        }
    }

    def __init__(self):
        self.config_file = "config/settings.json"
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件，如果不存在则创建默认配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 确保配置目录存在
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                # 保存默认配置
                self.save_config(self.DEFAULT_CONFIG)
                return self.DEFAULT_CONFIG
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.DEFAULT_CONFIG

    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get_minio_config(self) -> Dict[str, Any]:
        """获取MinIO配置"""
        return self.config.get("minio", self.DEFAULT_CONFIG["minio"])

    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return self.config.get("ui", self.DEFAULT_CONFIG["ui"])

    def get_commands_config(self) -> Dict[str, Any]:
        """获取命令生成配置"""
        return self.config.get("commands", self.DEFAULT_CONFIG["commands"])

    def update_minio_config(self, minio_config: Dict[str, Any]) -> bool:
        """更新MinIO配置"""
        self.config["minio"] = minio_config
        return self.save_config(self.config)

    def update_ui_config(self, ui_config: Dict[str, Any]) -> bool:
        """更新UI配置"""
        self.config["ui"] = ui_config
        return self.save_config(self.config)

    def update_commands_config(self, commands_config: Dict[str, Any]) -> bool:
        """更新命令生成配置"""
        self.config["commands"] = commands_config
        return self.save_config(self.config) 