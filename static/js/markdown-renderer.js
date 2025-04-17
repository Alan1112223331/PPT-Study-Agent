/**
 * Markdown和数学公式渲染器
 * 使用marked.js处理Markdown
 * 使用KaTeX渲染数学公式
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化渲染器
    initializeMarkdownRenderer();
    
    // 添加延迟检查，确保KaTeX完全加载
    setTimeout(checkKatexLoaded, 1000);
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

    // 加载KaTeX
    if (typeof katex === 'undefined') {
        // 加载KaTeX CSS
        loadCSSWithFallback(
            'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css',
            '/static/css/lib/katex.min.css'  // 本地备选路径
        );
        
        // 加载KaTeX JS
        loadScriptWithFallback(
            'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js',
            '/static/js/lib/katex.min.js',  // 本地备选路径
            function() {
                // 加载自动渲染扩展
                loadScriptWithFallback(
                    'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js',
                    '/static/js/lib/auto-render.min.js',  // 本地备选路径
                    function() {
                        console.log('KaTeX加载完成');
                        initializeKatexRenderer();
                    }
                );
            }
        );
    } else {
        initializeKatexRenderer();
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
    if (element.dataset.mathRendered === 'true') {
        console.log('元素已经渲染过，跳过处理');
        return;
    }

    // 渲染Markdown
    element.innerHTML = marked.parse(text);

    // 渲染数学公式
    renderMathInElement(element);
}

/**
 * 渲染元素中的数学公式
 * @param {HTMLElement} element - 包含数学公式的元素
 */
function renderMathInElement(element) {
    // 防止递归调用
    if (element.dataset.processingMath === 'true') {
        console.warn('检测到递归调用renderMathInElement，跳过处理');
        return;
    }
    
    // 检查元素是否已经渲染过数学公式
    if (element.dataset.mathRendered === 'true') {
        console.log('元素已经渲染过数学公式，跳过处理');
        return;
    }
    
    if (!isKatexReady()) {
        console.warn('KaTeX未完全加载，数学公式可能无法正确渲染');
        // 将渲染任务添加到队列，等待KaTeX加载完成后执行
        addToRenderQueue(element);
        return;
    }

    // 标记元素正在处理中
    element.dataset.processingMath = 'true';

    const renderOptions = {
        delimiters: [
            {left: '$$', right: '$$', display: true},   // 块级公式
            {left: '$', right: '$', display: false},    // 行内公式
            {left: '\\(', right: '\\)', display: false}, // 行内公式
            {left: '\\[', right: '\\]', display: true}   // 块级公式
        ],
        throwOnError: false,
        output: 'html'  // 确保输出HTML而不是文本
    };

    try {
        // 首先尝试使用window.renderMathInElement
        if (typeof window.renderMathInElement === 'function') {
            window.renderMathInElement(element, renderOptions);
            // 移除处理标记
            delete element.dataset.processingMath;
            return;
        }
        
        // 然后尝试使用katex.renderMathInElement
        if (typeof window.katex !== 'undefined' && typeof window.katex.renderMathInElement === 'function') {
            window.katex.renderMathInElement(element, renderOptions);
            // 移除处理标记
            delete element.dataset.processingMath;
            return;
        }

        // 不再尝试使用全局renderMathInElement，因为这会导致递归调用
        // 如果前两种方法都不可用，直接尝试手动渲染
        console.warn('无法找到可用的renderMathInElement函数，尝试手动渲染');
        tryManualRender(element);
        // 移除处理标记 - 这里不需要，因为tryManualRender会处理
        return;
    } catch (error) {
        console.error('渲染数学公式时出错:', error);
        // 尝试手动渲染每个公式
        tryManualRender(element);
        // 移除处理标记 - 这里不需要，因为tryManualRender会处理
    }
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
        if (element.dataset.mathRendered === 'true') {
            console.log('元素已经渲染过，跳过处理');
            return;
        }
        
        // 获取原始文本内容
        const originalText = element.textContent || element.innerText;
        // 渲染为Markdown
        renderMarkdown(originalText, element);
    });
}

// 渲染队列，存储等待KaTeX加载完成后需要渲染的元素
let renderQueue = [];

/**
 * 将元素添加到渲染队列
 * @param {HTMLElement} element - 要渲染的元素
 */
function addToRenderQueue(element) {
    renderQueue.push(element);
}

/**
 * 处理渲染队列中的所有元素
 */
function processRenderQueue() {
    if (renderQueue.length > 0 && isKatexReady()) {
        console.log(`处理渲染队列中的${renderQueue.length}个元素`);
        const elementsToRender = [...renderQueue];
        renderQueue = [];
        
        elementsToRender.forEach(function(element) {
            renderMathInElement(element);
        });
    }
}

/**
 * 检查KaTeX是否已完全加载
 * @returns {boolean} - KaTeX是否已准备好
 */
function isKatexReady() {
    return typeof window.katex !== 'undefined' && 
           (typeof window.renderMathInElement === 'function' || 
            typeof window.katex.renderMathInElement === 'function');
}

/**
 * 初始化KaTeX渲染器
 */
function initializeKatexRenderer() {
    if (typeof window.renderMathInElement === 'undefined' && typeof window.katex !== 'undefined') {
        if (typeof window.katex.renderMathInElement === 'function') {
            window.renderMathInElement = window.katex.renderMathInElement;
            console.log('KaTeX renderMathInElement 函数已初始化');
        }
    }
    
    // 处理渲染队列
    processRenderQueue();
}

/**
 * 检查KaTeX是否已加载，如果已加载则处理渲染队列
 */
function checkKatexLoaded() {
    if (isKatexReady()) {
        console.log('KaTeX已成功加载，处理渲染队列');
        processRenderQueue();
        // 重新处理页面上的所有Markdown元素
        processAllMarkdownElements();
    } else {
        console.warn('KaTeX尚未加载完成，尝试重新加载');
        // 如果KaTeX未加载，尝试重新加载
        if (typeof katex === 'undefined') {
            loadScriptWithFallback(
                'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js',
                '/static/js/lib/katex.min.js',
                function() {
                    loadScriptWithFallback(
                        'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js',
                        '/static/js/lib/auto-render.min.js',
                        function() {
                            initializeKatexRenderer();
                            // 再次检查
                            setTimeout(checkKatexLoaded, 1000);
                        }
                    );
                }
            );
        } else {
            // 再次检查
            setTimeout(checkKatexLoaded, 1000);
        }
    }
}

/**
 * 尝试手动渲染公式
 * @param {HTMLElement} element - 包含公式的元素
 */
function tryManualRender(element) {
    // 防止递归调用导致栈溢出
    if (element.dataset.processingMath === 'true') {
        console.warn('检测到递归调用tryManualRender，跳过处理');
        return;
    }
    
    // 标记元素正在处理中
    element.dataset.processingMath = 'true';
    
    if (typeof window.katex === 'undefined' || typeof window.katex.render !== 'function') {
        console.error('无法手动渲染公式：katex.render不可用');
        // 移除处理标记
        delete element.dataset.processingMath;
        return;
    }
    
    try {
        // 查找所有可能的公式，使用非贪婪匹配以避免正则表达式问题
        const text = element.innerHTML;
        
        // 使用更安全的正则表达式匹配行内公式和块级公式
        // 避免使用复杂的正则表达式，改用简单的字符串分割和处理方法
        let inlineMath = [];
        let displayMath = [];
        
        // 简单的字符串处理方法来提取公式
        // 提取行内公式 $...$
        let tempText = text;
        let startIdx = tempText.indexOf('$');
        while (startIdx !== -1) {
            let endIdx = tempText.indexOf('$', startIdx + 1);
            if (endIdx !== -1 && tempText.substring(startIdx + 1, endIdx).indexOf('\n') === -1) {
                inlineMath.push(tempText.substring(startIdx, endIdx + 1));
                tempText = tempText.substring(0, startIdx) + '###PLACEHOLDER###' + tempText.substring(endIdx + 1);
            }
            startIdx = tempText.indexOf('$', startIdx + 1);
        }
        
        // 提取块级公式 $$...$$
        tempText = text;
        startIdx = tempText.indexOf('$$');
        while (startIdx !== -1) {
            let endIdx = tempText.indexOf('$$', startIdx + 2);
            if (endIdx !== -1 && tempText.substring(startIdx + 2, endIdx).indexOf('\n') === -1) {
                displayMath.push(tempText.substring(startIdx, endIdx + 2));
                tempText = tempText.substring(0, startIdx) + '###PLACEHOLDER###' + tempText.substring(endIdx + 2);
            }
            startIdx = tempText.indexOf('$$', startIdx + 1);
        }
        
        // 手动渲染每个公式
        let renderedText = text;
        
        // 渲染行内公式
        inlineMath.forEach(function(formula) {
            try {
                const mathContent = formula.slice(1, -1);
                const renderedFormula = window.katex.renderToString(mathContent, {displayMode: false});
                // 使用字符串替换而不是正则表达式
                renderedText = renderedText.split(formula).join(renderedFormula);
            } catch (e) {
                console.error('手动渲染行内公式失败:', formula, e);
            }
        });
        
        // 渲染块级公式
        displayMath.forEach(function(formula) {
            try {
                const mathContent = formula.slice(2, -2);
                const renderedFormula = window.katex.renderToString(mathContent, {displayMode: true});
                // 使用字符串替换而不是正则表达式
                renderedText = renderedText.split(formula).join(renderedFormula);
            } catch (e) {
                console.error('手动渲染块级公式失败:', formula, e);
            }
        });
        
        // 更新元素内容
        if (renderedText !== text) {
            // 先设置内容，然后再移除处理标记
            element.innerHTML = renderedText;
            // 标记元素已经渲染过数学公式
            element.dataset.mathRendered = 'true';
            // 更新内容后再移除处理标记
            delete element.dataset.processingMath;
        } else {
            // 如果没有更新内容，也需要移除处理标记
            delete element.dataset.processingMath;
            // 标记元素已经渲染过数学公式
            element.dataset.mathRendered = 'true';
        }
    } catch (error) {
        console.error('手动渲染公式时出错:', error);
        // 确保在出错时也移除处理标记
        delete element.dataset.processingMath;
    }
}

// 导出函数供外部使用
window.markdownRenderer = {
    renderMarkdown: renderMarkdown,
    processAllMarkdownElements: processAllMarkdownElements,
    checkKatexLoaded: checkKatexLoaded
};