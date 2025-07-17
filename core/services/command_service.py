from typing import Dict, Any, Optional
import os
from datetime import timedelta
from ..utils.config_manager import ConfigManager
from .minio_service import MinioService

class CommandService:
    def __init__(self, config_manager: ConfigManager, minio_service: MinioService):
        self.config_manager = config_manager
        self.minio_service = minio_service

    def generate_command(self, file_info: Dict[str, Any], command_type: str, options: Dict[str, bool]) -> str:
        """根据文件信息和选项生成命令"""
        if command_type == "download":
            return self.generate_download_command(file_info, options)
        elif command_type == "extract":
            return self.generate_extract_command(file_info, options)
        elif command_type == "clipboard":
            return self.generate_clipboard_command(file_info, options)
        elif command_type == "batch":
            return self.generate_batch_command(file_info, options)
        else:
            raise ValueError(f"不支持的命令类型: {command_type}")

    def generate_download_command(self, file_info: Dict[str, Any], options: Dict[str, bool]) -> str:
        """生成下载命令"""
        url = self.minio_service.get_presigned_url(
            file_info["name"],
            expires=timedelta(hours=1)
        )
        
        if not url:
            return "# 获取下载链接失败"

        filename = os.path.basename(file_info["name"])
        
        # 基础命令
        if options.get("use_powershell", False):
            cmd = f'Invoke-WebRequest -Uri "{url}" -OutFile "{filename}"'
        else:
            cmd = f'curl -o "{filename}" "{url}"'

        # 添加进度显示
        if options.get("show_progress", False) and not options.get("use_powershell", False):
            cmd = cmd.replace("curl", "curl -#")

        # 添加自动删除
        if options.get("auto_delete", False):
            cmd += f' && del "{filename}"'

        return cmd

    def generate_extract_command(self, file_info: Dict[str, Any], options: Dict[str, bool]) -> str:
        """生成解压命令"""
        url = self.minio_service.get_presigned_url(
            file_info["name"],
            expires=timedelta(hours=1)
        )
        
        if not url:
            return "# 获取下载链接失败"

        filename = os.path.basename(file_info["name"])
        foldername = os.path.splitext(filename)[0]
        
        # PowerShell命令
        if options.get("use_powershell", False):
            cmd = (
                f'New-Item -ItemType Directory -Force -Path "{foldername}"; '
                f'Invoke-WebRequest -Uri "{url}" -OutFile "{filename}"; '
                f'Expand-Archive -Path "{filename}" -DestinationPath "{foldername}" -Force; '
            )
            if options.get("auto_delete", False):
                cmd += f'Remove-Item "{filename}"'
        # CMD命令
        else:
            cmd = (
                f'mkdir "{foldername}" 2>nul && '
                f'curl -o "{filename}" "{url}" && '
                f'powershell -command "Expand-Archive -Path \'{filename}\' -DestinationPath \'{foldername}\' -Force"'
            )
            if options.get("auto_delete", False):
                cmd += f' && del "{filename}"'

        return cmd

    def generate_clipboard_command(self, file_info: Dict[str, Any], options: Dict[str, bool]) -> str:
        """生成复制到剪贴板的命令"""
        url = self.minio_service.get_presigned_url(
            file_info["name"],
            expires=timedelta(hours=1)
        )
        
        if not url:
            return "# 获取下载链接失败"

        if options.get("use_powershell", False):
            return f'(Invoke-WebRequest -Uri "{url}").Content | Set-Clipboard'
        else:
            return f'curl "{url}" | clip'

    def generate_batch_command(self, files_info: Dict[str, Any], options: Dict[str, bool]) -> str:
        """生成批量处理命令"""
        commands = []
        
        for file_info in files_info.get("files", []):
            if file_info.get("type") == "archive":
                commands.append(self.generate_extract_command(file_info, options))
            elif file_info.get("type") == "text":
                commands.append(self.generate_clipboard_command(file_info, options))
            else:
                commands.append(self.generate_download_command(file_info, options))

        return " && \\\n".join(commands) 