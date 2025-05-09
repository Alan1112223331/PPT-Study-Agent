document.addEventListener('DOMContentLoaded', function() {
    // 获取元素
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressMessage = document.getElementById('progress-message');
    
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
            alert('请选择文件');
            return;
        }
        
        // 准备表单数据
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        // 显示进度区域
        progressContainer.style.display = 'block';
        progressMessage.textContent = '正在上传文件...';
        
        // 禁用上传按钮
        form.querySelector('button[type="submit"]').disabled = true;
        
        // 发送上传请求
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                progressMessage.textContent = '文件上传成功，正在转换...';
                progressBar.style.width = '30%';
                
                // 等待一小段时间后跳转到实时查看页面
                setTimeout(() => {
                    window.location.href = `/view/${data.session_id}`;
                }, 1500);
            } else {
                throw new Error(data.error || '上传失败');
            }
        })
        .catch(error => {
            try {
                // 尝试解析错误响应为JSON
                error.response.json().then(data => {
                    // 显示更详细的错误信息
                    const errorMsg = data.error + (data.allowed ? `\n允许的格式: ${data.allowed.join(', ')}` : '');
                    progressMessage.textContent = `错误: ${errorMsg}`;
                    console.error('上传错误:', data);
                }).catch(() => {
                    // 如果无法解析为JSON，则显示原始错误消息
                    progressMessage.textContent = `错误: ${error.message}`;
                });
            } catch (e) {
                // 普通错误
                progressMessage.textContent = `错误: ${error.message}`;
            }
            progressBar.style.width = '0%';
            form.querySelector('button[type="submit"]').disabled = false;
        });
    });
});
