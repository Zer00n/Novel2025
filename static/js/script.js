// 全局JavaScript函数

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 初始化弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // 自动隐藏警告消息
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// 收藏功能
function toggleFavorite(novelId, isAdd) {
    const btn = event.target;
    const originalText = btn.textContent;
    
    // 显示加载状态
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> 处理中...';
    
    fetch('/api/favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            novel_id: novelId,
            action: isAdd ? 'add' : 'remove'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新按钮状态
            if (isAdd) {
                btn.className = 'btn btn-warning';
                btn.textContent = '取消收藏';
                btn.onclick = () => toggleFavorite(novelId, false);
            } else {
                btn.className = 'btn btn-outline-warning';
                btn.textContent = '加入收藏';
                btn.onclick = () => toggleFavorite(novelId, true);
            }
            showMessage(data.message || (isAdd ? '收藏成功' : '取消收藏成功'), 'success');
        } else {
            showMessage(data.message || '操作失败', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('网络错误，请稍后重试', 'danger');
        btn.textContent = originalText;
    })
    .finally(() => {
        btn.disabled = false;
    });
}

// 提交评价
function submitReview(novelId) {
    const form = document.getElementById('reviewForm');
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // 验证表单
    const rating = formData.get('rating');
    if (!rating) {
        showMessage('请选择评分', 'warning');
        return false;
    }
    
    // 显示加载状态
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> 提交中...';
    
    const data = {
        novel_id: novelId,
        rating: parseInt(rating),
        comment: formData.get('comment') || ''
    };
    
    fetch('/api/review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('评价提交成功', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showMessage(data.message || '提交失败', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('网络错误，请稍后重试', 'danger');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = '提交评价';
    });
    
    return false;
}

// 显示消息提示
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // 插入到页面顶部
    const container = document.querySelector('.container, .container-fluid');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // 自动隐藏
    setTimeout(() => {
        const alert = new bootstrap.Alert(alertDiv);
        alert.close();
    }, 3000);
}

// 阅读设置相关函数
const ReadingSettings = {
    // 设置字体大小
    setFontSize: function(size) {
        const content = document.querySelector('.chapter-text, .chapter-content');
        if (content) {
            content.style.fontSize = size + 'px';
            localStorage.setItem('reading_font_size', size);
        }
    },
    
    // 设置行间距
    setLineHeight: function(height) {
        const content = document.querySelector('.chapter-text, .chapter-content');
        if (content) {
            content.style.lineHeight = height;
            localStorage.setItem('reading_line_height', height);
        }
    },
    
    // 设置阅读主题
    setTheme: function(theme) {
        const content = document.querySelector('#chapterContent, .reading-container');
        if (content) {
            content.className = content.className.replace(/theme-\w+/g, '');
            content.classList.add('theme-' + theme);
            localStorage.setItem('reading_theme', theme);
        }
        
        // 如果是暗色主题，应用到整个页面
        if (theme === 'dark') {
            document.body.classList.add('theme-dark');
        } else {
            document.body.classList.remove('theme-dark');
        }
    },
    
    // 全屏阅读
    toggleFullscreen: function() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.log(`Error attempting to enable fullscreen: ${err.message}`);
            });
        } else {
            document.exitFullscreen();
        }
    },
    
    // 恢复阅读设置
    restoreSettings: function() {
        const fontSize = localStorage.getItem('reading_font_size');
        if (fontSize) {
            this.setFontSize(fontSize);
            const fontSizeSlider = document.getElementById('fontSize');
            if (fontSizeSlider) fontSizeSlider.value = fontSize;
        }
        
        const lineHeight = localStorage.getItem('reading_line_height');
        if (lineHeight) {
            this.setLineHeight(lineHeight);
            const lineHeightSlider = document.getElementById('lineHeight');
            if (lineHeightSlider) lineHeightSlider.value = lineHeight;
        }
        
        const theme = localStorage.getItem('reading_theme');
        if (theme) {
            this.setTheme(theme);
        }
    }
};

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    // 只在阅读页面启用快捷键
    if (!document.querySelector('.chapter-content, .chapter-text')) return;
    
    switch(e.key) {
        case 'ArrowLeft':
            if (e.ctrlKey) {
                // Ctrl + 左箭头：上一章
                const prevBtn = document.querySelector('a[href*="chapter_number"]:contains("上一章")');
                if (prevBtn) {
                    prevBtn.click();
                    e.preventDefault();
                }
            }
            break;
            
        case 'ArrowRight':
            if (e.ctrlKey) {
                // Ctrl + 右箭头：下一章
                const nextBtn = document.querySelector('a[href*="chapter_number"]:contains("下一章")');
                if (nextBtn) {
                    nextBtn.click();
                    e.preventDefault();
                }
            }
            break;
            
        case 'F11':
            // F11：全屏
            ReadingSettings.toggleFullscreen();
            e.preventDefault();
            break;
            
        case 'Escape':
            // ESC：退出全屏
            if (document.fullscreenElement) {
                document.exitFullscreen();
            }
            break;
    }
});

// 搜索建议功能
function setupSearchSuggestions() {
    const searchInput = document.querySelector('input[name="q"]');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            hideSearchSuggestions();
            return;
        }
        
        searchTimeout = setTimeout(() => {
            fetchSearchSuggestions(query);
        }, 300);
    });
    
    // 点击其他地方时隐藏建议
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-suggestions')) {
            hideSearchSuggestions();
        }
    });
}

function fetchSearchSuggestions(query) {
    fetch(`/api/search-suggestions?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSearchSuggestions(data.suggestions);
            }
        })
        .catch(error => {
            console.error('Search suggestions error:', error);
        });
}

function showSearchSuggestions(suggestions) {
    hideSearchSuggestions(); // 先清除现有的建议
    
    if (suggestions.length === 0) return;
    
    const searchInput = document.querySelector('input[name="q"]');
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.className = 'search-suggestions';
    suggestionsDiv.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-top: none;
        max-height: 300px;
        overflow-y: auto;
        z-index: 1000;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    `;
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.style.cssText = `
            padding: 10px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
        `;
        item.textContent = suggestion;
        
        item.addEventListener('click', function() {
            searchInput.value = suggestion;
            hideSearchSuggestions();
            searchInput.closest('form').submit();
        });
        
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f5f5f5';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'white';
        });
        
        suggestionsDiv.appendChild(item);
    });
    
    // 插入建议列表
    const searchContainer = searchInput.closest('.search-form, form');
    if (searchContainer) {
        searchContainer.style.position = 'relative';
        searchContainer.appendChild(suggestionsDiv);
    }
}

function hideSearchSuggestions() {
    const suggestions = document.querySelector('.search-suggestions');
    if (suggestions) {
        suggestions.remove();
    }
}

// 图片懒加载
function setupLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // 不支持 IntersectionObserver 的浏览器
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// 页面加载完成后初始化
window.addEventListener('load', function() {
    ReadingSettings.restoreSettings();
    setupSearchSuggestions();
    setupLazyLoading();
});

// 工具函数
const Utils = {
    // 格式化数字
    formatNumber: function(num) {
        if (num >= 10000) {
            return (num / 10000).toFixed(1) + '万';
        }
        return num.toString();
    },
    
    // 格式化日期
    formatDate: function(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // 1分钟内
            return '刚刚';
        } else if (diff < 3600000) { // 1小时内
            return Math.floor(diff / 60000) + '分钟前';
        } else if (diff < 86400000) { // 1天内
            return Math.floor(diff / 3600000) + '小时前';
        } else if (diff < 2592000000) { // 30天内
            return Math.floor(diff / 86400000) + '天前';
        } else {
            return date.toLocaleDateString();
        }
    },
    
    // 防抖函数
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // 节流函数
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};