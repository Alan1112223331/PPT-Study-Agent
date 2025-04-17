import os
import uuid
import json
import threading
import datetime
import random
import string
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename

from utils.converter import convert_to_images
from utils.analyzer import analyze_images_realtime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 配置上传文件夹和结果文件夹
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'ppt', 'pptx', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(RESULTS_FOLDER, 'images'), exist_ok=True)
os.makedirs(os.path.join(RESULTS_FOLDER, 'descriptions'), exist_ok=True)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

app.config['UPLOAD_FOLDER'] = os.path.abspath(UPLOAD_FOLDER)
app.config['RESULTS_FOLDER'] = os.path.abspath(RESULTS_FOLDER)

# 存储处理任务状态
processing_tasks = {}

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
        
        # 分析图片并生成描述（实时处理）
        analyze_images_realtime(image_paths, desc_dir, callback=lambda idx, desc: update_analysis_status(session_id, idx, desc))
        
        # 处理完成
        processing_tasks[session_id]['completed'] = True
        
        # 将最终结果保存到JSON文件
        result_data = {
            'images': processing_tasks[session_id]['images'],
            'descriptions': processing_tasks[session_id]['descriptions']
        }
        
        with open(os.path.join(os.path.dirname(desc_dir), 'result.json'), 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        processing_tasks[session_id]['error'] = str(e)
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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
