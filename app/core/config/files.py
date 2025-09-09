from .base import BaseConfig


class FileConfig(BaseConfig):
    """文件上传配置"""

    # 最大文件大小（字节）
    max_file_size: int = 10485760  # 10MB

    # 上传目录
    upload_dir: str = "uploads"

    class Config:
        env_prefix = "FILE_"
