/**
 * 数学公式渲染器
 * 支持KaTeX和MathJax两种渲染引擎
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化数学公式渲染器
    initializeMathRenderer();
});

/**
 * 初始化数学公式渲染器
 */
function initializeMathRenderer() {
    // 默认使用KaTeX作为渲染引擎
    const mathEngine = localStorage.getItem('mathEngine') || 'KaTeX';
    
    // 加载相应的数学公式渲染库
    if (mathEngine === 'KaTeX') {
        loadKaTeX();
    } else {
        loadMathJax();
    }
}

/**
 * 加载KaTeX库及其依赖
 */
function loadKaTeX() {
    // 加载KaTeX CSS
    loadCSSWithFallback(
        'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css',
        '/static/css/lib/katex.min.css'
    );
    
    // 加载KaTeX主库
    loadScriptWithFallback(
        'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js',
        '/static/js/lib/katex.min.js',
        function() {
            // 加载KaTeX自动渲染扩展
            loadScriptWithFallback(
                'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js',
                '/static/js/lib/auto-render.min.js',
                function() {
                    // 渲染页面中的数学公式
                    renderMathInElements();
                }
            );
        }
    );
}

/**
 * 加载MathJax库
 */
function loadMathJax() {
    // MathJax配置
    window.MathJax = {
        tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']],
            processEscapes: true,
            processEnvironments: true
        },
        options: {
            skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
            ignoreHtmlClass: 'tex2jax_ignore',
            processHtmlClass: 'tex2jax_process'
        }
    };
    
    // 加载MathJax
    loadScriptWithFallback(
        'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js',
        '/static/js/lib/tex-mml-chtml.js',
        function() {
            // MathJax会自动渲染页面中的数学公式
            console.log('MathJax加载完成');
        }
    );
}

/**
 * 使用KaTeX渲染页面中的数学公式
 */
function renderMathInElements() {
    if (typeof renderMathInElement === 'undefined') {
        console.error('KaTeX auto-render扩展未加载');
        return;
    }
    
    // 查找所有description-content类的元素
    const descriptionElements = document.querySelectorAll('.description-content');
    
    descriptionElements.forEach(function(element) {
        // 检查元素是否已经被处理过
        if (element.dataset.mathRendered === 'true') {
            console.log('元素数学公式已经渲染过，跳过处理');
            return;
        }
        
        // 渲染数学公式
        renderMathInElement(element, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true}
            ],
            throwOnError: false
        });
        
        // 标记为已渲染
        element.dataset.mathRendered = 'true';
    });
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
 * 处理页面中所有的数学公式
 */
function processAllMathElements() {
    // 根据当前使用的引擎选择处理方法
    const mathEngine = localStorage.getItem('mathEngine') || 'KaTeX';
    
    if (mathEngine === 'KaTeX' && typeof renderMathInElement !== 'undefined') {
        renderMathInElements();
    } else if (mathEngine === 'MathJax' && typeof MathJax !== 'undefined') {
        // 对于MathJax，可以触发重新渲染
        if (MathJax.typesetPromise) {
            MathJax.typesetPromise();
        }
    }
}

/**
 * 切换数学公式渲染引擎
 * @param {string} engine - 'KaTeX' 或 'MathJax'
 */
function switchMathEngine(engine) {
    if (engine !== 'KaTeX' && engine !== 'MathJax') {
        console.error('不支持的数学引擎:', engine);
        return;
    }
    
    // 保存用户选择
    localStorage.setItem('mathEngine', engine);
    
    // 重新加载页面以应用新引擎
    window.location.reload();
}

// 导出函数供外部使用
window.mathRenderer = {
    processAllMathElements: processAllMathElements,
    switchMathEngine: switchMathEngine
};