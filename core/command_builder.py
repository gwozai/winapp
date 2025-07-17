# -*- coding: utf-8 -*-
import platform
import os
from typing import Dict, Any

class CommandBuilder:
    """命令生成器类"""
    
    def __init__(self):
        self.is_windows = platform.system().lower() == "windows"
        self.command_styles = {
            "MinIO CLI": self._build_minio_cli_command,
            "AWS CLI": self._build_aws_cli_command,
            "通用命令": self._build_generic_command
        }

    def _build_minio_cli_command(self, command_type: str, options: Dict[str, Any]) -> str:
        """构建MinIO CLI命令"""
        base_cmd = "mc"
        
        if command_type == "download":
            cmd = f"{base_cmd} cp"
            if options.get("recursive"):
                cmd += " --recursive"
            if options.get("concurrent"):
                cmd += f" --concurrent {options['concurrent']}"
            cmd += f" {options['path']} ."
            
        elif command_type == "upload":
            cmd = f"{base_cmd} cp"
            if options.get("recursive"):
                cmd += " --recursive"
            cmd += f" {options['source']} {options['dest']}"
            
        elif command_type == "copy":
            cmd = f"{base_cmd} cp"
            if options.get("recursive"):
                cmd += " --recursive"
            if options.get("preserve"):
                cmd += " --preserve"
            cmd += f" {options['source']} {options['dest']}"
            
        elif command_type == "move":
            cmd = f"{base_cmd} mv"
            if options.get("recursive"):
                cmd += " --recursive"
            cmd += f" {options['source']} {options['dest']}"
            
        elif command_type == "delete":
            cmd = f"{base_cmd} rm"
            if options.get("recursive"):
                cmd += " --recursive"
            if options.get("force"):
                cmd += " --force"
            cmd += f" {options['path']}"
            
        elif command_type == "mkdir":
            cmd = f"{base_cmd} mb"
            cmd += f" {options['path']}"
            
        elif command_type == "list":
            cmd = f"{base_cmd} ls"
            if options.get("recursive"):
                cmd += " --recursive"
            if options.get("human_readable"):
                cmd += " --human"
            cmd += f" {options['path']}"
            
        elif command_type == "sync":
            cmd = f"{base_cmd} mirror"
            if options.get("delete_extra"):
                cmd += " --remove"
            if options.get("dry_run"):
                cmd += " --dry-run"
            cmd += f" {options['source']} {options['dest']}"
            
        else:
            raise ValueError(f"不支持的命令类型: {command_type}")
            
        return cmd

    def _build_aws_cli_command(self, command_type: str, options: Dict[str, Any]) -> str:
        """构建AWS CLI命令"""
        base_cmd = "aws s3"
        
        if command_type == "download":
            cmd = f"{base_cmd} cp"
            if options.get("recursive"):
                cmd = f"{base_cmd} sync"
            cmd += f" s3://{options['path']} ."
            
        elif command_type == "upload":
            cmd = f"{base_cmd} cp"
            if options.get("recursive"):
                cmd = f"{base_cmd} sync"
            cmd += f" {options['source']} s3://{options['dest']}"
            
        elif command_type == "copy":
            cmd = f"{base_cmd} cp"
            if options.get("recursive"):
                cmd = f"{base_cmd} sync"
            cmd += f" s3://{options['source']} s3://{options['dest']}"
            
        elif command_type == "move":
            # AWS CLI没有直接的move命令，使用cp后rm
            cmd = f"{base_cmd} cp"
            if options.get("recursive"):
                cmd = f"{base_cmd} sync"
            cmd += f" s3://{options['source']} s3://{options['dest']} && "
            cmd += f"{base_cmd} rm s3://{options['source']}"
            if options.get("recursive"):
                cmd += " --recursive"
            
        elif command_type == "delete":
            cmd = f"{base_cmd} rm"
            if options.get("recursive"):
                cmd += " --recursive"
            cmd += f" s3://{options['path']}"
            
        elif command_type == "mkdir":
            # S3没有真正的目录，创建一个空对象
            cmd = f"touch empty && {base_cmd} cp empty s3://{options['path']}/ && rm empty"
            
        elif command_type == "list":
            cmd = f"{base_cmd} ls"
            if options.get("recursive"):
                cmd += " --recursive"
            cmd += f" s3://{options['path']}"
            
        elif command_type == "sync":
            cmd = f"{base_cmd} sync"
            if options.get("delete_extra"):
                cmd += " --delete"
            cmd += f" {options['source']} s3://{options['dest']}"
            
        else:
            raise ValueError(f"不支持的命令类型: {command_type}")
            
        return cmd

    def _build_generic_command(self, command_type: str, options: Dict[str, Any]) -> str:
        """构建通用命令（使用curl、wget等）"""
        if self.is_windows:
            return self._build_windows_command(command_type, options)
        else:
            return self._build_unix_command(command_type, options)

    def _build_windows_command(self, command_type: str, options: Dict[str, Any]) -> str:
        """构建Windows命令"""
        if command_type == "download":
            cmd = "curl -O"
            if options.get("concurrent"):
                cmd = "aria2c -x"
                cmd += f" {options['concurrent']}"
            cmd += f" {options['path']}"
            
        elif command_type == "upload":
            cmd = f"curl -T {options['source']} {options['dest']}"
            
        elif command_type == "copy":
            cmd = f"xcopy /Y"
            if options.get("recursive"):
                cmd += " /E"
            cmd += f" {options['source']} {options['dest']}\\"
            
        elif command_type == "move":
            cmd = f"move /Y {options['source']} {options['dest']}"
            
        elif command_type == "delete":
            if options.get("recursive"):
                cmd = f"rmdir /S /Q {options['path']}"
            else:
                cmd = f"del /F /Q {options['path']}"
            
        elif command_type == "mkdir":
            cmd = f"mkdir"
            if options.get("create_parents"):
                cmd += " /p"
            cmd += f" {options['path']}"
            
        elif command_type == "list":
            cmd = "dir"
            if options.get("recursive"):
                cmd += " /S"
            cmd += f" {options['path']}"
            
        elif command_type == "sync":
            cmd = f"robocopy {options['source']} {options['dest']} /MIR"
            if options.get("dry_run"):
                cmd += " /L"
            
        else:
            raise ValueError(f"不支持的命令类型: {command_type}")
            
        return cmd

    def _build_unix_command(self, command_type: str, options: Dict[str, Any]) -> str:
        """构建Unix命令"""
        if command_type == "download":
            cmd = "curl -O"
            if options.get("concurrent"):
                cmd = "aria2c -x"
                cmd += f" {options['concurrent']}"
            cmd += f" {options['path']}"
            
        elif command_type == "upload":
            cmd = f"curl -T {options['source']} {options['dest']}"
            
        elif command_type == "copy":
            cmd = "cp"
            if options.get("recursive"):
                cmd += " -r"
            if options.get("preserve"):
                cmd += " -p"
            cmd += f" {options['source']} {options['dest']}"
            
        elif command_type == "move":
            cmd = f"mv {options['source']} {options['dest']}"
            
        elif command_type == "delete":
            cmd = "rm"
            if options.get("recursive"):
                cmd += " -r"
            if options.get("force"):
                cmd += " -f"
            cmd += f" {options['path']}"
            
        elif command_type == "mkdir":
            cmd = "mkdir"
            if options.get("create_parents"):
                cmd += " -p"
            cmd += f" {options['path']}"
            
        elif command_type == "list":
            cmd = "ls"
            if options.get("recursive"):
                cmd += " -R"
            if options.get("human_readable"):
                cmd += " -h"
            cmd += f" {options['path']}"
            
        elif command_type == "sync":
            cmd = "rsync"
            if options.get("delete_extra"):
                cmd += " --delete"
            if options.get("dry_run"):
                cmd += " --dry-run"
            cmd += f" -av {options['source']}/ {options['dest']}/"
            
        else:
            raise ValueError(f"不支持的命令类型: {command_type}")
            
        return cmd

    def add_progress_option(self, command: str, cmd_style: str) -> str:
        """添加进度显示选项"""
        if cmd_style == "MinIO CLI":
            return command + " --progress"
        elif cmd_style == "AWS CLI":
            return command + " --progress"
        else:
            if "curl" in command:
                return command.replace("curl", "curl -#")
            elif "wget" in command:
                return command + " --progress=bar"
            elif "rsync" in command:
                return command + " --progress"
        return command

    def add_verbose_option(self, command: str, cmd_style: str) -> str:
        """添加详细输出选项"""
        if cmd_style == "MinIO CLI":
            return command + " -v"
        elif cmd_style == "AWS CLI":
            return command + " --debug"
        else:
            if "curl" in command:
                return command + " -v"
            elif "wget" in command:
                return command + " -v"
            elif "rsync" in command:
                return command + " -v"
        return command

    def build_download_command(self, **options) -> str:
        """构建下载命令"""
        return self.command_styles[options["cmd_style"]]("download", options)

    def build_upload_command(self, **options) -> str:
        """构建上传命令"""
        return self.command_styles[options["cmd_style"]]("upload", options)

    def build_copy_move_command(self, **options) -> str:
        """构建复制/移动命令"""
        command_type = "move" if options.get("is_move") else "copy"
        return self.command_styles[options["cmd_style"]](command_type, options)

    def build_delete_command(self, **options) -> str:
        """构建删除命令"""
        return self.command_styles[options["cmd_style"]]("delete", options)

    def build_mkdir_command(self, **options) -> str:
        """构建创建文件夹命令"""
        return self.command_styles[options["cmd_style"]]("mkdir", options)

    def build_list_command(self, **options) -> str:
        """构建列出文件命令"""
        return self.command_styles[options["cmd_style"]]("list", options)

    def build_sync_command(self, **options) -> str:
        """构建同步命令"""
        return self.command_styles[options["cmd_style"]]("sync", options)

    def build_archive_command(self, **options) -> str:
        """构建压缩/解压命令"""
        if options["operation"] == "压缩":
            if options["format"] == "zip":
                cmd = "zip -r"
                if options.get("exclude_hidden"):
                    cmd += " -x '.*'"
                cmd += f" {options['source']}.zip {options['source']}"
            else:
                tar_options = {
                    "tar": "",
                    "tar.gz": "z",
                    "tar.bz2": "j"
                }
                cmd = f"tar -c{tar_options[options['format']]}f"
                if options.get("exclude_hidden"):
                    cmd += " --exclude='.*'"
                cmd += f" {options['source']}.{options['format']} {options['source']}"
        else:
            if options["format"] == "zip":
                cmd = f"unzip {options['source']}"
            else:
                cmd = f"tar -xf {options['source']}"
                
        return cmd

    def build_command(self, files):
        """生成下载命令"""
        if not files:
            return None
            
        # 生成PowerShell命令
        commands = []
        
        # 如果有多个文件，创建临时目录
        if len(files) > 1:
            commands.append("# 创建临时目录")
            commands.append("$tempDir = New-Item -ItemType Directory -Path $env:TEMP -Name ('minio_files_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))")
            commands.append("Set-Location $tempDir")
            commands.append("")
            
        # 为每个文件生成下载命令
        for file_path in files:
            file_name = os.path.basename(file_path)
            commands.append(f"# 下载文件: {file_name}")
            commands.append(f"Invoke-WebRequest -Uri '{file_path}' -OutFile '{file_name}'")
            
            # 根据文件类型添加处理命令
            ext = os.path.splitext(file_name)[1].lower()
            if ext == '.zip':
                commands.append(f"Expand-Archive -Path '{file_name}' -DestinationPath (Join-Path (Get-Location) ([System.IO.Path]::GetFileNameWithoutExtension('{file_name}')))")
                commands.append(f"Remove-Item '{file_name}'  # 解压后删除ZIP文件")
            elif ext in ['.txt', '.log', '.md', '.json', '.xml', '.csv']:
                commands.append(f"Get-Content '{file_name}' | Set-Clipboard")
                commands.append("Write-Host '文件内容已复制到剪贴板'")
                
            commands.append("")
            
        # 如果创建了临时目录，添加打开目录的命令
        if len(files) > 1:
            commands.append("# 打开下载目录")
            commands.append("Invoke-Item $tempDir")
            
        return "\n".join(commands) 