/**
 * 登录权限控制
 * 未登录状态下仅允许访问白名单页面
 */
(function() {
    // 白名单页面（无需登录即可访问）
    var whiteList = [
        'register.html',
        'login.html',
        'forgot_password.html',
        'reset_password.html'
    ];
    
    // 获取当前页面文件名
    var currentPage = window.location.pathname.split('/').pop();
    if (!currentPage || currentPage === '') {
        currentPage = 'index.html';
    }
    
    // 检查是否在白名单中
    if (whiteList.indexOf(currentPage) === -1) {
        // 非白名单页面，需要检查登录状态
        checkLoginStatus();
    }
})();

/**
 * 检查登录状态
 */
function checkLoginStatus() {
    var loggedIn = localStorage.getItem('logged_in');
    var loginTime = localStorage.getItem('login_time');
    
    // 检查是否已登录
    if (loggedIn !== 'true') {
        // 未登录，跳转到登录页面
        window.location.href = 'login.html';
        return;
    }
    
    // 检查登录是否过期（3天）
    if (loginTime) {
        var now = Date.now();
        var threeDays = 3 * 24 * 60 * 60 * 1000; // 3天的毫秒数
        
        if (now - parseInt(loginTime) >= threeDays) {
            // 登录已过期，清除状态并跳转
            localStorage.removeItem('user');
            localStorage.removeItem('logged_in');
            localStorage.removeItem('login_time');
            window.location.href = 'login.html';
        }
    }
}
