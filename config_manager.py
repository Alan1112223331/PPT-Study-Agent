#!/usr/bin/env python3
"""
配置管理模块
负责加载和管理应用配置
"""

import os
import configparser
import secrets

class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = 'config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            self._create_default_config()
        
        self.config.read(self.config_file, encoding='utf-8')
        
        # 环境变量覆盖配置文件
        self._load_env_overrides()
        
        # 处理特殊配置项
        self._process_special_configs()
    
    def _create_default_config(self):
        """创建默认配置文件"""
        print(f"配置文件 {self.config_file} 不存在，正在创建默认配置...")
        
        default_config = """# PPT-Study-Agent 配置文件
# 请根据您的实际环境修改以下配置项

[api]
# OpenAI API 配置
api_key = your_api_key_here
base_url = https://api.alan-m-12.top/v1
model = gemini-2.0-flash
temperature = 0.2
max_retries = 3
timeout = 30

[server]
# Flask 服务器配置
host = 0.0.0.0
port = 2230
debug = false
secret_key = auto_generate

[app]
# 应用配置
upload_folder = uploads
results_folder = results
allowed_extensions = ppt,pptx,pdf
max_file_size = 100MB

[processing]
# 处理配置
max_context_slides = 5
image_detail = high
concurrent_processing = false

[ui]
# 用户界面配置
default_math_engine = KaTeX
enable_realtime_view = true
progress_update_interval = 2000

[logging]
# 日志配置
log_level = INFO
log_file = app.log
enable_console_log = true
"""
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(default_config)
    
    def _load_env_overrides(self):
        """从环境变量加载配置覆盖"""
        env_mappings = {
            'OPENAI_API_KEY': ('api', 'api_key'),
            'API_BASE_URL': ('api', 'base_url'),
            'MODEL_NAME': ('api', 'model'),
            'SERVER_HOST': ('server', 'host'),
            'SERVER_PORT': ('server', 'port'),
            'DEBUG': ('server', 'debug'),
            'SECRET_KEY': ('server', 'secret_key'),
            'UPLOAD_FOLDER': ('app', 'upload_folder'),
            'RESULTS_FOLDER': ('app', 'results_folder'),
            'LOG_LEVEL': ('logging', 'log_level'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            if os.getenv(env_var):
                if not self.config.has_section(section):
                    self.config.add_section(section)
                self.config.set(section, key, os.getenv(env_var))
    
    def _process_special_configs(self):
        """处理特殊配置项"""
        # 自动生成secret_key
        if self.get('server', 'secret_key', 'auto_generate') == 'auto_generate':
            secret_key = secrets.token_hex(16)
            self.config.set('server', 'secret_key', secret_key)
        
        # 转换文件大小
        max_size = self.get('app', 'max_file_size', '100MB')
        if max_size.endswith('MB'):
            size_mb = int(max_size[:-2])
            if not self.config.has_section('app'):
                self.config.add_section('app')
            self.config.set('app', 'max_file_size_bytes', str(size_mb * 1024 * 1024))
    
    def get(self, section: str, key: str, fallback: str = None) -> str:
        """获取配置值"""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if fallback is not None:
                return fallback
            raise
    
    def get_int(self, section: str, key: str, fallback: int = None) -> int:
        """获取整数配置值"""
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            if fallback is not None:
                return fallback
            raise
    
    def get_float(self, section: str, key: str, fallback: float = None) -> float:
        """获取浮点数配置值"""
        try:
            return self.config.getfloat(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            if fallback is not None:
                return fallback
            raise
    
    def get_bool(self, section: str, key: str, fallback: bool = None) -> bool:
        """获取布尔配置值"""
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            if fallback is not None:
                return fallback
            raise
    
    def get_list(self, section: str, key: str, separator: str = ',', fallback: list = None) -> list:
        """获取列表配置值"""
        try:
            value = self.config.get(section, key)
            return [item.strip() for item in value.split(separator) if item.strip()]
        except (configparser.NoSectionError, configparser.NoOptionError):
            if fallback is not None:
                return fallback
            raise
    
    def validate_config(self) -> bool:
        """验证配置"""
        errors = []
        
        # 检查必需的配置项
        api_key = self.get('api', 'api_key', 'your_api_key_here')
        if not api_key or api_key == 'your_api_key_here':
            errors.append("API密钥未配置，请设置 [api] api_key 或环境变量 OPENAI_API_KEY")
        
        base_url = self.get('api', 'base_url', '')
        if not base_url:
            errors.append("API基础URL未配置")
        
        model = self.get('api', 'model', '')
        if not model:
            errors.append("模型名称未配置")
        
        # 检查端口号范围
        try:
            port = self.get_int('server', 'port', 2230)
            if not (1 <= port <= 65535):
                errors.append(f"端口号 {port} 超出有效范围 (1-65535)")
        except ValueError:
            errors.append("端口号配置无效")
        
        # 检查文件夹权限
        upload_folder = self.get('app', 'upload_folder', 'uploads')
        results_folder = self.get('app', 'results_folder', 'results')
        
        for folder in [upload_folder, results_folder]:
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder, exist_ok=True)
                except PermissionError:
                    errors.append(f"无法创建文件夹: {folder}")
        
        if errors:
            print("配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def get_api_config(self) -> dict:
        """获取API配置"""
        return {
            'api_key': self.get('api', 'api_key', 'your_api_key_here'),
            'base_url': self.get('api', 'base_url', 'https://api.openai.com/v1'),
            'model': self.get('api', 'model', 'gpt-3.5-turbo'),
            'temperature': self.get_float('api', 'temperature', 0.2),
            'max_retries': self.get_int('api', 'max_retries', 3),
            'timeout': self.get_int('api', 'timeout', 30),
        }
    
    def get_server_config(self) -> dict:
        """获取服务器配置"""
        return {
            'host': self.get('server', 'host', '0.0.0.0'),
            'port': self.get_int('server', 'port', 2230),
            'debug': self.get_bool('server', 'debug', False),
            'secret_key': self.get('server', 'secret_key', secrets.token_hex(16)),
        }
    
    def get_app_config(self) -> dict:
        """获取应用配置"""
        return {
            'upload_folder': self.get('app', 'upload_folder', 'uploads'),
            'results_folder': self.get('app', 'results_folder', 'results'),
            'allowed_extensions': set(self.get_list('app', 'allowed_extensions', fallback=['ppt', 'pptx', 'pdf'])),
            'max_file_size_bytes': self.get_int('app', 'max_file_size_bytes', 100 * 1024 * 1024),
        }
    
    def get_processing_config(self) -> dict:
        """获取处理配置"""
        return {
            'max_context_slides': self.get_int('processing', 'max_context_slides', 5),
            'image_detail': self.get('processing', 'image_detail', 'high'),
            'concurrent_processing': self.get_bool('processing', 'concurrent_processing', False),
        }

# 全局配置实例
config = Config()
