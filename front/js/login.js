/**
 * 登录页面 JavaScript
 * 使用 jQuery 实现登录功能
 */

// 检查是否已登录（3天内有效）
function checkAutoLogin() {
    var loggedIn = localStorage.getItem('logged_in');
    var loginTime = localStorage.getItem('login_time');
    
    if (loggedIn === 'true' && loginTime) {
        var now = Date.now();
        var threeDays = 3 * 24 * 60 * 60 * 1000; // 3天的毫秒数
        
        if (now - parseInt(loginTime) < threeDays) {
            // 登录状态仍有效，自动跳转到首页
            window.location.href = 'index.html';
            return true;
        } else {
            // 登录状态已过期，清除本地存储
            localStorage.removeItem('user');
            localStorage.removeItem('logged_in');
            localStorage.removeItem('login_time');
        }
    }
    return false;
}

$(document).ready(function() {
    // 页面加载时检查自动登录
    if (checkAutoLogin()) {
        return; // 已自动登录，无需继续
    }
    
    // 表单提交处理
    $('.form').on('submit', function(e) {
        e.preventDefault();
        
        // 获取表单数据
        var username = $('#username').val().trim();
        var password = $('#password').val().trim();
        
        // 表单验证
        var errors = [];
        
        if (!username) {
            errors.push('请输入用户名');
        } else if (username.length < 3) {
            errors.push('用户名长度至少3个字符');
        }
        
        if (!password) {
            errors.push('请输入密码');
        } else if (password.length < 6) {
            errors.push('密码长度至少6个字符');
        }
        
        // 如果有错误，显示提示
        if (errors.length > 0) {
            showToast(errors.join('\n'), 'error');
            return;
        }
        
        // 提交登录请求
        submitLogin(username, password);
    });
    
    // 密码可见性切换
    $('#toggle-password').on('click', function() {
        togglePassword('password', this);
    });
});

/**
 * 提交登录请求
 */
function submitLogin(username, password) {
    // 使用全局配置的API地址
    var apiUrl = typeof AppConfig !== 'undefined' 
        ? AppConfig.API_BASE_URL + '/login' 
        : 'http://localhost:5000/api/login';
    
    $.ajax({
        url: apiUrl,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: username,
            password: password
        }),
        success: function(response) {
            if (response.success) {
                showToast(response.message, 'success');
                
                // 保存用户信息到本地存储
                localStorage.setItem('user', JSON.stringify(response.user));
                localStorage.setItem('logged_in', 'true');
                localStorage.setItem('login_time', Date.now().toString()); // 记录登录时间
                
                // 登录成功后跳转到首页
                setTimeout(function() {
                    window.location.href = 'index.html';
                }, 1500);
            } else {
                showToast(response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('登录请求失败:', error);
            showToast('网络连接失败，请稍后重试', 'error');
        }
    });
}

/**
 * 切换密码可见性
 */
function togglePassword(fieldId, iconElement) {
    var passwordField = $('#' + fieldId);
    var type = passwordField.attr('type') === 'password' ? 'text' : 'password';
    passwordField.attr('type', type);
    
    // 切换图标
    var iconSrc = $(iconElement).attr('src');
    if (iconSrc.includes('visibility.svg')) {
        $(iconElement).attr('src', 'icon/visibility_off.svg');
    } else {
        $(iconElement).attr('src', 'icon/visibility.svg');
    }
}

/**
 * 显示提示消息
 */
function showToast(message, type) {
    // 创建提示元素
    var toast = $('<div>').addClass('toast').addClass(type);
    toast.text(message);
    
    // 添加到页面
    $('body').append(toast);
    
    // 显示动画
    setTimeout(function() {
        toast.addClass('show');
    }, 10);
    
    // 3秒后自动消失
    setTimeout(function() {
        toast.removeClass('show');
        setTimeout(function() {
            toast.remove();
        }, 300);
    }, 3000);
}
