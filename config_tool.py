#!/usr/bin/env python3
"""
PPT-Study-Agent 配置管理工具
用于管理应用配置、验证设置和更新配置项
"""

import sys
import argparse
from config_manager import config

def show_config():
    """显示当前配置"""
    print("=== PPT-Study-Agent 当前配置 ===\n")
    
    print("[API 配置]")
    api_config = config.get_api_config()
    print(f"  API密钥: {'已设置' if api_config['api_key'] != 'your_api_key_here' else '未设置'}")
    print(f"  API地址: {api_config['base_url']}")
    print(f"  模型: {api_config['model']}")
    print(f"  温度: {api_config['temperature']}")
    print(f"  重试次数: {api_config['max_retries']}")
    print(f"  超时时间: {api_config['timeout']}秒")
    
    print("\n[服务器配置]")
    server_config = config.get_server_config()
    print(f"  地址: {server_config['host']}")
    print(f"  端口: {server_config['port']}")
    print(f"  调试模式: {server_config['debug']}")
    
    print("\n[应用配置]")
    app_config = config.get_app_config()
    print(f"  上传文件夹: {app_config['upload_folder']}")
    print(f"  结果文件夹: {app_config['results_folder']}")
    print(f"  允许的文件类型: {', '.join(app_config['allowed_extensions'])}")
    print(f"  最大文件大小: {app_config['max_file_size_bytes'] / (1024*1024):.0f}MB")
    
    print("\n[处理配置]")
    processing_config = config.get_processing_config()
    print(f"  上下文幻灯片数: {processing_config['max_context_slides']}")
    print(f"  图像详细度: {processing_config['image_detail']}")
    print(f"  并发处理: {processing_config['concurrent_processing']}")

def validate_config():
    """验证配置"""
    print("=== 配置验证 ===\n")
    
    if config.validate_config():
        print("✓ 配置验证成功！")
        return True
    else:
        print("❌ 配置验证失败！")
        return False

def set_config(section, key, value):
    """设置配置项"""
    try:
        if not config.config.has_section(section):
            config.config.add_section(section)
        
        config.config.set(section, key, value)
        
        # 保存到文件
        with open(config.config_file, 'w', encoding='utf-8') as f:
            config.config.write(f)
        
        print(f"✓ 设置成功: [{section}] {key} = {value}")
        
        # 重新加载配置
        config._load_config()
        
    except Exception as e:
        print(f"❌ 设置失败: {e}")

def setup_wizard():
    """配置向导"""
    print("=== PPT-Study-Agent 配置向导 ===\n")
    
    print("欢迎使用PPT-Study-Agent！")
    print("请按照提示配置必要的设置项。\n")
    
    # API密钥
    current_key = config.get('api', 'api_key', 'your_api_key_here')
    if current_key == 'your_api_key_here':
        print("1. 配置API密钥")
        print("   请输入您的OpenAI API密钥:")
        api_key = input("   API Key: ").strip()
        if api_key:
            set_config('api', 'api_key', api_key)
        else:
            print("   跳过API密钥配置")
    else:
        print("1. ✓ API密钥已配置")
    
    # API地址
    print("\n2. 配置API地址")
    current_url = config.get('api', 'base_url')
    print(f"   当前API地址: {current_url}")
    new_url = input("   新的API地址 (留空保持不变): ").strip()
    if new_url:
        set_config('api', 'base_url', new_url)
    
    # 模型
    print("\n3. 配置模型")
    current_model = config.get('api', 'model')
    print(f"   当前模型: {current_model}")
    print("   常用模型: gpt-4, gpt-3.5-turbo, gemini-2.0-flash, claude-3")
    new_model = input("   新的模型名称 (留空保持不变): ").strip()
    if new_model:
        set_config('api', 'model', new_model)
    
    # 服务器端口
    print("\n4. 配置服务器端口")
    current_port = config.get('server', 'port')
    print(f"   当前端口: {current_port}")
    new_port = input("   新的端口号 (留空保持不变): ").strip()
    if new_port:
        try:
            port_num = int(new_port)
            if 1 <= port_num <= 65535:
                set_config('server', 'port', new_port)
            else:
                print("   端口号必须在1-65535范围内")
        except ValueError:
            print("   请输入有效的端口号")
    
    print("\n✓ 配置向导完成！")
    print("运行 'python3 config_tool.py validate' 来验证配置。")

def main():
    parser = argparse.ArgumentParser(description='PPT-Study-Agent 配置管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # show 命令
    subparsers.add_parser('show', help='显示当前配置')
    
    # validate 命令
    subparsers.add_parser('validate', help='验证配置')
    
    # set 命令
    set_parser = subparsers.add_parser('set', help='设置配置项')
    set_parser.add_argument('section', help='配置节名称 (如: api, server, app)')
    set_parser.add_argument('key', help='配置键名称')
    set_parser.add_argument('value', help='配置值')
    
    # setup 命令
    subparsers.add_parser('setup', help='运行配置向导')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'show':
        show_config()
    elif args.command == 'validate':
        success = validate_config()
        sys.exit(0 if success else 1)
    elif args.command == 'set':
        set_config(args.section, args.key, args.value)
    elif args.command == 'setup':
        setup_wizard()

if __name__ == '__main__':
    main()
