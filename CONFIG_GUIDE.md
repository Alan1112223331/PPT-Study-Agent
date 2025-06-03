# PPT-Study-Agent 配置管理说明

## 概述

PPT-Study-Agent 现在支持通过配置文件管理所有设置项，包括 API 密钥、模型配置、服务器设置等。

## 配置文件

主配置文件是 `config.ini`，采用 INI 格式。配置文件包含以下几个部分：

### [api] - API 配置
- `api_key`: OpenAI API 密钥
- `base_url`: API 基础 URL
- `model`: 使用的模型名称
- `temperature`: 模型温度参数
- `max_retries`: 最大重试次数
- `timeout`: 超时时间（秒）

### [server] - 服务器配置
- `host`: 服务器绑定地址
- `port`: 服务器端口
- `debug`: 是否开启调试模式
- `secret_key`: Flask 密钥（可设为 auto_generate 自动生成）

### [app] - 应用配置
- `upload_folder`: 上传文件存储目录
- `results_folder`: 结果文件存储目录
- `allowed_extensions`: 允许的文件扩展名（逗号分隔）
- `max_file_size`: 最大文件大小

### [processing] - 处理配置
- `max_context_slides`: 上下文幻灯片数量
- `image_detail`: 图像分析详细度
- `concurrent_processing`: 是否启用并发处理

### [ui] - 用户界面配置
- `default_math_engine`: 默认数学渲染引擎
- `enable_realtime_view`: 是否启用实时视图
- `progress_update_interval`: 进度更新间隔（毫秒）

### [logging] - 日志配置
- `log_level`: 日志级别
- `log_file`: 日志文件路径
- `enable_console_log`: 是否启用控制台日志

## 环境变量覆盖

以下环境变量可以覆盖配置文件中的设置：

- `OPENAI_API_KEY` → `[api] api_key`
- `API_BASE_URL` → `[api] base_url`
- `MODEL_NAME` → `[api] model`
- `SERVER_HOST` → `[server] host`
- `SERVER_PORT` → `[server] port`
- `DEBUG` → `[server] debug`
- `SECRET_KEY` → `[server] secret_key`
- `UPLOAD_FOLDER` → `[app] upload_folder`
- `RESULTS_FOLDER` → `[app] results_folder`
- `LOG_LEVEL` → `[logging] log_level`

## 配置工具

### 查看当前配置
```bash
python3 config_tool.py show
```

### 验证配置
```bash
python3 config_tool.py validate
```

### 设置配置项
```bash
python3 config_tool.py set api api_key your_api_key_here
python3 config_tool.py set server port 3000
python3 config_tool.py set api model gpt-4
```

### 运行配置向导
```bash
python3 config_tool.py setup
```

## 启动方式

### 方式1：使用配置文件启动
```bash
python3 app.py
```

### 方式2：使用启动脚本
```bash
./start.sh
```

### 方式3：使用环境变量
```bash
export OPENAI_API_KEY=your_api_key_here
python3 app.py
```

### 方式4：临时指定API密钥
```bash
./start.sh your_api_key_here
```

## 配置优先级

1. 环境变量（最高优先级）
2. 配置文件
3. 默认值（最低优先级）

## 示例配置

### 开发环境配置
```ini
[api]
api_key = your_dev_api_key
base_url = https://api.openai.com/v1
model = gpt-3.5-turbo
temperature = 0.3

[server]
host = 127.0.0.1
port = 5000
debug = true

[logging]
log_level = DEBUG
enable_console_log = true
```

### 生产环境配置
```ini
[api]
api_key = your_prod_api_key
base_url = https://api.openai.com/v1
model = gpt-4
temperature = 0.2

[server]
host = 0.0.0.0
port = 2230
debug = false

[logging]
log_level = INFO
log_file = app.log
enable_console_log = false
```

## 故障排除

### 配置文件不存在
应用启动时会自动创建默认配置文件 `config.ini`。

### API 密钥未配置
运行 `python3 config_tool.py setup` 进行配置。

### 配置验证失败
运行 `python3 config_tool.py validate` 查看具体错误信息。

### 端口冲突
修改 `[server] port` 或设置环境变量 `SERVER_PORT`。

## 安全建议

1. 不要将包含真实 API 密钥的配置文件提交到版本控制系统
2. 生产环境建议使用环境变量而不是配置文件存储敏感信息
3. 定期轮换 API 密钥
4. 生产环境关闭调试模式
