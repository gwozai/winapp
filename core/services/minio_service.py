from typing import List, Optional, Dict, Any
from datetime import timedelta
from minio import Minio
from minio.error import MinioException
from ..utils.config_manager import ConfigManager
from ..utils.logger import LogManager
import os
import io

class MinioService:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.client = None
        self.logger = LogManager()
        self.setup_client()

    def setup_client(self):
        """初始化MinIO客户端"""
        try:
            config = self.config_manager.get_minio_config()
            print(f"正在连接MinIO服务器: {config['endpoint']}")
            print(f"使用存储桶: {config['bucket']}")
            self.client = Minio(
                endpoint=config["endpoint"],
                access_key=config["access_key"],
                secret_key=config["secret_key"],
                secure=config["secure"]
            )
            # 测试连接
            self.client.list_buckets()
            print("MinIO服务器连接成功")
            self.logger.log_minio_connection(
                endpoint=config["endpoint"],
                bucket=config["bucket"],
                success=True
            )
        except Exception as e:
            error_msg = str(e)
            print(f"MinIO客户端初始化失败: {error_msg}")
            self.logger.log_minio_connection(
                endpoint=config["endpoint"],
                bucket=config["bucket"],
                success=False,
                error_msg=error_msg
            )
            raise

    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """列出指定前缀的所有文件"""
        try:
            objects = self.client.list_objects(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                prefix=prefix,
                recursive=True
            )
            
            files = []
            for obj in objects:
                # 获取文件的元数据
                stat = self.client.stat_object(
                    bucket_name=self.config_manager.get_minio_config()["bucket"],
                    object_name=obj.object_name
                )
                
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "content_type": stat.content_type,
                    "metadata": stat.metadata
                })
            
            return files
        except MinioException as e:
            print(f"列出文件失败: {e}")
            return []

    def upload_file(self, file_path: str, object_name: Optional[str] = None) -> bool:
        """上传文件到MinIO"""
        try:
            if object_name is None:
                object_name = os.path.basename(file_path)
                
            self.client.fput_object(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                object_name=object_name,
                file_path=file_path
            )
            return True
        except MinioException as e:
            print(f"上传文件失败: {e}")
            return False

    def download_file(self, object_name: str, file_path: str) -> bool:
        """从MinIO下载文件"""
        try:
            self.client.fget_object(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                object_name=object_name,
                file_path=file_path
            )
            return True
        except MinioException as e:
            print(f"下载文件失败: {e}")
            return False

    def delete_file(self, object_name: str) -> bool:
        """删除MinIO中的文件"""
        try:
            self.client.remove_object(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                object_name=object_name
            )
            return True
        except MinioException as e:
            print(f"删除文件失败: {e}")
            return False

    def get_presigned_url(self, object_name: str, expires: timedelta = timedelta(hours=1)) -> Optional[str]:
        """获取文件的预签名URL"""
        try:
            print(f"正在获取文件的预签名URL: {object_name}")
            url = self.client.presigned_get_object(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                object_name=object_name,
                expires=expires
            )
            print(f"成功获取预签名URL: {url}")
            return url
        except MinioException as e:
            error_msg = str(e)
            print(f"获取预签名URL失败: {error_msg}")
            self.logger.log_error("获取预签名URL失败", f"文件: {object_name}, 错误: {error_msg}")
            return None

    def get_bucket_size(self) -> int:
        """获取存储桶的总大小（字节）"""
        try:
            total_size = 0
            objects = self.client.list_objects(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                recursive=True
            )
            for obj in objects:
                total_size += obj.size
            return total_size
        except MinioException as e:
            print(f"获取存储桶大小失败: {e}")
            return 0

    def create_folder(self, folder_name: str) -> bool:
        """在MinIO中创建文件夹（实际上是创建一个空对象）"""
        try:
            # 确保文件夹名称以/结尾
            if not folder_name.endswith('/'):
                folder_name += '/'
                
            # 创建一个空对象来表示文件夹
            self.client.put_object(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                object_name=folder_name,
                data=io.BytesIO(b""),
                length=0
            )
            return True
        except MinioException as e:
            print(f"创建文件夹失败: {e}")
            return False

    def rename_file(self, old_name: str, new_name: str) -> bool:
        """重命名MinIO中的文件（通过复制和删除实现）"""
        try:
            # 获取源对象
            data = self.client.get_object(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                object_name=old_name
            )
            
            # 获取源对象的元数据
            stat = self.client.stat_object(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                object_name=old_name
            )
            
            # 复制对象到新名称
            self.client.put_object(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                object_name=new_name,
                data=data,
                length=stat.size,
                content_type=stat.content_type,
                metadata=stat.metadata
            )
            
            # 删除原对象
            self.client.remove_object(
                bucket_name=self.config_manager.get_minio_config()["bucket"],
                object_name=old_name
            )
            
            return True
        except MinioException as e:
            print(f"重命名文件失败: {e}")
            return False 