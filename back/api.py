#!/usr/bin/env python3
import os
import sys
import json
import hashlib
import logging
from datetime import datetime

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    import pymysql
except ImportError:
    print("Installing required packages...")
    os.system('pip install flask pymysql flask-cors')
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    import pymysql

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# MySQL配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'mqzhifu',
    'password': 'mqzhifu',
    'database': 'test',
    'charset': 'utf8mb4'
}

def log_sql(query, params=None):
    """记录SQL查询日志"""
    if params:
        logging.info(f"SQL: {query} | Params: {params}")
    else:
        logging.info(f"SQL: {query}")

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        logging.info("数据库连接成功")
        return conn
    except Exception as e:
        logging.error(f"数据库连接失败: {e}")
        return None

def execute_sql(cursor, query, params=None):
    """执行SQL并记录日志"""
    print(f"[DEBUG] 准备执行SQL: {query}")
    print(f"[DEBUG] 参数: {params}")
    log_sql(query, params)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        print(f"[DEBUG] SQL执行成功")
    except Exception as e:
        print(f"[DEBUG] SQL执行失败: {e}")
        raise
    return cursor

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'success': False, 'message': '请填写完整信息'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor()
        
        # 检查用户名是否已存在
        execute_sql(cursor, "SELECT id FROM user WHERE username = %s", (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '用户名已存在'})
        
        # 检查邮箱是否已存在
        execute_sql(cursor, "SELECT id FROM user WHERE email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '邮箱已被注册'})
        
        # 插入新用户
        hashed_pwd = hash_password(password)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 检查表结构是否有password字段，如果没有则添加
        execute_sql(cursor, "DESCRIBE user")
        columns = [col[0] for col in cursor.fetchall()]
        if 'password' not in columns:
            execute_sql(cursor, "ALTER TABLE user ADD COLUMN password VARCHAR(255) NOT NULL COMMENT '密码'")
            conn.commit()
        if 'email' not in columns:
            execute_sql(cursor, "ALTER TABLE user ADD COLUMN email VARCHAR(255) NOT NULL COMMENT '邮箱'")
            conn.commit()
        
        # 插入用户数据
        execute_sql(cursor,
            "INSERT INTO user (username, email, password, gender, avatar, birthday, age, add_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (username, email, hashed_pwd, '未知', '', '', '0', now)
        )
        conn.commit()
        
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'message': '注册成功', 'user_id': user_id})
    
    except Exception as e:
        logging.error(f"注册错误: {e}")
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'})

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '请填写用户名和密码'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 检查表结构是否有password字段
        execute_sql(cursor, "DESCRIBE user")
        columns = [col['Field'] for col in cursor.fetchall()]
        if 'password' not in columns:
            conn.close()
            return jsonify({'success': False, 'message': '用户表结构不完整'})
        
        # 查询用户
        hashed_pwd = hash_password(password)
        logging.info(f"用户名: {username}, 密码哈希: {hashed_pwd[:20]}...")
        execute_sql(cursor, "SELECT id, username, email FROM user WHERE username = %s AND password = %s", (username, hashed_pwd))
        user = cursor.fetchone()
        logging.info(f"查询结果: {user}")
        
        conn.close()
        
        if user:
            # 保存登录状态（简单实现，实际应用中应使用session或JWT）
            return jsonify({
                'success': True,
                'message': '登录成功',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                }
            })
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'})
    
    except Exception as e:
        import traceback
        logging.error(f"登录错误类型: {type(e).__name__}")
        logging.error(f"登录错误信息: {str(e)}")
        logging.error(f"登录错误堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'})

@app.route('/api/check_login', methods=['GET'])
def check_login():
    """检查登录状态"""
    return jsonify({'success': True, 'message': '未登录', 'logged_in': False})

@app.route('/api/describe_table/<table_name>', methods=['GET'])
def describe_table(table_name):
    """查看表结构"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor()
        execute_sql(cursor, f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        conn.close()
        
        return jsonify({'success': True, 'columns': columns})
    
    except Exception as e:
        logging.error(f"查询表结构错误: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/add_smoke_record', methods=['POST'])
def add_smoke_record():
    """添加抽烟记录"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor()
        
        # 获取当前时间
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 插入记录
        execute_sql(cursor,
            "INSERT INTO smoke_record (uid, add_time) VALUES (%s, %s)",
            (user_id, now)
        )
        conn.commit()
        
        record_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '记录成功',
            'record_id': record_id,
            'smoke_time': now
        })
    
    except Exception as e:
        import traceback
        logging.error(f"添加抽烟记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})

if __name__ == '__main__':
    logging.info("API服务启动，监听端口 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
