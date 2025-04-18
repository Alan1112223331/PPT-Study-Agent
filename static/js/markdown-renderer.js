/**
 * Markdown渲染器
 * 使用marked.js处理Markdown
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化渲染器
    initializeMarkdownRenderer();
});

/**
 * 初始化Markdown渲染器
 */
function initializeMarkdownRenderer() {
    // 检查是否已加载所需库
    if (typeof marked === 'undefined') {
        loadScriptWithFallback(
            'https://cdn.jsdelivr.net/npm/marked@4.3.0/marked.min.js', 
            '/static/js/lib/marked.min.js',  // 本地备选路径
            function() {
                // 配置marked选项
                configureMarked();
            }
        );
    } else {
        configureMarked();
    }
}

/**
 * 配置Marked选项
 */
function configureMarked() {
    if (typeof marked !== 'undefined') {
        // 设置marked选项
        marked.setOptions({
            breaks: true,        // 允许换行
            gfm: true,          // 启用GitHub风格Markdown
            headerIds: true,    // 为标题生成ID
            mangle: false,      // 不转义HTML
            sanitize: false,    // 不净化输出
            silent: false,      // 不忽略错误
        });
        console.log('Marked配置完成');
    }
}

/**
 * 渲染Markdown内容
 * @param {string} text - Markdown文本
 * @param {HTMLElement} element - 要渲染到的元素
 */
function renderMarkdown(text, element) {
    if (typeof marked === 'undefined') {
        console.error('Marked库未加载');
        element.textContent = text;
        return;
    }

    // 检查元素是否已经被处理过，避免重复渲染
    if (element.dataset.rendered === 'true') {
        console.log('元素已经渲染过，跳过处理');
        return;
    }

    // 渲染Markdown
    element.innerHTML = marked.parse(text);
    
    // 标记为已渲染
    element.dataset.rendered = 'true';
}

/**
 * 加载外部JavaScript，带有备选URL
 * @param {string} primaryUrl - 主要脚本URL
 * @param {string} fallbackUrl - 备选脚本URL
 * @param {Function} callback - 加载完成后的回调
 */
function loadScriptWithFallback(primaryUrl, fallbackUrl, callback) {
    const script = document.createElement('script');
    script.src = primaryUrl;
    script.onload = callback || function() {};
    script.onerror = function() {
        console.warn('主要脚本加载失败，尝试备选URL:', primaryUrl);
        // 尝试加载备选URL
        const fallbackScript = document.createElement('script');
        fallbackScript.src = fallbackUrl;
        fallbackScript.onload = callback || function() {};
        fallbackScript.onerror = function() {
            console.error('备选脚本也加载失败:', fallbackUrl);
        };
        document.head.appendChild(fallbackScript);
    };
    document.head.appendChild(script);
}

/**
 * 加载外部CSS，带有备选URL
 * @param {string} primaryUrl - 主要CSS URL
 * @param {string} fallbackUrl - 备选CSS URL
 */
function loadCSSWithFallback(primaryUrl, fallbackUrl) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = primaryUrl;
    link.onerror = function() {
        console.warn('主要CSS加载失败，尝试备选URL:', primaryUrl);
        // 尝试加载备选URL
        const fallbackLink = document.createElement('link');
        fallbackLink.rel = 'stylesheet';
        fallbackLink.href = fallbackUrl;
        fallbackLink.onerror = function() {
            console.error('备选CSS也加载失败:', fallbackUrl);
        };
        document.head.appendChild(fallbackLink);
    };
    document.head.appendChild(link);
}

/**
 * 加载外部JavaScript (兼容旧代码)
 * @param {string} url - 脚本URL
 * @param {Function} callback - 加载完成后的回调
 */
function loadScript(url, callback) {
    loadScriptWithFallback(url, url, callback);
}

/**
 * 加载外部CSS (兼容旧代码)
 * @param {string} url - CSS URL
 */
function loadCSS(url) {
    loadCSSWithFallback(url, url);
}

/**
 * 处理页面中所有的Markdown内容元素
 */
function processAllMarkdownElements() {
    // 查找所有description-content类的元素
    const descriptionElements = document.querySelectorAll('.description-content');
    
    descriptionElements.forEach(function(element) {
        // 检查元素是否已经被处理过，避免重复渲染
        if (element.dataset.rendered === 'true') {
            console.log('元素已经渲染过，跳过处理');
            return;
        }
        
        // 获取原始文本内容
        const originalText = element.textContent || element.innerText;
        // 渲染为Markdown
        renderMarkdown(originalText, element);
    });
}

// 导出函数供外部使用
window.markdownRenderer = {
    renderMarkdown: renderMarkdown,
    processAllMarkdownElements: processAllMarkdownElements
};