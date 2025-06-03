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
            // 检查KaTeX是否正确加载
            if (typeof katex === 'undefined') {
                console.error('KaTeX主库加载失败');
                return;
            }
            
            // 加载KaTeX自动渲染扩展
            loadScriptWithFallback(
                'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js',
                '/static/js/lib/auto-render.min.js',
                function() {
                    // 检查auto-render是否正确加载
                    if (typeof renderMathInElement === 'undefined') {
                        console.error('KaTeX auto-render扩展加载失败');
                        return;
                    }
                    
                    console.log('KaTeX库加载完成');
                    // 延迟渲染以确保DOM完全准备好
                    setTimeout(function() {
                        renderMathInElements();
                        // 设置观察器以处理动态添加的内容
                        setupMathObserver();
                    }, 200);
                }
            );
        }
    );
}

/**
 * 加载MathJax库
 */
function loadMathJax() {
    // MathJax配置必须在加载前设置
    window.MathJax = {
        tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']],
            processEscapes: true,
            processEnvironments: true,
            packages: {'[+]': ['ams', 'newcommand', 'autoload']}
        },
        startup: {
            ready: function() {
                console.log('MathJax startup ready');
                MathJax.startup.defaultReady();
            },
            pageReady: function() {
                console.log('MathJax page ready - 开始渲染数学公式');
                return MathJax.startup.defaultPageReady().then(function() {
                    console.log('MathJax 初始渲染完成');
                    // 设置观察器以处理动态添加的内容
                    setupMathObserver();
                });
            }
        },
        options: {
            skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
            ignoreHtmlClass: 'tex2jax_ignore',
            processHtmlClass: 'tex2jax_process'
        },
        chtml: {
            scale: 1,
            minScale: 0.5,
            matchFontHeight: false,
            fontURL: 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/output/chtml/fonts/woff-v2'
        }
    };
    
    // 加载MathJax
    loadScriptWithFallback(
        'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js',
        '/static/js/lib/tex-mml-chtml.js',
        function() {
            console.log('MathJax脚本加载完成');
            // 检查MathJax是否正确加载
            if (typeof MathJax === 'undefined') {
                console.error('MathJax库加载失败');
                return;
            }
            console.log('MathJax库加载成功，版本:', MathJax.version);
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
        // 更灵活的重复渲染检测：允许强制重新渲染
        const forceRerender = element.dataset.forceRerender === 'true';
        if (element.dataset.mathRendered === 'true' && !forceRerender) {
            console.log('元素数学公式已经渲染过，跳过处理');
            return;
        }
        
        try {
            // 渲染数学公式，针对模型输出的特点进行优化
            renderMathInElement(element, {
                delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false},
                    {left: '\\(', right: '\\)', display: false},
                    {left: '\\[', right: '\\]', display: true}
                ],
                throwOnError: false,
                strict: false, // 允许非严格模式，提高兼容性
                trust: false, // 安全考虑
                macros: {
                    // 常用数学宏定义，支持模型常用符号
                    "\\RR": "\\mathbb{R}",
                    "\\CC": "\\mathbb{C}",
                    "\\NN": "\\mathbb{N}",
                    "\\ZZ": "\\mathbb{Z}",
                    "\\QQ": "\\mathbb{Q}",
                    "\\varepsilon": "\\epsilon",
                    "\\cdot": "\\bullet"
                },
                // 忽略某些可能导致渲染失败的标签
                ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
                ignoredClasses: ['tex2jax_ignore']
            });
            
            // 标记为已渲染
            element.dataset.mathRendered = 'true';
            element.dataset.forceRerender = 'false';
            console.log('数学公式渲染成功');
            
        } catch (error) {
            console.error('KaTeX渲染出错:', error);
            // 如果KaTeX失败，尝试回退到基本显示
            element.dataset.mathRendered = 'false';
        }
    });
}

/**
 * 使用MathJax渲染页面中的数学公式
 */
function renderMathWithMathJax() {
    if (typeof MathJax === 'undefined' || !MathJax.typesetPromise) {
        console.error('MathJax未正确加载或版本不兼容');
        return;
    }
    
    // 查找所有description-content类的元素
    const descriptionElements = document.querySelectorAll('.description-content');
    
    // 收集需要渲染的元素
    const elementsToRender = [];
    
    descriptionElements.forEach(function(element) {
        const forceRerender = element.dataset.forceRerender === 'true';
        if (element.dataset.mathRendered !== 'true' || forceRerender) {
            elementsToRender.push(element);
        }
    });
    
    if (elementsToRender.length === 0) {
        console.log('没有需要渲染的数学公式元素');
        return;
    }
    
    console.log('开始使用MathJax渲染', elementsToRender.length, '个元素');
    
    // 使用MathJax的typesetPromise方法进行渲染
    MathJax.typesetPromise(elementsToRender).then(function() {
        console.log('MathJax渲染完成');
        // 标记所有元素为已渲染
        elementsToRender.forEach(function(element) {
            element.dataset.mathRendered = 'true';
            element.dataset.forceRerender = 'false';
        });
    }).catch(function(error) {
        console.error('MathJax渲染出错:', error);
        // 将失败的元素标记为未渲染
        elementsToRender.forEach(function(element) {
            element.dataset.mathRendered = 'false';
        });
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
        renderMathWithMathJax();
    } else {
        console.warn('数学渲染引擎未准备好:', mathEngine);
    }
}

/**
 * 设置MutationObserver来监控DOM变化并自动渲染数学公式
 */
function setupMathObserver() {
    if (typeof MutationObserver === 'undefined') {
        console.warn('浏览器不支持MutationObserver');
        return;
    }
    
    const observer = new MutationObserver(function(mutations) {
        let shouldRender = false;
        
        mutations.forEach(function(mutation) {
            // 检查是否有新增的节点包含数学公式
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const hasDescriptionContent = node.classList.contains('description-content') ||
                                                    node.querySelector('.description-content');
                        const hasMathContent = node.textContent && 
                                             (node.textContent.includes('$') || 
                                              node.textContent.includes('\\(') ||
                                              node.textContent.includes('\\['));
                        
                        if (hasDescriptionContent || hasMathContent) {
                            shouldRender = true;
                        }
                    }
                });
            }
            
            // 检查文本内容变化
            if (mutation.type === 'characterData' || mutation.type === 'childList') {
                const target = mutation.target;
                if (target && target.textContent && 
                    (target.textContent.includes('$') || 
                     target.textContent.includes('\\(') ||
                     target.textContent.includes('\\['))) {
                    shouldRender = true;
                }
            }
        });
        
        if (shouldRender) {
            console.log('检测到DOM变化，重新渲染数学公式');
            // 延迟渲染以避免过于频繁的调用
            clearTimeout(window.mathRenderTimeout);
            window.mathRenderTimeout = setTimeout(function() {
                processAllMathElements();
            }, 300);
        }
    });
    
    // 开始观察整个文档的变化
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });
    
    console.log('数学公式DOM观察器已启动');
}

/**
 * 强制重新渲染所有数学公式
 */
function forceRerenderMath() {
    console.log('强制重新渲染数学公式');
    
    // 清除所有已渲染标记
    const descriptionElements = document.querySelectorAll('.description-content');
    descriptionElements.forEach(function(element) {
        element.dataset.mathRendered = 'false';
        element.dataset.forceRerender = 'true';
    });
    
    // 根据当前引擎重新渲染
    setTimeout(function() {
        processAllMathElements();
    }, 100);
}

/**
 * 获取当前使用的数学渲染引擎
 */
function getCurrentMathEngine() {
    return localStorage.getItem('mathEngine') || 'KaTeX';
}

/**
 * 切换数学渲染引擎
 */
function switchMathEngine(engine) {
    if (engine !== 'KaTeX' && engine !== 'MathJax') {
        console.error('不支持的数学引擎:', engine);
        return;
    }
    
    localStorage.setItem('mathEngine', engine);
    console.log('切换到数学引擎:', engine);
    
    // 重新加载页面以应用新的渲染引擎
    location.reload();
}

/**
 * 检查MathJax是否正确加载和配置
 */
function checkMathJaxStatus() {
    const status = {
        loaded: false,
        version: null,
        configured: false,
        ready: false,
        typesetPromise: false,
        error: null
    };
    
    try {
        if (typeof MathJax !== 'undefined') {
            status.loaded = true;
            status.version = MathJax.version || 'unknown';
            status.configured = !!MathJax.config;
            status.ready = !!(MathJax.startup && MathJax.startup.document);
            status.typesetPromise = typeof MathJax.typesetPromise === 'function';
        }
    } catch (error) {
        status.error = error.message;
    }
    
    return status;
}

/**
 * 检查KaTeX是否正确加载
 */
function checkKaTeXStatus() {
    const status = {
        loaded: false,
        version: null,
        autoRender: false,
        error: null
    };
    
    try {
        if (typeof katex !== 'undefined') {
            status.loaded = true;
            status.version = katex.version || 'unknown';
        }
        if (typeof renderMathInElement !== 'undefined') {
            status.autoRender = true;
        }
    } catch (error) {
        status.error = error.message;
    }
    
    return status;
}

/**
 * 获取完整的数学库状态信息
 */
function getMathLibrariesStatus() {
    return {
        currentEngine: getCurrentMathEngine(),
        katex: checkKaTeXStatus(),
        mathjax: checkMathJaxStatus(),
        timestamp: new Date().toISOString()
    };
}

// 导出函数供外部使用
window.mathRenderer = {
    processAllMathElements: processAllMathElements,
    switchMathEngine: switchMathEngine,
    forceRerenderMath: forceRerenderMath,
    renderMathInElements: renderMathInElements,
    renderMathWithMathJax: renderMathWithMathJax,
    getCurrentMathEngine: getCurrentMathEngine,
    getMathLibrariesStatus: getMathLibrariesStatus,
    checkMathJaxStatus: checkMathJaxStatus,
    checkKaTeXStatus: checkKaTeXStatus
};