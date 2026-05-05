/**
 * 注册页面 JavaScript
 * 使用 jQuery 实现注册功能
 */

$(document).ready(function() {
    // 表单提交处理
    $('.form').on('submit', function(e) {
        e.preventDefault();
        
        // 获取表单数据
        var username = $('input[type="text"]').val().trim();
        var email = $('input[type="email"]').val().trim();
        var password = $('#password').val().trim();
        var confirmPassword = $('#confirm-password').val().trim();
        
        // 表单验证
        var errors = [];
        
        if (!username) {
            errors.push('请输入用户名');
        } else if (username.length < 3 || username.length > 20) {
            errors.push('用户名长度应在3-20个字符之间');
        }
        
        if (!email) {
            errors.push('请输入邮箱');
        } else if (!isValidEmail(email)) {
            errors.push('请输入有效的邮箱地址');
        }
        
        if (!password) {
            errors.push('请输入密码');
        } else if (password.length < 6) {
            errors.push('密码长度至少6个字符');
        }
        
        if (!confirmPassword) {
            errors.push('请确认密码');
        } else if (password !== confirmPassword) {
            errors.push('两次输入的密码不一致');
        }
        
        // 如果有错误，显示提示
        if (errors.length > 0) {
            showToast(errors.join('\n'), 'error');
            return;
        }
        
        // 提交注册请求
        submitRegister(username, email, password);
    });
    
    // 密码可见性切换
    $('#toggle-password').on('click', function() {
        togglePassword('password', this);
    });
    
    $('#toggle-confirm-password').on('click', function() {
        togglePassword('confirm-password', this);
    });
});

/**
 * 邮箱验证
 */
function isValidEmail(email) {
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * 提交注册请求
 */
function submitRegister(username, email, password) {
    // 使用全局配置的API地址
    var apiUrl = typeof AppConfig !== 'undefined' 
        ? AppConfig.API_BASE_URL + '/register' 
        : 'http://localhost:5000/api/register';
    
    $.ajax({
        url: apiUrl,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: username,
            email: email,
            password: password
        }),
        success: function(response) {
            if (response.success) {
                showToast(response.message, 'success');
                // 注册成功后跳转到登录页面
                setTimeout(function() {
                    window.location.href = typeof AppConfig !== 'undefined' 
                        ? AppConfig.ROUTES.LOGIN_PAGE 
                        : 'login.html';
                }, 1500);
            } else {
                showToast(response.message, 'error');
            }
        },
        error: function(xhr, status, error) {
            console.error('注册请求失败:', error);
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
