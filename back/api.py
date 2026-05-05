#!/usr/bin/env python3
import os
import sys
import json
import hashlib
import logging
from datetime import datetime, timedelta

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

@app.route('/api/generate_test_data', methods=['POST'])
def generate_test_data():
    """生成测试数据：上周和昨天，每天10条记录"""
    import random
    from datetime import datetime, timedelta
    
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor()
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE smoke_record")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        # 生成日期范围：上周（7天前到1天前）和昨天
        today = datetime.now().date()
        dates = []
        
        # 上周：7天前到1天前
        for i in range(7, 0, -1):
            dates.append(today - timedelta(days=i))
        
        # 昨天
        dates.append(today - timedelta(days=1))
        
        total_inserted = 0
        
        for date in dates:
            # 每天生成10条记录
            for _ in range(10):
                # 生成随机时间
                hour = random.randint(6, 22)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                record_time = datetime.combine(date, datetime.min.time().replace(hour=hour, minute=minute, second=second))
                
                # 构建插入语句
                insert_columns = []
                insert_values = []
                
                if 'uid' in column_names:
                    insert_columns.append('uid')
                    insert_values.append(user_id)
                
                if 'add_time' in column_names:
                    insert_columns.append('add_time')
                    insert_values.append(record_time)
                
                # 检查其他可能的字段
                if 'time' in column_names and 'add_time' not in column_names:
                    insert_columns.append('time')
                    insert_values.append(record_time)
                
                if insert_columns:
                    placeholders = ', '.join(['%s'] * len(insert_columns))
                    sql = f"INSERT INTO smoke_record ({', '.join(insert_columns)}) VALUES ({placeholders})"
                    execute_sql(cursor, sql, insert_values)
                    total_inserted += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'成功生成 {total_inserted} 条测试记录',
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'records_per_day': 10
        })
    
    except Exception as e:
        import traceback
        logging.error(f"生成测试数据错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'生成失败: {str(e)}'})

@app.route('/api/clear_smoke_records', methods=['POST'])
def clear_smoke_records():
    """清空用户的所有抽烟记录"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor()
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE smoke_record")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        # 删除记录
        if 'uid' in column_names:
            execute_sql(cursor, "DELETE FROM smoke_record WHERE uid = %s", (user_id,))
        else:
            execute_sql(cursor, "DELETE FROM smoke_record")
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'成功清空 {deleted_count} 条抽烟记录'
        })
    
    except Exception as e:
        import traceback
        logging.error(f"清空记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'清空失败: {str(e)}'})

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
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE smoke_record")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        # 获取当前时间
        now = datetime.now()
        
        # 构建插入语句
        insert_columns = []
        insert_values = []
        
        if 'uid' in column_names:
            insert_columns.append('uid')
            insert_values.append(user_id)
        
        if 'add_time' in column_names:
            insert_columns.append('add_time')
            insert_values.append(now)
        
        # 检查其他可能的字段
        if 'time' in column_names and 'add_time' not in column_names:
            insert_columns.append('time')
            insert_values.append(now)
        
        if insert_columns:
            placeholders = ', '.join(['%s'] * len(insert_columns))
            sql = f"INSERT INTO smoke_record ({', '.join(insert_columns)}) VALUES ({placeholders})"
            execute_sql(cursor, sql, insert_values)
            conn.commit()
        
        record_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '记录成功',
            'record_id': record_id,
            'smoke_time': now.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        import traceback
        logging.error(f"添加抽烟记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})

@app.route('/api/get_today_smoke_records', methods=['GET'])
def get_today_smoke_records():
    """获取今日抽烟记录"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE smoke_record")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        # 获取今天的日期范围
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 查询今日记录
        if 'uid' in column_names:
            if 'add_time' in column_names:
                execute_sql(cursor, 
                    "SELECT * FROM smoke_record WHERE uid = %s AND add_time >= %s AND add_time < %s ORDER BY add_time ASC",
                    (user_id, today, tomorrow)
                )
            elif 'time' in column_names:
                execute_sql(cursor,
                    "SELECT * FROM smoke_record WHERE uid = %s AND time >= %s AND time < %s ORDER BY time ASC",
                    (user_id, today, tomorrow)
                )
        else:
            if 'add_time' in column_names:
                execute_sql(cursor,
                    "SELECT * FROM smoke_record WHERE add_time >= %s AND add_time < %s ORDER BY add_time ASC",
                    (today, tomorrow)
                )
        
        records = cursor.fetchall()
        conn.close()
        
        # 格式化时间
        for record in records:
            if 'add_time' in record and record['add_time']:
                if isinstance(record['add_time'], datetime):
                    record['time_str'] = record['add_time'].strftime('%H:%M')
                else:
                    record['time_str'] = str(record['add_time'])[11:16]
            elif 'time' in record and record['time']:
                if isinstance(record['time'], datetime):
                    record['time_str'] = record['time'].strftime('%H:%M')
                else:
                    record['time_str'] = str(record['time'])[11:16]
        
        return jsonify({
            'success': True,
            'count': len(records),
            'records': records
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取今日记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/get_smoke_statistics', methods=['GET'])
def get_smoke_statistics():
    """获取抽烟统计数据：上周日均、单日最低、昨天"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE smoke_record")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        # 确定时间字段
        time_field = 'add_time' if 'add_time' in column_names else ('time' if 'time' in column_names else None)
        
        if not time_field:
            conn.close()
            return jsonify({'success': False, 'message': '表结构不完整'})
        
        # 计算日期范围
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        last_week_start = today - timedelta(days=7)
        last_week_end = today - timedelta(days=1)
        
        # 获取昨天的记录数
        yesterday_start = yesterday.strftime('%Y-%m-%d')
        yesterday_end = today.strftime('%Y-%m-%d')
        
        if 'uid' in column_names:
            execute_sql(cursor,
                f"SELECT COUNT(*) as count FROM smoke_record WHERE uid = %s AND {time_field} >= %s AND {time_field} < %s",
                (user_id, yesterday_start, yesterday_end)
            )
        else:
            execute_sql(cursor,
                f"SELECT COUNT(*) as count FROM smoke_record WHERE {time_field} >= %s AND {time_field} < %s",
                (yesterday_start, yesterday_end)
            )
        yesterday_count = cursor.fetchone()['count']
        
        # 获取上周每天的记录数
        daily_counts = []
        for i in range(7, 0, -1):
            day = today - timedelta(days=i)
            day_start = day.strftime('%Y-%m-%d')
            day_end = (day + timedelta(days=1)).strftime('%Y-%m-%d')
            
            if 'uid' in column_names:
                execute_sql(cursor,
                    f"SELECT COUNT(*) as count FROM smoke_record WHERE uid = %s AND {time_field} >= %s AND {time_field} < %s",
                    (user_id, day_start, day_end)
                )
            else:
                execute_sql(cursor,
                    f"SELECT COUNT(*) as count FROM smoke_record WHERE {time_field} >= %s AND {time_field} < %s",
                    (day_start, day_end)
                )
            daily_counts.append(cursor.fetchone()['count'])
        
        # 计算上周日均
        last_week_avg = sum(daily_counts) / 7 if daily_counts else 0
        
        # 计算单日最低（上周中有记录的天数）
        days_with_records = [c for c in daily_counts if c > 0]
        single_day_min = min(days_with_records) if days_with_records else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'last_week_avg': round(last_week_avg, 1),
            'single_day_min': single_day_min,
            'yesterday_count': yesterday_count
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取统计数据错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/get_smoke_records_list', methods=['GET'])
def get_smoke_records_list():
    """获取抽烟记录列表（按日期分组）"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE smoke_record")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        # 查询所有记录
        if 'uid' in column_names:
            execute_sql(cursor,
                "SELECT * FROM smoke_record WHERE uid = %s ORDER BY add_time DESC",
                (user_id,)
            )
        else:
            execute_sql(cursor,
                "SELECT * FROM smoke_record ORDER BY add_time DESC"
            )
        
        records = cursor.fetchall()
        conn.close()
        
        # 按日期分组
        date_groups = {}
        for record in records:
            if 'add_time' in record and record['add_time']:
                if isinstance(record['add_time'], datetime):
                    date_str = record['add_time'].strftime('%Y-%m-%d')
                    time_str = record['add_time'].strftime('%H:%M')
                else:
                    date_str = str(record['add_time'])[:10]
                    time_str = str(record['add_time'])[11:16]
                
                if date_str not in date_groups:
                    date_groups[date_str] = {
                        'date': date_str,
                        'count': 0,
                        'times': []
                    }
                date_groups[date_str]['count'] += 1
                date_groups[date_str]['times'].append(time_str)
        
        # 转换为列表并排序
        result = sorted(date_groups.values(), key=lambda x: x['date'], reverse=True)
        
        # 计算统计数据
        total_records = len(records)
        total_days = len(result)
        daily_avg = round(total_records / total_days, 1) if total_days > 0 else 0
        
        return jsonify({
            'success': True,
            'total_records': total_records,
            'total_days': total_days,
            'daily_avg': daily_avg,
            'date_groups': result
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取记录列表错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/get_smoke_chart_data', methods=['GET'])
def get_smoke_chart_data():
    """获取抽烟图表数据（日/周/月统计）"""
    try:
        user_id = request.args.get('user_id')
        stat_type = request.args.get('type', 'day')  # day, week, month
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE smoke_record")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        time_field = 'add_time' if 'add_time' in column_names else None
        if not time_field:
            conn.close()
            return jsonify({'success': False, 'message': '表结构不完整'})
        
        today = datetime.now().date()
        labels = []
        data = []
        total = 0
        
        if stat_type == 'day':
            # 最近7天
            for i in range(6, -1, -1):
                day = today - timedelta(days=i)
                day_start = day.strftime('%Y-%m-%d')
                day_end = (day + timedelta(days=1)).strftime('%Y-%m-%d')
                
                # 标签：今天、昨天或日期
                if i == 0:
                    label = '今天'
                elif i == 1:
                    label = '昨天'
                else:
                    label = f'{day.month}/{day.day}'
                labels.append(label)
                
                if 'uid' in column_names:
                    execute_sql(cursor,
                        f"SELECT COUNT(*) as count FROM smoke_record WHERE uid = %s AND {time_field} >= %s AND {time_field} < %s",
                        (user_id, day_start, day_end)
                    )
                else:
                    execute_sql(cursor,
                        f"SELECT COUNT(*) as count FROM smoke_record WHERE {time_field} >= %s AND {time_field} < %s",
                        (day_start, day_end)
                    )
                count = cursor.fetchone()['count']
                data.append(count)
                total += count
                
        elif stat_type == 'week':
            # 最近7周
            for i in range(6, -1, -1):
                week_start_date = today - timedelta(days=i*7 + today.weekday())
                week_end_date = week_start_date + timedelta(days=7)
                
                week_start = week_start_date.strftime('%Y-%m-%d')
                week_end = week_end_date.strftime('%Y-%m-%d')
                
                label = f'{week_start_date.month}/{week_start_date.day}'
                labels.append(label)
                
                if 'uid' in column_names:
                    execute_sql(cursor,
                        f"SELECT COUNT(*) as count FROM smoke_record WHERE uid = %s AND {time_field} >= %s AND {time_field} < %s",
                        (user_id, week_start, week_end)
                    )
                else:
                    execute_sql(cursor,
                        f"SELECT COUNT(*) as count FROM smoke_record WHERE {time_field} >= %s AND {time_field} < %s",
                        (week_start, week_end)
                    )
                count = cursor.fetchone()['count']
                data.append(count)
                total += count
                
        elif stat_type == 'month':
            # 最近3个月
            for i in range(2, -1, -1):
                # 计算i个月前的月份
                target_month = today.month - i
                target_year = today.year
                while target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                month_start = f'{target_year}-{target_month:02d}-01'
                
                # 计算下个月的第一天
                next_month = target_month + 1
                next_year = target_year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                month_end = f'{next_year}-{next_month:02d}-01'
                
                label = f'{target_year}/{target_month}'
                labels.append(label)
                
                if 'uid' in column_names:
                    execute_sql(cursor,
                        f"SELECT COUNT(*) as count FROM smoke_record WHERE uid = %s AND {time_field} >= %s AND {time_field} < %s",
                        (user_id, month_start, month_end)
                    )
                else:
                    execute_sql(cursor,
                        f"SELECT COUNT(*) as count FROM smoke_record WHERE {time_field} >= %s AND {time_field} < %s",
                        (month_start, month_end)
                    )
                count = cursor.fetchone()['count']
                data.append(count)
                total += count
        
        conn.close()
        
        return jsonify({
            'success': True,
            'labels': labels,
            'data': data,
            'total': total,
            'type': stat_type
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取图表数据错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/get_expense_chart_data', methods=['GET'])
def get_expense_chart_data():
    """获取消费图表数据（日/周/月统计）"""
    try:
        user_id = request.args.get('user_id')
        stat_type = request.args.get('type', 'day')  # day, week, month
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE expenses")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        time_field = 'real_time' if 'real_time' in column_names else 'add_time'
        
        today = datetime.now().date()
        labels = []
        data = []
        total = 0
        
        if stat_type == 'day':
            # 最近7天
            for i in range(6, -1, -1):
                day = today - timedelta(days=i)
                day_start = day.strftime('%Y-%m-%d')
                day_end = (day + timedelta(days=1)).strftime('%Y-%m-%d')
                
                # 标签：今天、昨天或日期
                if i == 0:
                    label = '今天'
                elif i == 1:
                    label = '昨天'
                else:
                    label = f'{day.month}/{day.day}'
                labels.append(label)
                
                execute_sql(cursor,
                    f"SELECT COALESCE(SUM(price), 0) as total FROM expenses WHERE {uid_field} = %s AND {time_field} >= %s AND {time_field} < %s",
                    (user_id, day_start, day_end)
                )
                amount = int(float(cursor.fetchone()['total']))
                data.append(amount)
                total += amount
                
        elif stat_type == 'week':
            # 最近7周
            for i in range(6, -1, -1):
                week_start_date = today - timedelta(days=i*7 + today.weekday())
                week_end_date = week_start_date + timedelta(days=7)
                
                week_start = week_start_date.strftime('%Y-%m-%d')
                week_end = week_end_date.strftime('%Y-%m-%d')
                
                label = f'{week_start_date.month}/{week_start_date.day}'
                labels.append(label)
                
                execute_sql(cursor,
                    f"SELECT COALESCE(SUM(price), 0) as total FROM expenses WHERE {uid_field} = %s AND {time_field} >= %s AND {time_field} < %s",
                    (user_id, week_start, week_end)
                )
                amount = int(float(cursor.fetchone()['total']))
                data.append(amount)
                total += amount
                
        elif stat_type == 'month':
            # 最近3个月
            for i in range(2, -1, -1):
                # 计算i个月前的月份
                target_month = today.month - i
                target_year = today.year
                while target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                month_start = f'{target_year}-{target_month:02d}-01'
                
                # 计算下个月的第一天
                next_month = target_month + 1
                next_year = target_year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                month_end = f'{next_year}-{next_month:02d}-01'
                
                label = f'{target_year}/{target_month}'
                labels.append(label)
                
                execute_sql(cursor,
                    f"SELECT COALESCE(SUM(price), 0) as total FROM expenses WHERE {uid_field} = %s AND {time_field} >= %s AND {time_field} < %s",
                    (user_id, month_start, month_end)
                )
                amount = int(float(cursor.fetchone()['total']))
                data.append(amount)
                total += amount
        
        conn.close()
        
        return jsonify({
            'success': True,
            'labels': labels,
            'data': data,
            'total': total,
            'type': stat_type
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取消费图表数据错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/get_categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    try:
        category_type = request.args.get('type')  # 1: 消费记录, 2: 日常记录
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        if category_type:
            execute_sql(cursor, "SELECT * FROM category WHERE type = %s ORDER BY sort, id", (int(category_type),))
        else:
            execute_sql(cursor, "SELECT * FROM category ORDER BY type, sort, id")
        
        categories = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'categories': categories
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取分类错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    """添加消费记录"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        title = data.get('title')
        price = data.get('price')
        category = data.get('category')
        real_time = data.get('real_time')
        
        if not user_id or not title or not price or not category or not real_time:
            return jsonify({'success': False, 'message': '参数不完整'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE expenses")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        
        # 切换回普通cursor用于INSERT
        cursor.close()
        cursor = conn.cursor()
        
        execute_sql(cursor,
            f"INSERT INTO expenses ({uid_field}, price, category, title, real_time, add_time) VALUES (%s, %s, %s, %s, %s, NOW())",
            (user_id, price, category, title, real_time)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '添加成功'
        })
    
    except Exception as e:
        import traceback
        logging.error(f"添加消费记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})

@app.route('/api/add_daily', methods=['POST'])
def add_daily():
    """添加日常记录"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        title = data.get('title')
        category = data.get('category')
        real_time = data.get('real_time')
        
        if not user_id or not title or not category or not real_time:
            return jsonify({'success': False, 'message': '参数不完整'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE daily")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        
        # 切换回普通cursor用于INSERT
        cursor.close()
        cursor = conn.cursor()
        
        execute_sql(cursor,
            f"INSERT INTO daily ({uid_field}, category, title, real_time, add_time) VALUES (%s, %s, %s, %s, NOW())",
            (user_id, category, title, real_time)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '添加成功'
        })
    
    except Exception as e:
        import traceback
        logging.error(f"添加日常记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})

@app.route('/api/get_today_expenses', methods=['GET'])
def get_today_expenses():
    """获取今日消费记录"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE expenses")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 获取今日消费记录
        execute_sql(cursor,
            f"SELECT * FROM expenses WHERE {uid_field} = %s AND real_time >= %s AND real_time < %s ORDER BY real_time DESC",
            (user_id, today, tomorrow)
        )
        expenses = cursor.fetchall()
        
        # 计算总金额
        execute_sql(cursor,
            f"SELECT SUM(price) as total FROM expenses WHERE {uid_field} = %s AND real_time >= %s AND real_time < %s",
            (user_id, today, tomorrow)
        )
        total_result = cursor.fetchone()
        # 计算总金额
        total = int(float(total_result['total'])) if total_result['total'] else 0
        
        # 获取分类信息
        execute_sql(cursor, "SELECT * FROM category WHERE type = 1")
        categories = cursor.fetchall()
        category_map = {cat['id']: cat['name'] for cat in categories}
        
        conn.close()
        
        # 格式化数据
        formatted_expenses = []
        for expense in expenses:
            formatted_expenses.append({
                'id': expense['id'],
                'title': expense['title'],
                'price': int(float(expense['price'])),
                'category': expense['category'],
                'category_name': category_map.get(expense['category'], '未知'),
                'real_time': expense['real_time'].strftime('%H:%M') if isinstance(expense['real_time'], datetime) else expense['real_time']
            })
        
        return jsonify({
            'success': True,
            'expenses': formatted_expenses,
            'total': float(total),
            'count': len(formatted_expenses)
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取今日消费记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/get_expense_breakdown', methods=['GET'])
def get_expense_breakdown():
    """获取支出构成数据"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE expenses")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 按分类统计今日消费
        execute_sql(cursor,
            f"SELECT category, SUM(price) as total FROM expenses WHERE {uid_field} = %s AND real_time >= %s AND real_time < %s GROUP BY category ORDER BY total DESC",
            (user_id, today, tomorrow)
        )
        category_stats = cursor.fetchall()
        
        # 获取分类信息
        execute_sql(cursor, "SELECT * FROM category WHERE type = 1")
        categories = cursor.fetchall()
        category_map = {cat['id']: cat['name'] for cat in categories}
        
        conn.close()
        
        # 计算总金额
        total = sum([int(float(stat['total'])) for stat in category_stats])
        
        # 格式化数据，计算占比
        breakdown = []
        for stat in category_stats:
            price_int = int(float(stat['total']))
            percent = round((price_int / total * 100), 1) if total > 0 else 0
            breakdown.append({
                'category': stat['category'],
                'name': category_map.get(stat['category'], '未知'),
                'total': price_int,
                'percent': percent
            })
        
        # 只返回前5个
        breakdown = breakdown[:5]
        
        return jsonify({
            'success': True,
            'breakdown': breakdown,
            'total': total
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取支出构成错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/get_purchase_records', methods=['GET'])
def get_purchase_records():
    """获取购烟记录（category=10）"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE expenses")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        
        # 获取购烟记录（category=10）
        execute_sql(cursor,
            f"SELECT * FROM expenses WHERE {uid_field} = %s AND category = 10 ORDER BY real_time DESC LIMIT 10",
            (user_id,)
        )
        records = cursor.fetchall()
        
        # 计算总花费
        execute_sql(cursor,
            f"SELECT SUM(price) as total FROM expenses WHERE {uid_field} = %s AND category = 10",
            (user_id,)
        )
        total_result = cursor.fetchone()
        total = int(float(total_result['total'])) if total_result['total'] else 0
        
        conn.close()
        
        # 格式化数据
        formatted_records = []
        for record in records:
            formatted_records.append({
                'id': record['id'],
                'title': record['title'],
                'price': int(float(record['price'])),
                'real_time': record['real_time'].strftime('%Y-%m-%d') if isinstance(record['real_time'], datetime) else str(record['real_time'])[:10]
            })
        
        return jsonify({
            'success': True,
            'records': formatted_records,
            'total': total
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取购烟记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/add_purchase_record', methods=['POST'])
def add_purchase_record():
    """添加购烟记录"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        title = data.get('title')
        price = data.get('price')
        real_time = data.get('real_time')
        
        if not user_id or not title or not price:
            return jsonify({'success': False, 'message': '参数不完整'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE expenses")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        
        # 切换回普通cursor用于INSERT
        cursor.close()
        cursor = conn.cursor()
        
        # real_time 取当前时间
        real_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        execute_sql(cursor,
            f"INSERT INTO expenses ({uid_field}, category, title, price, real_time, add_time) VALUES (%s, 10, %s, %s, %s, NOW())",
            (user_id, title, price, real_time)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '添加成功'
        })
    
    except Exception as e:
        import traceback
        logging.error(f"添加购烟记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})

@app.route('/api/get_daily_records', methods=['GET'])
def get_daily_records():
    """获取日常记录"""
    try:
        user_id = request.args.get('user_id')
        date = request.args.get('date')  # 格式：YYYY-MM-DD
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE daily")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        
        if date:
            # 查询指定日期的记录
            execute_sql(cursor,
                f"SELECT * FROM daily WHERE {uid_field} = %s AND DATE(real_time) = %s ORDER BY real_time ASC",
                (user_id, date)
            )
        else:
            # 查询今天的记录
            today = datetime.now().strftime('%Y-%m-%d')
            execute_sql(cursor,
                f"SELECT * FROM daily WHERE {uid_field} = %s AND DATE(real_time) = %s ORDER BY real_time ASC",
                (user_id, today)
            )
        
        records = cursor.fetchall()
        
        # 获取分类信息
        execute_sql(cursor, "SELECT * FROM category WHERE type = 2")
        categories = cursor.fetchall()
        category_map = {cat['id']: cat for cat in categories}
        
        conn.close()
        
        # 格式化数据
        formatted_records = []
        for record in records:
            real_time = record['real_time']
            if isinstance(real_time, datetime):
                time_str = real_time.strftime('%H:%M')
            else:
                time_str = str(real_time)[-5:] if len(str(real_time)) >= 5 else '00:00'
            
            category_id = record.get('category')
            category_info = category_map.get(category_id, {})
            
            formatted_records.append({
                'id': record['id'],
                'title': record['title'],
                'category': category_id,
                'category_name': category_info.get('name', '其它'),
                'category_type': category_info.get('icon_type', 'other'),
                'real_time': time_str
            })
        
        return jsonify({
            'success': True,
            'records': formatted_records,
            'date': date or datetime.now().strftime('%Y-%m-%d')
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取日常记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/get_daily_analytics', methods=['GET'])
def get_daily_analytics():
    """获取日常分类统计"""
    try:
        user_id = request.args.get('user_id')
        date = request.args.get('date')  # 格式：YYYY-MM-DD
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE daily")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 查询指定日期的记录
        execute_sql(cursor,
            f"SELECT * FROM daily WHERE {uid_field} = %s AND DATE(real_time) = %s ORDER BY real_time ASC",
            (user_id, date)
        )
        
        records = cursor.fetchall()
        
        # 获取分类信息
        execute_sql(cursor, "SELECT * FROM category WHERE type = 2")
        categories = cursor.fetchall()
        category_map = {cat['id']: cat for cat in categories}
        
        conn.close()
        
        # 按分类统计
        category_counts = {}
        for record in records:
            cat_id = record.get('category')
            if cat_id not in category_counts:
                category_counts[cat_id] = 0
            category_counts[cat_id] += 1
        
        # 格式化数据
        analytics = []
        total = len(records)
        for cat_id, count in category_counts.items():
            category_info = category_map.get(cat_id, {})
            analytics.append({
                'category': cat_id,
                'name': category_info.get('name', '其它'),
                'count': count,
                'percent': round((count / total * 100), 1) if total > 0 else 0
            })
        
        # 按数量排序
        analytics.sort(key=lambda x: x['count'], reverse=True)
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'total': total,
            'date': date
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取日常统计错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/get_daily_records', methods=['GET'])
def get_daily_records():
    """获取日常记录"""
    try:
        user_id = request.args.get('user_id')
        date = request.args.get('date')  # 格式：YYYY-MM-DD
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE daily")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        
        if date:
            # 查询指定日期的记录
            execute_sql(cursor,
                f"SELECT * FROM daily WHERE {uid_field} = %s AND DATE(real_time) = %s ORDER BY real_time ASC",
                (user_id, date)
            )
        else:
            # 查询今天的记录
            today = datetime.now().strftime('%Y-%m-%d')
            execute_sql(cursor,
                f"SELECT * FROM daily WHERE {uid_field} = %s AND DATE(real_time) = %s ORDER BY real_time ASC",
                (user_id, today)
            )
        
        records = cursor.fetchall()
        
        # 获取分类信息
        execute_sql(cursor, "SELECT * FROM category WHERE type = 2")
        categories = cursor.fetchall()
        category_map = {cat['id']: cat for cat in categories}
        
        conn.close()
        
        # 格式化数据
        formatted_records = []
        for record in records:
            real_time = record['real_time']
            if isinstance(real_time, datetime):
                time_str = real_time.strftime('%H:%M')
            else:
                time_str = str(real_time)[-5:] if len(str(real_time)) >= 5 else '00:00'
            
            category_id = record.get('category')
            category_info = category_map.get(category_id, {})
            
            formatted_records.append({
                'id': record['id'],
                'title': record['title'],
                'category': category_id,
                'category_name': category_info.get('name', '其它'),
                'category_type': category_info.get('icon_type', 'other'),
                'real_time': time_str
            })
        
        return jsonify({
            'success': True,
            'records': formatted_records,
            'date': date or datetime.now().strftime('%Y-%m-%d')
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取日常记录错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/get_daily_analytics', methods=['GET'])
def get_daily_analytics():
    """获取日常分类统计"""
    try:
        user_id = request.args.get('user_id')
        date = request.args.get('date')  # 格式：YYYY-MM-DD
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 获取表结构
        execute_sql(cursor, "DESCRIBE daily")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        uid_field = 'uid' if 'uid' in column_names else 'user_id'
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 查询指定日期的记录
        execute_sql(cursor,
            f"SELECT * FROM daily WHERE {uid_field} = %s AND DATE(real_time) = %s ORDER BY real_time ASC",
            (user_id, date)
        )
        
        records = cursor.fetchall()
        
        # 获取分类信息
        execute_sql(cursor, "SELECT * FROM category WHERE type = 2")
        categories = cursor.fetchall()
        category_map = {cat['id']: cat for cat in categories}
        
        conn.close()
        
        # 按分类统计
        category_counts = {}
        for record in records:
            cat_id = record.get('category')
            if cat_id not in category_counts:
                category_counts[cat_id] = 0
            category_counts[cat_id] += 1
        
        # 格式化数据
        analytics = []
        total = len(records)
        for cat_id, count in category_counts.items():
            category_info = category_map.get(cat_id, {})
            analytics.append({
                'category': cat_id,
                'name': category_info.get('name', '其它'),
                'count': count,
                'percent': round((count / total * 100), 1) if total > 0 else 0
            })
        
        # 按数量排序
        analytics.sort(key=lambda x: x['count'], reverse=True)
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'total': total,
            'date': date
        })
    
    except Exception as e:
        import traceback
        logging.error(f"获取日常统计错误: {e}")
        logging.error(f"堆栈:\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

if __name__ == '__main__':
    logging.info("API服务启动，监听端口 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
