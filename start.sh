#!/bin/bash

# PPT-Study-Agent 简易启动脚本

echo "启动 PPT-Study-Agent..."

# 切换到应用目录
cd "$(dirname "$0")"

# 检查配置文件是否存在
if [ ! -f "config.ini" ]; then
    echo "配置文件 config.ini 不存在，正在创建默认配置..."
    python3 -c "from config_manager import config; print('配置文件已创建')" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "错误: 无法创建配置文件，请检查依赖"
        exit 1
    fi
fi

# 设置API密钥（如果通过命令行参数提供）
if [ "$1" != "" ]; then
    export OPENAI_API_KEY="$1"
    echo "使用提供的API密钥: ${1:0:8}..."
fi

# 检查API密钥是否已配置
API_CONFIGURED=$(python3 -c "
try:
    from config_manager import config
    api_key = config.get('api', 'api_key')
    import os
    env_key = os.getenv('OPENAI_API_KEY')
    if env_key or (api_key and api_key != 'your_api_key_here'):
        print('yes')
    else:
        print('no')
except Exception as e:
    print('error')
")

if [ "$API_CONFIGURED" = "no" ]; then
    echo "⚠️  API密钥未配置！"
    echo "请使用以下方式之一配置API密钥："
    echo "1. 运行: ./start.sh your_api_key_here"
    echo "2. 设置环境变量: export OPENAI_API_KEY=your_api_key"
    echo "3. 编辑 config.ini 文件中的 [api] api_key"
    exit 1
elif [ "$API_CONFIGURED" = "error" ]; then
    echo "错误: 配置系统有问题，请检查依赖"
    exit 1
fi

echo "✓ 配置检查通过"
echo "启动服务器..."
echo "访问地址: http://localhost:2230"
echo ""

# 启动应用
python3 app.py
