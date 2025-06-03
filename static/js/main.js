// 全局变量
let uploadingSessions = new Set();

document.addEventListener('DOMContentLoaded', function() {
    // 获取元素
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const successMessage = document.getElementById('success-message');
    const errorMessage = document.getElementById('error-message');
    
    // 加载历史记录
    loadHistory();
    
    // 每5秒刷新一次历史记录以更新进度
    setInterval(loadHistory, 5000);
    
    // 显示选择的文件名
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            fileName.textContent = this.files[0].name;
        } else {
            fileName.textContent = '未选择文件';
        }
    });
    
    // 处理表单提交
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 检查是否选择了文件
        if (fileInput.files.length === 0) {
            showError('请选择文件');
            return;
        }
        
        // 准备表单数据
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        hideMessages();
        
        // 临时禁用上传按钮，防止重复点击
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = '上传中...';
        
        // 发送上传请求
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                uploadingSessions.add(data.session_id);
                
                // 重新加载历史记录
                loadHistory();
                
                // 重置表单
                form.reset();
                fileName.textContent = '未选择文件';
                
                showSuccess('文件上传成功，正在后台处理...');
            } else {
                throw new Error(data.error || '上传失败');
            }
        })
        .catch(error => {
            showError(error.message);
        })
        .finally(() => {
            // 恢复上传按钮
            submitBtn.disabled = false;
            submitBtn.textContent = '上传并分析';
        });
    });
});

// 加载历史记录
function loadHistory() {
    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            displayHistory(data.records);
            updateHistoryCount(data.records.length, data.max_records);
        })
        .catch(error => {
            console.error('加载历史记录失败:', error);
        });
}

// 显示历史记录
function displayHistory(records) {
    const historyList = document.getElementById('history-list');
    
    if (records.length === 0) {
        historyList.innerHTML = '<div class="no-history">暂无分析记录</div>';
        return;
    }
    
    const html = records.map(record => {
        // 修复状态判断逻辑
        const isCompleted = record.status === 'completed' || record.completed === true;
        const isError = record.status === 'error';
        const isProcessing = !isCompleted && !isError;
        
        const statusClass = isCompleted ? 'completed' : 
                           isError ? 'error' : 'processing';
        
        const statusText = isCompleted ? '已完成' :
                          isError ? '处理失败' : '处理中';
        
        const statusBadgeClass = isCompleted ? 'status-completed' :
                                isError ? 'status-error' : 'status-processing';
        
        return `
            <div class="history-item ${statusClass}" data-session-id="${record.session_id}">
                <div class="history-filename">${record.original_filename}</div>
                <div class="history-time">${formatTime(record.created_at)}</div>
                <div class="history-status ${statusBadgeClass}">${statusText}</div>
                ${isProcessing ? `
                    <div class="progress-info">进度: ${record.processed_images || 0}/${record.total_images || 0}</div>
                ` : ''}
                <div class="history-actions">
                    <button class="btn-view" onclick="viewResults('${record.session_id}')">查看结果</button>
                    <button class="btn-delete" onclick="deleteRecord('${record.session_id}')">删除</button>
                </div>
            </div>
        `;
    }).join('');
    
    historyList.innerHTML = html;
}

// 更新历史记录计数
function updateHistoryCount(current, max) {
    document.getElementById('history-count').textContent = `(${current}/${max})`;
}

// 格式化时间
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffMinutes < 1) {
        return '刚刚';
    } else if (diffMinutes < 60) {
        return `${diffMinutes}分钟前`;
    } else if (diffMinutes < 1440) {
        return `${Math.floor(diffMinutes / 60)}小时前`;
    } else {
        return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// 查看结果
function viewResults(sessionId) {
    window.open(`/view/${sessionId}`, '_blank');
}

// 删除记录
function deleteRecord(sessionId) {
    if (!confirm('确定要删除这条记录吗？删除后将无法恢复。')) {
        return;
    }
    
    fetch(`/api/history/${sessionId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('记录删除成功');
            loadHistory();
        } else {
            showError(data.error || '删除失败');
        }
    })
    .catch(error => {
        showError('删除失败: ' + error.message);
    });
}

// 显示成功消息
function showSuccess(message) {
    const successElement = document.getElementById('success-message');
    successElement.textContent = message;
    successElement.style.display = 'block';
    
    setTimeout(() => {
        successElement.style.display = 'none';
    }, 5000);
}

// 显示错误消息
function showError(message) {
    const errorElement = document.getElementById('error-message');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 8000);
}

// 隐藏所有消息
function hideMessages() {
    document.getElementById('success-message').style.display = 'none';
    document.getElementById('error-message').style.display = 'none';
}
