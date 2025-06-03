#!/bin/bash

# PPT-Study-Agent 启动脚本（配置管理版本）
# 支持配置文件和环境变量管理

echo "=== PPT-Study-Agent 启动脚本 ==="
echo ""

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3"
    exit 1
fi
python3 --version

# 检查必要的包
echo ""
echo "检查必要的Python包..."
python3 -c "import flask; print(f'Flask: {flask.__version__}')" 2>/dev/null || echo "警告: Flask未安装"
python3 -c "import openai; print(f'OpenAI: {openai.__version__}')" 2>/dev/null || echo "警告: OpenAI未安装"

# 检查配置文件
echo ""
echo "检查配置文件..."
if [ -f "config.ini" ]; then
    echo "✓ config.ini 配置文件存在"
    
    # 检查API密钥是否已配置
    API_KEY=$(python3 -c "
import configparser
import os
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('api', 'api_key')
    # 检查环境变量覆盖
    env_key = os.getenv('OPENAI_API_KEY')
    if env_key:
        print(env_key[:8] + '...' if len(env_key) > 8 else env_key)
    elif api_key and api_key != 'your_api_key_here':
        print(api_key[:8] + '...' if len(api_key) > 8 else api_key)
    else:
        print('')
except:
    print('')
    ")
    
    if [ -z "$API_KEY" ]; then
        echo "⚠️  API密钥未配置"
        echo "请在 config.ini 中设置 [api] api_key 或设置环境变量 OPENAI_API_KEY"
        echo "示例: export OPENAI_API_KEY=your_api_key_here"
    else
        echo "✓ API密钥已配置: $API_KEY"
    fi
else
    echo "⚠️  config.ini 不存在，将创建默认配置文件"
fi

# 检查系统依赖
echo ""
echo "检查系统依赖..."
if command -v soffice &> /dev/null; then
    echo "✓ LibreOffice 已安装"
else
    echo "警告: LibreOffice 未安装，PPT转换功能可能无法正常工作"
fi

if command -v pdftoppm &> /dev/null; then
    echo "✓ poppler-utils 已安装"
else
    echo "警告: poppler-utils 未安装，PDF转图片功能可能无法正常工作"
fi

# 启动应用
echo ""
echo "正在验证配置..."
python3 -c "
from config_manager import config
if config.validate_config():
    print('✓ 配置验证成功')
    server_config = config.get_server_config()
    print(f'服务器配置: {server_config[\"host\"]}:{server_config[\"port\"]}')
    print(f'使用模型: {config.get(\"api\", \"model\")}')
else:
    print('❌ 配置验证失败')
    exit(1)
" || exit 1

echo ""
echo "启动PPT-Study-Agent应用..."
echo "主页面: http://localhost:2230"
echo "数学公式测试页面: http://localhost:2230/math-test"
echo "配置检查页面: http://localhost:2230/check-math-engine"
echo "数学公式测试页面: http://localhost:2230/math-test"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 切换到应用目录
cd "$(dirname "$0")"

# 启动Flask应用
python3 app.py
