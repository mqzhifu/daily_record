/**
 * 全局配置文件
 * 定义应用的全局常量和配置参数
 */
var AppConfig = {
    // 后端API基础地址
    API_BASE_URL: 'http://192.168.3.205:5000/api',
    
    // 静态资源基础地址
    STATIC_BASE_URL: 'http://192.168.3.205:90',
    
    // 路由路径
    ROUTES: {
        LOGIN: '/login',
        REGISTER: '/register',
        INDEX: '/index.html',
        LOGIN_PAGE: 'login.html'
    }
};

/**
 * 获取API基础地址
 */
function getApiBaseUrl() {
    return AppConfig.API_BASE_URL;
}

/**
 * 获取静态资源基础地址
 */
function getStaticBaseUrl() {
    return AppConfig.STATIC_BASE_URL;
}
