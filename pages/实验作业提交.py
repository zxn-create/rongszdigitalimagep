import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from datetime import datetime, timedelta
import sqlite3
import os
import zipfile
import tempfile
import shutil
import base64
import time
import pandas as pd
import random
from scipy import ndimage
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="作业提交台",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
.stButton button:hover {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: white;
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(220, 38, 38, 0.4);
    border-color: #dc2626;
}
    
.stButton button:hover::before {
    left: 100%;
}

/* 特殊按钮样式 */
.stButton button.primary-btn {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: white;
    border: 2px solid #dc2626;
}

.stButton button.secondary-btn {
    background: linear-gradient(135deg, #ffffff, #fef2f2);
    color: #dc2626;
    border: 2px solid #dc2626;
}

.stButton button.success-btn {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    border: 2px solid #059669;
}

.stButton button.warning-btn {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
    border: 2px solid #d97706;
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

/* 文件上传区域 */
.stFileUploader {
    border: 2px dashed #dc2626 !important;
    border-radius: 12px !important;
    background: #fef2f2 !important;
}

/* 作业类型卡片 */
.assignment-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    margin: 15px 0;
    border: 2px solid;
    transition: all 0.3s ease;
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    position: relative;
    overflow: hidden;
}

.assignment-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 5px;
    height: 100%;
}

.assignment-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.2);
}

.assignment-experiment {
    border-color: #3b82f6;
}

.assignment-experiment::before {
    background: linear-gradient(to bottom, #3b82f6, #1d4ed8);
}

.assignment-midterm {
    border-color: #f59e0b;
}

.assignment-midterm::before {
    background: linear-gradient(to bottom, #f59e0b, #d97706);
}

.assignment-final {
    border-color: #10b981;
}

.assignment-final::before {
    background: linear-gradient(to bottom, #10b981, #059669);
}

.assignment-icon {
    font-size: 2.5rem;
    margin-bottom: 15px;
}

.assignment-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 10px;
    color: #333;
}

.assignment-deadline {
    background: #fef3c7;
    color: #d97706;
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 0.9rem;
    display: inline-block;
    margin: 10px 0;
}

/* 提交状态徽章 */
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

.status-submitted {
    background: linear-gradient(135deg, #dbeafe, #bfdbfe);
    color: #1d4ed8;
    border: 2px solid #3b82f6;
}

/* 统计卡片 */
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

/* 提交成功特效 */
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

/* 作业进度条 */
.progress-container {
    background: #f3f4f6;
    border-radius: 10px;
    padding: 15px;
    margin: 15px 0;
}

.progress-bar {
    height: 10px;
    background: #e5e7eb;
    border-radius: 5px;
    overflow: hidden;
    margin: 10px 0;
}

.progress-fill {
    height: 100%;
    border-radius: 5px;
    transition: width 0.5s ease;
}

.progress-experiment {
    background: linear-gradient(90deg, #3b82f6, #1d4ed8);
}

.progress-midterm {
    background: linear-gradient(90deg, #f59e0b, #d97706);
}

.progress-final {
    background: linear-gradient(90deg, #10b981, #059669);
}

/* 文件预览卡片 */
.file-preview-card {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    transition: all 0.3s ease;
}

.file-preview-card:hover {
    border-color: #dc2626;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.1);
}

.file-icon {
    font-size: 2rem;
    margin-right: 15px;
}

.file-info h5 {
    margin: 0;
    color: #333;
}

.file-info p {
    margin: 5px 0 0 0;
    color: #666;
    font-size: 0.9rem;
}

/* 教师管理面板 */
.teacher-panel {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border: 2px solid #0ea5e9;
    border-radius: 15px;
    padding: 25px;
    margin: 20px 0;
    box-shadow: 0 4px 6px rgba(14, 165, 233, 0.2);
}

/* 学生列表 */
.student-list {
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.student-item {
    padding: 15px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.3s ease;
}

.student-item:hover {
    background: #f9fafb;
}

.student-item:last-child {
    border-bottom: none;
}

.student-info {
    display: flex;
    align-items: center;
}

.student-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-right: 15px;
}

.student-name {
    font-weight: bold;
    color: #333;
}

.student-id {
    color: #666;
    font-size: 0.9rem;
}

.student-stats {
    display: flex;
    gap: 15px;
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-weight: bold;
    color: #dc2626;
    font-size: 1.2rem;
}

.stat-label {
    color: #666;
    font-size: 0.8rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .stats-card {
        margin: 10px 0;
    }
    
    .assignment-card {
        padding: 15px;
    }
}

/* 文件预览样式 */
.file-preview-container {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    background: #f9fafb;
}

.file-preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e5e7eb;
}

.file-preview-content {
    max-height: 400px;
    overflow-y: auto;
}

.preview-image {
    max-width: 100%;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.code-preview {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 15px;
    border-radius: 8px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 14px;
    overflow-x: auto;
    white-space: pre;
}

.text-preview {
    background: white;
    padding: 15px;
    border-radius: 8px;
    font-family: 'Arial', sans-serif;
    font-size: 14px;
    line-height: 1.6;
    white-space: pre-wrap;
    word-wrap: break-word;
}
</style>
""", unsafe_allow_html=True)
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
# 创建上传文件存储目录
UPLOAD_DIR = "assignment_submissions"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def get_beijing_time():
    """获取北京时间"""
    utc_now = datetime.utcnow()
    beijing_time = utc_now + timedelta(hours=8)
    return beijing_time

# 使用主程序的数据库
DB_NAME = 'image_processing_platform.db'

# 数据库初始化 - 使用主程序的数据库
def init_assignment_db():
    """初始化作业提交数据库 - 使用主程序的数据库"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 检查表是否存在
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assignments'")
    table_exists = c.fetchone()
    
    if not table_exists:
        # 创建作业表
        c.execute('''
            CREATE TABLE assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_type TEXT NOT NULL,  -- 'experiment', 'midterm', 'final'
                assignment_number INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                deadline TEXT,
                max_score INTEGER DEFAULT 100,
                created_at TEXT NOT NULL,
                teacher_username TEXT,  -- 创建作业的教师
                experiment_card TEXT,   -- 实验卡内容/附件路径
                experiment_materials TEXT -- 实验文档/资料
            )
        ''')
    
    # 检查提交表（使用主程序的experiment_submissions表）
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='experiment_submissions'")
    submissions_exists = c.fetchone()
    
    if not submissions_exists:
        # 主程序已经创建了experiment_submissions表
        # 这里只确保字段完整
        pass
    
    # 添加 assignment_type 字段到 experiment_submissions 表（如果不存在）
    try:
        c.execute("ALTER TABLE experiment_submissions ADD COLUMN assignment_type TEXT DEFAULT 'experiment'")
    except sqlite3.OperationalError:
        # 字段已存在
        pass
    
    conn.commit()
    conn.close()
    
    # 初始化作业数据
    init_default_assignments()

def init_default_assignments():
    """初始化默认作业"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 检查是否已有作业
    c.execute("SELECT COUNT(*) FROM assignments")
    count = c.fetchone()[0]
    
    if count == 0:
        current_time = get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')
        
        # 实验作业
        experiments = [
            (1, "实验卡1下载", "仔细查看实验卡1的内容"),
            (2, "实验卡2下载", "仔细查看实验卡2的内容"),
            (3, "实验卡3下载", "仔细查看实验卡3的内容"),
            (4, "实验卡4下载", "仔细查看实验卡4的内容"),
            (5, "实验卡5下载", "仔细查看实验卡5的内容"),
            (6, "实验卡6下载", "仔细查看实验卡6的内容"),
            (7, "实验卡7下载", "仔细查看实验卡7的内容"),
            (8, "实验卡8下载", "仔细查看实验卡8的内容")
        ]
        
        for i, (num, title, desc) in enumerate(experiments):
            deadline = (get_beijing_time() + timedelta(days=14+i*7)).strftime('%Y-%m-%d')
            c.execute('''
                INSERT INTO assignments (assignment_type, assignment_number, title, description, deadline, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('experiment', num, title, desc, deadline, current_time))
        
        # 期中作业
        midterm_deadline = (get_beijing_time() + timedelta(days=60)).strftime('%Y-%m-%d')
        c.execute('''
            INSERT INTO assignments (assignment_type, assignment_number, title, description, deadline, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('midterm', 1, '图像处理综合应用', '根据老师要求和结合学习的数字图形处理的知识,在老师要求时间内提交', midterm_deadline, current_time))
        
        # 期末作业
        final_deadline = (get_beijing_time() + timedelta(days=120)).strftime('%Y-%m-%d')
        c.execute('''
            INSERT INTO assignments (assignment_type, assignment_number, title, description, deadline, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('final', 1, '图像处理项目开发', '根据老师要求和结合学习的数字图形处理的知识，在老师要求时间内提交', final_deadline, current_time))
    
    conn.commit()
    conn.close()

def save_uploaded_files(uploaded_files, student_username, assignment_id):
    """保存上传的文件"""
    saved_files = []
    if uploaded_files:
        # 创建按学生和作业分类的目录
        student_dir = os.path.join(UPLOAD_DIR, student_username)
        assignment_dir = os.path.join(student_dir, str(assignment_id))
        
        if not os.path.exists(assignment_dir):
            os.makedirs(assignment_dir)
        
        for uploaded_file in uploaded_files:
            # 安全文件名处理
            safe_filename = "".join(c for c in uploaded_file.name if c.isalnum() or c in "._- ").rstrip()
            file_path = os.path.join(assignment_dir, safe_filename)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files.append(safe_filename)
    
    return saved_files

def save_teacher_experiment_card_files(teacher_username, assignment_id, uploaded_files):
    """保存教师上传的实验卡附件"""
    saved_files = []
    if uploaded_files:
        # 创建教师目录结构
        teacher_dir = os.path.join(UPLOAD_DIR, "teachers", teacher_username)
        assignment_dir = os.path.join(teacher_dir, str(assignment_id))
        
        if not os.path.exists(assignment_dir):
            os.makedirs(assignment_dir)
        
        for uploaded_file in uploaded_files:
            # 安全文件名处理
            safe_filename = "".join(c for c in uploaded_file.name if c.isalnum() or c in "._- ").rstrip()
            file_path = os.path.join(assignment_dir, safe_filename)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files.append(safe_filename)
    
    return saved_files

def download_experiment_card(assignment_id):
    """下载实验卡 - 修复版本，解决中文编码问题"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # 获取实验卡信息
        c.execute('''
            SELECT experiment_card, teacher_username, assignment_number 
            FROM assignments 
            WHERE id = ?
        ''', (assignment_id,))
        result = c.fetchone()
        conn.close()
        
        if not result or not result[0]:
            return None, "找不到实验卡内容"
            
        card_content, teacher_username, assignment_number = result
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # 创建ZIP文件，指定UTF-8编码
        zip_filename = f"实验卡_实验{assignment_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 修复中文文件名编码问题
            zipf.filename_encoding = 'utf-8'
            
            # 添加实验卡内容
            card_filename = f"实验{assignment_number}_实验卡内容.txt"
            card_path = os.path.join(temp_dir, card_filename)
            
            with open(card_path, "w", encoding="utf-8") as f:
                f.write(card_content)
            
            # 使用正确的编码写入文件名
            zipf.write(card_path, card_filename)
            
            # 添加教师上传的附件（如果有）
            if teacher_username:
                teacher_dir = os.path.join(UPLOAD_DIR, "teachers", teacher_username, str(assignment_id))
                if os.path.exists(teacher_dir):
                    for root, dirs, files in os.walk(teacher_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # 在ZIP文件中创建"附件"目录，保持原文件名
                            arcname = os.path.join("附件", file)
                            zipf.write(file_path, arcname)
        
        return zip_path, None
    except Exception as e:
        return None, f"下载失败：{str(e)}"

def get_assignment_by_id(assignment_id):
    """通过ID获取作业信息"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT * FROM assignments WHERE id = ?', (assignment_id,))
        assignment = c.fetchone()
        conn.close()
        return assignment
    except Exception as e:
        st.error(f"获取作业信息失败：{str(e)}")
        return None

def get_assignments_by_type(assignment_type):
    """按类型获取作业列表"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT * FROM assignments WHERE assignment_type = ?', (assignment_type,))
        assignments = c.fetchall()
        conn.close()
        return assignments
    except Exception as e:
        st.error(f"获取作业列表失败：{str(e)}")
        return []

def get_assignment_files_with_paths(student_username, assignment_id):
    """获取作业文件列表及完整路径"""
    assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
    file_info = []
    
    if os.path.exists(assignment_dir):
        for root, dirs, files in os.walk(assignment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, assignment_dir)
                file_size = os.path.getsize(file_path)
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                
                file_info.append({
                    'name': file,
                    'path': file_path,
                    'relative_path': rel_path,
                    'size': file_size,
                    'modified': modified_time
                })
    
    return file_info

def get_assignment_files(student_username, assignment_id):
    """获取作业文件列表"""
    assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
    if os.path.exists(assignment_dir):
        return os.listdir(assignment_dir)
    return []

def create_zip_file(student_username, assignment_id):
    """创建包含所有提交文件的ZIP包，修复中文文件名编码问题"""
    assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
    if os.path.exists(assignment_dir):
        # 使用临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
            zip_filename = tmp_zip.name
            
        # 创建ZIP文件，使用UTF-8编码
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as zipf:
            # 设置文件名编码为UTF-8
            zipf.filename_encoding = 'utf-8'
            
            for root, dirs, files in os.walk(assignment_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(assignment_dir))
                    # 直接使用原始文件名，ZIP会使用UTF-8编码
                    zipf.write(file_path, arcname)
        
        return zip_filename
    return None

def get_all_assignments():
    """获取所有作业"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM assignments ORDER BY assignment_type, assignment_number')
    assignments = c.fetchall()
    conn.close()
    return assignments

def get_assignment_by_type(assignment_type):
    """根据类型获取作业"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM assignments WHERE assignment_type = ?', (assignment_type,))
    assignments = c.fetchall()
    conn.close()
    return assignments

def get_assignment_id_by_type_and_number(assignment_type, assignment_number):
    """根据作业类型和编号获取作业ID"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM assignments WHERE assignment_type = ? AND assignment_number = ?", 
              (assignment_type, assignment_number))
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return None

def get_student_submissions(student_username, assignment_type=None):
    """获取学生的提交记录 - 使用主程序的experiment_submissions表"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if assignment_type:
        c.execute('''
            SELECT es.*, a.title, a.description, a.deadline, a.assignment_type
            FROM experiment_submissions es
            JOIN assignments a ON es.experiment_number = a.assignment_number 
                AND es.assignment_type = a.assignment_type
            WHERE es.student_username = ? AND es.assignment_type = ?
            ORDER BY es.submission_time DESC
        ''', (student_username, assignment_type))
    else:
        c.execute('''
            SELECT es.*, a.title, a.description, a.deadline, a.assignment_type
            FROM experiment_submissions es
            JOIN assignments a ON es.experiment_number = a.assignment_number 
                AND es.assignment_type = a.assignment_type
            WHERE es.student_username = ?
            ORDER BY es.submission_time DESC
        ''', (student_username,))
    
    submissions = c.fetchall()
    conn.close()
    return submissions

def submit_assignment(student_username, student_name, assignment_id, assignment_type, content, uploaded_files):
    """提交作业 - 修复版本，确保assignment_type正确存储"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # 获取作业信息
        assignment = get_assignment_by_id(assignment_id)
        if not assignment:
            return False, "找不到对应的作业", None
        
        assignment_number = assignment[2]  # assignment_number字段
        assignment_title = assignment[3]
        
        # 检查是否已有提交
        c.execute('''
            SELECT id, resubmission_count FROM experiment_submissions 
            WHERE student_username = ? AND experiment_number = ? AND assignment_type = ?
        ''', (student_username, assignment_number, assignment_type))
        existing = c.fetchone()
        
        submission_time = get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存上传的文件
        saved_files = save_uploaded_files(uploaded_files, student_username, assignment_id)
        file_names_str = ','.join(saved_files) if saved_files else ''
        
        if existing:
            # 重新提交
            submission_id = existing[0]
            resubmission_count = existing[1] + 1
            
            # 更新提交记录
            c.execute('''
                UPDATE experiment_submissions 
                SET submission_content = ?, submission_time = ?, 
                    status = 'pending', resubmission_count = ?, assignment_type = ?
                WHERE id = ?
            ''', (content + "\n\n提交文件: " + file_names_str, submission_time, resubmission_count, assignment_type, submission_id))
            
            message = f"作业重新提交成功！这是第{resubmission_count}次提交"
        else:
            # 新提交
            # 插入新记录 - 包含assignment_type
            c.execute('''
                INSERT INTO experiment_submissions 
                (student_username, experiment_number, experiment_title, 
                 submission_content, submission_time, status, resubmission_count, assignment_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (student_username, assignment_number, assignment_title,
                  content + "\n\n提交文件: " + file_names_str, submission_time, 'pending', 0, assignment_type))
            
            submission_id = c.lastrowid
            message = "作业提交成功！"
        
        conn.commit()
        conn.close()
        return True, message, submission_id
    except Exception as e:
        return False, f"提交失败：{str(e)}", None

def get_all_submissions(assignment_type=None):
    """获取所有学生的提交（教师端） - 修复版本"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if assignment_type:
        c.execute('''
            SELECT es.*, a.title, a.assignment_type, a.assignment_number
            FROM experiment_submissions es
            JOIN assignments a ON es.experiment_number = a.assignment_number 
                AND es.assignment_type = a.assignment_type
            WHERE es.assignment_type = ?
            ORDER BY es.submission_time DESC
        ''', (assignment_type,))
    else:
        c.execute('''
            SELECT es.*, a.title, a.assignment_type, a.assignment_number
            FROM experiment_submissions es
            JOIN assignments a ON es.experiment_number = a.assignment_number 
                AND es.assignment_type = a.assignment_type
            ORDER BY es.submission_time DESC
        ''')
    
    submissions = c.fetchall()
    conn.close()
    return submissions

def update_submission_score(submission_id, score, feedback, can_view_score, status):
    """更新作业评分"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute('''
            UPDATE experiment_submissions 
            SET score = ?, teacher_feedback = ?, allow_view_score = ?, status = ?
            WHERE id = ?
        ''', (score, feedback, can_view_score, status, submission_id))
        
        conn.commit()
        conn.close()
        return True, "评分更新成功！"
    except Exception as e:
        return False, f"更新失败：{str(e)}"

def get_submission_stats():
    """获取提交统计信息"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 总提交数
    c.execute("SELECT COUNT(*) FROM experiment_submissions")
    total = c.fetchone()[0]
    
    # 按状态统计
    c.execute("SELECT status, COUNT(*) FROM experiment_submissions GROUP BY status")
    status_stats = dict(c.fetchall())
    
    # 平均分
    c.execute("SELECT AVG(score) FROM experiment_submissions WHERE status = 'graded'")
    avg_score = c.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total': total,
        'status': status_stats,
        'avg_score': avg_score
    }

def get_experiment_title(experiment_number):
    """获取实验标题"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT title FROM assignments WHERE assignment_number = ? AND assignment_type = 'experiment'", (experiment_number,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        titles = {
            1: "实验卡1",
            2: "实验卡2",
            3: "实验卡3",
            4: "实验卡4",
            5: "实验卡5",
            6: "实验卡6",
            7: "实验卡7",
            8: "实验卡8"
        }
        return titles.get(experiment_number, f"实验{experiment_number}")

def get_experiment_description(experiment_number):
    """获取实验描述"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT description FROM assignments WHERE assignment_number = ? AND assignment_type = 'experiment'", (experiment_number,))
    result = c.fetchone()
    conn.close()
    
    if result and result[0]:
        return result[0]
    else:
        descriptions = {
            1: "**实验要求：** \n**提交内容：** 实验报告、源代码、处理前后的对比图像。",
            2: "**实验要求：** \n**提交内容：** 实验报告、源代码、边缘检测结果图像。",
            3: "**实验要求：** \n**提交内容：** 实验报告、源代码、滤波效果对比图像。",
            4: "**实验要求：** \n**提交内容：** 实验报告、源代码、形态学操作结果图像。",
            5: "**实验要求：** \n**提交内容：** 实验报告、源代码、分割结果图像。",
            6: "**实验要求：** \n**提交内容：** 实验报告、源代码、特征匹配结果图像。",
            7: "**实验要求：** \n**提交内容：** 实验报告、源代码、增强前后对比图像。",
            8: "**实验要求：** \n**提交内容：** 实验报告、源代码、几何变换结果图像。"
        }
        return descriptions.get(experiment_number, "")

def save_experiment_card(assignment_id, teacher_username, card_content, uploaded_files):
    """保存实验卡 - 修复版本"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # 保存上传的文件
        saved_files = []
        if uploaded_files:
            saved_files = save_teacher_experiment_card_files(teacher_username, assignment_id, uploaded_files)
        
        # 构建实验卡内容，包含文件信息
        experiment_card_content = card_content
        if saved_files:
            experiment_card_content += "\n\n附件文件: " + ', '.join(saved_files)
        
        # 更新作业表中的实验卡信息
        c.execute('''
            UPDATE assignments 
            SET teacher_username = ?, experiment_card = ?
            WHERE id = ?
        ''', (teacher_username, experiment_card_content, assignment_id))
        
        conn.commit()
        conn.close()
        return True, "实验卡上传成功！"
    except Exception as e:
        return False, f"上传失败：{str(e)}"

def save_experiment_materials(assignment_id, teacher_username, materials_content, uploaded_files):
    """保存实验文档/资料"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # 保存上传的文件
        saved_files = []
        if uploaded_files:
            teacher_dir = os.path.join(UPLOAD_DIR, "teachers", teacher_username, "materials")
            if not os.path.exists(teacher_dir):
                os.makedirs(teacher_dir)
            
            assignment_dir = os.path.join(teacher_dir, str(assignment_id))
            if not os.path.exists(assignment_dir):
                os.makedirs(assignment_dir)
            
            for uploaded_file in uploaded_files:
                safe_filename = "".join(c for c in uploaded_file.name if c.isalnum() or c in "._- ").rstrip()
                file_path = os.path.join(assignment_dir, safe_filename)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_files.append(safe_filename)
        
        # 更新作业表中的实验资料信息
        experiment_materials_content = materials_content
        if saved_files:
            experiment_materials_content += "\n\n附件文件: " + ', '.join(saved_files)
        
        c.execute('''
            UPDATE assignments 
            SET teacher_username = ?, experiment_materials = ?
            WHERE id = ?
        ''', (teacher_username, experiment_materials_content, assignment_id))
        
        conn.commit()
        conn.close()
        return True, "实验文档上传成功！"
    except Exception as e:
        return False, f"上传失败：{str(e)}"

def get_experiment_materials(assignment_id):
    """获取实验文档/资料"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT experiment_materials FROM assignments WHERE id = ?", (assignment_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return ""

def download_student_files(student_username, assignment_id):
    """下载学生提交的文件，修复中文编码问题"""
    if not student_username or not assignment_id:
        st.error("缺少必要参数：学生用户名和作业ID")
        return None
        
    assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
    if not os.path.exists(assignment_dir):
        st.error(f"文件路径不存在: {assignment_dir}")
        return None
        
    try:
        # 使用临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
            zip_path = tmp_zip.name
            
        # 创建ZIP文件，使用UTF-8编码
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 设置文件名编码为UTF-8
            zipf.filename_encoding = 'utf-8'
            
            for root, dirs, files in os.walk(assignment_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(assignment_dir))
                    zipf.write(file_path, arcname)
        
        # 验证文件是否创建成功
        if os.path.getsize(zip_path) == 0:
            st.error("创建的压缩包为空，请检查源文件")
            os.remove(zip_path)
            return None
            
        return zip_path
    except Exception as e:
        st.error(f"创建压缩包失败: {str(e)}")
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)
        return None

def preview_file(file_path):
    """预览文件内容"""
    if not os.path.exists(file_path):
        return None, "文件不存在"
    
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # 图像文件
            image = Image.open(file_path)
            return image, "image"
        
        elif file_ext in ['.txt', '.py', '.java', '.cpp', '.c', '.html', '.css', '.js', '.md']:
            # 文本文件
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content, "text"
        
        elif file_ext in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx']:
            # 文档文件 - 显示基本信息
            file_size = os.path.getsize(file_path)
            return f"文档文件: {os.path.basename(file_path)}\n大小: {file_size} 字节\n类型: {file_ext[1:].upper()}", "info"
        
        elif file_ext in ['.zip', '.rar', '.7z']:
            # 压缩文件
            return f"压缩文件: {os.path.basename(file_path)}\n包含多个文件", "info"
        
        else:
            return f"不支持预览的文件类型: {file_ext}", "info"
            
    except Exception as e:
        return None, f"预览失败: {str(e)}"

def download_single_submission(submission_id, student_username, assignment_type, assignment_number):
    """下载单次提交的文件"""
    try:
        # 获取作业ID
        assignment_id = get_assignment_id_by_type_and_number(assignment_type, assignment_number)
        if not assignment_id:
            return None, "找不到对应的作业"
        
        # 获取文件目录
        assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
        if not os.path.exists(assignment_dir):
            return None, "没有找到提交的文件"
        
        # 创建临时ZIP文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
            zip_path = tmp_zip.name
        
        # 创建ZIP文件，使用UTF-8编码
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 设置文件名编码为UTF-8
            zipf.filename_encoding = 'utf-8'
            
            for root, dirs, files in os.walk(assignment_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(assignment_dir))
                    zipf.write(file_path, arcname)
        
        filename = f"{student_username}_{assignment_type}_{assignment_number}_submission_{submission_id}.zip"
        return zip_path, filename, None
        
    except Exception as e:
        return None, None, f"下载失败: {str(e)}"

# 新增功能：成绩导出和学生筛选相关函数
def get_all_students():
    """获取所有学生用户名"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT DISTINCT student_username FROM experiment_submissions ORDER BY student_username")
    students = [row[0] for row in c.fetchall()]
    conn.close()
    return students

def get_student_grades(student_username=None, assignment_type=None):
    """获取学生成绩数据"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    query = '''
        SELECT 
            es.student_username,
            es.experiment_number,
            a.assignment_type,
            a.title,
            es.score,
            es.status,
            es.submission_time,
            es.teacher_feedback
        FROM experiment_submissions es
        JOIN assignments a ON es.experiment_number = a.assignment_number 
            AND es.assignment_type = a.assignment_type
        WHERE es.status = 'graded'
    '''
    
    params = []
    if student_username:
        query += " AND es.student_username = ?"
        params.append(student_username)
    
    if assignment_type:
        query += " AND a.assignment_type = ?"
        params.append(assignment_type)
    
    query += " ORDER BY es.student_username, a.assignment_type, es.experiment_number"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    # 转换为DataFrame
    df = pd.DataFrame(rows, columns=[
        'student_username', 'experiment_number', 'assignment_type', 
        'title', 'score', 'status', 'submission_time', 'teacher_feedback'
    ])
    
    return df

def export_grades_to_excel(student_username=None, assignment_type=None):
    """导出成绩到Excel文件"""
    df = get_student_grades(student_username, assignment_type)
    
    if df.empty:
        return None, "没有找到成绩数据"
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        excel_path = tmp_file.name
    
    try:
        # 创建Excel写入器
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # 按作业类型分组
            for assignment_type_group in df['assignment_type'].unique():
                df_type = df[df['assignment_type'] == assignment_type_group].copy()
                
                # 计算每个学生的平均分
                if assignment_type_group == 'experiment':
                    # 实验成绩，计算每次实验的平均分
                    df_summary = df_type.pivot_table(
                        index='student_username',
                        columns='experiment_number',
                        values='score',
                        aggfunc='first'
                    )
                    df_summary['平均分'] = df_summary.mean(axis=1, skipna=True)
                    df_summary['总分'] = df_summary.iloc[:, :8].sum(axis=1, skipna=True)  # 只计算前8次实验
                else:
                    # 期中/期末成绩
                    df_summary = df_type[['student_username', 'title', 'score', 'submission_time']].copy()
                
                # 写入Excel
                sheet_name = {
                    'experiment': '实验成绩',
                    'midterm': '期中成绩',
                    'final': '期末成绩'
                }.get(assignment_type_group, assignment_type_group)
                
                # 写入详细数据
                df_type.to_excel(writer, sheet_name=sheet_name + '_详细', index=False)
                
                # 写入汇总数据
                if assignment_type_group == 'experiment':
                    df_summary.to_excel(writer, sheet_name=sheet_name + '_汇总')
                else:
                    df_summary.to_excel(writer, sheet_name=sheet_name + '_汇总', index=False)
        
        return excel_path, None
    except Exception as e:
        return None, f"导出失败：{str(e)}"

def get_student_summary_stats(student_username=None):
    """获取学生成绩汇总统计"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    query = '''
        SELECT 
            es.student_username,
            a.assignment_type,
            COUNT(*) as submission_count,
            AVG(es.score) as avg_score,
            MIN(es.score) as min_score,
            MAX(es.score) as max_score
        FROM experiment_submissions es
        JOIN assignments a ON es.experiment_number = a.assignment_number 
            AND es.assignment_type = a.assignment_type
        WHERE es.status = 'graded'
    '''
    
    params = []
    if student_username:
        query += " AND es.student_username = ?"
        params.append(student_username)
    
    query += " GROUP BY es.student_username, a.assignment_type ORDER BY es.student_username"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    # 转换为DataFrame
    df = pd.DataFrame(rows, columns=[
        'student_username', 'assignment_type', 'submission_count', 
        'avg_score', 'min_score', 'max_score'
    ])
    
    return df

def get_submission_timeline(student_username=None):
    """获取提交时间线数据"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    query = '''
        SELECT 
            student_username,
            submission_time,
            assignment_type,
            experiment_number,
            score
        FROM experiment_submissions
        WHERE status = 'graded'
    '''
    
    params = []
    if student_username:
        query += " AND student_username = ?"
        params.append(student_username)
    
    query += " ORDER BY submission_time"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    df = pd.DataFrame(rows, columns=[
        'student_username', 'submission_time', 'assignment_type', 
        'experiment_number', 'score'
    ])
    
    # 转换时间格式
    if not df.empty:
        df['submission_time'] = pd.to_datetime(df['submission_time'])
        df['date'] = df['submission_time'].dt.date
        df['time'] = df['submission_time'].dt.time
    
    return df

# 渲染侧边栏
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; 
            padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px;
            box-shadow: 0 6px 12px rgba(220, 38, 38, 0.3);'>
            <h3>📚 学习导航</h3>
            <p style='margin: 10px 0 0 0; font-size: 1rem;'>融思政 · 重实践 · 促创新</p>
        </div>
        """, unsafe_allow_html=True)

        # 快速导航
        st.markdown("### 🧭 快速导航")
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("main.py")
        if st.button("🔬 图像处理实验室", use_container_width=True):
            st.switch_page("pages/1_🔬_图像处理实验室.py")
        if st.button("🏫加入班级与在线签到", use_container_width=True):
            st.switch_page("pages/分班和在线签到.py")
        if st.button("📚 学习资源中心", use_container_width=True):
            st.switch_page("pages/2_📚_学习资源中心.py")
        if st.button("📝 我的思政足迹", use_container_width=True):
            st.switch_page("pages/3_📝_我的思政足迹.py")
        if st.button("🏆 成果展示", use_container_width=True):
            st.switch_page("pages/4_🏆_成果展示.py")

        # 用户信息显示 - 使用安全的访问方式
        if st.session_state.get('logged_in', False):
            st.markdown("### 👤 用户信息")
            username = st.session_state.get('username', '')
            role = st.session_state.get('role', '')
            student_name = st.session_state.get('student_name', '')
            
            if username:
                st.info(f"**用户名:** {username}")
            if role:
                st.info(f"**身份:** {role}")
            if student_name:
                st.info(f"**姓名:** {student_name}")
            
            if st.button("🚪 退出登录", use_container_width=True):
                for key in ['logged_in', 'username', 'role', 'student_name']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        st.markdown("---")

        # 思政理论学习 - 修改版本
        st.markdown("### 🎯 思政理论学习")
        
        # 修改思政理论学习链接为更合适的内容（已移除URL，只显示主题）
        theory_links = [
            "图像处理中的工匠精神",
            "科技创新与爱国情怀", 
            "技术伦理与社会责任",
            "科学家精神传承",
            "社会主义核心价值观实践",
            "科技报国使命担当"
        ]
        
        for topic in theory_links:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #fef2f2, #ffecec);
                color: #dc2626;
                border: 1px solid #dc2626;
                padding: 8px 16px;
                border-radius: 8px;
                margin: 5px 0;
                cursor: pointer;
                transition: all 0.3s;
                text-align: center;
            ">
                📖 {topic}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # 实验指南
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fee2e2, #fecaca); padding: 20px; 
                    border-radius: 12px; border-left: 4px solid #dc2626; margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);'>
            <h4 style='color: #dc2626;'>📚 学习指南</h4>
            <ol style='padding-left: 20px; color: #7f1d1d;'>
                <li style='color: #dc2626;'>选择提交模块</li>
                <li style='color: #dc2626;'>完成实验提交</li>
                <li style='color: #dc2626;'>完成期中提交</li>
                <li style='color: #dc2626;'>完成期末提交</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        # 系统信息
        st.markdown("---")
        st.markdown("**📊 系统信息**")
        st.text(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.text("状态: 🟢 正常运行")
        st.text("版本: v2.1.0")

# 初始化数据库
init_assignment_db()
render_sidebar()

# 检查登录状态
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""

# 主界面
if not st.session_state.logged_in:
    st.title("🔒 访问受限")
    st.markdown("---")
    st.warning("请先登录系统以访问作业提交功能")
    st.info("请在主页面点击右上角的'登录/注册'按钮进行登录")
    st.markdown("---")
    if st.button("🏠 返回首页"):
        st.switch_page("main.py")
else:
    st.title(f"📚 作业提交平台 - 欢迎，{st.session_state.username}")
    st.markdown("---")
    
    # 显示用户信息
    user_col1, user_col2, user_col3 = st.columns(3)
    with user_col1:
        st.info(f"👤 用户: {st.session_state.username}")
    with user_col2:
        st.info(f"🎓 身份: {st.session_state.role}")
    with user_col3:
        if st.button("🚪 退出登录"):
            for key in ['logged_in', 'username', 'role', 'student_name']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # 创建四个主要标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🧪 实验作业", "📊 期中作业", "🎓 期末作业", "👨‍🏫 教师管理"])
    
    with tab1:
        # 学生端实验卡下载
        st.markdown("### 📚 实验卡资源")
        assignments = get_assignments_by_type('experiment')
        if assignments:
            for assignment in assignments:
                assignment_id = assignment[0]
                assignment_type = assignment[1]
                assignment_number = assignment[2]
                title = assignment[3]
                description = assignment[4]
                deadline = assignment[5]
                
                # 获取实验卡内容
                experiment_card = assignment[8] if len(assignment) > 8 else None
                teacher_username = assignment[7] if len(assignment) > 7 else None
                
                with st.expander(f"实验{assignment_number}: {title}", expanded=False):
                    st.markdown(description)
                    
                    # 显示实验卡内容（如果有）
                    if experiment_card:
                        st.markdown("---")
                        st.markdown("#### 实验卡内容：")
                        st.text_area("实验卡", experiment_card, height=200, disabled=True, key=f"card_{assignment_id}")
                    
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button(f"📥 下载实验卡", key=f"student_download_card_{assignment_id}"):
                            with st.spinner("正在准备实验卡..."):
                                zip_path, error = download_experiment_card(assignment_id)
                                if zip_path and os.path.exists(zip_path):
                                    with open(zip_path, "rb") as f:
                                        # 使用UTF-8编码的文件名
                                        zip_data = f.read()
                                        # 创建下载按钮
                                        st.download_button(
                                            label="✅ 点击下载",
                                            data=zip_data,
                                            file_name=f"实验{assignment_number}_实验卡_{datetime.now().strftime('%Y%m%d')}.zip",
                                            mime="application/zip",
                                            key=f"student_card_download_{assignment_id}",
                                            use_container_width=True
                                        )
                                    # 清理临时文件
                                    try:
                                        temp_dir = os.path.dirname(zip_path)
                                        if os.path.exists(zip_path):
                                            os.remove(zip_path)
                                        if os.path.exists(temp_dir):
                                            shutil.rmtree(temp_dir)
                                    except:
                                        pass
                                elif error:
                                    st.error(error)
                                else:
                                    st.warning("该实验暂无实验卡")
        else:
            st.info("暂无实验卡资源")

        st.markdown("### 📝 实验作业提交中心")
        
        # 根据用户角色显示不同的内容
        if st.session_state.get('role') == 'student':
            # 学生端：实验提交界面
            st.markdown("#### 🎓 学生实验提交")
            
            # 实验选择
            experiment_number = st.selectbox(
                "选择实验",
                options=[1, 2, 3, 4, 5, 6, 7, 8],
                format_func=lambda x: f"实验{x}"
            )
            

            
            # 显示实验描述
            st.markdown(get_experiment_description(experiment_number))
            
            # 显示教师上传的实验文档（如果有）
            assignments = get_assignment_by_type('experiment')
            assignment_id = None
            for assignment in assignments:
                if assignment[2] == experiment_number:
                    assignment_id = assignment[0]
                    break
            
            if assignment_id:
                experiment_materials = get_experiment_materials(assignment_id)
                if experiment_materials:
                    with st.expander("📖 查看实验文档/资料", expanded=False):
                        st.markdown(experiment_materials)
            
            # 提交内容
            submission_content = st.text_area(
                "实验报告内容",
                placeholder="请详细描述您的实验过程、结果分析、遇到的问题及解决方案...",
                height=300,
                key=f"exp_content_{experiment_number}"
            )
            
            # 文件上传 - 支持多种格式
            uploaded_files = st.file_uploader(
                "上传实验文件（代码、结果图像、报告文档等）",
                type=['py', 'jpg', 'png', 'zip', 'rar', 'pdf', 'ppt', 'pptx', 'doc', 'docx', 'txt', 'cpp', 'c', 'java'],
                accept_multiple_files=True,
                help="支持多种文件格式：代码文件(.py, .java, .cpp, .c)、图像文件(.jpg, .png)、文档(.pdf, .doc, .docx)、演示文稿(.ppt, .pptx)、压缩包(.zip, .rar)等",
                key=f"exp_files_{experiment_number}"
            )
            
            # 显示已选择的文件
            if uploaded_files:
                st.markdown("**已选择的文件:**")
                for i, file in enumerate(uploaded_files):
                    file_size = file.size / 1024
                    size_unit = "KB" if file_size < 1024 else "MB"
                    size_value = file_size if file_size < 1024 else file_size / 1024
                    
                    st.markdown(f"""
                    <div class='file-preview-card'>
                        <div style='display: flex; align-items: center;'>
                            <div class='file-icon'>📎</div>
                            <div class='file-info'>
                                <h5>{file.name}</h5>
                                <p>大小: {size_value:.1f} {size_unit} | 类型: {file.type if hasattr(file, 'type') else '未知'}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("📤 提交实验", use_container_width=True, type="primary", key=f"submit_exp_{experiment_number}"):
                    if submission_content.strip():
                        # 获取实验对应的作业ID
                        assignments = get_assignment_by_type('experiment')
                        assignment_id = None
                        for assignment in assignments:
                            if assignment[2] == experiment_number:  # assignment_number字段
                                assignment_id = assignment[0]
                                break
                        
                        if assignment_id:
                            success, message, submission_id = submit_assignment(
                                st.session_state.username,
                                st.session_state.get('student_name', st.session_state.username),
                                assignment_id,
                                'experiment',
                                submission_content,
                                uploaded_files
                            )
                            if success:
                                # 显示提交成功特效
                                st.markdown(f"""
                                <div class='submission-success'>
                                    <h1 style='color: #16a34a; margin-bottom: 20px;'>🎉 提交成功！</h1>
                                    <p style='font-size: 1.5rem; margin-bottom: 20px;'>您的实验报告已成功提交</p>
                                    <div style='background: white; padding: 20px; border-radius: 15px; display: inline-block; margin-bottom: 20px;'>
                                        <p style='margin: 0; font-weight: bold; font-size: 1.2rem;'>提交ID: <span style='color: #dc2626;'>{submission_id}</span></p>
                                    </div>
                                    <p style='font-size: 1.1rem;'>请等待老师批阅，您可以在下方查看提交记录</p>
                                    <div style='font-size: 2rem; margin-top: 20px;'>
                                        🎊 🎈 🎉 ✨ 🎇
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # 多重特效
                                st.balloons()
                                st.snow()
                                
                                # 添加成功提示
                                st.success("✅ 实验提交成功！")
                                
                                # 自动显示提交记录
                                st.session_state.show_my_experiments = True
                                
                                # 添加延迟刷新
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("找不到对应的实验作业")
                    else:
                        st.error("请填写实验报告内容")
            
            with col2:
                if st.button("🔄 查看我的实验提交", use_container_width=True, key="view_my_experiments"):
                    st.session_state.show_my_experiments = True
            
            # 显示我的实验提交记录
            if st.session_state.get('show_my_experiments', False):
                st.markdown("---")
                st.markdown("### 📋 我的实验提交记录")
                
                submissions = get_student_submissions(st.session_state.username, 'experiment')
                
                if submissions:
                    # 统计信息
                    total_submissions = len(submissions)
                    graded_submissions = len([s for s in submissions if s[6] == 'graded'])  # 第6个是status
                    pending_submissions = len([s for s in submissions if s[6] == 'pending'])
                    graded_scores = [s[8] for s in submissions if s[6] == 'graded' and s[8] is not None]  # 第8个是score
                    average_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
                    
                    # 显示统计卡片
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""
                        <div class='stats-card'>
                            <div>📊 总提交</div>
                            <div class='stats-number'>{total_submissions}</div>
                            <div class='stats-label'>实验总数</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class='stats-card'>
                            <div>✅ 已批改</div>
                            <div class='stats-number'>{graded_submissions}</div>
                            <div class='stats-label'>完成评分</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class='stats-card'>
                            <div>⏳ 待批改</div>
                            <div class='stats-number'>{pending_submissions}</div>
                            <div class='stats-label'>等待评分</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"""
                        <div class='stats-card'>
                            <div>🎯 平均分</div>
                            <div class='stats-number'>{average_score:.1f}</div>
                            <div class='stats-label'>当前成绩</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 显示详细提交记录
                    st.markdown("### 详细提交记录")
                    for sub_idx, sub in enumerate(submissions):
                        # 安全解包
                        try:
                            submission_id = sub[0]
                            student_username = sub[1]
                            experiment_number = sub[2]
                            experiment_title = sub[3] if len(sub) > 3 else f"实验{experiment_number}"
                            submission_content = sub[4] if len(sub) > 4 else ""
                            submission_time = sub[5] if len(sub) > 5 else ""
                            status = sub[6] if len(sub) > 6 else "pending"
                            teacher_feedback = sub[7] if len(sub) > 7 else None
                            score = sub[8] if len(sub) > 8 else None
                            resubmission_count = sub[9] if len(sub) > 9 else 0
                            allow_view_score = sub[10] if len(sub) > 10 else False
                            assignment_title = sub[11] if len(sub) > 11 else f"实验{experiment_number}"
                            description = sub[12] if len(sub) > 12 else ""
                            deadline = sub[13] if len(sub) > 13 else ""
                        except IndexError as e:
                            st.error(f"数据格式错误: {e}")
                            continue
                        
                        status_info = {
                            'pending': ('⏳ 待批改', 'status-pending'),
                            'graded': ('✅ 已评分', 'status-graded'),
                            'returned': ('🔙 已退回', 'status-returned')
                        }.get(status, ('⚪ 未知', ''))
                        
                        with st.expander(f"{status_info[0]} - 实验{experiment_number} - {submission_time}", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown("**📝 提交内容:**")
                                st.text_area("内容", submission_content, height=150, 
                                           key=f"student_exp_content_{submission_id}_{experiment_number}_{sub_idx}", 
                                           disabled=True)
                                
                                # 解析提交的文件
                                if "提交文件:" in submission_content:
                                    file_section = submission_content.split("提交文件:")[-1].strip()
                                    if file_section:
                                        st.markdown("**📎 提交的文件:**")
                                        files = []
                                        for filename in file_section.split(','):
                                            if filename.strip():
                                                files.append(filename.strip())
                                                st.markdown(f"- {filename}")
                                        
                                        # 提供单次提交文件下载
                                        if files:
                                            assignment_id = None
                                            assignments = get_assignment_by_type('experiment')
                                            for assignment in assignments:
                                                if assignment[2] == experiment_number:
                                                    assignment_id = assignment[0]
                                                    break
                                            
                                            if assignment_id:
                                                zip_path = download_student_files(student_username, assignment_id)
                                                if zip_path and os.path.exists(zip_path):
                                                    with open(zip_path, "rb") as f:
                                                        zip_data = f.read()
                                                        st.download_button(
                                                            label="📦 下载本次提交所有文件",
                                                            data=zip_data,
                                                            file_name=f"实验{experiment_number}_提交_{submission_time.replace(':', '-').replace(' ', '_')}.zip",
                                                            mime="application/zip",
                                                            key=f"student_single_zip_{submission_id}_{experiment_number}_{sub_idx}",
                                                            use_container_width=True
                                                        )
                                                
                                                # 单独文件预览和下载
                                                st.markdown("**🔍 文件预览:**")
                                                assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
                                                if os.path.exists(assignment_dir):
                                                    for file_idx, filename in enumerate(files):
                                                        file_path = os.path.join(assignment_dir, filename)
                                                        if os.path.exists(file_path):
                                                            file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                            with file_preview_col1:
                                                                with st.expander(f"📄 {filename}", expanded=False):
                                                                    preview_result, preview_type = preview_file(file_path)
                                                                    if preview_result:
                                                                        if preview_type == "image":
                                                                            st.image(preview_result, caption=filename)
                                                                        elif preview_type == "text":
                                                                            st.code(preview_result, language='text')
                                                                        else:
                                                                            st.info(preview_result)
                                                            with file_preview_col2:
                                                                with open(file_path, "rb") as f:
                                                                    file_data = f.read()
                                                                    st.download_button(
                                                                        label="📥 下载",
                                                                        data=file_data,
                                                                        file_name=filename,
                                                                        mime="application/octet-stream",
                                                                        key=f"single_file_{submission_id}_{experiment_number}_{file_idx}"
                                                                    )
                                
                                # 显示分数和反馈（如果已评分且允许查看）
                                if status == 'graded' and allow_view_score and score is not None:
                                    score_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
                                    st.markdown(f"""
                                    <div style='background: {score_color}; color: white; padding: 15px; border-radius: 10px; 
                                                font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                        🎯 得分: {score}/100
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if teacher_feedback:
                                        st.markdown("**💬 教师反馈:**")
                                        st.info(teacher_feedback)
                            
                            with col2:
                                st.markdown(f"**📊 状态:**")
                                st.markdown(f"<span class='{status_info[1]} status-badge'>{status_info[0]}</span>", unsafe_allow_html=True)
                                st.markdown(f"**🕒 提交时间:** {submission_time}")
                                st.markdown(f"**🔢 提交ID:** `{submission_id}`")
                                st.markdown(f"**🔄 提交次数:** {resubmission_count}")

                                # 添加分数显示（美观版本）
                                if status == 'graded' and allow_view_score and score is not None:
                                    score_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
                                    st.markdown(f"""
                                    <div style='background: {score_color}; color: white; padding: 15px; border-radius: 10px; 
                                                font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                        🎯 得分: {score}/100
                                    </div>
                                    """, unsafe_allow_html=True)
                                elif status == 'graded' and not allow_view_score:
                                    st.markdown("""
                                    <div style='background: #6b7280; color: white; padding: 15px; border-radius: 10px; 
                                                font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                        🔒 得分暂不可查看
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:  # 待批改状态
                                    st.markdown("""
                                    <div style='background: #f59e0b; color: white; padding: 15px; border-radius: 10px; 
                                                font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                        ⏳ 得分待批改
                                    </div>
                                    """, unsafe_allow_html=True)

                                if status == 'pending':
                                    if st.button("撤回", key=f"withdraw_{submission_id}_{experiment_number}_{sub_idx}", use_container_width=True):
                                        # 撤回功能
                                        conn = sqlite3.connect(DB_NAME)
                                        c = conn.cursor()
                                        c.execute('DELETE FROM experiment_submissions WHERE id = ? AND student_username = ?', 
                                                 (submission_id, st.session_state.username))
                                        
                                        # 删除对应的文件
                                        assignments = get_assignment_by_type('experiment')
                                        assignment_id = None
                                        for assignment in assignments:
                                            if assignment[2] == experiment_number:
                                                assignment_id = assignment[0]
                                                break
                                        
                                        if assignment_id:
                                            assignment_dir = os.path.join(UPLOAD_DIR, st.session_state.username, str(assignment_id))
                                            if os.path.exists(assignment_dir):
                                                shutil.rmtree(assignment_dir)
                                        
                                        conn.commit()
                                        conn.close()
                                        st.success("提交已撤回！")
                                        st.rerun()
                else:
                    st.info("暂无实验提交记录，请先提交实验报告")
        
        elif st.session_state.get('role') == 'teacher':
            # 教师端：实验管理界面
            st.markdown("#### 👨‍🏫 教师实验管理")
            
            # 实验卡上传和管理
            st.markdown("### 📋 实验卡管理")
            experiment_number = st.selectbox(
                "选择实验",
                options=[1, 2, 3, 4, 5, 6, 7, 8],
                format_func=lambda x: f"实验{x}",
                key="teacher_experiment_select"
            )
            
            # 获取该实验的作业信息
            assignments = get_assignment_by_type('experiment')
            assignment_id = None
            current_card = ""
            current_materials = ""
            for assignment in assignments:
                if assignment[2] == experiment_number:
                    assignment_id = assignment[0]
                    current_card = assignment[8] if len(assignment) > 8 else ""  # experiment_card字段
                    current_materials = assignment[9] if len(assignment) > 9 else ""  # experiment_materials字段
                    break
            
            if assignment_id:
                # 显示当前实验卡内容
                if current_card:
                    st.markdown("#### 当前实验卡内容：")
                    st.text_area("实验卡内容", current_card, height=200, disabled=True, key=f"current_card_{assignment_id}")
                
                # 实验卡管理 - 增强版
                with st.expander("📝 上传/更新实验卡", expanded=True):
                    st.markdown("#### 编辑实验卡")
                    card_content = st.text_area(
                        "实验卡内容",
                        value=current_card if current_card else f"实验{experiment_number}任务要求：",
                        height=200,
                        placeholder="请输入实验任务要求、步骤、评分标准等...",
                        key=f"teacher_card_content_{experiment_number}"
                    )
                    
                    card_files = st.file_uploader(
                        "上传实验卡附件",
                        type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'png', 'zip', 'ppt', 'pptx'],
                        accept_multiple_files=True,
                        help="可上传实验指导书、参考代码、数据文件等",
                        key=f"teacher_card_files_{experiment_number}"
                    )
                    
                    # 显示已选择的文件
                    if card_files:
                        st.markdown("**已选择的附件:**")
                        for i, file in enumerate(card_files):
                            file_size = file.size / 1024
                            size_unit = "KB" if file_size < 1024 else "MB"
                            size_value = file_size if file_size < 1024 else file_size / 1024
                            
                            st.markdown(f"""
                            <div class='file-preview-card'>
                                <div style='display: flex; align-items: center;'>
                                    <div class='file-icon'>📎</div>
                                    <div class='file-info'>
                                        <h5>{file.name}</h5>
                                        <p>大小: {size_value:.1f} {size_unit} | 类型: {file.type if hasattr(file, 'type') else '未知'}</p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📤 上传/更新实验卡", use_container_width=True, key=f"teacher_upload_card_{experiment_number}"):
                            if card_content.strip():
                                success, message = save_experiment_card(
                                    assignment_id,
                                    st.session_state.username,
                                    card_content,
                                    card_files
                                )
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.error("请输入实验卡内容")
                    
                    with col2:
                        # 实验卡下载按钮
                        if current_card:
                            if st.button("📥 下载实验卡", key=f"teacher_download_card_{assignment_id}"):
                                with st.spinner("正在准备实验卡..."):
                                    zip_path, error = download_experiment_card(assignment_id)
                                    if zip_path and os.path.exists(zip_path):
                                        with open(zip_path, "rb") as f:
                                            zip_data = f.read()
                                            st.download_button(
                                                label="✅ 点击下载",
                                                data=zip_data,
                                                file_name=f"实验{experiment_number}_实验卡_{datetime.now().strftime('%Y%m%d')}.zip",
                                                mime="application/zip",
                                                key=f"teacher_card_download_{assignment_id}",
                                                use_container_width=True
                                            )
                                        # 清理临时文件
                                        try:
                                            temp_dir = os.path.dirname(zip_path)
                                            if os.path.exists(zip_path):
                                                os.remove(zip_path)
                                            if os.path.exists(temp_dir):
                                                shutil.rmtree(temp_dir)
                                        except:
                                            pass
                                    elif error:
                                        st.error(error)
                                    else:
                                        st.warning("该实验暂无实验卡")

            
            # 获取所有学生的实验提交 - 修复版本
            st.markdown("### 📝 学生作业批改")
            experiment_submissions = get_all_submissions('experiment')
            
            if experiment_submissions:
                # 教师端统计信息
                total_submissions = len(experiment_submissions)
                pending_submissions = len([s for s in experiment_submissions if s[6] == 'pending'])  # 第6个是status
                graded_submissions = len([s for s in experiment_submissions if s[6] == 'graded'])
                graded_scores = [s[8] for s in experiment_submissions if s[6] == 'graded' and s[8] is not None]  # 第8个是score
                average_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
                
                # 显示统计卡片
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class='stats-card'>
                        <div>📊 总提交</div>
                        <div class='stats-number'>{total_submissions}</div>
                        <div class='stats-label'>所有实验</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class='stats-card'>
                        <div>⏳ 待批改</div>
                        <div class='stats-number'>{pending_submissions}</div>
                        <div class='stats-label'>等待评分</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class='stats-card'>
                        <div>✅ 已批改</div>
                        <div class='stats-number'>{graded_submissions}</div>
                        <div class='stats-label'>完成评分</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                    <div class='stats-card'>
                        <div>🎯 平均分</div>
                        <div class='stats-number'>{average_score:.1f}</div>
                        <div class='stats-label'>班级平均</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 按状态筛选
                st.markdown("### 🔍 筛选提交")
                filter_status = st.selectbox(
                    "筛选状态",
                    ["全部", "待批改", "已评分", "已退回"],
                    key="teacher_filter_status"
                )
                
                filtered_submissions = experiment_submissions
                if filter_status == "待批改":
                    filtered_submissions = [s for s in experiment_submissions if s[6] == 'pending']
                elif filter_status == "已评分":
                    filtered_submissions = [s for s in experiment_submissions if s[6] == 'graded']
                elif filter_status == "已退回":
                    filtered_submissions = [s for s in experiment_submissions if s[6] == 'returned']
                
                st.markdown(f"**找到 {len(filtered_submissions)} 个提交**")
                
                # 显示提交列表
                for sub_idx, sub in enumerate(filtered_submissions):
                    # 安全解包
                    try:
                        submission_id = sub[0]
                        student_username = sub[1]
                        experiment_number = sub[2]
                        experiment_title = sub[3] if len(sub) > 3 else ""
                        submission_content = sub[4] if len(sub) > 4 else ""
                        submission_time = sub[5] if len(sub) > 5 else ""
                        status = sub[6] if len(sub) > 6 else "pending"
                        teacher_feedback = sub[7] if len(sub) > 7 else None
                        score = sub[8] if len(sub) > 8 else None
                        resubmission_count = sub[9] if len(sub) > 9 else 0
                        allow_view_score = sub[10] if len(sub) > 10 else False
                        assignment_title = sub[11] if len(sub) > 11 else f"实验{experiment_number}"
                        assignment_type = sub[12] if len(sub) > 12 else "experiment"
                    except IndexError as e:
                        st.error(f"数据格式错误: {e}")
                        continue
                    
                    status_info = {
                        'pending': ('⏳ 待批改', 'status-pending'),
                        'graded': ('✅ 已评分', 'status-graded'),
                        'returned': ('🔙 已退回', 'status-returned')
                    }.get(status, ('⚪ 未知', ''))
                    
                    with st.expander(f"{student_username} - 实验{experiment_number} - {status_info[0]} - {submission_time}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown("**👤 学生:**")
                            st.info(f"**{student_username}**")
                            
                            st.markdown("**📝 提交内容:**")
                            st.text_area("内容", submission_content, height=150, 
                                       key=f"teacher_content_{submission_id}_{experiment_number}_{student_username}_{sub_idx}", 
                                       disabled=True)
                            
                            # 显示提交的文件
                            if "提交文件:" in submission_content:
                                file_section = submission_content.split("提交文件:")[-1].strip()
                                if file_section:
                                    st.markdown("**📎 提交的文件:**")
                                    files = []
                                    for filename in file_section.split(','):
                                        if filename.strip():
                                            files.append(filename.strip())
                                            st.markdown(f"- {filename}")
                                    
                                    # 提供单次提交下载
                                    if files:
                                        assignment_id = get_assignment_id_by_type_and_number('experiment', experiment_number)
                                        if assignment_id:
                                            # 下载完整提交的ZIP包
                                            zip_path = download_student_files(student_username, assignment_id)
                                            if zip_path and os.path.exists(zip_path):
                                                with open(zip_path, "rb") as f:
                                                    zip_data = f.read()
                                                    st.download_button(
                                                        label="📦 下载本次提交完整文件",
                                                        data=zip_data,
                                                        file_name=f"{student_username}_实验{experiment_number}_提交.zip",
                                                        mime="application/zip",
                                                        use_container_width=True,
                                                        key=f"teacher_download_full_{submission_id}_{experiment_number}_{student_username}_{sub_idx}"
                                                    )
                                            
                                            # 文件预览和单独下载
                                            st.markdown("**🔍 文件预览:**")
                                            assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
                                            if os.path.exists(assignment_dir):
                                                for file_idx, filename in enumerate(files):
                                                    file_path = os.path.join(assignment_dir, filename)
                                                    if os.path.exists(file_path):
                                                        file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                        with file_preview_col1:
                                                            with st.expander(f"📄 {filename}", expanded=False):
                                                                preview_result, preview_type = preview_file(file_path)
                                                                if preview_result:
                                                                    if preview_type == "image":
                                                                        st.image(preview_result, caption=filename)
                                                                    elif preview_type == "text":
                                                                        st.code(preview_result, language='python' if filename.endswith('.py') else 'text')
                                                                    else:
                                                                        st.info(preview_result)
                                                        with file_preview_col2:
                                                            with open(file_path, "rb") as f:
                                                                file_data = f.read()
                                                                st.download_button(
                                                                    label="📥 单独下载",
                                                                    data=file_data,
                                                                    file_name=filename,
                                                                    mime="application/octet-stream",
                                                                    key=f"teacher_single_file_{submission_id}_{experiment_number}_{student_username}_{file_idx}"
                                                                )
                            
                            # 显示现有评分和反馈
                            if status == 'graded' and score is not None:
                                st.markdown(f"""
                                <div style='background: #10b981; color: white; padding: 15px; border-radius: 10px; 
                                            font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                    🎯 当前得分: {score}/100
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if teacher_feedback:
                                    st.markdown("**💬 当前反馈:**")
                                    st.info(teacher_feedback)
                        
                        with col2:
                            st.markdown(f"**📊 状态:**")
                            st.markdown(f"<span class='{status_info[1]} status-badge'>{status_info[0]}</span>", unsafe_allow_html=True)
                            st.markdown(f"**🕒 提交时间:** {submission_time}")
                            st.markdown(f"**🔢 提交ID:** `{submission_id}`")
                            st.markdown(f"**🔄 提交次数:** {resubmission_count}")
                            
                            # 评分表单
                            st.markdown("---")
                            st.markdown("**📝 评分与反馈**")
                            
                            with st.form(key=f"teacher_grade_form_{submission_id}_{experiment_number}_{student_username}_{sub_idx}"):
                                current_score = score if score is not None else 0
                                new_score = st.slider("评分", 0, 100, current_score, 
                                                    key=f"teacher_score_{submission_id}_{experiment_number}_{student_username}_{sub_idx}")
                                new_feedback = st.text_area("教师反馈", teacher_feedback if teacher_feedback else "", 
                                                          placeholder="请输入对学生的反馈意见...", 
                                                          key=f"teacher_feedback_{submission_id}_{experiment_number}_{student_username}_{sub_idx}")
                                can_view = st.checkbox("允许学生查看分数", value=bool(allow_view_score), 
                                                     key=f"teacher_view_{submission_id}_{experiment_number}_{student_username}_{sub_idx}")
                                new_status = st.selectbox("状态", 
                                                        ["pending", "graded", "returned"], 
                                                        index=["pending", "graded", "returned"].index(status) if status in ["pending", "graded", "returned"] else 0,
                                                        key=f"teacher_status_{submission_id}_{experiment_number}_{student_username}_{sub_idx}")
                                
                                submitted = st.form_submit_button("💾 保存评分", use_container_width=True)
                                if submitted:
                                    success, message = update_submission_score(submission_id, new_score, new_feedback, can_view, new_status)
                                    if success:
                                        st.success("✅ " + message)
                                        st.rerun()
                                    else:
                                        st.error("❌ " + message)
            else:
                st.info("暂无学生提交的实验报告")
        
        else:
            # 其他角色提示
            st.warning("此功能仅对学生和教师开放")
    
    with tab2:
        st.markdown("### 📊 期中作业提交中心")
        
        # 获取期中作业信息
        midterm_assignments = get_assignment_by_type('midterm')
        
        if midterm_assignments:
            for assignment in midterm_assignments:
                assignment_id = assignment[0]
                assignment_type = assignment[1]
                assignment_number = assignment[2]
                title = assignment[3]
                description = assignment[4]
                deadline = assignment[5]
                max_score = assignment[6]
                created_at = assignment[7]
                teacher_username = assignment[8] if len(assignment) > 8 else ""
                experiment_card = assignment[9] if len(assignment) > 9 else ""
                
                st.markdown(f"""
                <div class='assignment-card assignment-midterm'>
                    <div class='assignment-icon'>📊</div>
                    <div class='assignment-title'>{title}</div>
                    <div style='color: #666; margin-bottom: 10px;'>期中作业</div>
                    <div style='margin-bottom: 15px;'>{description}</div>
                    <div class='assignment-deadline'>⏰ 截止日期: {"按照要求时间"}</div>
                    <div style='margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;'>
                        <strong>作业要求:</strong> 请提交完整的项目文档、源代码、演示文稿和运行结果
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 显示实验卡内容（如果有）
                if experiment_card and st.session_state.get('role') == 'student':
                    st.markdown("---")
                    with st.expander("📋 期中作业要求", expanded=False):
                        st.markdown(experiment_card)
                        
                        # 下载实验卡按钮
                        if st.button(f"📥 下载期中作业要求", key=f"midterm_download_card_{assignment_id}"):
                            with st.spinner("正在准备作业要求..."):
                                zip_path, error = download_experiment_card(assignment_id)
                                if zip_path and os.path.exists(zip_path):
                                    with open(zip_path, "rb") as f:
                                        st.download_button(
                                            label="✅ 点击下载",
                                            data=f.read(),
                                            file_name=f"期中作业要求_{datetime.now().strftime('%Y%m%d')}.zip",
                                            mime="application/zip",
                                            key=f"midterm_card_download_{assignment_id}",
                                            use_container_width=True
                                        )
                                    # 清理临时文件
                                    try:
                                        temp_dir = os.path.dirname(zip_path)
                                        if os.path.exists(zip_path):
                                            os.remove(zip_path)
                                        if os.path.exists(temp_dir):
                                            shutil.rmtree(temp_dir)
                                    except:
                                        pass
                                elif error:
                                    st.error(error)
                                else:
                                    st.warning("暂无作业要求")
                
                # 学生提交界面
                if st.session_state.get('role') == 'student':
                    st.markdown("---")
                    st.markdown("#### 🎓 期中作业提交")
                    
                    # 学生信息
                    col1, col2 = st.columns(2)
                    with col1:
                        student_name = st.text_input("姓名", value=st.session_state.get('student_name', ''), key="midterm_name")
                    with col2:
                        student_id = st.text_input("学号", value=st.session_state.username, key="midterm_id")
                    
                    # 作业内容
                    content = st.text_area(
                        "项目报告/说明文档",
                        placeholder="请详细描述您的项目设计思路、实现过程、功能说明、遇到的问题及解决方案...",
                        height=200,
                        key="midterm_content"
                    )
                    
                    # 文件上传 - 特别支持PPT和压缩包
                    uploaded_files = st.file_uploader(
                        "上传期中作业文件",
                        type=['ppt', 'pptx', 'pdf', 'doc', 'docx', 'zip', 'rar', '7z', 'py', 'java', 'cpp', 'c', 
                              'jpg', 'png', 'gif', 'txt', 'xls', 'xlsx', 'mp4', 'avi', 'mov'],
                        accept_multiple_files=True,
                        help="必须包含：演示文稿(.ppt, .pptx)、项目文档(.pdf, .doc, .docx)、源代码压缩包(.zip, .rar)、结果截图等",
                        key="midterm_files"
                    )
                    
                    if uploaded_files:
                        st.markdown("**已选择的文件:**")
                        for i, file in enumerate(uploaded_files):
                            file_size = file.size / 1024
                            size_unit = "KB" if file_size < 1024 else "MB"
                            size_value = file_size if file_size < 1024 else file_size / 1024
                            
                            st.markdown(f"""
                            <div class='file-preview-card'>
                                <div style='display: flex; align-items: center;'>
                                    <div class='file-icon'>📎</div>
                                    <div class='file-info'>
                                        <h5>{file.name}</h5>
                                        <p>大小: {size_value:.1f} {size_unit} | 类型: {file.type if hasattr(file, 'type') else '未知'}</p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 提交按钮
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if st.button("📤 提交期中作业", key="submit_midterm", use_container_width=True, type="primary"):
                            if content.strip():
                                success, message, submission_id = submit_assignment(
                                    st.session_state.username,
                                    student_name,
                                    assignment_id,
                                    'midterm',
                                    content,
                                    uploaded_files
                                )
                                
                                if success:
                                    st.markdown(f"""
                                    <div class='submission-success'>
                                        <h1 style='color: #16a34a; margin-bottom: 20px;'>🎉 期中作业提交成功！</h1>
                                        <p style='font-size: 1.5rem; margin-bottom: 20px;'>{message}</p>
                                        <div style='background: white; padding: 20px; border-radius: 15px; display: inline-block; margin-bottom: 20px;'>
                                            <p style='margin: 0; font-weight: bold; font-size: 1.2rem;'>
                                                提交ID: <span style='color: #dc2626;'>{submission_id}</span>
                                            </p>
                                        </div>
                                        <p style='font-size: 1.1rem;'>请等待老师批阅</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.balloons()
                                    st.success("✅ 期中作业提交成功！")
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.error("请填写项目报告内容")
                    
                    with col2:
                        if st.button("🔄 查看我的期中提交", key="view_midterm", use_container_width=True):
                            st.session_state.show_my_midterm = True
                    
                    # 显示我的期中作业提交记录
                    if st.session_state.get('show_my_midterm', False):
                        st.markdown("---")
                        st.markdown("### 📋 我的期中作业提交")
                        
                        submissions = get_student_submissions(st.session_state.username, 'midterm')
                        
                        if submissions:
                            for sub_idx, sub in enumerate(submissions):
                                # 安全解包
                                try:
                                    submission_id = sub[0]
                                    student_username = sub[1]
                                    experiment_number = sub[2]
                                    experiment_title = sub[3] if len(sub) > 3 else ""
                                    submission_content = sub[4] if len(sub) > 4 else ""
                                    submission_time = sub[5] if len(sub) > 5 else ""
                                    status = sub[6] if len(sub) > 6 else "pending"
                                    teacher_feedback = sub[7] if len(sub) > 7 else None
                                    score = sub[8] if len(sub) > 8 else None
                                    resubmission_count = sub[9] if len(sub) > 9 else 0
                                    allow_view_score = sub[10] if len(sub) > 10 else False
                                    assignment_title = sub[11] if len(sub) > 11 else f"期中作业"
                                    description = sub[12] if len(sub) > 12 else ""
                                    deadline = sub[13] if len(sub) > 13 else ""
                                except IndexError as e:
                                    st.error(f"数据格式错误: {e}")
                                    continue
                                
                                status_info = {
                                    'pending': ('⏳ 待批改', 'status-pending'),
                                    'graded': ('✅ 已评分', 'status-graded'),
                                    'returned': ('🔙 已退回', 'status-returned')
                                }.get(status, ('⚪ 未知', ''))
                                
                                with st.expander(f"{status_info[0]} - {assignment_title} - {submission_time}", expanded=False):
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.markdown("**📝 项目报告:**")
                                        st.text_area("内容", submission_content, height=150, 
                                                   key=f"midterm_content_{submission_id}_{sub_idx}", 
                                                   disabled=True)
                                        
                                        if "提交文件:" in submission_content:
                                            file_section = submission_content.split("提交文件:")[-1].strip()
                                            if file_section:
                                                st.markdown("**📎 提交的文件:**")
                                                files = []
                                                for filename in file_section.split(','):
                                                    if filename.strip():
                                                        files.append(filename.strip())
                                                        st.markdown(f"- {filename}")
                                                
                                                # 提供单次提交下载
                                                if files:
                                                    assignment_id = None
                                                    assignments = get_assignment_by_type('midterm')
                                                    for assignment in assignments:
                                                        if assignment[2] == 1:  # 期中作业只有一个
                                                            assignment_id = assignment[0]
                                                            break
                                                    
                                                    if assignment_id:
                                                        zip_path = download_student_files(student_username, assignment_id)
                                                        if zip_path and os.path.exists(zip_path):
                                                            with open(zip_path, "rb") as f:
                                                                zip_data = f.read()
                                                                st.download_button(
                                                                    label="📦 下载本次提交所有文件",
                                                                    data=zip_data,
                                                                    file_name=f"期中作业_提交_{submission_time.replace(':', '-').replace(' ', '_')}.zip",
                                                                    mime="application/zip",
                                                                    key=f"midterm_zip_{submission_id}_{sub_idx}",
                                                                    use_container_width=True
                                                                )
                                                        
                                                        # 文件预览
                                                        st.markdown("**🔍 文件预览:**")
                                                        assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
                                                        if os.path.exists(assignment_dir):
                                                            for file_idx, filename in enumerate(files):
                                                                file_path = os.path.join(assignment_dir, filename)
                                                                if os.path.exists(file_path):
                                                                    file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                                    with file_preview_col1:
                                                                        with st.expander(f"📄 {filename}", expanded=False):
                                                                            preview_result, preview_type = preview_file(file_path)
                                                                            if preview_result:
                                                                                if preview_type == "image":
                                                                                    st.image(preview_result, caption=filename)
                                                                                elif preview_type == "text":
                                                                                    st.code(preview_result, language='text')
                                                                                else:
                                                                                    st.info(preview_result)
                                                                    with file_preview_col2:
                                                                        with open(file_path, "rb") as f:
                                                                            file_data = f.read()
                                                                            st.download_button(
                                                                                label="📥 下载",
                                                                                data=file_data,
                                                                                file_name=filename,
                                                                                mime="application/octet-stream",
                                                                                key=f"midterm_single_file_{submission_id}_{file_idx}"
                                                                            )
                                        
                                        if status == 'graded' and allow_view_score and score is not None:
                                            score_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
                                            st.markdown(f"""
                                            <div style='background: {score_color}; color: white; padding: 15px; border-radius: 10px; 
                                                        font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                                🎯 得分: {score}/100
                                            </div>
                                            """, unsafe_allow_html=True)
                                            
                                            if teacher_feedback:
                                                st.markdown("**💬 教师反馈:**")
                                                st.info(teacher_feedback)
                                    
                                    with col2:
                                        st.markdown(f"**📊 状态:**")
                                        st.markdown(f"<span class='{status_info[1]} status-badge'>{status_info[0]}</span>", unsafe_allow_html=True)
                                        st.markdown(f"**🕒 提交时间:** {submission_time}")
                                        st.markdown(f"**🔄 提交次数:** {resubmission_count}")
                        else:
                            st.info("暂无期中作业提交记录")
                elif st.session_state.get('role') == 'teacher':
                    st.markdown(f"**📊去教师管理进行批改和管理**")
                        
    
    with tab3:
        st.markdown("### 🎓 期末作业提交中心")
        
        # 获取期末作业信息
        final_assignments = get_assignment_by_type('final')
        
        if final_assignments:
            for assignment in final_assignments:
                assignment_id = assignment[0]
                assignment_type = assignment[1]
                assignment_number = assignment[2]
                title = assignment[3]
                description = assignment[4]
                deadline = assignment[5]
                max_score = assignment[6]
                created_at = assignment[7]
                teacher_username = assignment[8] if len(assignment) > 8 else ""
                experiment_card = assignment[9] if len(assignment) > 9 else ""
                
                st.markdown(f"""
                <div class='assignment-card assignment-final'>
                    <div class='assignment-icon'>🎓</div>
                    <div class='assignment-title'>{title}</div>
                    <div style='color: #666; margin-bottom: 10px;'>期末大作业</div>
                    <div style='margin-bottom: 15px;'>{description}</div>
                    <div class='assignment-deadline'>⏰ 截止日期: {"按照要求时间"}</div>
                    <div style='margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;'>
                        <strong>项目要求:</strong> 
                        1. 完整的项目报告（含需求分析、设计文档、测试报告）<br>
                        2. 完整的源代码工程<br>
                        3. 项目演示文稿（PPT）<br>
                        4. 运行演示视频（可选）<br>
                        5. 用户手册/使用说明
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 显示实验卡内容（如果有）
                if experiment_card and st.session_state.get('role') == 'student':
                    st.markdown("---")
                    with st.expander("📋 期末作业要求", expanded=False):
                        st.markdown(experiment_card)
                        
                        # 下载实验卡按钮
                        if st.button(f"📥 下载期末作业要求", key=f"final_download_card_{assignment_id}"):
                            with st.spinner("正在准备作业要求..."):
                                zip_path, error = download_experiment_card(assignment_id)
                                if zip_path and os.path.exists(zip_path):
                                    with open(zip_path, "rb") as f:
                                        st.download_button(
                                            label="✅ 点击下载",
                                            data=f.read(),
                                            file_name=f"期末作业要求_{datetime.now().strftime('%Y%m%d')}.zip",
                                            mime="application/zip",
                                            key=f"final_card_download_{assignment_id}",
                                            use_container_width=True
                                        )
                                    # 清理临时文件
                                    try:
                                        temp_dir = os.path.dirname(zip_path)
                                        if os.path.exists(zip_path):
                                            os.remove(zip_path)
                                        if os.path.exists(temp_dir):
                                            shutil.rmtree(temp_dir)
                                    except:
                                        pass
                                elif error:
                                    st.error(error)
                                else:
                                    st.warning("暂无作业要求")
                
                # 学生提交界面
                if st.session_state.get('role') == 'student':
                    st.markdown("---")
                    st.markdown("#### 🎓 期末作业提交")
                    
                    # 学生信息
                    col1, col2 = st.columns(2)
                    with col1:
                        student_name = st.text_input("姓名", value=st.session_state.get('student_name', ''), key="final_name")
                    with col2:
                        student_id = st.text_input("学号", value=st.session_state.username, key="final_id")
                    
                    # 项目概述
                    content = st.text_area(
                        "项目报告/设计文档",
                        placeholder="请详细描述您的项目：\n1. 项目背景与意义\n2. 需求分析\n3. 系统设计\n4. 实现过程\n5. 测试结果\n6. 总结与展望...",
                        height=250,
                        key="final_content"
                    )
                    
                    # 文件上传 - 支持完整项目文件
                    uploaded_files = st.file_uploader(
                        "上传期末作业文件",
                        type=['ppt', 'pptx', 'pdf', 'doc', 'docx', 'zip', 'rar', '7z', 'tar', 'gz', 
                              'py', 'java', 'cpp', 'c', 'html', 'css', 'js',
                              'jpg', 'png', 'gif', 'bmp', 'mp4', 'avi', 'mov', 'wmv',
                              'txt', 'md', 'xls', 'xlsx', 'csv', 'json', 'xml'],
                        accept_multiple_files=True,
                        help="必须包含：项目报告(.pdf, .doc)、演示文稿(.ppt, .pptx)、源代码工程(.zip, .rar)、运行截图、演示视频等",
                        key="final_files"
                    )
                    
                    if uploaded_files:
                        st.markdown("**已选择的文件（期末项目）:**")
                        for i, file in enumerate(uploaded_files):
                            file_size = file.size / 1024
                            size_unit = "KB" if file_size < 1024 else "MB"
                            if size_unit == "MB":
                                size_value = file_size / 1024
                            else:
                                size_value = file_size
                            
                            st.markdown(f"""
                            <div class='file-preview-card'>
                                <div style='display: flex; align-items: center;'>
                                    <div class='file-icon'>📦</div>
                                    <div class='file-info'>
                                        <h5>{file.name}</h5>
                                        <p>大小: {size_value:.1f} {size_unit} | 类型: {file.type if hasattr(file, 'type') else '未知'}</p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 提交按钮
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if st.button("🎓 提交期末作业", key="submit_final", use_container_width=True, type="primary"):
                            if content.strip():
                                success, message, submission_id = submit_assignment(
                                    st.session_state.username,
                                    student_name,
                                    assignment_id,
                                    'final',
                                    content,
                                    uploaded_files
                                )
                                
                                if success:
                                    st.markdown(f"""
                                    <div class='submission-success'>
                                        <h1 style='color: #16a34a; margin-bottom: 20px;'>🎉 期末作业提交成功！</h1>
                                        <p style='font-size: 1.5rem; margin-bottom: 20px;'>{message}</p>
                                        <div style='background: white; padding: 20px; border-radius: 15px; display: inline-block; margin-bottom: 20px;'>
                                            <p style='margin: 0; font-weight: bold; font-size: 1.2rem;'>
                                                提交ID: <span style='color: #dc2626;'>{submission_id}</span>
                                            </p>
                                        </div>
                                        <p style='font-size: 1.1rem;'>您的毕业设计/期末项目已提交，请等待老师评审</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.balloons()
                                    st.snow()
                                    st.success("✅ 期末作业提交成功！")
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.error("请填写项目报告内容")
                    
                    with col2:
                        if st.button("🔄 查看我的期末提交", key="view_final", use_container_width=True):
                            st.session_state.show_my_final = True
                    
                    # 显示我的期末作业提交记录
                    if st.session_state.get('show_my_final', False):
                        st.markdown("---")
                        st.markdown("### 📋 我的期末作业提交")
                        
                        submissions = get_student_submissions(st.session_state.username, 'final')
                        
                        if submissions:
                            for sub_idx, sub in enumerate(submissions):
                                # 安全解包
                                try:
                                    submission_id = sub[0]
                                    student_username = sub[1]
                                    experiment_number = sub[2]
                                    experiment_title = sub[3] if len(sub) > 3 else ""
                                    submission_content = sub[4] if len(sub) > 4 else ""
                                    submission_time = sub[5] if len(sub) > 5 else ""
                                    status = sub[6] if len(sub) > 6 else "pending"
                                    teacher_feedback = sub[7] if len(sub) > 7 else None
                                    score = sub[8] if len(sub) > 8 else None
                                    resubmission_count = sub[9] if len(sub) > 9 else 0
                                    allow_view_score = sub[10] if len(sub) > 10 else False
                                    assignment_title = sub[11] if len(sub) > 11 else "期末作业"
                                    description = sub[12] if len(sub) > 12 else ""
                                    deadline = sub[13] if len(sub) > 13 else ""
                                except IndexError as e:
                                    st.error(f"数据格式错误: {e}")
                                    continue
                                
                                status_info = {
                                    'pending': ('⏳ 待评审', 'status-pending'),
                                    'graded': ('✅ 已评分', 'status-graded'),
                                    'returned': ('🔙 需修改', 'status-returned')
                                }.get(status, ('⚪ 未知', ''))
                                
                                with st.expander(f"{status_info[0]} - {assignment_title} - {submission_time}", expanded=False):
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.markdown("**📝 项目报告:**")
                                        st.text_area("内容", submission_content, height=150, 
                                                   key=f"final_content_{submission_id}_{sub_idx}", 
                                                   disabled=True)
                                        
                                        if "提交文件:" in submission_content:
                                            file_section = submission_content.split("提交文件:")[-1].strip()
                                            if file_section:
                                                st.markdown("**📦 提交的项目文件:**")
                                                files = []
                                                for filename in file_section.split(','):
                                                    if filename.strip():
                                                        files.append(filename.strip())
                                                        st.markdown(f"- {filename}")
                                                
                                                # 提供单次提交下载
                                                if files:
                                                    assignment_id = None
                                                    assignments = get_assignment_by_type('final')
                                                    for assignment in assignments:
                                                        if assignment[2] == 1:  # 期末作业只有一个
                                                            assignment_id = assignment[0]
                                                            break
                                                    
                                                    if assignment_id:
                                                        zip_path = download_student_files(student_username, assignment_id)
                                                        if zip_path and os.path.exists(zip_path):
                                                            with open(zip_path, "rb") as f:
                                                                zip_data = f.read()
                                                                st.download_button(
                                                                    label="📦 下载本次提交完整项目",
                                                                    data=zip_data,
                                                                    file_name=f"期末项目_提交_{submission_time.replace(':', '-').replace(' ', '_')}.zip",
                                                                    mime="application/zip",
                                                                    key=f"final_zip_{submission_id}_{sub_idx}",
                                                                    use_container_width=True
                                                                )
                                                        
                                                        # 文件预览
                                                        st.markdown("**🔍 文件预览:**")
                                                        assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
                                                        if os.path.exists(assignment_dir):
                                                            for file_idx, filename in enumerate(files):
                                                                file_path = os.path.join(assignment_dir, filename)
                                                                if os.path.exists(file_path):
                                                                    file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                                    with file_preview_col1:
                                                                        with st.expander(f"📄 {filename}", expanded=False):
                                                                            preview_result, preview_type = preview_file(file_path)
                                                                            if preview_result:
                                                                                if preview_type == "image":
                                                                                    st.image(preview_result, caption=filename)
                                                                                elif preview_type == "text":
                                                                                    st.code(preview_result, language='text')
                                                                                else:
                                                                                    st.info(preview_result)
                                                                    with file_preview_col2:
                                                                        with open(file_path, "rb") as f:
                                                                            file_data = f.read()
                                                                            st.download_button(
                                                                                label="📥 下载",
                                                                                data=file_data,
                                                                                file_name=filename,
                                                                                mime="application/octet-stream",
                                                                                key=f"final_single_file_{submission_id}_{file_idx}"
                                                                            )
                                        
                                        if status == 'graded' and allow_view_score and score is not None:
                                            score_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
                                            st.markdown(f"""
                                            <div style='background: {score_color}; color: white; padding: 15px; border-radius: 10px; 
                                                        font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                                🎯 项目得分: {score}/100
                                            </div>
                                            """, unsafe_allow_html=True)
                                            
                                            if teacher_feedback:
                                                st.markdown("**💬 教师评审意见:**")
                                                st.info(teacher_feedback)
                                    
                                    with col2:
                                        st.markdown(f"**📊 状态:**")
                                        st.markdown(f"<span class='{status_info[1]} status-badge'>{status_info[0]}</span>", unsafe_allow_html=True)
                                        st.markdown(f"**🕒 提交时间:** {submission_time}")
                                        st.markdown(f"**🔄 提交次数:** {resubmission_count}")
                                        if deadline:
                                            st.markdown(f"**⏰ 截止日期:** {deadline}")
                        else:
                            st.info("暂无期末作业提交记录")
                elif st.session_state.get('role') == 'teacher':
                    st.markdown(f"**📊去教师管理进行批改和管理**")
    
    with tab4:
        st.markdown("### 👨‍🏫 教师管理中心")
        
        if st.session_state.get('role') != 'teacher':
            st.warning("❌ 此功能仅对教师开放")
        else:
            # 教师管理子标签页 - 按作业类型分类
            teacher_sub_tab1, teacher_sub_tab2, teacher_sub_tab3, teacher_sub_tab4 = st.tabs([
                "🧪 实验作业管理", "📊 期中作业管理", "🎓 期末作业管理", "📈 成绩管理与导出"
            ])
            
            with teacher_sub_tab1:
                st.markdown("#### 实验作业管理")
                
                # 实验卡上传和管理
                st.markdown("### 📋 实验卡管理")
                experiment_number = st.selectbox(
                    "选择实验",
                    options=[1, 2, 3, 4, 5, 6, 7, 8],
                    format_func=lambda x: f"实验{x}",
                    key="teacher_tab_experiment_select"
                )
                
                # 获取该实验的作业信息
                assignments = get_assignment_by_type('experiment')
                assignment_id = None
                current_card = ""
                current_materials = ""
                for assignment in assignments:
                    if assignment[2] == experiment_number:
                        assignment_id = assignment[0]
                        current_card = assignment[8] if len(assignment) > 8 else ""  # experiment_card字段
                        current_materials = assignment[9] if len(assignment) > 9 else ""  # experiment_materials字段
                        break
                
                if assignment_id:
                    # 显示当前实验卡内容
                    if current_card:
                        st.markdown("#### 当前实验卡内容：")
                        st.text_area("实验卡内容", current_card, height=200, disabled=True, key=f"teacher_current_card_{assignment_id}")
                    
                    # 实验卡管理 - 增强版
                    with st.expander("📝 上传/更新实验卡", expanded=True):
                        st.markdown("#### 编辑实验卡")
                        card_content = st.text_area(
                            "实验卡内容",
                            value=current_card if current_card else f"实验{experiment_number}任务要求：",
                            height=200,
                            placeholder="请输入实验任务要求、步骤、评分标准等...",
                            key=f"teacher_tab_card_content_{experiment_number}"
                        )
                        
                        card_files = st.file_uploader(
                            "上传实验卡附件",
                            type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'png', 'zip', 'ppt', 'pptx'],
                            accept_multiple_files=True,
                            help="可上传实验指导书、参考代码、数据文件等",
                            key=f"teacher_tab_card_files_{experiment_number}"
                        )
                        
                        # 显示已选择的文件
                        if card_files:
                            st.markdown("**已选择的附件:**")
                            for i, file in enumerate(card_files):
                                file_size = file.size / 1024
                                size_unit = "KB" if file_size < 1024 else "MB"
                                size_value = file_size if file_size < 1024 else file_size / 1024
                                
                                st.markdown(f"""
                                <div class='file-preview-card'>
                                    <div style='display: flex; align-items: center;'>
                                        <div class='file-icon'>📎</div>
                                        <div class='file-info'>
                                            <h5>{file.name}</h5>
                                            <p>大小: {size_value:.1f} {size_unit} | 类型: {file.type if hasattr(file, 'type') else '未知'}</p>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📤 上传/更新实验卡", use_container_width=True, key=f"teacher_tab_upload_card_{experiment_number}"):
                                if card_content.strip():
                                    success, message = save_experiment_card(
                                        assignment_id,
                                        st.session_state.username,
                                        card_content,
                                        card_files
                                    )
                                    if success:
                                        st.success(message)
                                        st.rerun()
                                    else:
                                        st.error(message)
                                else:
                                    st.error("请输入实验卡内容")
                        
                        with col2:
                            # 实验卡下载按钮
                            if current_card:
                                if st.button("📥 下载实验卡", key=f"teacher_tab_download_card_{assignment_id}"):
                                    with st.spinner("正在准备实验卡..."):
                                        zip_path, error = download_experiment_card(assignment_id)
                                        if zip_path and os.path.exists(zip_path):
                                            with open(zip_path, "rb") as f:
                                                zip_data = f.read()
                                                st.download_button(
                                                    label="✅ 点击下载",
                                                    data=zip_data,
                                                    file_name=f"实验{experiment_number}_实验卡_{datetime.now().strftime('%Y%m%d')}.zip",
                                                    mime="application/zip",
                                                    key=f"teacher_tab_card_download_{assignment_id}",
                                                    use_container_width=True
                                                )
                                            # 清理临时文件
                                            try:
                                                temp_dir = os.path.dirname(zip_path)
                                                if os.path.exists(zip_path):
                                                    os.remove(zip_path)
                                                if os.path.exists(temp_dir):
                                                    shutil.rmtree(temp_dir)
                                            except:
                                                pass
                                        elif error:
                                            st.error(error)
                                        else:
                                            st.warning("该实验暂无实验卡")

                
                # 实验提交管理
                st.markdown("### 📝 学生实验提交管理")
                experiment_submissions = get_all_submissions('experiment')
                
                if experiment_submissions:
                    # 教师端统计信息
                    total_submissions = len(experiment_submissions)
                    pending_submissions = len([s for s in experiment_submissions if s[6] == 'pending'])
                    graded_submissions = len([s for s in experiment_submissions if s[6] == 'graded'])
                    graded_scores = [s[8] for s in experiment_submissions if s[6] == 'graded' and s[8] is not None]
                    average_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
                    
                    # 显示统计卡片
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown('<div class="stats-card"><div>📊 总提交</div><div class="stats-number">{}</div><div class="stats-label">所有实验</div></div>'.format(total_submissions), unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="stats-card"><div>⏳ 待批改</div><div class="stats-number">{}</div><div class="stats-label">等待评分</div></div>'.format(pending_submissions), unsafe_allow_html=True)
                    with col3:
                        st.markdown('<div class="stats-card"><div>✅ 已批改</div><div class="stats-number">{}</div><div class="stats-label">完成评分</div></div>'.format(graded_submissions), unsafe_allow_html=True)
                    with col4:
                        st.markdown('<div class="stats-card"><div>🎯 平均分</div><div class="stats-number">{}</div><div class="stats-label">班级平均</div></div>'.format(int(average_score)), unsafe_allow_html=True)
                    
                    # 学生筛选
                    st.markdown("### 🔍 学生筛选")
                    all_students = get_all_students()
                    all_students.insert(0, "全部学生")
                    selected_student = st.selectbox(
                        "选择学生",
                        options=all_students,
                        key="teacher_tab_filter_student"
                    )
                    
                    # 按状态筛选
                    filter_status = st.selectbox(
                        "筛选状态",
                        ["全部", "待批改", "已评分", "已退回"],
                        key="teacher_tab_filter_status"
                    )
                    
                    # 筛选提交
                    filtered_submissions = experiment_submissions
                    
                    # 按学生筛选
                    if selected_student != "全部学生":
                        filtered_submissions = [s for s in filtered_submissions if s[1] == selected_student]
                    
                    # 按状态筛选
                    if filter_status == "待批改":
                        filtered_submissions = [s for s in filtered_submissions if s[6] == 'pending']
                    elif filter_status == "已评分":
                        filtered_submissions = [s for s in filtered_submissions if s[6] == 'graded']
                    elif filter_status == "已退回":
                        filtered_submissions = [s for s in filtered_submissions if s[6] == 'returned']
                    
                    st.markdown(f"**找到 {len(filtered_submissions)} 个提交**")
                    
                    # 显示提交列表
                    for sub_idx, sub in enumerate(filtered_submissions):
                        try:
                            submission_id = sub[0]
                            student_username = sub[1]
                            experiment_number = sub[2]
                            experiment_title = sub[3] if len(sub) > 3 else ""
                            submission_content = sub[4] if len(sub) > 4 else ""
                            submission_time = sub[5] if len(sub) > 5 else ""
                            status = sub[6] if len(sub) > 6 else "pending"
                            teacher_feedback = sub[7] if len(sub) > 7 else None
                            score = sub[8] if len(sub) > 8 else None
                            resubmission_count = sub[9] if len(sub) > 9 else 0
                            allow_view_score = sub[10] if len(sub) > 10 else False
                            assignment_title = sub[11] if len(sub) > 11 else f"实验{experiment_number}"
                            assignment_type = sub[12] if len(sub) > 12 else "experiment"
                        except IndexError as e:
                            st.error(f"数据格式错误: {e}")
                            continue
                        
                        status_info = {
                            'pending': ('⏳ 待批改', 'status-pending'),
                            'graded': ('✅ 已评分', 'status-graded'),
                            'returned': ('🔙 已退回', 'status-returned')
                        }.get(status, ('⚪ 未知', ''))
                        
                        with st.expander(f"{student_username} - 实验{experiment_number} - {status_info[0]} - {submission_time}", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown("**👤 学生:**")
                                st.info(f"**{student_username}**")
                                
                                st.markdown("**📝 提交内容:**")
                                st.text_area("内容", submission_content, height=150, 
                                           key=f"teacher_tab_content_{submission_id}_{experiment_number}_{student_username}_{sub_idx}", 
                                           disabled=True)
                                
                                # 显示提交的文件
                                if "提交文件:" in submission_content:
                                    file_section = submission_content.split("提交文件:")[-1].strip()
                                    if file_section:
                                        st.markdown("**📎 提交的文件:**")
                                        files = []
                                        for filename in file_section.split(','):
                                            if filename.strip():
                                                files.append(filename.strip())
                                                st.markdown(f"- {filename}")
                                        
                                        # 提供单次提交下载
                                        if files:
                                            assignment_id = get_assignment_id_by_type_and_number('experiment', experiment_number)
                                            if assignment_id:
                                                # 下载完整提交
                                                zip_path = download_student_files(student_username, assignment_id)
                                                if zip_path and os.path.exists(zip_path):
                                                    with open(zip_path, "rb") as f:
                                                        zip_data = f.read()
                                                        st.download_button(
                                                            label="📦 下载本次提交完整文件",
                                                            data=zip_data,
                                                            file_name=f"{student_username}_实验{experiment_number}_提交.zip",
                                                            mime="application/zip",
                                                            use_container_width=True,
                                                            key=f"teacher_tab_download_full_{submission_id}_{experiment_number}_{student_username}_{sub_idx}"
                                                        )
                                                
                                                # 文件预览
                                                st.markdown("**🔍 文件预览:**")
                                                assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
                                                if os.path.exists(assignment_dir):
                                                    for file_idx, filename in enumerate(files):
                                                        file_path = os.path.join(assignment_dir, filename)
                                                        if os.path.exists(file_path):
                                                            file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                            with file_preview_col1:
                                                                with st.expander(f"📄 {filename}", expanded=False):
                                                                    preview_result, preview_type = preview_file(file_path)
                                                                    if preview_result:
                                                                        if preview_type == "image":
                                                                            st.image(preview_result, caption=filename)
                                                                        elif preview_type == "text":
                                                                            st.code(preview_result, language='python' if filename.endswith('.py') else 'text')
                                                                        else:
                                                                            st.info(preview_result)
                                                            with file_preview_col2:
                                                                with open(file_path, "rb") as f:
                                                                    file_data = f.read()
                                                                    st.download_button(
                                                                        label="📥 单独下载",
                                                                        data=file_data,
                                                                        file_name=filename,
                                                                        mime="application/octet-stream",
                                                                        key=f"teacher_tab_single_file_{submission_id}_{experiment_number}_{student_username}_{file_idx}"
                                                                    )
                                
                                # 显示现有评分和反馈
                                if status == 'graded' and score is not None:
                                    st.markdown(f"""
                                    <div style='background: #10b981; color: white; padding: 15px; border-radius: 10px; 
                                                font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                        🎯 当前得分: {score}/100
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if teacher_feedback:
                                        st.markdown("**💬 当前反馈:**")
                                        st.info(teacher_feedback)
                            
                            with col2:
                                st.markdown(f"**📊 状态:**")
                                st.markdown(f"<span class='{status_info[1]} status-badge'>{status_info[0]}</span>", unsafe_allow_html=True)
                                st.markdown(f"**🕒 提交时间:** {submission_time}")
                                st.markdown(f"**🔄 提交次数:** {resubmission_count}")
                                
                                # 评分表单
                                st.markdown("---")
                                st.markdown("**📝 评分与反馈**")
                                
                                with st.form(key=f"teacher_tab_grade_form_{submission_id}_{experiment_number}_{student_username}_{sub_idx}"):
                                    current_score = score if score is not None else 0
                                    new_score = st.slider("评分", 0, 100, current_score, 
                                                        key=f"teacher_tab_score_{submission_id}_{experiment_number}_{student_username}_{sub_idx}")
                                    new_feedback = st.text_area("教师反馈", teacher_feedback if teacher_feedback else "", 
                                                              placeholder="请输入对学生的反馈意见...", 
                                                              key=f"teacher_tab_feedback_{submission_id}_{experiment_number}_{student_username}_{sub_idx}")
                                    can_view = st.checkbox("允许学生查看分数", value=bool(allow_view_score), 
                                                         key=f"teacher_tab_view_{submission_id}_{experiment_number}_{student_username}_{sub_idx}")
                                    new_status = st.selectbox("状态", 
                                                            ["pending", "graded", "returned"], 
                                                            index=["pending", "graded", "returned"].index(status) if status in ["pending", "graded", "returned"] else 0,
                                                            key=f"teacher_tab_status_{submission_id}_{experiment_number}_{student_username}_{sub_idx}")
                                    
                                    submitted = st.form_submit_button("💾 保存评分", use_container_width=True)
                                    if submitted:
                                        success, message = update_submission_score(submission_id, new_score, new_feedback, can_view, new_status)
                                        if success:
                                            st.success("✅ " + message)
                                            st.rerun()
                                        else:
                                            st.error("❌ " + message)
                else:
                    st.info("暂无学生提交的实验报告")
            
            with teacher_sub_tab2:
                st.markdown("#### 📊 期中作业管理")
                
                # 获取期中作业信息
                midterm_assignments = get_assignment_by_type('midterm')
                
                if midterm_assignments:
                    for assignment in midterm_assignments:
                        assignment_id = assignment[0]
                        assignment_type = assignment[1]
                        assignment_number = assignment[2]
                        title = assignment[3]
                        description = assignment[4]
                        deadline = assignment[5]
                        max_score = assignment[6]
                        created_at = assignment[7]
                        teacher_username = assignment[8] if len(assignment) > 8 else ""
                        experiment_card = assignment[9] if len(assignment) > 9 else ""
                        
                        st.markdown(f"""
                        <div class='assignment-card assignment-midterm'>
                            <div class='assignment-icon'>📊</div>
                            <div class='assignment-title'>{title}</div>
                            <div style='color: #666; margin-bottom: 10px;'>期中作业</div>
                            <div style='margin-bottom: 15px;'>{description}</div>
                            <div class='assignment-deadline'>⏰ 截止日期: {deadline}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 显示当前实验卡内容
                    if experiment_card:
                        st.markdown("#### 当前期中作业要求：")
                        st.text_area("作业要求", experiment_card, height=200, disabled=True, key=f"teacher_midterm_current_card_{assignment_id}")
                    
                    # 期中作业管理 - 实验卡上传
                    with st.expander("📝 期中作业要求管理", expanded=True):
                        st.markdown("#### 上传/更新期中作业要求")
                        card_content = st.text_area(
                            "期中作业要求",
                            value=experiment_card if experiment_card else "期中作业任务要求：",
                            height=200,
                            placeholder="请输入期中作业任务要求、评分标准等...",
                            key="teacher_midterm_card_content"
                        )
                        
                        card_files = st.file_uploader(
                            "上传期中作业附件",
                            type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'zip'],
                            accept_multiple_files=True,
                            help="可上传期中作业指导书、参考资料等",
                            key="teacher_midterm_card_files"
                        )
                        
                        # 显示已选择的文件
                        if card_files:
                            st.markdown("**已选择的附件:**")
                            for i, file in enumerate(card_files):
                                file_size = file.size / 1024
                                size_unit = "KB" if file_size < 1024 else "MB"
                                size_value = file_size if file_size < 1024 else file_size / 1024
                                
                                st.markdown(f"""
                                <div class='file-preview-card'>
                                    <div style='display: flex; align-items: center;'>
                                        <div class='file-icon'>📎</div>
                                        <div class='file-info'>
                                            <h5>{file.name}</h5>
                                            <p>大小: {size_value:.1f} {size_unit} | 类型: {file.type if hasattr(file, 'type') else '未知'}</p>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📤 上传/更新期中作业要求", use_container_width=True, key="teacher_upload_midterm_card"):
                                if card_content.strip():
                                    success, message = save_experiment_card(
                                        assignment_id,
                                        st.session_state.username,
                                        card_content,
                                        card_files
                                    )
                                    if success:
                                        st.success(message)
                                        st.rerun()
                                    else:
                                        st.error(message)
                                else:
                                    st.error("请输入期中作业要求内容")
                        
                        with col2:
                            # 实验卡下载按钮
                            if experiment_card:
                                if st.button("📥 下载期中作业要求", key=f"teacher_midterm_download_card_{assignment_id}"):
                                    with st.spinner("正在准备作业要求..."):
                                        zip_path, error = download_experiment_card(assignment_id)
                                        if zip_path and os.path.exists(zip_path):
                                            with open(zip_path, "rb") as f:
                                                zip_data = f.read()
                                                st.download_button(
                                                    label="✅ 点击下载",
                                                    data=zip_data,
                                                    file_name=f"期中作业要求_{datetime.now().strftime('%Y%m%d')}.zip",
                                                    mime="application/zip",
                                                    key=f"teacher_midterm_card_download_{assignment_id}",
                                                    use_container_width=True
                                                )
                                            # 清理临时文件
                                            try:
                                                temp_dir = os.path.dirname(zip_path)
                                                if os.path.exists(zip_path):
                                                    os.remove(zip_path)
                                                if os.path.exists(temp_dir):
                                                    shutil.rmtree(temp_dir)
                                            except:
                                                pass
                                        elif error:
                                            st.error(error)
                                        else:
                                            st.warning("该作业暂无要求")
                    
                    # 期中提交管理
                    st.markdown("### 📝 期中作业提交管理")
                    midterm_submissions = get_all_submissions('midterm')
                    
                    if midterm_submissions:
                        # 统计信息
                        total_submissions = len(midterm_submissions)
                        pending_submissions = len([s for s in midterm_submissions if s[6] == 'pending'])
                        graded_submissions = len([s for s in midterm_submissions if s[6] == 'graded'])
                        graded_scores = [s[8] for s in midterm_submissions if s[6] == 'graded' and s[8] is not None]
                        average_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
                        
                        # 显示统计卡片
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown('<div class="stats-card"><div>📊 总提交</div><div class="stats-number">{}</div><div class="stats-label">期中作业</div></div>'.format(total_submissions), unsafe_allow_html=True)
                        with col2:
                            st.markdown('<div class="stats-card"><div>⏳ 待批改</div><div class="stats-number">{}</div><div class="stats-label">等待评分</div></div>'.format(pending_submissions), unsafe_allow_html=True)
                        with col3:
                            st.markdown('<div class="stats-card"><div>✅ 已批改</div><div class="stats-number">{}</div><div class="stats-label">完成评分</div></div>'.format(graded_submissions), unsafe_allow_html=True)
                        with col4:
                            st.markdown('<div class="stats-card"><div>🎯 平均分</div><div class="stats-number">{}</div><div class="stats-label">班级平均</div></div>'.format(int(average_score)), unsafe_allow_html=True)
                        
                        # 学生筛选
                        st.markdown("### 🔍 学生筛选")
                        all_students = get_all_students()
                        all_students.insert(0, "全部学生")
                        selected_student = st.selectbox(
                            "选择学生",
                            options=all_students,
                            key="teacher_midterm_filter_student"
                        )
                        
                        # 筛选提交
                        filtered_submissions = midterm_submissions
                        
                        if selected_student != "全部学生":
                            filtered_submissions = [s for s in filtered_submissions if s[1] == selected_student]
                        
                        # 显示期中提交列表
                        for sub_idx, sub in enumerate(filtered_submissions):
                            try:
                                submission_id = sub[0]
                                student_username = sub[1]
                                experiment_number = sub[2]
                                submission_content = sub[4] if len(sub) > 4 else ""
                                submission_time = sub[5] if len(sub) > 5 else ""
                                status = sub[6] if len(sub) > 6 else "pending"
                                teacher_feedback = sub[7] if len(sub) > 7 else None
                                score = sub[8] if len(sub) > 8 else None
                                resubmission_count = sub[9] if len(sub) > 9 else 0
                                allow_view_score = sub[10] if len(sub) > 10 else False
                                assignment_title = sub[11] if len(sub) > 11 else "期中作业"
                                assignment_type = sub[12] if len(sub) > 12 else "midterm"
                            except IndexError as e:
                                st.error(f"数据格式错误: {e}")
                                continue
                            
                            status_info = {
                                'pending': ('⏳ 待批改', 'status-pending'),
                                'graded': ('✅ 已评分', 'status-graded'),
                                'returned': ('🔙 已退回', 'status-returned')
                            }.get(status, ('⚪ 未知', ''))
                            
                            with st.expander(f"{student_username} - {assignment_title} - {status_info[0]} - {submission_time}", expanded=False):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown("**👤 学生:**")
                                    st.info(f"**{student_username}**")
                                    
                                    st.markdown("**📝 提交内容:**")
                                    st.text_area("内容", submission_content, height=150, 
                                               key=f"teacher_midterm_content_{submission_id}_{student_username}_{sub_idx}", 
                                               disabled=True)
                                    
                                    # 显示提交的文件
                                    if "提交文件:" in submission_content:
                                        file_section = submission_content.split("提交文件:")[-1].strip()
                                        if file_section:
                                            st.markdown("**📎 提交的文件:**")
                                            files = []
                                            for filename in file_section.split(','):
                                                if filename.strip():
                                                    files.append(filename.strip())
                                                    st.markdown(f"- {filename}")
                                            
                                            # 提供单次提交下载
                                            if files:
                                                assignment_id = get_assignment_id_by_type_and_number('midterm', 1)
                                                if assignment_id:
                                                    # 下载完整提交
                                                    zip_path = download_student_files(student_username, assignment_id)
                                                    if zip_path and os.path.exists(zip_path):
                                                        with open(zip_path, "rb") as f:
                                                            zip_data = f.read()
                                                            st.download_button(
                                                                label="📦 下载本次提交完整文件",
                                                                data=zip_data,
                                                                file_name=f"{student_username}_期中作业_提交.zip",
                                                                mime="application/zip",
                                                                use_container_width=True,
                                                                key=f"teacher_midterm_download_full_{submission_id}_{student_username}_{sub_idx}"
                                                            )
                                                    
                                                    # 文件预览
                                                    st.markdown("**🔍 文件预览:**")
                                                    assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
                                                    if os.path.exists(assignment_dir):
                                                        for file_idx, filename in enumerate(files):
                                                            file_path = os.path.join(assignment_dir, filename)
                                                            if os.path.exists(file_path):
                                                                file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                                with file_preview_col1:
                                                                    with st.expander(f"📄 {filename}", expanded=False):
                                                                        preview_result, preview_type = preview_file(file_path)
                                                                        if preview_result:
                                                                            if preview_type == "image":
                                                                                st.image(preview_result, caption=filename)
                                                                            elif preview_type == "text":
                                                                                st.code(preview_result, language='text')
                                                                            else:
                                                                                st.info(preview_result)
                                                                with file_preview_col2:
                                                                    with open(file_path, "rb") as f:
                                                                        file_data = f.read()
                                                                        st.download_button(
                                                                            label="📥 单独下载",
                                                                            data=file_data,
                                                                            file_name=filename,
                                                                            mime="application/octet-stream",
                                                                            key=f"teacher_midterm_single_file_{submission_id}_{student_username}_{file_idx}"
                                                                        )
                                    
                                    # 显示现有评分和反馈
                                    if status == 'graded' and score is not None:
                                        st.markdown(f"""
                                        <div style='background: #10b981; color: white; padding: 15px; border-radius: 10px; 
                                                    font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                            🎯 当前得分: {score}/100
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        if teacher_feedback:
                                            st.markdown("**💬 当前反馈:**")
                                            st.info(teacher_feedback)
                                
                                with col2:
                                    st.markdown(f"**📊 状态:**")
                                    st.markdown(f"<span class='{status_info[1]} status-badge'>{status_info[0]}</span>", unsafe_allow_html=True)
                                    st.markdown(f"**🕒 提交时间:** {submission_time}")
                                    st.markdown(f"**🔄 提交次数:** {resubmission_count}")
                                    
                                    # 评分表单
                                    st.markdown("---")
                                    st.markdown("**📝 评分与反馈**")
                                    
                                    with st.form(key=f"teacher_midterm_grade_form_{submission_id}_{student_username}_{sub_idx}"):
                                        current_score = score if score is not None else 0
                                        new_score = st.slider("评分", 0, 100, current_score, 
                                                            key=f"teacher_midterm_score_{submission_id}_{student_username}_{sub_idx}")
                                        new_feedback = st.text_area("教师反馈", teacher_feedback if teacher_feedback else "", 
                                                                  placeholder="请输入对学生的反馈意见...", 
                                                                  key=f"teacher_midterm_feedback_{submission_id}_{student_username}_{sub_idx}")
                                        can_view = st.checkbox("允许学生查看分数", value=bool(allow_view_score), 
                                                             key=f"teacher_midterm_view_{submission_id}_{student_username}_{sub_idx}")
                                        new_status = st.selectbox("状态", 
                                                                ["pending", "graded", "returned"], 
                                                                index=["pending", "graded", "returned"].index(status) if status in ["pending", "graded", "returned"] else 0,
                                                                key=f"teacher_midterm_status_{submission_id}_{student_username}_{sub_idx}")
                                        
                                        submitted = st.form_submit_button("💾 保存评分", use_container_width=True)
                                        if submitted:
                                            success, message = update_submission_score(submission_id, new_score, new_feedback, can_view, new_status)
                                            if success:
                                                st.success("✅ " + message)
                                                st.rerun()
                                            else:
                                                st.error("❌ " + message)
                    else:
                        st.info("暂无学生提交的期中作业")
            
            with teacher_sub_tab3:
                st.markdown("#### 🎓 期末作业管理")
                
                # 获取期末作业信息
                final_assignments = get_assignment_by_type('final')
                
                if final_assignments:
                    for assignment in final_assignments:
                        assignment_id = assignment[0]
                        assignment_type = assignment[1]
                        assignment_number = assignment[2]
                        title = assignment[3]
                        description = assignment[4]
                        deadline = assignment[5]
                        max_score = assignment[6]
                        created_at = assignment[7]
                        teacher_username = assignment[8] if len(assignment) > 8 else ""
                        experiment_card = assignment[9] if len(assignment) > 9 else ""
                        
                        st.markdown(f"""
                        <div class='assignment-card assignment-final'>
                            <div class='assignment-icon'>🎓</div>
                            <div class='assignment-title'>{title}</div>
                            <div style='color: #666; margin-bottom: 10px;'>期末大作业</div>
                            <div style='margin-bottom: 15px;'>{description}</div>
                            <div class='assignment-deadline'>⏰ 截止日期: {deadline}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 显示当前实验卡内容
                    if experiment_card:
                        st.markdown("#### 当前期末作业要求：")
                        st.text_area("作业要求", experiment_card, height=200, disabled=True, key=f"teacher_final_current_card_{assignment_id}")
                    
                    # 期末作业管理 - 实验卡上传
                    with st.expander("📝 期末作业要求管理", expanded=True):
                        st.markdown("#### 上传/更新期末作业要求")
                        card_content = st.text_area(
                            "期末作业要求",
                            value=experiment_card if experiment_card else "期末作业任务要求：",
                            height=200,
                            placeholder="请输入期末作业任务要求、评分标准等...",
                            key="teacher_final_card_content"
                        )
                        
                        card_files = st.file_uploader(
                            "上传期末作业附件",
                            type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'zip'],
                            accept_multiple_files=True,
                            help="可上传期末作业指导书、参考资料等",
                            key="teacher_final_card_files"
                        )
                        
                        # 显示已选择的文件
                        if card_files:
                            st.markdown("**已选择的附件:**")
                            for i, file in enumerate(card_files):
                                file_size = file.size / 1024
                                size_unit = "KB" if file_size < 1024 else "MB"
                                size_value = file_size if file_size < 1024 else file_size / 1024
                                
                                st.markdown(f"""
                                <div class='file-preview-card'>
                                    <div style='display: flex; align-items: center;'>
                                        <div class='file-icon'>📎</div>
                                        <div class='file-info'>
                                            <h5>{file.name}</h5>
                                            <p>大小: {size_value:.1f} {size_unit} | 类型: {file.type if hasattr(file, 'type') else '未知'}</p>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📤 上传/更新期末作业要求", use_container_width=True, key="teacher_upload_final_card"):
                                if card_content.strip():
                                    success, message = save_experiment_card(
                                        assignment_id,
                                        st.session_state.username,
                                        card_content,
                                        card_files
                                    )
                                    if success:
                                        st.success(message)
                                        st.rerun()
                                    else:
                                        st.error(message)
                                else:
                                    st.error("请输入期末作业要求内容")
                        
                        with col2:
                            # 实验卡下载按钮
                            if experiment_card:
                                if st.button("📥 下载期末作业要求", key=f"teacher_final_download_card_{assignment_id}"):
                                    with st.spinner("正在准备作业要求..."):
                                        zip_path, error = download_experiment_card(assignment_id)
                                        if zip_path and os.path.exists(zip_path):
                                            with open(zip_path, "rb") as f:
                                                zip_data = f.read()
                                                st.download_button(
                                                    label="✅ 点击下载",
                                                    data=zip_data,
                                                    file_name=f"期末作业要求_{datetime.now().strftime('%Y%m%d')}.zip",
                                                    mime="application/zip",
                                                    key=f"teacher_final_card_download_{assignment_id}",
                                                    use_container_width=True
                                                )
                                            # 清理临时文件
                                            try:
                                                temp_dir = os.path.dirname(zip_path)
                                                if os.path.exists(zip_path):
                                                    os.remove(zip_path)
                                                if os.path.exists(temp_dir):
                                                    shutil.rmtree(temp_dir)
                                            except:
                                                pass
                                        elif error:
                                            st.error(error)
                                        else:
                                            st.warning("该作业暂无要求")
                    
                    # 期末提交管理
                    st.markdown("### 📝 期末作业提交管理")
                    final_submissions = get_all_submissions('final')
                    
                    if final_submissions:
                        # 统计信息
                        total_submissions = len(final_submissions)
                        pending_submissions = len([s for s in final_submissions if s[6] == 'pending'])
                        graded_submissions = len([s for s in final_submissions if s[6] == 'graded'])
                        graded_scores = [s[8] for s in final_submissions if s[6] == 'graded' and s[8] is not None]
                        average_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
                        
                        # 显示统计卡片
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown('<div class="stats-card"><div>📊 总提交</div><div class="stats-number">{}</div><div class="stats-label">期末作业</div></div>'.format(total_submissions), unsafe_allow_html=True)
                        with col2:
                            st.markdown('<div class="stats-card"><div>⏳ 待批改</div><div class="stats-number">{}</div><div class="stats-label">等待评分</div></div>'.format(pending_submissions), unsafe_allow_html=True)
                        with col3:
                            st.markdown('<div class="stats-card"><div>✅ 已批改</div><div class="stats-number">{}</div><div class="stats-label">完成评分</div></div>'.format(graded_submissions), unsafe_allow_html=True)
                        with col4:
                            st.markdown('<div class="stats-card"><div>🎯 平均分</div><div class="stats-number">{}</div><div class="stats-label">班级平均</div></div>'.format(int(average_score)), unsafe_allow_html=True)
                        
                        # 学生筛选
                        st.markdown("### 🔍 学生筛选")
                        all_students = get_all_students()
                        all_students.insert(0, "全部学生")
                        selected_student = st.selectbox(
                            "选择学生",
                            options=all_students,
                            key="teacher_final_filter_student"
                        )
                        
                        # 筛选提交
                        filtered_submissions = final_submissions
                        
                        if selected_student != "全部学生":
                            filtered_submissions = [s for s in filtered_submissions if s[1] == selected_student]
                        
                        # 显示期末提交列表
                        for sub_idx, sub in enumerate(filtered_submissions):
                            try:
                                submission_id = sub[0]
                                student_username = sub[1]
                                experiment_number = sub[2]
                                submission_content = sub[4] if len(sub) > 4 else ""
                                submission_time = sub[5] if len(sub) > 5 else ""
                                status = sub[6] if len(sub) > 6 else "pending"
                                teacher_feedback = sub[7] if len(sub) > 7 else None
                                score = sub[8] if len(sub) > 8 else None
                                resubmission_count = sub[9] if len(sub) > 9 else 0
                                allow_view_score = sub[10] if len(sub) > 10 else False
                                assignment_title = sub[11] if len(sub) > 11 else "期末作业"
                                assignment_type = sub[12] if len(sub) > 12 else "final"
                            except IndexError as e:
                                st.error(f"数据格式错误: {e}")
                                continue
                            
                            status_info = {
                                'pending': ('⏳ 待评审', 'status-pending'),
                                'graded': ('✅ 已评分', 'status-graded'),
                                'returned': ('🔙 需修改', 'status-returned')
                            }.get(status, ('⚪ 未知', ''))
                            
                            with st.expander(f"{student_username} - {assignment_title} - {status_info[0]} - {submission_time}", expanded=False):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown("**👤 学生:**")
                                    st.info(f"**{student_username}**")
                                    
                                    st.markdown("**📝 提交内容:**")
                                    st.text_area("内容", submission_content, height=150, 
                                               key=f"teacher_final_content_{submission_id}_{student_username}_{sub_idx}", 
                                               disabled=True)
                                    
                                    # 显示提交的文件
                                    if "提交文件:" in submission_content:
                                        file_section = submission_content.split("提交文件:")[-1].strip()
                                        if file_section:
                                            st.markdown("**📦 提交的项目文件:**")
                                            files = []
                                            for filename in file_section.split(','):
                                                if filename.strip():
                                                    files.append(filename.strip())
                                                    st.markdown(f"- {filename}")
                                            
                                            # 提供单次提交下载
                                            if files:
                                                assignment_id = get_assignment_id_by_type_and_number('final', 1)
                                                if assignment_id:
                                                    # 下载完整提交
                                                    zip_path = download_student_files(student_username, assignment_id)
                                                    if zip_path and os.path.exists(zip_path):
                                                        with open(zip_path, "rb") as f:
                                                            zip_data = f.read()
                                                            st.download_button(
                                                                label="📦 下载本次提交完整文件",
                                                                data=zip_data,
                                                                file_name=f"{student_username}_期末作业_提交.zip",
                                                                mime="application/zip",
                                                                use_container_width=True,
                                                                key=f"teacher_final_download_full_{submission_id}_{student_username}_{sub_idx}"
                                                            )
                                                    
                                                    # 文件预览
                                                    st.markdown("**🔍 文件预览:**")
                                                    assignment_dir = os.path.join(UPLOAD_DIR, student_username, str(assignment_id))
                                                    if os.path.exists(assignment_dir):
                                                        for file_idx, filename in enumerate(files):
                                                            file_path = os.path.join(assignment_dir, filename)
                                                            if os.path.exists(file_path):
                                                                file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                                with file_preview_col1:
                                                                    with st.expander(f"📄 {filename}", expanded=False):
                                                                        preview_result, preview_type = preview_file(file_path)
                                                                        if preview_result:
                                                                            if preview_type == "image":
                                                                                st.image(preview_result, caption=filename)
                                                                            elif preview_type == "text":
                                                                                st.code(preview_result, language='text')
                                                                            else:
                                                                                st.info(preview_result)
                                                                with file_preview_col2:
                                                                    with open(file_path, "rb") as f:
                                                                        file_data = f.read()
                                                                        st.download_button(
                                                                            label="📥 单独下载",
                                                                            data=file_data,
                                                                            file_name=filename,
                                                                            mime="application/octet-stream",
                                                                            key=f"teacher_final_single_file_{submission_id}_{student_username}_{file_idx}"
                                                                        )
                                    
                                    # 显示现有评分和反馈
                                    if status == 'graded' and score is not None:
                                        st.markdown(f"""
                                        <div style='background: #10b981; color: white; padding: 15px; border-radius: 10px; 
                                                    font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                            🎯 当前得分: {score}/100
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        if teacher_feedback:
                                            st.markdown("**💬 当前反馈:**")
                                            st.info(teacher_feedback)
                                
                                with col2:
                                    st.markdown(f"**📊 状态:**")
                                    st.markdown(f"<span class='{status_info[1]} status-badge'>{status_info[0]}</span>", unsafe_allow_html=True)
                                    st.markdown(f"**🕒 提交时间:** {submission_time}")
                                    st.markdown(f"**🔄 提交次数:** {resubmission_count}")
                                    
                                    # 评分表单
                                    st.markdown("---")
                                    st.markdown("**📝 评分与反馈**")
                                    
                                    with st.form(key=f"teacher_final_grade_form_{submission_id}_{student_username}_{sub_idx}"):
                                        current_score = score if score is not None else 0
                                        new_score = st.slider("评分", 0, 100, current_score, 
                                                            key=f"teacher_final_score_{submission_id}_{student_username}_{sub_idx}")
                                        new_feedback = st.text_area("教师反馈", teacher_feedback if teacher_feedback else "", 
                                                                  placeholder="请输入对学生的反馈意见...", 
                                                                  key=f"teacher_final_feedback_{submission_id}_{student_username}_{sub_idx}")
                                        can_view = st.checkbox("允许学生查看分数", value=bool(allow_view_score), 
                                                             key=f"teacher_final_view_{submission_id}_{student_username}_{sub_idx}")
                                        new_status = st.selectbox("状态", 
                                                                ["pending", "graded", "returned"], 
                                                                index=["pending", "graded", "returned"].index(status) if status in ["pending", "graded", "returned"] else 0,
                                                                key=f"teacher_final_status_{submission_id}_{student_username}_{sub_idx}")
                                        
                                        submitted = st.form_submit_button("💾 保存评分", use_container_width=True)
                                        if submitted:
                                            success, message = update_submission_score(submission_id, new_score, new_feedback, can_view, new_status)
                                            if success:
                                                st.success("✅ " + message)
                                                st.rerun()
                                            else:
                                                st.error("❌ " + message)
                else:
                    st.info("暂无期末作业信息")
            
            with teacher_sub_tab4:
                st.markdown("#### 📈 成绩管理与导出")
                
                # 成绩概览
                st.markdown("### 📊 成绩概览")
                
                # 获取所有学生
                all_students = get_all_students()
                
                # 学生筛选
                col1, col2 = st.columns([3, 1])
                with col1:
                    selected_student = st.selectbox(
                        "选择学生",
                        options=["全部学生"] + all_students,
                        key="grade_export_filter_student"
                    )
                
                with col2:
                    selected_assignment_type = st.selectbox(
                        "选择作业类型",
                        options=["全部类型", "experiment", "midterm", "final"],
                        key="grade_export_filter_type"
                    )
                
                # 获取成绩数据
                student_filter = None if selected_student == "全部学生" else selected_student
                type_filter = None if selected_assignment_type == "全部类型" else selected_assignment_type
                
                # 获取成绩数据
                grades_df = get_student_grades(student_filter, type_filter)
                
                if not grades_df.empty:
                    # 显示数据概览
                    st.markdown(f"**找到 {len(grades_df)} 条成绩记录**")
                    
                    # 显示数据表格
                    st.dataframe(grades_df, use_container_width=True)
                    
                    # 成绩统计
                    st.markdown("### 📈 成绩统计")
                    
                    # 按作业类型分组统计
                    if 'assignment_type' in grades_df.columns:
                        stats_cols = st.columns(3)
                        
                        for idx, (assign_type, group) in enumerate(grades_df.groupby('assignment_type')):
                            with stats_cols[idx % 3]:
                                avg_score = group['score'].mean()
                                max_score = group['score'].max()
                                min_score = group['score'].min()
                                count = len(group)
                                
                                assign_name = {
                                    'experiment': '实验作业',
                                    'midterm': '期中作业',
                                    'final': '期末作业'
                                }.get(assign_type, assign_type)
                                
                                st.markdown(f"""
                                <div class='stats-card'>
                                    <div>{assign_name}</div>
                                    <div class='stats-number'>{avg_score:.1f}</div>
                                    <div class='stats-label'>平均分 (共{count}份)</div>
                                    <div style='font-size: 0.8rem; color: #666; margin-top: 10px;'>
                                        最高: {max_score} | 最低: {min_score}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # 导出功能
                    st.markdown("### 📤 成绩导出")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📥 导出实验成绩", use_container_width=True, key="export_experiment"):
                            with st.spinner("正在生成Excel文件..."):
                                excel_path, error = export_grades_to_excel(student_filter, 'experiment')
                                if excel_path and os.path.exists(excel_path):
                                    with open(excel_path, "rb") as f:
                                        excel_data = f.read()
                                        st.download_button(
                                            label="✅ 下载实验成绩",
                                            data=excel_data,
                                            file_name=f"实验成绩_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            use_container_width=True
                                        )
                                    # 清理临时文件
                                    try:
                                        if os.path.exists(excel_path):
                                            os.remove(excel_path)
                                    except:
                                        pass
                                elif error:
                                    st.error(error)
                    
                    with col2:
                        if st.button("📥 导出期中成绩", use_container_width=True, key="export_midterm"):
                            with st.spinner("正在生成Excel文件..."):
                                excel_path, error = export_grades_to_excel(student_filter, 'midterm')
                                if excel_path and os.path.exists(excel_path):
                                    with open(excel_path, "rb") as f:
                                        excel_data = f.read()
                                        st.download_button(
                                            label="✅ 下载期中成绩",
                                            data=excel_data,
                                            file_name=f"期中成绩_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            use_container_width=True
                                        )
                                    # 清理临时文件
                                    try:
                                        if os.path.exists(excel_path):
                                            os.remove(excel_path)
                                    except:
                                        pass
                                elif error:
                                    st.error(error)
                    
                    with col3:
                        if st.button("📥 导出期末成绩", use_container_width=True, key="export_final"):
                            with st.spinner("正在生成Excel文件..."):
                                excel_path, error = export_grades_to_excel(student_filter, 'final')
                                if excel_path and os.path.exists(excel_path):
                                    with open(excel_path, "rb") as f:
                                        excel_data = f.read()
                                        st.download_button(
                                            label="✅ 下载期末成绩",
                                            data=excel_data,
                                            file_name=f"期末成绩_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            use_container_width=True
                                        )
                                    # 清理临时文件
                                    try:
                                        if os.path.exists(excel_path):
                                            os.remove(excel_path)
                                    except:
                                        pass
                                elif error:
                                    st.error(error)
                    
                    # 导出所有成绩
                    st.markdown("---")
                    if st.button("📦 导出所有成绩（完整报告）", use_container_width=True, type="primary", key="export_all"):
                        with st.spinner("正在生成完整成绩报告..."):
                            excel_path, error = export_grades_to_excel(student_filter, None)
                            if excel_path and os.path.exists(excel_path):
                                with open(excel_path, "rb") as f:
                                    excel_data = f.read()
                                    st.download_button(
                                        label="✅ 下载完整成绩报告",
                                        data=excel_data,
                                        file_name=f"成绩报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True
                                    )
                                # 清理临时文件
                                try:
                                    if os.path.exists(excel_path):
                                        os.remove(excel_path)
                                except:
                                    pass
                            elif error:
                                st.error(error)
                    
                    # 成绩分析图表
                    if len(grades_df) > 0:
                        st.markdown("### 📊 成绩分布分析")
                        
                        # 按作业类型分组显示图表
                        assignment_types = grades_df['assignment_type'].unique()
                        
                        for assign_type in assignment_types:
                            assign_name = {
                                'experiment': '实验作业',
                                'midterm': '期中作业',
                                'final': '期末作业'
                            }.get(assign_type, assign_type)
                            
                            type_df = grades_df[grades_df['assignment_type'] == assign_type]
                            
                            if assign_type == 'experiment':
                                # 实验成绩按实验编号分组
                                st.markdown(f"#### {assign_name}成绩分布")
                                
                                # 创建分组柱状图
                                fig, ax = plt.subplots(figsize=(8, 5))
                                
                                # 按学生和实验编号分组
                                pivot_df = type_df.pivot_table(
                                    index='student_username',
                                    columns='experiment_number',
                                    values='score',
                                    aggfunc='mean'
                                )
                                
                                # 绘制热力图
                                import seaborn as sns
                                plt.figure(figsize=(8, 5))
                                sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="YlOrRd", 
                                          cbar_kws={'label': '分数'}, linewidths=0.5)
                                plt.title(f'{assign_name}成绩热力图')
                                plt.xlabel('实验编号')
                                plt.ylabel('学生')
                                st.pyplot(plt)
                            else:
                                # 期中/期末成绩直方图
                                st.markdown(f"#### {assign_name}成绩分布")
                                
                                fig, ax = plt.subplots(figsize=(8, 5))
                                scores = type_df['score'].dropna()
                                ax.hist(scores, bins=10, edgecolor='black', alpha=0.7, color='#dc2626')
                                ax.set_xlabel('分数')
                                ax.set_ylabel('人数')
                                ax.set_title(f'{assign_name}成绩分布直方图')
                                ax.grid(True, alpha=0.3)
                                st.pyplot(fig)
                else:
                    st.info("暂无成绩数据")
