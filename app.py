import os
import uuid
import json
import threading
import datetime
import random
import string
import shutil
import glob
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename

from config_manager import config
from utils.converter import convert_to_images
from utils.analyzer import analyze_images_realtime

app = Flask(__name__)

# 获取配置
server_config = config.get_server_config()
app_config = config.get_app_config()
app_config['max_history_records'] = config.get_int('app', 'max_history_records', 30)

# 设置Flask配置
app.secret_key = server_config['secret_key']

# 配置文件夹
UPLOAD_FOLDER = app_config['upload_folder']
RESULTS_FOLDER = app_config['results_folder']
ALLOWED_EXTENSIONS = app_config['allowed_extensions']

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(RESULTS_FOLDER, 'images'), exist_ok=True)
os.makedirs(os.path.join(RESULTS_FOLDER, 'descriptions'), exist_ok=True)

app.config['UPLOAD_FOLDER'] = os.path.abspath(UPLOAD_FOLDER)
app.config['RESULTS_FOLDER'] = os.path.abspath(RESULTS_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = app_config['max_file_size_bytes']

# 存储处理任务状态
processing_tasks = {}

# 历史记录存储 - 存储格式：{session_id: record_info}
history_records = {}
HISTORY_FILE = 'history.json'

def load_history():
    """加载历史记录"""
    global history_records
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history_records = json.load(f)
        
        # 验证历史记录的完整性，清理无效记录
        valid_records = {}
        for session_id, record in history_records.items():
            if validate_record(session_id, record):
                valid_records[session_id] = record
            else:
                # 清理无效记录的文件
                cleanup_session_files(session_id)
        
        history_records = valid_records
        save_history()
    except Exception as e:
        print(f"加载历史记录失败: {e}")
        history_records = {}

def save_history():
    """保存历史记录"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_records, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存历史记录失败: {e}")

def validate_record(session_id, record):
    """验证记录的有效性"""
    try:
        # 检查必要字段
        required_fields = ['session_id', 'original_filename', 'created_at', 'status']
        for field in required_fields:
            if field not in record:
                return False
        
        # 检查文件是否存在
        session_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        session_results_dir = os.path.join(app.config['RESULTS_FOLDER'], session_id)
        
        if not os.path.exists(session_upload_dir) and not os.path.exists(session_results_dir):
            return False
            
        return True
    except:
        return False

def cleanup_session_files(session_id):
    """清理会话相关的所有文件"""
    try:
        # 清理上传文件
        session_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        if os.path.exists(session_upload_dir):
            shutil.rmtree(session_upload_dir)
        
        # 清理结果文件
        session_results_dir = os.path.join(app.config['RESULTS_FOLDER'], session_id)
        if os.path.exists(session_results_dir):
            shutil.rmtree(session_results_dir)
            
        print(f"已清理会话文件: {session_id}")
    except Exception as e:
        print(f"清理会话文件失败 {session_id}: {e}")

def manage_history_limit():
    """管理历史记录数量限制"""
    max_records = app_config.get('max_history_records', 30)
    
    if len(history_records) >= max_records:
        # 按创建时间排序，删除最早的记录
        sorted_records = sorted(history_records.items(), 
                              key=lambda x: x[1].get('created_at', ''))
        
        # 计算需要删除的记录数量
        to_delete = len(history_records) - max_records + 1
        
        for i in range(to_delete):
            session_id, record = sorted_records[i]
            cleanup_session_files(session_id)
            del history_records[session_id]
            print(f"由于达到历史记录上限，删除了记录: {record.get('original_filename', session_id)}")
        
        save_history()

def add_history_record(session_id, original_filename, new_filename):
    """添加历史记录"""
    manage_history_limit()
    
    record = {
        'session_id': session_id,
        'original_filename': original_filename,
        'new_filename': new_filename,
        'created_at': datetime.datetime.now().isoformat(),
        'status': 'converting',
        'total_images': 0,
        'processed_images': 0
    }
    
    history_records[session_id] = record
    save_history()

def update_history_record(session_id, **kwargs):
    """更新历史记录"""
    if session_id in history_records:
        history_records[session_id].update(kwargs)
        save_history()

# 启动时加载历史记录
load_history()

def allowed_file(filename):
    """检查文件类型是否允许"""
    if '.' not in filename:
        return False
    
    # 获取文件扩展名（确保转换为小写）
    ext = filename.rsplit('.', 1)[1].lower().strip()
    
    # 输出日志帮助调试
    print(f"检查文件: {filename}, 扩展名: {ext}, 允许: {ext in ALLOWED_EXTENSIONS}")
    
    return ext in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/math-test')
def math_test():
    """数学公式渲染测试页面"""
    return render_template('math_test.html')

@app.route('/static/results/<path:filename>')
def results_static(filename):
    return send_from_directory(os.path.abspath(RESULTS_FOLDER), filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    
    # 检查文件是否为空
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 获取原始文件名和扩展名
    original_filename = file.filename
    
    # 尝试获取文件扩展名
    try:
        # 确保正确处理带有多个点的文件名
        if '.' in original_filename:
            # 将扩展名转换为小写
            extension = original_filename.rsplit('.', 1)[1].lower()
        else:
            extension = ''
    except Exception as e:
        print(f"获取文件扩展名出错: {str(e)}")
        extension = ''
    
    # 检查文件类型是否在允许列表中
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({
            'error': f'不支持的文件类型: {extension if extension else "无扩展名"}',
            'allowed': list(ALLOWED_EXTENSIONS)
        }), 400
    
    # 生成唯一会话ID
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    
    # 创建会话文件夹
    session_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    session_results_dir = os.path.join(app.config['RESULTS_FOLDER'], session_id)
    session_images_dir = os.path.join(session_results_dir, 'images')
    session_desc_dir = os.path.join(session_results_dir, 'descriptions')
    
    os.makedirs(session_upload_dir, exist_ok=True)
    os.makedirs(session_images_dir, exist_ok=True)
    os.makedirs(session_desc_dir, exist_ok=True)
    
    # 生成新的安全文件名 (时间戳+随机数), 保留原始扩展名
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    new_filename = f"{timestamp}_{random_suffix}.{extension}"
    
    # 保存上传的文件
    filepath = os.path.join(session_upload_dir, new_filename)
    file.save(filepath)
    
    # 记录文件重命名信息
    print(f"文件重命名: {original_filename} -> {new_filename}")
    
    # 初始化任务状态
    processing_tasks[session_id] = {
        'status': 'converting',
        'total_images': 0,
        'processed_images': 0,
        'descriptions': [],
        'images': [],
        'original_filename': original_filename,  # 保存原始文件名以供参考
        'new_filename': new_filename,
        'completed': False
    }
    
    # 添加到历史记录
    add_history_record(session_id, original_filename, new_filename)
    
    # 启动后台处理线程
    thread = threading.Thread(target=process_file_background, args=(session_id, filepath, session_images_dir, session_desc_dir))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': '文件上传成功，正在处理...'
    })

def process_file_background(session_id, filepath, images_dir, desc_dir):
    """后台处理文件的函数"""
    try:
        # 转换文件为图片
        image_paths = convert_to_images(filepath, images_dir)
        
        # 更新任务状态
        processing_tasks[session_id]['status'] = 'analyzing'
        processing_tasks[session_id]['total_images'] = len(image_paths)
        processing_tasks[session_id]['images'] = [os.path.basename(img) for img in image_paths]
        
        # 更新历史记录
        update_history_record(session_id, 
                            status='analyzing', 
                            total_images=len(image_paths))
        
        # 分析图片并生成描述（实时处理）
        analyze_images_realtime(image_paths, desc_dir, callback=lambda idx, desc: update_analysis_status(session_id, idx, desc))
        
        # 处理完成
        processing_tasks[session_id]['completed'] = True
        
        # 更新历史记录状态为完成
        update_history_record(session_id, 
                            status='completed',
                            completed=True,
                            processed_images=len(image_paths))
        
        # 将最终结果保存到JSON文件
        result_data = {
            'images': processing_tasks[session_id]['images'],
            'descriptions': processing_tasks[session_id]['descriptions']
        }
        
        with open(os.path.join(os.path.dirname(desc_dir), 'result.json'), 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        processing_tasks[session_id]['error'] = str(e)
        # 更新历史记录状态为错误
        update_history_record(session_id, status='error', error=str(e))
        print(f"处理文件时出错: {str(e)}")

def update_analysis_status(session_id, index, description):
    """更新分析状态的回调函数"""
    if session_id in processing_tasks:
        # 确保descriptions列表长度足够
        while len(processing_tasks[session_id]['descriptions']) <= index:
            processing_tasks[session_id]['descriptions'].append(None)
        
        # 更新描述和进度
        processing_tasks[session_id]['descriptions'][index] = description
        processing_tasks[session_id]['processed_images'] = index + 1
        
        # 更新历史记录进度
        update_history_record(session_id, processed_images=index + 1)

@app.route('/status/<session_id>')
def get_status(session_id):
    """获取当前处理状态"""
    if session_id not in processing_tasks:
        return jsonify({'error': '会话不存在'}), 404
        
    task = processing_tasks[session_id]
    return jsonify({
        'status': task['status'],
        'total_images': task['total_images'],
        'processed_images': task['processed_images'],
        'completed': task['completed'],
        'error': task.get('error')
    })

@app.route('/partial-results/<session_id>')
def get_partial_results(session_id):
    """获取部分处理结果"""
    if session_id not in processing_tasks:
        return jsonify({'error': '会话不存在'}), 404
        
    task = processing_tasks[session_id]
    
    # 构建当前已处理的幻灯片数据
    slides = []
    for i, (image, description) in enumerate(zip(task['images'][:task['processed_images']], 
                                             task['descriptions'][:task['processed_images']])):
        if description:  # 只返回已完成分析的幻灯片
            slides.append({
                'number': i + 1,
                'image': f"/results/{session_id}/images/{image}",
                'description': description
            })
    
    return jsonify({
        'slides': slides,
        'total_processed': task['processed_images'],
        'total_images': task['total_images'],
        'completed': task['completed']
    })

@app.route('/view/<session_id>')
def view_results(session_id):
    """展示实时处理结果的页面"""
    if session_id not in processing_tasks:
        return "会话不存在或已过期", 404
        
    return render_template('realtime_view.html', session_id=session_id)

@app.route('/results/<session_id>/images/<filename>')
def get_image(session_id, filename):
    """获取图片文件"""
    # 使用send_from_directory直接提供文件，避免重定向循环
    images_dir = os.path.join(app.config['RESULTS_FOLDER'], session_id, 'images')
    return send_from_directory(images_dir, filename)

@app.route('/check-math-engine')
def check_math_engine():
    return render_template('check_math_engine.html')

@app.route('/api/history')
def get_history():
    """获取历史记录列表"""
    try:
        # 按创建时间倒序排列
        sorted_records = sorted(history_records.values(), 
                              key=lambda x: x.get('created_at', ''), 
                              reverse=True)
        
        # 更新正在处理中的记录状态
        for record in sorted_records:
            session_id = record['session_id']
            if session_id in processing_tasks:
                task = processing_tasks[session_id]
                record.update({
                    'status': task.get('status', record.get('status')),
                    'total_images': task.get('total_images', record.get('total_images', 0)),
                    'processed_images': task.get('processed_images', record.get('processed_images', 0)),
                    'completed': task.get('completed', False),
                    'error': task.get('error')
                })
        
        return jsonify({
            'success': True,
            'records': sorted_records,
            'max_records': app_config.get('max_history_records', 30)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history/<session_id>', methods=['DELETE'])
def delete_history_record(session_id):
    """删除历史记录"""
    try:
        if session_id not in history_records:
            return jsonify({'success': False, 'error': '记录不存在'}), 404
        
        # 清理相关文件
        cleanup_session_files(session_id)
        
        # 从历史记录中删除
        del history_records[session_id]
        
        # 从处理任务中删除（如果存在）
        if session_id in processing_tasks:
            del processing_tasks[session_id]
        
        # 保存历史记录
        save_history()
        
        return jsonify({'success': True, 'message': '记录删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # 验证配置
    if not config.validate_config():
        print("配置验证失败，请检查配置文件")
        exit(1)
    
    print("配置验证成功，启动服务器...")
    print(f"服务器将运行在: http://{server_config['host']}:{server_config['port']}")
    print(f"使用模型: {config.get('api', 'model')}")
    
    app.run(
        debug=server_config['debug'],
        host=server_config['host'],
        port=server_config['port']
    )
