# pages/5_🏫_班级管理与在线签到.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import bcrypt
import time
import random
import hashlib
import uuid
import plotly.graph_objects as go
import plotly.express as px

# 页面配置
st.set_page_config(
    page_title="班级管理与在线签到 - 融思政",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 获取北京时间（中国时区）
def get_beijing_time():
    """获取当前北京时间"""
    # 中国使用东八区（UTC+8）
    return datetime.utcnow() + timedelta(hours=8)

def to_beijing_time_str(dt=None):
    """将datetime对象转换为北京时间的字符串格式"""
    if dt is None:
        dt = get_beijing_time()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def from_beijing_time_str(time_str):
    """从北京时间的字符串转换为datetime对象"""
    return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

# 初始化数据库表（用于班级和签到）
def init_classroom_db():
    """初始化班级管理和签到相关数据库表"""
    conn = sqlite3.connect('image_processing_platform.db')
    c = conn.cursor()
    
    # 创建班级表
    c.execute('''
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code VARCHAR(12) UNIQUE NOT NULL,
            class_name VARCHAR(100) NOT NULL,
            teacher_username VARCHAR(50) NOT NULL,
            description TEXT,
            max_students INTEGER DEFAULT 50,
            created_at TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            subscription_tier VARCHAR(20) DEFAULT 'free',
            FOREIGN KEY (teacher_username) REFERENCES users (username)
        )
    ''')
    
    # 创建班级成员表
    c.execute('''
        CREATE TABLE IF NOT EXISTS classroom_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code VARCHAR(12) NOT NULL,
            student_username VARCHAR(50) NOT NULL,
            joined_at TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            role VARCHAR(20) DEFAULT 'student',
            UNIQUE(class_code, student_username),
            FOREIGN KEY (class_code) REFERENCES classrooms (class_code),
            FOREIGN KEY (student_username) REFERENCES users (username)
        )
    ''')
    
    # 创建签到活动表
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_code VARCHAR(10) UNIQUE NOT NULL,
            class_code VARCHAR(12) NOT NULL,
            session_name VARCHAR(100) NOT NULL,
            teacher_username VARCHAR(50) NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 10,
            location_lat REAL,
            location_lng REAL,
            location_name VARCHAR(100),
            qr_code_data TEXT,
            attendance_type VARCHAR(20) DEFAULT 'standard',
            status VARCHAR(20) DEFAULT 'scheduled',
            created_at TEXT NOT NULL,
            total_students INTEGER DEFAULT 0,
            attended_students INTEGER DEFAULT 0,
            FOREIGN KEY (class_code) REFERENCES classrooms (class_code),
            FOREIGN KEY (teacher_username) REFERENCES users (username)
        )
    ''')
    
    # 创建签到记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_code VARCHAR(10) NOT NULL,
            student_username VARCHAR(50) NOT NULL,
            class_code VARCHAR(12) NOT NULL,
            check_in_time TEXT NOT NULL,
            check_in_method VARCHAR(20) DEFAULT 'manual',
            device_info TEXT,
            ip_address VARCHAR(45),
            location_lat REAL,
            location_lng REAL,
            is_late BOOLEAN DEFAULT FALSE,
            points_earned INTEGER DEFAULT 10,
            status VARCHAR(20) DEFAULT 'present',
            UNIQUE(session_code, student_username),
            FOREIGN KEY (session_code) REFERENCES attendance_sessions (session_code),
            FOREIGN KEY (student_username) REFERENCES users (username)
        )
    ''')
    
    # 创建订阅套餐表
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_code VARCHAR(20) UNIQUE NOT NULL,
            plan_name VARCHAR(50) NOT NULL,
            price_monthly REAL DEFAULT 0,
            price_yearly REAL DEFAULT 0,
            max_classes INTEGER DEFAULT 1,
            max_students_per_class INTEGER DEFAULT 30,
            max_attendance_sessions INTEGER DEFAULT 20,
            features TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TEXT NOT NULL
        )
    ''')
    
    # 创建教师订阅表
    c.execute('''
        CREATE TABLE IF NOT EXISTS teacher_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_username VARCHAR(50) NOT NULL,
            plan_code VARCHAR(20) NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            payment_status VARCHAR(20) DEFAULT 'active',
            auto_renew BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (teacher_username) REFERENCES users (username),
            FOREIGN KEY (plan_code) REFERENCES subscription_plans (plan_code)
        )
    ''')
    
    # 创建通知表
    c.execute('''
        CREATE TABLE IF NOT EXISTS class_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code VARCHAR(12) NOT NULL,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            notification_type VARCHAR(20) DEFAULT 'announcement',
            created_by VARCHAR(50) NOT NULL,
            created_at TEXT NOT NULL,
            is_urgent BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (class_code) REFERENCES classrooms (class_code),
            FOREIGN KEY (created_by) REFERENCES users (username)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # 初始化默认订阅套餐
    init_default_plans()

def init_default_plans():
    """初始化默认的订阅套餐"""
    default_plans = [
        {
            'plan_code': 'free',
            'plan_name': '免费版',
            'price_monthly': 0,
            'price_yearly': 0,
            'max_classes': 1,
            'max_students_per_class': 30,
            'max_attendance_sessions': 10,
            'features': '基础班级管理,标准签到功能,基本数据分析'
        },
        {
            'plan_code': 'pro',
            'plan_name': '专业版',
            'price_monthly': 29.9,
            'price_yearly': 299,
            'max_classes': 5,
            'max_students_per_class': 100,
            'max_attendance_sessions': 100,
            'features': '专业版功能,高级数据分析,地理位置签到,批量导入,自定义设置'
        },
        {
            'plan_code': 'enterprise',
            'plan_name': '企业版',
            'price_monthly': 99.9,
            'price_yearly': 999,
            'max_classes': 50,
            'max_students_per_class': 500,
            'max_attendance_sessions': 9999,
            'features': '企业级功能,API接口,专属客服,高级安全,定制开发'
        }
    ]
    
    conn = sqlite3.connect('image_processing_platform.db')
    c = conn.cursor()
    
    for plan in default_plans:
        try:
            c.execute("SELECT id FROM subscription_plans WHERE plan_code = ?", (plan['plan_code'],))
            if c.fetchone() is None:
                created_at = to_beijing_time_str()
                c.execute('''
                    INSERT INTO subscription_plans 
                    (plan_code, plan_name, price_monthly, price_yearly, max_classes, 
                     max_students_per_class, max_attendance_sessions, features, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    plan['plan_code'], plan['plan_name'], plan['price_monthly'],
                    plan['price_yearly'], plan['max_classes'], plan['max_students_per_class'],
                    plan['max_attendance_sessions'], plan['features'], created_at
                ))
        except Exception as e:
            print(f"初始化套餐失败: {str(e)}")
    
    conn.commit()
    conn.close()
def delete_classroom_simple(class_code, teacher_username):
    """简单删除班级 - 软删除（标记为不活跃）"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 简单验证：检查班级是否存在且教师匹配
        c.execute("""
            SELECT teacher_username FROM classrooms 
            WHERE class_code = ?
        """, (class_code,))
        
        result = c.fetchone()
        if not result:
            conn.close()
            return False, "班级不存在"
        
        if result[0] != teacher_username:
            conn.close()
            return False, "只有创建教师可以删除班级"
        
        # 简单的软删除：将班级标记为不活跃
        c.execute("""
            UPDATE classrooms 
            SET is_active = FALSE 
            WHERE class_code = ?
        """, (class_code,))
        
        conn.commit()
        conn.close()
        return True, "班级已成功删除"
    except Exception as e:
        return False, f"删除失败: {str(e)}"
def get_classroom_stats(class_code):
    """获取班级统计信息"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 获取班级基本信息
        c.execute("""
            SELECT 
                c.class_name,
                c.teacher_username,
                c.created_at,
                COUNT(DISTINCT cm.id) as total_members,
                COUNT(DISTINCT a.id) as total_sessions,
                COUNT(DISTINCT ar.id) as total_attendance_records
            FROM classrooms c
            LEFT JOIN classroom_members cm ON c.class_code = cm.class_code
            LEFT JOIN attendance_sessions a ON c.class_code = a.class_code
            LEFT JOIN attendance_records ar ON a.session_code = ar.session_code
            WHERE c.class_code = ?
            GROUP BY c.id
        """, (class_code,))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'class_name': result[0],
                'teacher_username': result[1],
                'created_at': result[2],
                'total_members': result[3],
                'total_sessions': result[4],
                'total_attendance_records': result[5]
            }
        return None
    except Exception as e:
        print(f"获取班级统计失败: {str(e)}")
        return None
# 生成唯一代码
def generate_unique_code(prefix="", length=8):
    """生成唯一的班级代码或签到代码"""
    timestamp = str(int(time.time()))[-4:]
    random_str = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:length-4]
    return f"{prefix}{timestamp}{random_str}".upper()

# 数据库操作函数
def create_classroom(teacher_username, class_name, description="", max_students=50):
    """创建新班级"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 检查教师是否有可用的班级名额
        c.execute("""
            SELECT COUNT(*) FROM classrooms 
            WHERE teacher_username = ? AND is_active = TRUE
        """, (teacher_username,))
        current_classes = c.fetchone()[0]
        
        # 获取教师订阅计划
        c.execute("""
            SELECT sp.max_classes 
            FROM teacher_subscriptions ts
            JOIN subscription_plans sp ON ts.plan_code = sp.plan_code
            WHERE ts.teacher_username = ? 
            AND ts.payment_status = 'active'
            AND ts.end_date > ?
        """, (teacher_username, to_beijing_time_str()[:10]))
        
        result = c.fetchone()
        if result:
            max_allowed_classes = result[0]
        else:
            # 如果没有有效订阅，使用免费套餐
            max_allowed_classes = 10000000000
        
        if current_classes >= max_allowed_classes:
            return False, f"已达到班级数量上限({max_allowed_classes}个)，请升级套餐"
        
        # 生成班级代码
        class_code = generate_unique_code("CLS", 8)
        
        # 创建班级
        created_at = to_beijing_time_str()
        c.execute('''
            INSERT INTO classrooms 
            (class_code, class_name, teacher_username, description, max_students, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (class_code, class_name, teacher_username, description, max_students, created_at))
        
        # 将教师自动加入班级
        c.execute('''
            INSERT INTO classroom_members 
            (class_code, student_username, joined_at, role)
            VALUES (?, ?, ?, 'teacher')
        ''', (class_code, teacher_username, created_at))
        
        conn.commit()
        conn.close()
        return True, class_code
    except Exception as e:
        return False, f"创建班级失败: {str(e)}"

def join_classroom(student_username, class_code):
    """学生加入班级"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 检查班级是否存在且活跃
        c.execute("""
            SELECT class_name, max_students, is_active 
            FROM classrooms 
            WHERE class_code = ?
        """, (class_code,))
        
        class_info = c.fetchone()
        if not class_info:
            return False, "班级不存在"
        
        if not class_info[2]:
            return False, "班级已关闭"
        
        # 检查班级是否已满
        c.execute("""
            SELECT COUNT(*) FROM classroom_members 
            WHERE class_code = ? AND status = 'active'
        """, (class_code,))
        
        current_students = c.fetchone()[0]
        max_students = class_info[1]
        
        if current_students >= max_students:
            return False, "班级人数已满"
        
        # 检查是否已经加入
        c.execute("""
            SELECT id FROM classroom_members 
            WHERE class_code = ? AND student_username = ?
        """, (class_code, student_username))
        
        if c.fetchone():
            return False, "您已加入该班级"
        
        # 加入班级
        joined_at = to_beijing_time_str()
        c.execute('''
            INSERT INTO classroom_members 
            (class_code, student_username, joined_at)
            VALUES (?, ?, ?)
        ''', (class_code, student_username, joined_at))
        
        conn.commit()
        conn.close()
        return True, "成功加入班级"
    except Exception as e:
        return False, f"加入班级失败: {str(e)}"

def create_attendance_session(class_code, teacher_username, session_name, 
                             start_time, end_time, duration_minutes=10,
                             location_name=None, attendance_type='standard'):
    """创建签到活动"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 生成签到代码
        session_code = generate_unique_code("ATT", 6)
        
        # 获取班级总人数
        c.execute("""
            SELECT COUNT(*) FROM classroom_members 
            WHERE class_code = ? AND status = 'active' AND role = 'student'
        """, (class_code,))
        
        total_students = c.fetchone()[0]
        
        # 创建签到活动
        created_at = to_beijing_time_str()
        c.execute('''
            INSERT INTO attendance_sessions 
            (session_code, class_code, session_name, teacher_username, 
             start_time, end_time, duration_minutes, location_name,
             attendance_type, status, created_at, total_students)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'scheduled', ?, ?)
        ''', (session_code, class_code, session_name, teacher_username,
              start_time, end_time, duration_minutes, location_name,
              attendance_type, created_at, total_students))
        
        conn.commit()
        conn.close()
        return True, session_code
    except Exception as e:
        return False, f"创建签到失败: {str(e)}"

def check_in_attendance(session_code, student_username, check_in_method='manual',
                       device_info=None, ip_address=None):
    """学生签到 - 修改：放宽签到条件"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 检查签到活动是否存在
        c.execute("""
            SELECT class_code, start_time, end_time, status 
            FROM attendance_sessions 
            WHERE session_code = ?
        """, (session_code,))
        
        session_info = c.fetchone()
        if not session_info:
            return False, "签到活动不存在"
        
        # 修改：放宽签到条件，允许非active状态也签到
        # if session_info[3] != 'active':
        #     return False, "签到活动未激活"
        
        class_code = session_info[0]
        start_time = from_beijing_time_str(session_info[1])
        end_time = from_beijing_time_str(session_info[2])
        current_time = get_beijing_time()
        
        # 检查时间是否在有效范围内
        if current_time < start_time:
            return False, "签到活动尚未开始"
        if current_time > end_time:
            # 修改：允许超时15分钟内签到
            time_difference = (current_time - end_time).total_seconds() / 60
            if time_difference > 15:
                return False, "签到活动已结束"
        
        # 检查学生是否在班级中
        c.execute("""
            SELECT id FROM classroom_members 
            WHERE class_code = ? AND student_username = ? AND status = 'active'
        """, (class_code, student_username))
        
        if not c.fetchone():
            return False, "您不在该班级中"
        
        # 检查是否已经签到
        c.execute("""
            SELECT id FROM attendance_records 
            WHERE session_code = ? AND student_username = ?
        """, (session_code, student_username))
        
        if c.fetchone():
            return False, "您已经签到过了"
        
        # 判断是否迟到
        is_late = current_time > start_time + timedelta(minutes=5)
        points_earned = 5 if is_late else 10
        
        # 记录签到
        check_in_time = to_beijing_time_str(current_time)
        c.execute('''
            INSERT INTO attendance_records 
            (session_code, student_username, class_code, check_in_time,
             check_in_method, device_info, ip_address, is_late, points_earned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_code, student_username, class_code, check_in_time,
              check_in_method, device_info, ip_address, is_late, points_earned))
        
        # 更新签到统计
        c.execute("""
            UPDATE attendance_sessions 
            SET attended_students = attended_students + 1 
            WHERE session_code = ?
        """, (session_code,))
        
        conn.commit()
        conn.close()
        return True, "签到成功"
    except Exception as e:
        return False, f"签到失败: {str(e)}"

def get_teacher_classes(teacher_username):
    """获取教师创建的所有班级"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        c.execute("""
            SELECT c.class_code, c.class_name, c.description, 
                   c.created_at, c.max_students, c.is_active,
                   COUNT(DISTINCT cm.student_username) as student_count,
                   COUNT(DISTINCT a.id) as session_count
            FROM classrooms c
            LEFT JOIN classroom_members cm ON c.class_code = cm.class_code AND cm.role = 'student'
            LEFT JOIN attendance_sessions a ON c.class_code = a.class_code
            WHERE c.teacher_username = ?
            GROUP BY c.id
            ORDER BY c.created_at DESC
        """, (teacher_username,))
        
        classes = []
        columns = [description[0] for description in c.description]
        
        for row in c.fetchall():
            classes.append(dict(zip(columns, row)))
        
        conn.close()
        return classes
    except Exception as e:
        print(f"获取班级失败: {str(e)}")
        return []

def get_student_classes(student_username):
    """获取学生加入的所有班级"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        c.execute("""
            SELECT c.class_code, c.class_name, c.description, 
                   c.teacher_username, cm.joined_at,
                   COUNT(DISTINCT cm2.student_username) as total_students,
                   COUNT(DISTINCT a.id) as total_sessions
            FROM classroom_members cm
            JOIN classrooms c ON cm.class_code = c.class_code
            LEFT JOIN classroom_members cm2 ON c.class_code = cm2.class_code
            LEFT JOIN attendance_sessions a ON c.class_code = a.class_code
            WHERE cm.student_username = ? AND cm.status = 'active'
            GROUP BY c.id
            ORDER BY cm.joined_at DESC
        """, (student_username,))
        
        classes = []
        columns = [description[0] for description in c.description]
        
        for row in c.fetchall():
            classes.append(dict(zip(columns, row)))
        
        conn.close()
        return classes
    except Exception as e:
        print(f"获取学生班级失败: {str(e)}")
        return []

def get_class_attendance_sessions(class_code):
    """获取班级的所有签到活动"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        c.execute("""
            SELECT session_code, session_name, start_time, end_time,
                   duration_minutes, location_name, attendance_type,
                   status, total_students, attended_students,
                   created_at
            FROM attendance_sessions
            WHERE class_code = ?
            ORDER BY start_time DESC
        """, (class_code,))
        
        sessions = []
        columns = [description[0] for description in c.description]
        
        for row in c.fetchall():
            sessions.append(dict(zip(columns, row)))
        
        conn.close()
        return sessions
    except Exception as e:
        print(f"获取签到活动失败: {str(e)}")
        return []

def get_attendance_details(session_code):
    """获取签到活动的详细信息"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 获取签到活动基本信息
        c.execute("""
            SELECT * FROM attendance_sessions WHERE session_code = ?
        """, (session_code,))
        
        session_info = c.fetchone()
        columns = [description[0] for description in c.description]
        session_dict = dict(zip(columns, session_info)) if session_info else None
        
        # 获取签到记录
        c.execute("""
            SELECT ar.*, u.username 
            FROM attendance_records ar
            JOIN users u ON ar.student_username = u.username
            WHERE ar.session_code = ?
            ORDER BY ar.check_in_time
        """, (session_code,))
        
        records = []
        columns = [description[0] for description in c.description]
        
        for row in c.fetchall():
            records.append(dict(zip(columns, row)))
        
        conn.close()
        return session_dict, records
    except Exception as e:
        print(f"获取签到详情失败: {str(e)}")
        return None, []

# 现代化CSS样式（与主页保持一致）
def apply_modern_css():
    st.markdown("""
    <style>
    /* 现代化米色主题变量 */
    :root {
        --primary-red: #dc2626;
        --dark-red: #b91c1c;
        --accent-red: #ef4444;
        --light-red: #fee2e2;
        --beige-light: #fefaf0;
        --beige-medium: #fdf6e3;
        --beige-dark: #faf0d9;
        --gold: #d4af37;
        --light-gold: #fef3c7;
        --dark-text: #1f2937;
        --light-text: #6b7280;
        --card-shadow: 0 10px 25px -5px rgba(220, 38, 38, 0.1), 0 8px 10px -6px rgba(220, 38, 38, 0.1);
        --hover-shadow: 0 25px 50px -12px rgba(220, 38, 38, 0.25);
    }
    
    /* 整体页面背景 - 米色渐变 */
    .stApp {
        background: linear-gradient(135deg, #fefaf0 0%, #fdf6e3 50%, #faf0d9 100%);
    }
    /* 侧边栏样式 - 米色渐变 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #fdf6e3 0%, #faf0d9 50%, #f5e6c8 100%) !important;
    }
    
    /* 现代化头部 */
    .modern-header {
        background: linear-gradient(135deg, var(--primary-red) 0%, var(--dark-red) 100%);
        color: white;
        padding: 30px;
        text-align: center;
        border-radius: 20px;
        margin: 20px 0 30px 0;
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .class-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: var(--card-shadow);
        border-left: 4px solid var(--primary-red);
        transition: all 0.3s ease;
    }
    
    .class-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--hover-shadow);
    }
    
    .attendance-card {
        background: linear-gradient(135deg, #fff, #fef2f2);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border: 2px solid var(--primary-red);
        position: relative;
        overflow: hidden;
    }
    
    .attendance-card.active {
        border-color: #10b981;
        background: linear-gradient(135deg, #fff, #f0fdf4);
    }
    
    .attendance-card.expired {
        border-color: #9ca3af;
        background: linear-gradient(135deg, #fff, #f3f4f6);
        opacity: 0.8;
    }
    
    .subscription-card {
        background: linear-gradient(135deg, #fff, #fefaf0);
        border-radius: 15px;
        padding: 30px;
        margin: 15px 0;
        border: 3px solid var(--gold);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .subscription-card.featured {
        border-color: var(--primary-red);
        transform: scale(1.05);
        z-index: 2;
    }
    
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }
    
    .badge-danger {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
    }
    
    .badge-info {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
    }
    
    .qr-code-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        display: inline-block;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 2px solid var(--primary-red);
    }
    
    .timer-container {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: var(--primary-red);
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: var(--card-shadow);
        margin-bottom: 20px;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--primary-red);
        margin: 10px 0;
    }
    
    .stat-label {
        color: var(--light-text);
        font-size: 0.9rem;
    }
    
    .feature-list {
        list-style: none;
        padding: 0;
        margin: 15px 0;
    }
    
    .feature-list li {
        padding: 8px 0;
        padding-left: 25px;
        position: relative;
    }
    
    .feature-list li:before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #10b981;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
# 现代化实验室CSS（增强版）
st.markdown("""
<style>
:root {
    --primary-red: #dc2626;
    --dark-red: #b91c1c;
    --light-red: #fef2f2;
    --accent-red: #ef4444;
    --gold: #f59e0b;
    --beige-light: #fefaf0;
    --beige-medium: #fdf6e3;
    --beige-dark: #faf0d9;
}

/* 整体页面背景 - 米色渐变 */
.stApp {
    background: linear-gradient(135deg, #fefaf0 0%, #fdf6e3 50%, #faf0d9 100%);
}

.lab-header {
    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
    color: white;
    padding: 40px 30px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 8px 32px rgba(220, 38, 38, 0.3);
    border: 3px solid #f59e0b;
}

.lab-title {
    font-size: 2.8rem;
    margin-bottom: 10px;
    font-weight: bold;
}

.ideology-card {
    background: linear-gradient(135deg, #fef2f2, #fff);
    padding: 25px;
    border-radius: 15px;
    border: 2px solid #dc2626;
    margin: 20px 0;
    box-shadow: 0 6px 12px rgba(220, 38, 38, 0.15);
}

.info-card {
    background: linear-gradient(135deg, #fef2f2, #ffecec);
    padding: 20px;
    border-radius: 12px;
    border-left: 4px solid #dc2626;
    margin: 15px 0;
    box-shadow: 0 4px 6px rgba(220, 38, 38, 0.1);
}

.image-container {
    border: 3px solid #dc2626;
    border-radius: 12px;
    padding: 15px;
    background: white;
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.image-container:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(220, 38, 38, 0.2);
}

/* 现代化按钮 */
.stButton button {
    background: linear-gradient(135deg, #ffffff, #fef2f2);
    color: #dc2626;
    border: 2px solid #dc2626;
    padding: 14px 28px;
    border-radius: 50px;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);
    transition: all 0.3s ease;
    font-size: 1rem;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
}
    
.stButton button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(220, 38, 38, 0.1), transparent);
    transition: left 0.6s;
}
.stButton button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(220, 38, 38, 0.1), transparent);
    transition: left 0.6s;
}
   
.stButton button:hover {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: white;
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(220, 38, 38, 0.4);
    border-color: #dc2626;
}
    

/* 特殊按钮样式 - 金色边框 */
.stButton button.gold-btn {
    border: 2px solid #d4af37;
    color: #d4af37;
    background: linear-gradient(135deg, #fffdf6, #fefaf0);
}
    
.stButton button.gold-btn:hover {
    background: linear-gradient(135deg, #d4af37, #b8941f);
    color: white;
    border-color: #d4af37;
} border-color: #d4af37;
}
/* 整体页面内容区域 */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    background: linear-gradient(135deg, #fefaf0 0%, #fdf6e3 50%, #faf0d9 100%);
}

/* 侧边栏样式 - 米色渐变 */
section[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #fdf6e3 0%, #faf0d9 50%, #f5e6c8 100%) !important;
}

.file-item {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 10px;
    margin: 5px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.file-item:hover {
    background: #e9ecef;
}

/* 标签页样式 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: linear-gradient(135deg, #fdf6e3, #faf0d9);
    padding: 10px;
    border-radius: 15px;
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.3s ease;
    background: white;
    border: 2px solid #e5e7eb;
}

.stTabs [data-baseweb="tab"]:hover {
    background: #fef2f2;
    border-color: #dc2626;
    color: #dc2626;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
    color: white !important;
    border-color: #dc2626 !important;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

/* 滑动条样式 */
.stSlider [data-baseweb="slider"] [aria-valuetext] {
    color: #dc2626 !important;
}

/* 文件上传区域 */
.stFileUploader {
    border: 2px dashed #dc2626 !important;
    border-radius: 12px !important;
    background: #fef2f2 !important;
}

/* 特效样式 */
.effect-preview {
    position: relative;
    overflow: hidden;
    border-radius: 10px;
    margin: 10px 0;
}

.effect-preview img {
    transition: transform 0.5s ease;
}

.effect-preview:hover img {
    transform: scale(1.05);
}

/* 进度条样式 */
.stProgress > div > div > div > div {
    background-color: #dc2626 !important;
}

/* 警告框样式 */
.stAlert {
    border-radius: 12px !important;
    border: 2px solid !important;
}

/* 实验卡片 */
.experiment-card {
    background: linear-gradient(135deg, #ffffff, #fef2f2);
    border: 2px solid #e5e7eb;
    border-radius: 15px;
    padding: 25px;
    margin: 20px 0;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.experiment-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 5px;
    height: 100%;
    background: linear-gradient(to bottom, #dc2626, #f59e0b);
}

.experiment-card:hover {
    border-color: #dc2626;
    box-shadow: 0 10px 25px rgba(220, 38, 38, 0.15);
    transform: translateY(-3px);
}

.experiment-number {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.2rem;
    margin-bottom: 15px;
}

/* 参数面板 */
.param-panel {
    background: linear-gradient(135deg, #f8f9fa, #ffffff);
    border: 2px solid #e9ecef;
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
}

.param-panel h4 {
    color: #dc2626;
    border-bottom: 2px solid #f59e0b;
    padding-bottom: 10px;
    margin-bottom: 15px;
}

/* 比较视图 */
.comparison-view {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin: 20px 0;
}

.comparison-box {
    text-align: center;
    padding: 15px;
    background: white;
    border-radius: 10px;
    border: 2px solid #e5e7eb;
}

.comparison-box h5 {
    margin-bottom: 10px;
    color: #333;
    font-weight: 600;
}

/* 统计卡片增强 */
.stats-card {
    background: linear-gradient(135deg, #ffffff, #fef2f2);
    padding: 25px;
    border-radius: 15px;
    border: 2px solid #dc2626;
    text-align: center;
    margin: 10px;
    position: relative;
    overflow: hidden;
}

.stats-card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(220, 38, 38, 0.1), transparent);
    transform: rotate(45deg);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { transform: rotate(45deg) translateX(-100%); }
    100% { transform: rotate(45deg) translateX(100%); }
}

.stats-number {
    font-size: 2.5rem;
    font-weight: bold;
    color: #dc2626;
    margin: 15px 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stats-label {
    font-size: 0.9rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* 状态徽章增强 */
.status-badge {
    padding: 8px 20px;
    border-radius: 25px;
    font-size: 0.9rem;
    font-weight: bold;
    display: inline-block;
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.status-pending {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    color: #d97706;
    border: 2px solid #f59e0b;
}

.status-graded {
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    color: #059669;
    border: 2px solid #10b981;
}

.status-returned {
    background: linear-gradient(135deg, #fee2e2, #fca5a5);
    color: #dc2626;
    border: 2px solid #ef4444;
}

/* 教师评分卡片增强 */
.grading-card {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    padding: 25px;
    border-radius: 15px;
    border: 2px solid #0ea5e9;
    margin: 15px 0;
    box-shadow: 0 4px 6px rgba(14, 165, 233, 0.2);
    position: relative;
}

.grading-card::before {
    content: '👨‍🏫';
    position: absolute;
    top: 10px;
    right: 10px;
    font-size: 1.5rem;
    opacity: 0.3;
}

/* 提交成功特效增强 */
.submission-success {
    text-align: center;
    padding: 50px;
    background: linear-gradient(135deg, #dcfce7, #bbf7d0);
    border-radius: 20px;
    border: 4px solid #22c55e;
    margin: 20px 0;
    animation: celebrate 2s ease-in-out;
    position: relative;
    overflow: hidden;
}

.submission-success::before {
    content: '🎉';
    font-size: 4rem;
    position: absolute;
    top: 20px;
    left: 20px;
    opacity: 0.3;
}

.submission-success::after {
    content: '✨';
    font-size: 3rem;
    position: absolute;
    bottom: 20px;
    right: 20px;
    opacity: 0.3;
}

@keyframes celebrate {
    0% { transform: scale(0.8); opacity: 0; }
    50% { transform: scale(1.05); opacity: 1; }
    100% { transform: scale(1); opacity: 1; }
}

/* 颜色通道样式 */
.channel-display {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin: 20px 0;
}

.channel-box {
    text-align: center;
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-weight: bold;
}

.channel-red { background: linear-gradient(135deg, #ef4444, #dc2626); }
.channel-green { background: linear-gradient(135deg, #10b981, #059669); }
.channel-blue { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.channel-gray { background: linear-gradient(135deg, #6b7280, #4b5563); }
/* 提交记录卡片 */
.submission-card {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.submission-card:hover {
    border-color: #dc2626;
    box-shadow: 0 6px 12px rgba(220, 38, 38, 0.2);
    transform: translateY(-2px);
}

/* 特效预览网格 */
.effects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.effect-item {
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    cursor: pointer;
}

.effect-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

.effect-thumb {
    height: 150px;
    overflow: hidden;
}

.effect-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.effect-item:hover .effect-thumb img {
    transform: scale(1.1);
}

.effect-info {
    padding: 15px;
    text-align: center;
}

.effect-info h5 {
    margin: 0;
    color: #333;
}

.effect-info p {
    margin: 5px 0 0 0;
    color: #666;
    font-size: 0.9rem;
}
/* 状态徽章 */
.status-badge {
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: bold;
    display: inline-block;
}

.status-pending {
    background: #fef3c7;
    color: #d97706;
    border: 1px solid #f59e0b;
}

.status-graded {
    background: #d1fae5;
    color: #059669;
    border: 1px solid #10b981;
}

.status-returned {
    background: #fee2e2;
    color: #dc2626;
    border: 1px solid #ef4444;
}

/* 统计卡片 */
.stats-card {
    background: linear-gradient(135deg, #fef2f2, #fff);
    padding: 20px;
    border-radius: 12px;
    border: 2px solid #dc2626;
    text-align: center;
    margin: 10px;
}

.stats-number {
    font-size: 2rem;
    font-weight: bold;
    color: #dc2626;
    margin: 10px 0;
}

.stats-label {
    font-size: 0.9rem;
    color: #666;
}

/* 烟花特效容器 */
.fireworks-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 9999;
}

/* 教师评分卡片 */
.grading-card {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    padding: 20px;
    border-radius: 12px;
    border: 2px solid #0ea5e9;
    margin: 15px 0;
    box-shadow: 0 4px 6px rgba(14, 165, 233, 0.2);
}

/* 提交特效 */
.submission-success {
    text-align: center;
    padding: 40px;
    background: linear-gradient(135deg, #dcfce7, #bbf7d0);
    border-radius: 20px;
    border: 4px solid #22c55e;
    margin: 20px 0;
    animation: celebrate 2s ease-in-out;
}

@keyframes celebrate {
    0% { transform: scale(0.8); opacity: 0; }
    50% { transform: scale(1.05); opacity: 1; }
    100% { transform: scale(1); opacity: 1; }
}

.confetti {
    position: fixed;
    width: 10px;
    height: 10px;
    background: #ff0000;
    opacity: 0.7;
    animation: fall linear forwards;
}

@keyframes fall {
    to {
        transform: translateY(100vh) rotate(360deg);
        opacity: 0;
    }
}
</style>
""", unsafe_allow_html=True)
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; 
            padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px;
            box-shadow: 0 6px 12px rgba(220, 38, 38, 0.3);'>
            <h3 style='margin: 0;'>🏫 班级管理</h3>
            <p style='margin: 10px 0 0 0; font-size: 1rem;'>智能签到 · 高效教学</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 快速导航
        st.markdown("### 🧭 快速导航")
        
        if st.button("🏠 返回首页", width='stretch'):
            st.switch_page("main.py")
        
        if st.session_state.logged_in:
            role = st.session_state.role
            
            if role == "teacher":
                if st.button("📊 教师控制台", width='stretch'):
                    st.session_state.current_page = "teacher_dashboard"
                    st.rerun()
                if st.button("➕ 创建班级", width='stretch'):
                    st.session_state.current_page = "create_classroom"
                    st.rerun()
                if st.button("📝 创建签到", width='stretch'):
                    st.session_state.current_page = "create_attendance"
                    st.rerun()
            
            elif role == "student":
                if st.button("🎯 我的班级", width='stretch'):
                    st.session_state.current_page = "student_classes"
                    st.rerun()
                if st.button("📱 在线签到", width='stretch'):
                    st.session_state.current_page = "attendance_checkin"
                    st.rerun()
                if st.button("🔍 查找班级", width='stretch'):
                    st.session_state.current_page = "find_classroom"
                    st.rerun()
        
        # 平台特色
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fee2e2, #fecaca); padding: 25px; 
                    border-radius: 15px; border-left: 5px solid #dc2626; margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);'>
            <h4 style='color: #dc2626;'>🎯 功能特色</h4>
            <ul style='padding-left: 20px; color: #7f1d1d;'>
                <li style='color: #dc2626;'>🏫 智能分班管理</li>
                <li style='color: #dc2626;'>📱 多种签到方式</li>
                <li style='color: #dc2626;'>📊 实时数据分析</li>
                <li style='color: #dc2626;'>🔒 安全可靠</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 签到状态
        if st.session_state.logged_in:
            try:
                conn = sqlite3.connect('image_processing_platform.db')
                c = conn.cursor()
                
                username = st.session_state.username
                role = st.session_state.role
                
                if role == "student":
                    # 学生签到统计
                    c.execute("""
                        SELECT 
                            COUNT(DISTINCT session_code) as total_sessions,
                            COUNT(*) as attended_sessions,
                            AVG(points_earned) as avg_points
                        FROM attendance_records 
                        WHERE student_username = ?
                    """, (username,))
                    
                    result = c.fetchone()
                    if result:
                        total_sessions, attended_sessions, avg_points = result
                        
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #f0fdf4, #dcfce7); padding: 20px; 
                                    border-radius: 12px; border: 2px solid #10b981; margin-bottom: 20px;'>
                            <h5 style='color: #10b981; text-align: center;'>📊 我的签到</h5>
                            <p style='color: #065f46; text-align: center; font-size: 0.9rem;'>
                            📅 总活动: {total}<br>
                            ✅ 已签到: {attended}<br>
                            ⭐ 平均分: {points:.1f}分
                            </p>
                        </div>
                        """.format(total=total_sessions or 0, attended=attended_sessions or 0, points=avg_points or 0), 
                        unsafe_allow_html=True)
                
                conn.close()
            except:
                pass
        
        # 今日提示
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fef3c7, #fde68a); padding: 20px; 
                    border-radius: 12px; border: 2px solid #d4af37; margin-bottom: 20px;'>
            <h5 style='color: #b45309; text-align: center;'>💡 使用提示</h5>
            <p style='font-size: 0.85rem; color: #78350f; text-align: center;'>
            教师可创建班级和签到活动<br>
            学生可加入班级并参与签到<br>
            签到可获得积分奖励
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 系统信息
        st.markdown("---")
        st.markdown("**📊 系统信息**")
        st.text(f"北京时间: {get_beijing_time().strftime('%Y-%m-%d %H:%M')}")
        st.text("状态: 🟢 运行中")
        st.text("版本: v1.0.0")

def render_teacher_dashboard():
    """教师控制台"""
    st.markdown("""
    <div class='modern-header'>
        <h2>👨‍🏫 教师控制台</h2>
        <p>管理班级、创建签到、查看统计</p>
    </div>
    """, unsafe_allow_html=True)
    
    username = st.session_state.username




    # ============ 修改这里：获取真实的统计数据 ============
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 1. 获取班级数量
        c.execute("""
            SELECT COUNT(*) FROM classrooms 
            WHERE teacher_username = ? AND is_active = TRUE
        """, (username,))
        total_classes = c.fetchone()[0] or 0
        
        # 2. 获取总学生数
        c.execute("""
            SELECT COUNT(DISTINCT cm.student_username) 
            FROM classrooms c
            JOIN classroom_members cm ON c.class_code = cm.class_code
            WHERE c.teacher_username = ? 
            AND c.is_active = TRUE
            AND cm.role = 'student'
            AND cm.status = 'active'
        """, (username,))
        total_students = c.fetchone()[0] or 0
        
        # 3. 获取签到活动总数
        c.execute("""
            SELECT COUNT(*) 
            FROM attendance_sessions
            WHERE teacher_username = ?
        """, (username,))
        total_sessions = c.fetchone()[0] or 0
        
        # 4. 获取平均到课率

        c.execute("""
            SELECT 
                session_code,
                total_students,
                attended_students
            FROM attendance_sessions
            WHERE teacher_username = ?
            AND status = 'completed'
            AND total_students > 0
        """, (username,))
        
        sessions = c.fetchall()
        
        if sessions:
            total_attendance_rate = 0
            valid_sessions = 0
            
            for session in sessions:
                session_code, total_students, attended_students = session
                if total_students > 0:
                    rate = (attended_students / total_students) * 100
                    total_attendance_rate += rate
                    valid_sessions += 1
            
            if valid_sessions > 0:
                avg_attendance_rate = round(total_attendance_rate / valid_sessions, 1)
            else:
                avg_attendance_rate = 0
        else:
            avg_attendance_rate = 0        
        conn.close()
        
    except Exception as e:
        # 如果出错，使用默认值
        print(f"获取统计数据失败: {str(e)}")
        total_classes = 0
        total_students = 0
        total_sessions = 0
        avg_attendance_rate = 0    
    # 统计卡片
    col1, col2, col3= st.columns(3)
    
    # 使用f-string或format方法
    with col1:
        html1 = f"""
        <div class='stat-card'>
            <div>🏫</div>
            <div class='stat-number'>{total_classes}</div>
            <div class='stat-label'>我的班级</div>
        </div>
        """
        st.markdown(html1, unsafe_allow_html=True)
    
    with col2:
        html2 = f"""
        <div class='stat-card'>
            <div>👥</div>
            <div class='stat-number'>{total_students}</div>
            <div class='stat-label'>总学生数</div>
        </div>
        """
        st.markdown(html2, unsafe_allow_html=True)
    
    with col3:
        html3 = f"""
        <div class='stat-card'>
            <div>📝</div>
            <div class='stat-number'>{total_sessions}</div>
            <div class='stat-label'>签到活动</div>
        </div>
        """
        st.markdown(html3, unsafe_allow_html=True)
    
    # 获取教师班级数据
    teacher_classes = get_teacher_classes(username)
    
    if teacher_classes:
        # 显示班级列表
        st.markdown("### 📚 我的班级")
        
        for class_info in teacher_classes:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='padding: 15px;'>
                        <h4 style='margin: 0; color: #dc2626;'>{class_info['class_name']}</h4>
                        <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                        班级代码: <strong>{class_info['class_code']}</strong>
                        </p>
                        <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                        {class_info['description'] or '暂无描述'}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='padding: 15px;'>
                        <p style='margin: 5px 0;'>👥 学生: {class_info['student_count']}/{class_info['max_students']}</p>
                        <p style='margin: 5px 0;'>📝 签到: {class_info['session_count']}次</p>
                        <p style='margin: 5px 0;'>📅 创建: {class_info['created_at'][:10]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if st.button("管理", key=f"manage_{class_info['class_code']}"):
                        st.session_state.selected_class = class_info['class_code']
                        st.session_state.current_page = "class_management"
                        st.rerun()
        
        # 快速操作
        st.markdown("---")
        st.markdown("### ⚡ 快速操作")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ 创建新班级", width='stretch'):
                st.session_state.current_page = "create_classroom"
                st.rerun()
        
        with col2:
            if st.button("📝 创建签到", width='stretch'):
                st.session_state.current_page = "create_attendance"
                st.rerun()
        
    else:
        # 没有班级的提示
        st.info("您还没有创建任何班级，点击下方按钮创建第一个班级吧！")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ 创建我的第一个班级", width='stretch', type="primary"):
                st.session_state.current_page = "create_classroom"
                st.rerun()
def update_classroom_info(class_code, teacher_username, class_name=None, description=None, max_students=None):
    """
    更新班级信息
    
    Args:
        class_code: 班级代码
        teacher_username: 教师用户名（用于权限验证）
        class_name: 新的班级名称（可选）
        description: 新的班级描述（可选）
        max_students: 新的最大学生数（可选）
    
    Returns:
        (success, message): 成功标志和信息
    """
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 验证教师权限
        c.execute("""
            SELECT teacher_username, class_name FROM classrooms 
            WHERE class_code = ? AND is_active = TRUE
        """, (class_code,))
        
        result = c.fetchone()
        if not result:
            conn.close()
            return False, "班级不存在或已被删除"
        
        current_teacher = result[0]
        current_class_name = result[1]
        
        if current_teacher != teacher_username:
            conn.close()
            return False, "只有创建教师可以修改班级信息"
        
        # 构建更新语句
        update_fields = []
        update_values = []
        
        if class_name:
            update_fields.append("class_name = ?")
            update_values.append(class_name)
        
        if description is not None:  # 允许空描述
            update_fields.append("description = ?")
            update_values.append(description)
        
        if max_students:
            # 检查新的人数限制是否小于当前人数
            c.execute("""
                SELECT COUNT(*) FROM classroom_members 
                WHERE class_code = ? AND status = 'active'
            """, (class_code,))
            
            current_student_count = c.fetchone()[0]
            
            if max_students < current_student_count:
                conn.close()
                return False, f"当前已有 {current_student_count} 名学生，最大学生数不能小于当前人数"
            
            update_fields.append("max_students = ?")
            update_values.append(max_students)
        
        if not update_fields:
            conn.close()
            return True, "没有需要更新的信息"
        
        # 执行更新
        update_query = f"""
            UPDATE classrooms 
            SET {', '.join(update_fields)}
            WHERE class_code = ?
        """
        
        update_values.append(class_code)
        c.execute(update_query, tuple(update_values))
        
        conn.commit()
        conn.close()
        
        # 记录修改日志
        changes = []
        if class_name:
            changes.append(f"名称: {current_class_name} → {class_name}")
        if description is not None:
            changes.append("描述已更新")
        if max_students:
            changes.append(f"最大人数: {max_students}")
        
        log_entry = f"{to_beijing_time_str()} - 教师 {teacher_username} 更新了班级 {class_code}: {', '.join(changes)}"
        print(log_entry)
        
        return True, "班级信息更新成功"
        
    except sqlite3.Error as e:
        return False, f"数据库错误: {str(e)}"
    except Exception as e:
        return False, f"更新班级信息失败: {str(e)}"
def render_create_classroom():
    """创建班级页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>➕ 创建新班级</h2>
        <p>创建您的第一个教学班级</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 移除表单结构，使用独立输入
    col1, col2 = st.columns(2)
    
    with col1:
        class_name = st.text_input("📝 班级名称", 
                                  placeholder="例如：2025春季数字图像处理班",
                                  key="class_name_input")
    
    with col2:
        max_students = st.number_input("👥 最大学生数", 
                                     min_value=1, 
                                     max_value=500, 
                                     value=50,
                                     key="max_students_input")
    
    description = st.text_area("📋 班级描述",
                             placeholder="请输入班级介绍、课程目标等信息...",
                             height=100,
                             key="description_input")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        create_btn = st.button("🚀 创建班级", width='stretch', type="primary")
    
    with col_btn2:
        cancel_btn = st.button("❌ 取消", width='stretch')
    
    if cancel_btn:
        st.session_state.current_page = "teacher_dashboard"
        st.rerun()
    
    if create_btn:
        if class_name:
            with st.spinner("正在创建班级..."):
                success, result = create_classroom(
                    st.session_state.username,
                    class_name,
                    description,
                    max_students
                )
                
                if success:
                    st.success(f"🎉 班级创建成功！班级代码：**{result}**")
                    st.info("请将班级代码分享给学生，学生可以使用此代码加入班级")
                    
                    # 显示操作选项（不使用表单结构）
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🏫 前往班级管理", width='stretch', key="go_to_manage"):
                            st.session_state.selected_class = result
                            st.session_state.current_page = "class_management"
                            st.rerun()
                    
                    with col2:
                        if st.button("📝 立即创建签到", width='stretch', key="go_to_create_attendance"):
                            st.session_state.selected_class = result
                            st.session_state.current_page = "create_attendance"
                            st.rerun()
                else:
                    st.error(f"❌ {result}")
        else:
            st.warning("⚠️ 请输入班级名称")
def delete_classroom_enhanced(class_code, teacher_username, delete_type="soft"):
    """
    删除班级（增强版）
    
    Args:
        class_code: 班级代码
        teacher_username: 教师用户名
        delete_type: 删除类型
            - 'soft': 软删除（只标记为不活跃）
            - 'hard': 硬删除（删除所有相关数据）
    """
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 验证教师权限
        c.execute("""
            SELECT teacher_username, class_name FROM classrooms 
            WHERE class_code = ?
        """, (class_code,))
        
        result = c.fetchone()
        if not result:
            conn.close()
            return False, "班级不存在"
        
        if result[0] != teacher_username:
            conn.close()
            return False, "只有创建教师可以删除班级"
        
        class_name = result[1]
        
        if delete_type == "soft":
            # 软删除：更新班级状态
            c.execute("""
                UPDATE classrooms 
                SET is_active = FALSE 
                WHERE class_code = ?
            """, (class_code,))
            
            # 可选：更新成员状态
            # c.execute("""
            #     UPDATE classroom_members 
            #     SET status = 'deleted' 
            #     WHERE class_code = ?
            # """, (class_code,))
            
            message = f"班级 '{class_name}' 已标记为删除（不活跃状态）"
            
        elif delete_type == "hard":
            # 硬删除：删除所有相关数据
            # 注意：按照外键约束顺序删除
            
            # 1. 删除签到记录
            c.execute("""
                DELETE FROM attendance_records 
                WHERE session_code IN (
                    SELECT session_code FROM attendance_sessions WHERE class_code = ?
                )
            """, (class_code,))
            
            # 2. 删除签到活动
            c.execute("""
                DELETE FROM attendance_sessions WHERE class_code = ?
            """, (class_code,))
            
            # 3. 删除通知
            c.execute("""
                DELETE FROM class_notifications WHERE class_code = ?
            """, (class_code,))
            
            # 4. 删除班级成员
            c.execute("""
                DELETE FROM classroom_members WHERE class_code = ?
            """, (class_code,))
            
            # 5. 删除班级
            c.execute("""
                DELETE FROM classrooms WHERE class_code = ?
            """, (class_code,))
            
            message = f"班级 '{class_name}' 及相关数据已永久删除"
        
        else:
            conn.close()
            return False, "无效的删除类型"
        
        conn.commit()
        conn.close()
        
        # 记录删除日志（在实际应用中，可以记录到日志文件或数据库）
        log_entry = f"{to_beijing_time_str()} - 教师 {teacher_username} 删除了班级 {class_code} ({class_name}) - 类型: {delete_type}"
        print(log_entry)
        
        return True, message
        
    except sqlite3.IntegrityError as e:
        return False, f"数据库完整性错误: {str(e)}"
    except Exception as e:
        return False, f"删除班级失败: {str(e)}"
def render_class_management():
    """班级管理页面 - 修改：允许学生查看班级详情"""
    if 'selected_class' not in st.session_state:
        st.session_state.current_page = "teacher_dashboard"
        st.rerun()
    
    class_code = st.session_state.selected_class
    
    # 获取班级信息
    conn = sqlite3.connect('image_processing_platform.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT class_name, description, teacher_username, created_at 
        FROM classrooms 
        WHERE class_code = ?
    """, (class_code,))
    
    class_info = c.fetchone()
    
    if not class_info:
        st.error("班级不存在")
        return
    
    class_name, description, teacher_username, created_at = class_info
    
    # 检查当前用户是否有权限管理班级
    role = st.session_state.role
    username = st.session_state.username
    is_teacher = (role == "teacher" and username == teacher_username)
    
    # 获取班级成员
    c.execute("""
        SELECT cm.student_username, cm.joined_at, cm.role,
               (SELECT COUNT(*) FROM attendance_records ar 
                WHERE ar.student_username = cm.student_username 
                AND ar.class_code = ?) as attendance_count
        FROM classroom_members cm
        WHERE cm.class_code = ? AND cm.status = 'active'
        ORDER BY cm.joined_at
    """, (class_code, class_code))
    
    members = c.fetchall()
    
    # 获取签到活动
    c.execute("""
        SELECT session_code, session_name, start_time, end_time, 
               status, total_students, attended_students
        FROM attendance_sessions
        WHERE class_code = ?
        ORDER BY start_time DESC
        LIMIT 10
    """, (class_code,))
    
    sessions = c.fetchall()
    
    conn.close()
    
    st.markdown(f"""
    <div class='modern-header'>
        <h2>🏫 {class_name}</h2>
        <p>班级代码: <strong>{class_code}</strong> | 创建时间: {created_at[:10]}</p>
        <p>授课教师: {teacher_username} | 您的角色: {'教师' if is_teacher else '学生'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 根据用户角色显示不同的选项卡
    if is_teacher:
        # 教师端：显示完整功能
        tab1, tab2, tab3, tab4 = st.tabs(["👥 班级成员", "📝 签到活动", "📊 数据分析", "⚙️ 班级设置"])
    else:
        # 学生端：只显示查看功能
        tab1, tab2, tab3 = st.tabs(["👥 班级成员", "📝 签到活动", "📊 数据分析"])
    
    with tab1:
        st.markdown(f"### 👥 班级成员 ({len(members)}人)")
        
        if members:
            # 成员表格
            members_data = []
            for member in members:
                username, joined_at, role, attendance_count = member
                members_data.append({
                    "用户名": username,
                    "身份": "教师" if role == "teacher" else "学生",
                    "加入时间": joined_at[:10],
                    "参与签到": attendance_count or 0
                })
            
            df_members = pd.DataFrame(members_data)
            st.dataframe(df_members, width='stretch', hide_index=True)
            
            # 只有教师可以导出成员名单
            if is_teacher:
                csv = df_members.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 导出成员名单",
                    data=csv,
                    file_name=f"{class_code}_members.csv",
                    mime="text/csv",
                    width='stretch'
                )
        else:
            st.info("暂无班级成员")
        
        # 只有教师可以添加成员
        if is_teacher:
            st.markdown("---")
            st.markdown("### ➕ 添加成员")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_member = st.text_input("输入用户名添加成员", placeholder="请输入学生用户名", key="new_member_input")
            
            with col2:
                if st.button("添加", width='stretch', key="add_member_btn"):
                    if new_member:
                        success, msg = join_classroom(new_member, class_code)
                        if success:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        st.warning("请输入用户名")
    
    with tab2:
        st.markdown("### 📝 签到活动")
        
        if sessions:
            for session in sessions:
                session_code, session_name, start_time, end_time, status, total, attended = session
                
                start_dt = from_beijing_time_str(start_time)
                end_dt = from_beijing_time_str(end_time)
                
                attendance_rate = (attended / total * 100) if total > 0 else 0
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='padding: 15px; border-radius: 10px; background: #f9fafb;'>
                        <h4 style='margin: 0;'>{session_name}</h4>
                        <p style='margin: 5px 0; font-size: 0.9rem; color: #6b7280;'>
                        📅 {start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')}
                        </p>
                        <p style='margin: 5px 0; font-size: 0.9rem;'>
                        签到代码: <code>{session_code}</code>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    badge_class = 'badge-success' if status == 'completed' else 'badge-warning' if status == 'active' else 'badge-info'
                    badge_text = '已完成' if status == 'completed' else '进行中' if status == 'active' else '已计划'
                    
                    st.markdown(f"""
                    <div style='padding: 15px;'>
                        <p style='margin: 5px 0;'>👥 {attended}/{total}</p>
                        <p style='margin: 5px 0;'>📊 {attendance_rate:.1f}%</p>
                        <p style='margin: 5px 0;'>
                        <span class='badge {badge_class}'>
                            {badge_text}
                        </span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if st.button("详情", key=f"detail_{session_code}"):
                        st.session_state.selected_session = session_code
                        st.session_state.current_page = "attendance_detail"
                        st.rerun()
        else:
            st.info("暂无签到活动")
        
        # 只有教师可以创建签到
        if is_teacher:
            st.markdown("---")
            if st.button("➕ 创建新签到活动", width='stretch'):
                st.session_state.current_page = "create_attendance"
                st.rerun()
    
    with tab3:
        st.markdown("### 📊 数据分析")
        
        if sessions:
            # 创建简单的图表
            session_names = []
            attendance_rates = []
            
            for session in sessions:
                session_code, session_name, start_time, end_time, status, total, attended = session
                rate = (attended / total * 100) if total > 0 else 0
                
                session_names.append(session_name[:15] + "..." if len(session_name) > 15 else session_name)
                attendance_rates.append(rate)
            
            # 使用Plotly创建条形图
            fig = go.Figure(data=[
                go.Bar(
                    x=session_names,
                    y=attendance_rates,
                    marker_color=['#ef4444' if rate < 70 else '#f59e0b' if rate < 90 else '#10b981' for rate in attendance_rates]
                )
            ])
            
            fig.update_layout(
                title="各签到活动参与率",
                xaxis_title="签到活动",
                yaxis_title="参与率 (%)",
                yaxis=dict(range=[0, 100]),
                height=400
            )
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("暂无数据可分析")
    
    # 只有教师可以看到班级设置
    if is_teacher and 'tab4' in locals():
        with tab4:
            st.markdown("### ⚙️ 班级设置")
            
    # 只有教师可以看到班级设置
    if is_teacher and 'tab4' in locals():
        with tab4:

        
            # 使用独立输入
            new_class_name = st.text_input("班级名称", value=class_name, key="new_class_name")
            new_description = st.text_area("班级描述", value=description or "", height=100, key="new_description")
        







def render_create_attendance():
    """创建签到活动页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>📝 创建签到活动</h2>
        <p>为您的班级创建在线签到</p>
    </div>
    """, unsafe_allow_html=True)
    
    username = st.session_state.username
    
    # 获取教师的班级列表
    teacher_classes = get_teacher_classes(username)
    
    if not teacher_classes:
        st.warning("您还没有创建任何班级，请先创建班级")
        if st.button("🏫 去创建班级"):
            st.session_state.current_page = "create_classroom"
            st.rerun()
        return
    
    # 选择班级
    class_options = {c['class_code']: f"{c['class_name']} ({c['class_code']})" for c in teacher_classes}
    selected_class = st.selectbox("选择班级", options=list(class_options.keys()), 
                                 format_func=lambda x: class_options[x],
                                 key="class_select")
    
    # 使用独立输入，而不是表单
    col1, col2 = st.columns(2)
    
    with col1:
        session_name = st.text_input("📝 签到活动名称", 
                                    placeholder="例如：第1次课程签到",
                                    key="session_name_input")
    
    with col2:
        attendance_type = st.selectbox("📱 签到方式", 
                                      options=['standard'],
                                      format_func=lambda x: {
                                          'standard': '标准签到'

                                      }[x],
                                      key="attendance_type_select")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # 修复：使用正确的函数名 st.date_input 和 st.time_input
        date_val = st.date_input("📅 签到日期", 
                               value=get_beijing_time().date(),
                               min_value=get_beijing_time().date(),
                               key="date_input")
        time_val = st.time_input("⏰ 开始时间", 
                               value=(get_beijing_time() + timedelta(minutes=5)).time(),
                               key="time_input")
        start_time = datetime.combine(date_val, time_val)
    
    with col4:
        duration_minutes = st.number_input("⏱️ 签到时长(分钟)", 
                                         min_value=1, 
                                         max_value=180, 
                                         value=15,
                                         key="duration_input")
    
    end_time = start_time + timedelta(minutes=duration_minutes)
    location_name = st.text_input("📍 签到地点(可选)", 
                                 placeholder="例如：信息楼301教室",
                                 key="location_input")    
    
    st.info(f"签到时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')} 至 {end_time.strftime('%H:%M:%S')} (北京时间)")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        create_btn = st.button("🚀 创建签到", width='stretch', type="primary", key="create_attendance_btn")
    
    with col_btn2:
        cancel_btn = st.button("❌ 取消", width='stretch', key="cancel_attendance_btn")
    
    if cancel_btn:
        st.session_state.current_page = "teacher_dashboard"
        st.rerun()
    
    if create_btn:
        if session_name:
            with st.spinner("正在创建签到活动..."):
                success, result = create_attendance_session(
                    selected_class,
                    username,
                    session_name,
                    start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    duration_minutes,
                    location_name,
                    attendance_type
                )
                
                if success:
                    st.success(f"🎉 签到活动创建成功！签到代码：**{result}**")
                    
                    # 显示签到信息卡片
                    type_mapping = {
                        'standard': '标准签到', 
                        'qr_code': '二维码签到', 
                        'location': '位置签到'
                    }
                    
                    st.markdown(f"""
                    <div class='attendance-card active'>
                        <h3 style='margin: 0; color: #10b981;'>签到信息</h3>
                        <p><strong>签到代码：</strong>{result}</p>
                        <p><strong>签到方式：</strong>{type_mapping.get(attendance_type, '标准签到')}</p>
                        <p><strong>有效时间：</strong>{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}</p>
                        <p><strong>签到地点：</strong>{location_name or "无限制"}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 复制代码按钮
                    st.code(result, language="text")
                    
                    # 操作按钮
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 复制签到代码", width='stretch', key="copy_code_btn"):
                            st.toast("签到代码已复制到剪贴板")
                    
                    with col2:
                        if st.button("📊 查看签到详情", width='stretch', key="view_detail_btn"):
                            st.session_state.selected_session = result
                            st.session_state.current_page = "attendance_detail"
                            st.rerun()
                else:
                    st.error(f"❌ {result}")
        else:
            st.warning("⚠️ 请输入签到活动名称")

def render_attendance_checkin():
    """学生签到页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>📱 在线签到</h2>
        <p>参与班级签到活动</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        st.warning("请先登录")
        return
    
    username = st.session_state.username
    
    # 获取学生可用的签到活动
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 获取学生加入的班级
        c.execute("""
            SELECT cm.class_code 
            FROM classroom_members cm
            WHERE cm.student_username = ? AND cm.status = 'active'
        """, (username,))
        
        class_codes = [row[0] for row in c.fetchall()]
        
        if not class_codes:
            st.info("您还没有加入任何班级")
            if st.button("🔍 查找班级"):
                st.session_state.current_page = "find_classroom"
                st.rerun()
            return
        
        # 获取这些班级中活跃的签到活动
        current_time = to_beijing_time_str()
        
        placeholders = ','.join(['?' for _ in class_codes])
        query = f"""
            SELECT a.session_code, a.session_name, a.class_code, 
                   a.start_time, a.end_time, a.location_name,
                   c.class_name,
                   CASE WHEN ar.id IS NOT NULL THEN 1 ELSE 0 END as has_checked_in
            FROM attendance_sessions a
            JOIN classrooms c ON a.class_code = c.class_code
            LEFT JOIN attendance_records ar ON a.session_code = ar.session_code 
                AND ar.student_username = ?
            WHERE a.class_code IN ({placeholders})
            AND ? BETWEEN a.start_time AND a.end_time
            ORDER BY a.end_time ASC
        """
        
        params = class_codes.copy()
        params.insert(0, username)
        params.append(current_time)
        
        c.execute(query, params)
        active_sessions = c.fetchall()
        
        # 获取即将开始的签到活动
        query_upcoming = f"""
            SELECT a.session_code, a.session_name, a.class_code, 
                   a.start_time, a.end_time, a.location_name,
                   c.class_name,
                   CASE WHEN ar.id IS NOT NULL THEN 1 ELSE 0 END as has_checked_in
            FROM attendance_sessions a
            JOIN classrooms c ON a.class_code = c.class_code
            LEFT JOIN attendance_records ar ON a.session_code = ar.session_code 
                AND ar.student_username = ?
            WHERE a.class_code IN ({placeholders})
            AND a.start_time > ?
            ORDER BY a.start_time ASC
            LIMIT 5
        """
        
        params_upcoming = class_codes.copy()
        params_upcoming.insert(0, username)
        params_upcoming.append(current_time)
        
        c.execute(query_upcoming, params_upcoming)
        upcoming_sessions = c.fetchall()
        
        conn.close()
        
        # 显示当前可签到活动
        if active_sessions:
            st.markdown("### 🟢 当前可签到")
            
            for session in active_sessions:
                (session_code, session_name, class_code, start_time, 
                 end_time, location_name, class_name, has_checked_in) = session
                
                start_dt = from_beijing_time_str(start_time)
                end_dt = from_beijing_time_str(end_time)
                
                # 计算剩余时间
                remaining_minutes = (end_dt - get_beijing_time()).total_seconds() / 60
                
                if has_checked_in:
                    # 已经签到
                    st.markdown(f"""
                    <div class='attendance-card' style='border-color: #10b981;'>
                        <h4 style='margin: 0; color: #10b981;'>✅ {session_name}</h4>
                        <p style='margin: 5px 0;'><strong>班级：</strong>{class_name}</p>
                        <p style='margin: 5px 0;'><strong>时间：</strong>{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}</p>
                        <p style='margin: 5px 0;'><strong>地点：</strong>{location_name or '无限制'}</p>
                        <p style='margin: 5px 0; color: #10b981; font-weight: bold;'>✓ 您已完成签到</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # 可以签到
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div style='padding: 15px; border-radius: 10px; background: #f0fdf4;'>
                                <h4 style='margin: 0;'>{session_name}</h4>
                                <p style='margin: 5px 0;'><strong>班级：</strong>{class_name}</p>
                                <p style='margin: 5px 0;'><strong>时间：</strong>{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}</p>
                                <p style='margin: 5px 0;'><strong>地点：</strong>{location_name or '无限制'}</p>
                                <p style='margin: 5px 0; color: #ef4444;'>
                                ⏰ 剩余时间: {int(remaining_minutes)}分钟
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("签到", key=f"checkin_{session_code}", width='stretch'):
                                with st.spinner("正在签到..."):
                                    success, msg = check_in_attendance(
                                        session_code, 
                                        username,
                                        check_in_method='web',
                                        device_info='Web Browser'
                                    )
                                    
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
        
        else:
            st.info("暂无当前可签到的活动")
        
        # 显示即将开始的签到活动
        if upcoming_sessions:
            st.markdown("### 📅 即将开始")
            
            for session in upcoming_sessions:
                (session_code, session_name, class_code, start_time, 
                 end_time, location_name, class_name, has_checked_in) = session
                
                start_dt = from_beijing_time_str(start_time)
                time_until = (start_dt - get_beijing_time()).total_seconds() / 3600
                
                if time_until < 24:  # 24小时内
                    st.markdown(f"""
                    <div class='attendance-card'>
                        <h4 style='margin: 0;'>{session_name}</h4>
                        <p style='margin: 5px 0;'><strong>班级：</strong>{class_name}</p>
                        <p style='margin: 5px 0;'><strong>开始时间：</strong>{start_dt.strftime('%m月%d日 %H:%M')}</p>
                        <p style='margin: 5px 0;'><strong>地点：</strong>{location_name or '待定'}</p>
                        <p style='margin: 5px 0; color: #f59e0b;'>
                        ⏳ 将在{int(time_until)}小时后开始
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 手动输入签到代码
        st.markdown("---")
        st.markdown("### 🔢 手动签到")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            manual_code = st.text_input("输入签到代码", placeholder="请输入6位签到代码", key="manual_code_input")
        
        with col2:
            if st.button("提交", width='stretch', key="manual_submit_btn"):
                if manual_code:
                    with st.spinner("正在验证签到代码..."):
                        success, msg = check_in_attendance(
                            manual_code.upper(),
                            username,
                            check_in_method='manual',
                            device_info='Web Browser'
                        )
                        
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.warning("请输入签到代码")
    
    except Exception as e:
        st.error(f"获取签到信息失败: {str(e)}")

def render_find_classroom():
    """查找班级页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>🔍 查找班级</h2>
        <p>查找并加入感兴趣的班级</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 搜索班级
    search_type = st.radio("搜索方式", ["🔢 班级代码", "📝 班级名称"], horizontal=True, key="search_type_radio")
    
    if search_type == "🔢 班级代码":
        class_code = st.text_input("请输入班级代码", placeholder="例如：CLS123456", key="class_code_search")
        
        if class_code:
            # 查询班级信息
            try:
                conn = sqlite3.connect('image_processing_platform.db')
                c = conn.cursor()
                
                c.execute("""
                    SELECT c.class_code, c.class_name, c.description, 
                           c.teacher_username, c.created_at, c.max_students,
                           COUNT(cm.student_username) as current_students
                    FROM classrooms c
                    LEFT JOIN classroom_members cm ON c.class_code = cm.class_code 
                        AND cm.status = 'active'
                    WHERE c.class_code = ? AND c.is_active = TRUE
                    GROUP BY c.id
                """, (class_code.upper(),))
                
                class_info = c.fetchone()
                
                if class_info:
                    (class_code, class_name, description, teacher_username, 
                     created_at, max_students, current_students) = class_info
                    
                    # 检查是否已经加入
                    c.execute("""
                        SELECT id FROM classroom_members 
                        WHERE class_code = ? AND student_username = ?
                    """, (class_code, st.session_state.username))
                    
                    already_joined = c.fetchone() is not None
                    
                    conn.close()
                    
                    # 显示班级信息卡片
                    st.markdown(f"""
                    <div class='class-card'>
                        <h3 style='color: #dc2626;'>{class_name}</h3>
                        <p><strong>班级代码：</strong><code>{class_code}</code></p>
                        <p><strong>授课教师：</strong>{teacher_username}</p>
                        <p><strong>创建时间：</strong>{created_at[:10]}</p>
                        <p><strong>班级规模：</strong>{current_students}/{max_students}人</p>
                        <p><strong>班级描述：</strong></p>
                        <p style='color: #6b7280;'>{description or '暂无描述'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 加入按钮
                    if not already_joined:
                        if current_students >= max_students:
                            st.error("⚠️ 班级人数已满")
                        else:
                            if st.button("🎯 加入班级", type="primary", width='stretch', key="join_class_btn"):
                                success, msg = join_classroom(st.session_state.username, class_code)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                    else:
                        st.success("✅ 您已加入该班级")
                else:
                    st.warning("未找到该班级，请检查班级代码是否正确")
                    
            except Exception as e:
                st.error(f"查询失败: {str(e)}")
    
    else:  # 按班级名称搜索
        class_name_keyword = st.text_input("请输入班级名称关键词", placeholder="例如：图像处理", key="class_name_search")
        
        if class_name_keyword:
            try:
                conn = sqlite3.connect('image_processing_platform.db')
                c = conn.cursor()
                
                c.execute("""
                    SELECT c.class_code, c.class_name, c.description, 
                           c.teacher_username, c.created_at,
                           COUNT(cm.student_username) as current_students,
                           c.max_students
                    FROM classrooms c
                    LEFT JOIN classroom_members cm ON c.class_code = cm.class_code 
                        AND cm.status = 'active'
                    WHERE c.class_name LIKE ? AND c.is_active = TRUE
                    GROUP BY c.id
                    ORDER BY c.created_at DESC
                    LIMIT 10
                """, (f"%{class_name_keyword}%",))
                
                classes = c.fetchall()
                conn.close()
                
                if classes:
                    st.markdown(f"### 找到 {len(classes)} 个相关班级")
                    
                    for class_info in classes:
                        (class_code, class_name, description, teacher_username, 
                         created_at, current_students, max_students) = class_info
                        
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div style='padding: 15px; border-radius: 10px; background: #f9fafb; margin-bottom: 10px;'>
                                    <h4 style='margin: 0;'>{class_name}</h4>
                                    <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                                    教师: {teacher_username} | 创建: {created_at[:10]}
                                    </p>
                                    <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                                    人数: {current_students}/{max_students}
                                    </p>
                                    <p style'margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                                    {description[:100] if description else '暂无描述'}...
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                if st.button("查看详情", key=f"view_{class_code}"):
                                    # 显示班级代码
                                    st.info(f"班级代码: {class_code}")
                else:
                    st.info("未找到相关班级")
                    
            except Exception as e:
                st.error(f"搜索失败: {str(e)}")

def render_subscription_plans():
    """订阅套餐页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>💎 升级套餐</h2>
        <p>选择适合您的套餐，解锁更多功能</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取订阅套餐
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        c.execute("""
            SELECT plan_code, plan_name, price_monthly, price_yearly,
                   max_classes, max_students_per_class, max_attendance_sessions,
                   features
            FROM subscription_plans
            WHERE is_active = TRUE
            ORDER BY price_monthly
        """)
        
        plans = c.fetchall()
        conn.close()
        
        if plans:
            # 显示套餐卡片
            cols = st.columns(len(plans))
            
            for idx, plan in enumerate(plans):
                (plan_code, plan_name, price_monthly, price_yearly,
                 max_classes, max_students, max_sessions, features) = plan
                
                with cols[idx]:
                    is_featured = plan_code == "pro"  # 专业版作为推荐套餐
                    
                    st.markdown(f"""
                    <div class='subscription-card {'featured' if is_featured else ''}'>
                        <h3 style='color: {'#dc2626' if is_featured else '#1f2937'};'>
                            {plan_name}
                        </h3>
                        <div style='margin: 20px 0;'>
                            <span style='font-size: 2.5rem; font-weight: bold; color: #dc2626;'>
                                ¥{price_monthly}
                            </span>
                            <span style='color: #6b7280;'>/月</span>
                        </div>
                        <p style='color: #6b7280; margin-bottom: 20px;'>
                            ¥{price_yearly}/年 (省{int((1 - price_yearly/(price_monthly*12))*100)}%)
                        </p>
                        
                        <div class='feature-list'>
                            <li>最多 {max_classes} 个班级</li>
                            <li>每班最多 {max_students} 人</li>
                            <li>最多 {max_sessions} 次签到</li>
                            <li>{features}</li>
                        </div>
                        
                        <div style='margin-top: 30px;'>
                            {is_featured and '🔥 ' or ''}
                            {plan_code == 'free' and '当前套餐' or '立即升级'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if plan_code != "free":
                        if st.button(f"选择{plan_name}", key=f"plan_{plan_code}", width='stretch'):
                            # 这里实现支付逻辑
                            st.info(f"选择套餐: {plan_name}")
                            # 在实际应用中，这里应该跳转到支付页面
            
            # 企业版定制咨询
            st.markdown("---")
            st.markdown("### 🏢 企业定制")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("""
                <div style='padding: 25px; background: linear-gradient(135deg, #fefaf0, #fff); 
                            border-radius: 15px; border: 2px dashed #d4af37;'>
                    <h4 style='color: #d4af37;'>需要更多功能？</h4>
                    <p style='color: #6b7280;'>
                    我们可以为您提供定制化解决方案，包括：
                    </p>
                    <ul style='color: #6b7280;'>
                        <li>API接口集成</li>
                        <li>私有化部署</li>
                        <li>定制功能开发</li>
                        <li>专属技术支持</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("联系我们", width='stretch', key="contact_us_btn"):
                    st.info("请联系: business@example.com")
        
    except Exception as e:
        st.error(f"加载套餐失败: {str(e)}")

def render_attendance_detail():
    """签到详情页面"""
    if 'selected_session' not in st.session_state:
        st.session_state.current_page = "teacher_dashboard"
        st.rerun()
    
    session_code = st.session_state.selected_session
    
    # 获取签到详情
    session_info, attendance_records = get_attendance_details(session_code)
    
    if not session_info:
        st.error("签到活动不存在")
        return
    
    st.markdown(f"""
    <div class='modern-header'>
        <h2>📊 签到详情</h2>
        <p>{session_info['session_name']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 基本信息
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("签到代码", session_code)
    
    with col2:
        attendance_rate = (session_info['attended_students'] / session_info['total_students'] * 100) if session_info['total_students'] > 0 else 0
        st.metric("签到率", f"{attendance_rate:.1f}%")
    
    with col3:
        st.metric("参与人数", f"{session_info['attended_students']}/{session_info['total_students']}")
    
    # 签到记录表格
    st.markdown("### 📋 签到记录")
    
    if attendance_records:
        records_data = []
        for record in attendance_records:
            check_in_time = from_beijing_time_str(record['check_in_time'])
            start_time = from_beijing_time_str(session_info['start_time'])
            is_late = check_in_time > start_time + timedelta(minutes=5)
            
            records_data.append({
                "学生": record['username'],
                "签到时间": record['check_in_time'],
                "签到方式": record['check_in_method'],
                "是否迟到": "是" if is_late else "否",
                "获得积分": record['points_earned'],
                "状态": record['status']
            })
        
        df_records = pd.DataFrame(records_data)
        st.dataframe(df_records, width='stretch', hide_index=True)
        
        # 导出数据
        csv = df_records.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 导出签到记录",
            data=csv,
            file_name=f"attendance_{session_code}.csv",
            mime="text/csv",
            width='stretch'
        )
    else:
        st.info("暂无签到记录")
    
    # 统计图表
    st.markdown("### 📈 签到统计")
    
    if attendance_records:
        # 迟到统计
        late_count = sum(1 for record in attendance_records 
                        if from_beijing_time_str(record['check_in_time']) > 
                           from_beijing_time_str(session_info['start_time']) + timedelta(minutes=5))
        on_time_count = len(attendance_records) - late_count
        
        fig1 = go.Figure(data=[
            go.Pie(
                labels=['准时', '迟到'],
                values=[on_time_count, late_count],
                hole=.3,
                marker_colors=['#10b981', '#ef4444']
            )
        ])
        
        fig1.update_layout(
            title="准时情况分布",
            height=300
        )
        
        st.plotly_chart(fig1, width='stretch')

def render_student_classes():
    """学生班级页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>🎯 我的班级</h2>
        <p>我加入的所有班级</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        st.warning("请先登录")
        return
    
    username = st.session_state.username
    
    # 获取学生加入的班级
    student_classes = get_student_classes(username)
    
    if student_classes:
        st.markdown(f"### 📚 共加入 {len(student_classes)} 个班级")
        
        for class_info in student_classes:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='padding: 15px;'>
                        <h4 style='margin: 0; color: #dc2626;'>{class_info['class_name']}</h4>
                        <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                        班级代码: <strong>{class_info['class_code']}</strong>
                        </p>
                        <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                        授课教师: {class_info['teacher_username']}
                        </p>
                        <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                        {class_info['description'] or '暂无描述'}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='padding: 15px;'>
                        <p style='margin: 5px 0;'>👥 学生: {class_info['total_students']}人</p>
                        <p style='margin: 5px 0;'>📝 活动: {class_info['total_sessions']}次</p>
                        <p style='margin: 5px 0;'>📅 加入: {class_info['joined_at'][:10]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if st.button("查看", key=f"view_{class_info['class_code']}"):
                        st.session_state.selected_class = class_info['class_code']
                        st.session_state.current_page = "class_management"
                        st.rerun()
    else:
        st.info("您还没有加入任何班级")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 查找班级", width='stretch', type="primary"):
                st.session_state.current_page = "find_classroom"
                st.rerun()

def main():
    # 初始化数据库
    init_classroom_db()
    
    # 初始化session_state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'role' not in st.session_state:
        st.session_state.role = ""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "teacher_dashboard" if st.session_state.get('role') == 'teacher' else "student_classes"
    if 'selected_class' not in st.session_state:
        st.session_state.selected_class = ""
    if 'selected_session' not in st.session_state:
        st.session_state.selected_session = ""
    
    # 应用CSS样式
    apply_modern_css()
    
    # 检查登录状态
    if not st.session_state.logged_in:
        st.warning("请先登录系统")
        if st.button("返回首页登录"):
            st.switch_page("main.py")
        return
    
    # 渲染侧边栏
    render_sidebar()
    
    # 根据当前页面渲染内容
    current_page = st.session_state.current_page
    role = st.session_state.role
    
    # 教师端页面
    if role == "teacher":
        if current_page == "teacher_dashboard":
            render_teacher_dashboard()
        elif current_page == "create_classroom":
            render_create_classroom()
        elif current_page == "class_management":
            render_class_management()
        elif current_page == "create_attendance":
            render_create_attendance()
        elif current_page == "subscription":
            render_subscription_plans()
        elif current_page == "attendance_detail":
            render_attendance_detail()
        elif current_page == "reports":
            st.info("报表功能开发中...")
        else:
            render_teacher_dashboard()
    
    # 学生端页面
    elif role == "student":
        if current_page == "student_classes":
            render_student_classes()
        elif current_page == "attendance_checkin":
            render_attendance_checkin()
        elif current_page == "find_classroom":
            render_find_classroom()
        elif current_page == "class_management":
            render_class_management()  # 学生也可以查看班级管理
        else:
            render_student_classes()
    
    # 公共页面
    elif current_page == "subscription":
        render_subscription_plans()

if __name__ == "__main__":
    main()
