#!/usr/bin/env python3
"""
导入现有会话到历史记录
"""

import os
import json
import datetime
from pathlib import Path

def import_existing_sessions():
    """导入现有的会话到历史记录"""
    results_dir = Path('results')
    uploads_dir = Path('uploads')
    history_file = 'history.json'
    
    # 加载现有历史记录
    try:
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history_records = json.load(f)
        else:
            history_records = {}
    except:
        history_records = {}
    
    # 遍历results目录中的会话
    for session_dir in results_dir.iterdir():
        if session_dir.is_dir() and session_dir.name not in ['images', 'descriptions']:
            session_id = session_dir.name
            
            # 如果已经在历史记录中，跳过
            if session_id in history_records:
                continue
            
            # 检查result.json是否存在
            result_file = session_dir / 'result.json'
            if not result_file.exists():
                continue
            
            try:
                # 读取result.json
                with open(result_file, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                
                # 查找对应的上传文件
                upload_dir = uploads_dir / session_id
                original_filename = "unknown_file"
                if upload_dir.exists():
                    files = list(upload_dir.glob('*'))
                    if files:
                        original_filename = files[0].name
                        # 提取原始文件名（去掉时间戳前缀）
                        parts = original_filename.split('_', 2)
                        if len(parts) >= 3:
                            # 尝试恢复原始文件名
                            ext = original_filename.split('.')[-1]
                            original_filename = f"imported_file.{ext}"
                
                # 获取文件修改时间作为创建时间
                created_at = datetime.datetime.fromtimestamp(
                    result_file.stat().st_mtime
                ).isoformat()
                
                # 创建历史记录
                record = {
                    'session_id': session_id,
                    'original_filename': original_filename,
                    'created_at': created_at,
                    'status': 'completed',
                    'total_images': len(result_data.get('images', [])),
                    'processed_images': len(result_data.get('descriptions', [])),
                }
                
                history_records[session_id] = record
                print(f"导入会话: {session_id} - {original_filename}")
                
            except Exception as e:
                print(f"导入会话 {session_id} 时出错: {e}")
    
    # 保存历史记录
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_records, f, ensure_ascii=False, indent=2)
        print(f"成功导入 {len(history_records)} 条历史记录")
    except Exception as e:
        print(f"保存历史记录失败: {e}")

if __name__ == '__main__':
    import_existing_sessions()
