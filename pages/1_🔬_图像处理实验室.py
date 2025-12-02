import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from datetime import datetime
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
    page_title="图像处理实验室 - 融思政平台",
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

# 创建上传文件存储目录
UPLOAD_DIR = "experiment_submissions"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def get_beijing_time():
    """获取北京时间"""
    from datetime import datetime, timedelta
    
    # 获取当前UTC时间
    utc_now = datetime.utcnow()
    
    # 北京是UTC+8时区
    beijing_time = utc_now + timedelta(hours=8)
    
    return beijing_time.strftime('%Y-%m-%d %H:%M:%S')

# 数据库函数 - 完整版
def init_experiment_db():
    """初始化实验提交数据库"""
    conn = sqlite3.connect('image_processing_platform.db')
    c = conn.cursor()
    
    # 检查表是否存在
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='experiment_submissions'")
    table_exists = c.fetchone()
    
    if table_exists:
        # 表已存在，检查所有必需的列
        c.execute("PRAGMA table_info(experiment_submissions)")
        columns = [column[1] for column in c.fetchall()]
        
        required_columns = {
            'can_view_score': 'BOOLEAN DEFAULT 0',
            'file_names': 'TEXT DEFAULT ""',
            'resubmission_count': 'INTEGER DEFAULT 0'
        }
        
        for col_name, col_type in required_columns.items():
            if col_name not in columns:
                try:
                    c.execute(f'ALTER TABLE experiment_submissions ADD COLUMN {col_name} {col_type}')
                except:
                    pass
    else:
        # 创建新表
        c.execute('''
            CREATE TABLE experiment_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_username TEXT NOT NULL,
                experiment_number INTEGER NOT NULL,
                experiment_title TEXT NOT NULL,
                submission_content TEXT NOT NULL,
                submission_time TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                teacher_feedback TEXT DEFAULT '',
                score INTEGER DEFAULT 0,
                can_view_score BOOLEAN DEFAULT 0,
                resubmission_count INTEGER DEFAULT 0,
                file_names TEXT DEFAULT ''
            )
        ''')
    
    conn.commit()
    conn.close()

def save_uploaded_files(uploaded_files, submission_id, student_username):
    """保存上传的文件"""
    saved_files = []
    if uploaded_files:
        submission_dir = os.path.join(UPLOAD_DIR, f"{student_username}_{submission_id}")
        if not os.path.exists(submission_dir):
            os.makedirs(submission_dir)
        
        for uploaded_file in uploaded_files:
            file_path = os.path.join(submission_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files.append(uploaded_file.name)
    
    return saved_files

def get_submission_files(submission_id, student_username):
    """获取提交的文件列表"""
    submission_dir = os.path.join(UPLOAD_DIR, f"{student_username}_{submission_id}")
    if os.path.exists(submission_dir):
        return os.listdir(submission_dir)
    return []

def get_file_path(submission_id, student_username, filename):
    """获取文件路径"""
    return os.path.join(UPLOAD_DIR, f"{student_username}_{submission_id}", filename)

def create_zip_file(submission_id, student_username):
    """创建包含所有提交文件的ZIP包"""
    submission_dir = os.path.join(UPLOAD_DIR, f"{student_username}_{submission_id}")
    if os.path.exists(submission_dir):
        zip_path = os.path.join(UPLOAD_DIR, f"{student_username}_{submission_id}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(submission_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, submission_dir))
        return zip_path
    return None

def submit_experiment(student_username, experiment_number, experiment_title, submission_content, uploaded_files):
    """提交实验"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        submission_time = get_beijing_time()  # 使用北京时间
        
        # 先插入提交记录
        c.execute('''
            INSERT INTO experiment_submissions 
            (student_username, experiment_number, experiment_title, submission_content, submission_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_username, experiment_number, experiment_title, submission_content, submission_time))
        
        submission_id = c.lastrowid
        
        # 保存上传的文件
        saved_files = save_uploaded_files(uploaded_files, submission_id, student_username)
        
        # 更新文件名字段
        c.execute('''
            UPDATE experiment_submissions 
            SET file_names = ? 
            WHERE id = ?
        ''', (','.join(saved_files), submission_id))
        
        conn.commit()
        conn.close()
        return True, "实验提交成功！", submission_id
    except Exception as e:
        return False, f"提交失败：{str(e)}", None





def get_student_experiments(student_username):
    """获取学生的实验提交记录"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        c.execute('''
            SELECT * FROM experiment_submissions 
            WHERE student_username = ? 
            ORDER BY submission_time DESC
        ''', (student_username,))
        results = c.fetchall()
        conn.close()
        return results
    except Exception as e:
        st.error(f"获取学生实验记录失败: {str(e)}")
        return []

def get_all_experiments():
    """获取所有学生的实验提交（教师端使用）"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        c.execute('''
            SELECT es.*, u.role 
            FROM experiment_submissions es
            JOIN users u ON es.student_username = u.username
            ORDER BY es.submission_time DESC
        ''')
        results = c.fetchall()
        conn.close()
        return results
    except Exception as e:
        st.error(f"获取所有实验记录失败: {str(e)}")
        return []

def update_experiment_score(submission_id, score, feedback, can_view_score, status):
    """更新实验评分和反馈"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        c.execute('''
            UPDATE experiment_submissions 
            SET score = ?, teacher_feedback = ?, can_view_score = ?, status = ?
            WHERE id = ?
        ''', (score, feedback, can_view_score, status, submission_id))
        conn.commit()
        conn.close()
        return True, "评分更新成功！"
    except Exception as e:
        return False, f"更新失败：{str(e)}"


def withdraw_experiment(submission_id, student_username):
    """撤回实验提交"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        c.execute('''
            DELETE FROM experiment_submissions 
            WHERE id = ? AND student_username = ? AND status = 'pending'
        ''', (submission_id, student_username))
        
        # 删除对应的文件
        submission_dir = os.path.join(UPLOAD_DIR, f"{student_username}_{submission_id}")
        if os.path.exists(submission_dir):
            shutil.rmtree(submission_dir)
        
        conn.commit()
        conn.close()
        return True, "实验提交已撤回！"
    except Exception as e:
        return False, "撤回失败：只能撤回待批改状态的提交"

def get_experiment_title(number):
    titles = {
        1: "图像增强技术实践",
        2: "边缘检测算法比较",
        3: "图像滤波处理实验",
        4: "图像锐化技术应用",
        5: "采样与量化分析",
        6: "彩色图像分割实践",
        7: "颜色通道分析与处理",
        8: "图像特效处理技术",
        9: "图像绘画风格转换",
        10: "风格迁移与艺术化",
        11: "老照片上色与修复",
        12: "数字形态学转换",
        13: "综合图像处理项目"
    }
    return titles.get(number, f"实验{number}")

def get_experiment_description(number):
    descriptions = {
        1: "使用不同的图像增强技术处理图像，分析比较效果",
        2: "实现并比较多种边缘检测算法的性能",
        3: "应用中值滤波、均值滤波等技术进行图像去噪",
        4: "使用拉普拉斯算子等方法进行图像锐化",
        5: "分析不同采样率和量化等级对图像质量的影响",
        6: "实现基于RGB和HSI颜色空间的图像分割",
        7: "分析RGB通道并进行通道分离与重组",
        8: "添加雨点、雪花、樱花等多种特效",
        9: "实现油画、素描、水墨画等绘画效果",
        10: "应用梵高、星空等艺术风格迁移",
        11: "将黑白照片转换为彩色照片",
        12: "应用腐蚀、膨胀等形态学操作",
        13: "综合运用多种图像处理技术完成实际项目"
    }
    return descriptions.get(number, "完成指定的图像处理实验")

# 初始化数据库
init_experiment_db()

# ======================= 图像处理函数 =======================

# 1. 图像增强函数
def apply_histogram_equalization(image):
    """直方图均衡化"""
    if len(image.shape) == 3:
        img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
        output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    else:
        output = cv2.equalizeHist(image)
    return output

def apply_contrast_adjustment(image, alpha, beta):
    """对比度调整"""
    output = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return output

def apply_gamma_correction(image, gamma):
    """伽马校正"""
    if gamma <= 0:
        # 可以返回原图或设置默认值
        gamma = 0.1  # 或 return image.copy()
    
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def apply_clahe(image, clip_limit=2.0, tile_grid_size=(8,8)):
    """限制对比度自适应直方图均衡化"""
    if len(image.shape) == 3:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        output = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    else:
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        output = clahe.apply(image)
    return output

# 2. 边缘检测函数
def apply_canny_edge(image, threshold1=50, threshold2=150):
    """Canny边缘检测"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    edges = cv2.Canny(gray, threshold1, threshold2)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

def apply_sobel_edge(image, ksize=3):
    """Sobel边缘检测"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
    
    # 使用cv2.magnitude计算梯度幅值（更高效）
    magnitude = cv2.magnitude(sobelx, sobely)
    
    # 转换为8位无符号整数（自动取绝对值）
    magnitude = cv2.convertScaleAbs(magnitude)
    
    return cv2.cvtColor(magnitude, cv2.COLOR_GRAY2BGR)

def apply_laplacian_edge(image):
    """Laplacian边缘检测"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # 计算Laplacian（可能产生负值）
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    
    # 取绝对值并转换为8位
    laplacian_abs = cv2.convertScaleAbs(laplacian)
    
    return cv2.cvtColor(laplacian_abs, cv2.COLOR_GRAY2BGR)

# 3. 线性变换函数
def apply_affine_transform(image, angle=0, scale=1.0, tx=0, ty=0):
    """仿射变换"""
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, scale)
    matrix[0, 2] += tx
    matrix[1, 2] += ty
    return cv2.warpAffine(image, matrix, (width, height))

def apply_perspective_transform(image, perspective_strength=0.1):
    """透视变换"""
    height, width = image.shape[:2]
    
    src_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    
    # 根据strength参数控制透视强度
    offset_x = int(width * perspective_strength)
    offset_y = int(height * perspective_strength)
    
    dst_points = np.float32([
        [offset_x, offset_y],
        [width - offset_x, offset_y],
        [offset_x, height - offset_y],
        [width - offset_x, height - offset_y]
    ])
    
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    return cv2.warpPerspective(image, matrix, (width, height))

# 4. 图像锐化函数
def apply_sharpen_filter(image, kernel_size=3):
    """
    应用锐化滤波器
    kernel_size: 滤波器大小，必须是奇数
    """
    # 确保kernel_size是奇数
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # 创建锐化核
    kernel_sharpen = np.zeros((kernel_size, kernel_size), dtype=np.float32)
    center = kernel_size // 2
    
    # 中心为正值，周围为负值
    for i in range(kernel_size):
        for j in range(kernel_size):
            if i == center and j == center:
                kernel_sharpen[i, j] = kernel_size * kernel_size
            else:
                kernel_sharpen[i, j] = -1
    
    # 应用滤波器
    sharpened = cv2.filter2D(image, -1, kernel_sharpen)
    
    # 可选：归一化结果
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    
    return sharpened

def apply_unsharp_masking(image, sigma=1.0, amount=1.0):
    """
    应用非锐化掩蔽
    sigma: 高斯模糊的标准差
    amount: 锐化程度
    """
    # 高斯模糊
    blurred = cv2.GaussianBlur(image, (0, 0), sigma)
    
    # 计算原始与模糊的差异
    detail = cv2.subtract(image, blurred)
    
    # 增强细节并加回原图
    sharpened = cv2.addWeighted(image, 1.0, detail, amount, 0)
    
    # 确保结果在0-255范围内
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    
    return sharpened

def apply_laplacian_sharpening(image):
    """
    拉普拉斯锐化
    """
    # 转换为灰度
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # 拉普拉斯算子
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    
    # 转换为8位并增强
    laplacian = cv2.convertScaleAbs(laplacian)
    
    # 加回原图
    if len(image.shape) == 3:
        # 彩色图像
        result = image.copy().astype(np.float32)
        for i in range(3):
            result[:, :, i] = np.clip(result[:, :, i] + laplacian, 0, 255)
        result = result.astype(np.uint8)
    else:
        # 灰度图像
        result = cv2.addWeighted(gray, 1.0, laplacian, 0.5, 0)
    
    return result

def apply_high_boost_filter(image, A=1.5):
    """
    高频提升滤波
    A: 增强系数，通常>1
    """
    # 低通滤波（模糊）
    low_pass = cv2.GaussianBlur(image, (5, 5), 1.0)
    
    # 高频分量 = 原图 - 低通
    high_freq = cv2.subtract(image, low_pass)
    
    # 高频提升 = 原图 + (A-1) * 高频分量
    result = cv2.addWeighted(image, 1.0, high_freq, A-1, 0)
    
    # 确保结果在有效范围内
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    return result

def apply_adaptive_sharpen(image, strength=0.5):
    """
    自适应锐化，基于边缘检测
    strength: 锐化强度 (0-1)
    """
    # 边缘检测
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    edges = cv2.Canny(gray, 50, 150)
    
    # 创建边缘遮罩
    edges_mask = edges.astype(np.float32) / 255.0
    
    # 应用锐化（仅在有边缘的区域）
    sharpened = apply_unsharp_masking(image, sigma=1.0, amount=strength*3)
    
    # 混合：边缘区域用锐化，其他区域用原图
    if len(image.shape) == 3:
        edges_mask = cv2.cvtColor(edges_mask, cv2.COLOR_GRAY2BGR)
    
    result = image * (1 - edges_mask) + sharpened * edges_mask
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    return result

# 5. 采样与量化函数
def apply_sampling(image, ratio=2):
    """图像采样"""
    height, width = image.shape[:2]
    new_height = max(1, height // ratio)  # 防止除0
    new_width = max(1, width // ratio)
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

def apply_quantization(image, levels=16):
    """图像量化"""
    # 确保levels合理
    levels = max(2, min(256, levels))
    
    step = 256 / levels  # 使用浮点数除法
    
    if len(image.shape) == 3:
        quantized = image.copy().astype(np.float32)
        for i in range(3):
            quantized[:,:,i] = np.round(quantized[:,:,i] / step) * step
    else:
        quantized = np.round(image.astype(np.float32) / step) * step
    
    return np.clip(quantized, 0, 255).astype(np.uint8)

# 6. 彩色图像分割函数
def apply_rgb_segmentation(image, lower_color, upper_color):
    """RGB颜色分割"""
    if len(lower_color) != 3 or len(upper_color) != 3:
        raise ValueError("颜色范围必须是3个值的元组/列表 (B, G, R)")
    
    mask = cv2.inRange(image, lower_color, upper_color)
    result = cv2.bitwise_and(image, image, mask=mask)
    return result

def apply_hsv_segmentation(image, lower_hsv, upper_hsv):
    """HSV颜色分割"""
    if len(lower_hsv) != 3 or len(upper_hsv) != 3:
        raise ValueError("HSV范围必须是3个值的元组/列表 (H, S, V)")
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    result = cv2.bitwise_and(image, image, mask=mask)
    return result

# 7. 颜色通道分析与处理
def split_channels(image):
    """分离RGB通道"""
    if len(image.shape) != 3:
        # 灰度图像处理
        return [image.copy(), image.copy(), image.copy()]
    
    b, g, r = cv2.split(image)
    zeros = np.zeros_like(b)
    
    red_channel = cv2.merge([zeros, zeros, r])
    green_channel = cv2.merge([zeros, g, zeros])
    blue_channel = cv2.merge([b, zeros, zeros])
    
    return [red_channel, green_channel, blue_channel]

def adjust_channel(image, channel_index, value):
    """调整特定通道"""
    adjusted = image.copy()
    
    # 确保channel_index有效
    if channel_index < 0 or channel_index >= adjusted.shape[2]:
        return adjusted
    
    # 使用cv2.add确保不溢出
    adjusted[:,:,channel_index] = cv2.add(adjusted[:,:,channel_index], value)
    
    # 裁剪到有效范围
    adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
    
    return adjusted

def create_channel_histogram(image):
    """创建通道直方图"""
    if len(image.shape) == 3:
        # 彩色图像
        histograms = []
        for i in range(3):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            # 归一化以便比较
            hist = cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
            histograms.append(hist.flatten())
        return histograms
    else:
        # 灰度图像
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return [hist.flatten()]

# 8. 特效处理函数
def add_rain_effect(image, intensity=100, opacity=0.5):
    """添加雨滴特效"""
    rain_layer = np.zeros_like(image, dtype=np.uint8)
    height, width = image.shape[:2]
    
    for _ in range(intensity * 5):  # 增加数量
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        length = random.randint(15, 40)
        thickness = random.randint(1, 3)
        color = random.randint(180, 240)
        
        for i in range(length):
            if y+i < height and x+i//3 < width:
                cv2.line(rain_layer, (x+i//3, y+i), (x+i//3+thickness, y+i), 
                        (color, color, color), thickness)
    
    # 高斯模糊
    rain_layer = cv2.GaussianBlur(rain_layer, (5, 5), 0)
    
    # 添加运动模糊（关键改进）
    kernel_size = 7
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[:, kernel_size//2] = 1.0 / kernel_size
    rain_layer = cv2.filter2D(rain_layer, -1, kernel)
    
    result = cv2.addWeighted(image, 1-opacity, rain_layer, opacity, 0)
    return result

def add_snow_effect(image, intensity=200, opacity=0.3):
    """添加雪花特效"""
    snow_layer = np.zeros_like(image, dtype=np.uint8)
    height, width = image.shape[:2]
    
    # 创建雪花（增加大小变化）
    for _ in range(intensity * 3):  # 增加雪花数量
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        radius = random.randint(1, 5)  # 增加大小范围
        brightness = random.randint(180, 255)  # 增加亮度范围
    
        cv2.circle(snow_layer, (x, y), radius, 
                  (brightness, brightness, brightness), -1)
    
    # 应用轻微模糊
    snow_layer = cv2.GaussianBlur(snow_layer, (5, 5), 0)
    
    # 添加垂直运动模糊（关键改进！）
    kernel = np.array([[0, 0, 0],
                       [1, 1, 1],
                       [0, 0, 0]]) / 3.0
    snow_layer = cv2.filter2D(snow_layer, -1, kernel)
    
    # 叠加雪花层
    result = cv2.addWeighted(image, 1 - opacity, snow_layer, opacity, 0)
    return result

def apply_sakura_effect(image, sakura_intensity):
    """添加樱花特效 - 新增"""
    try:
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        height, width = image.shape[:2]
        sakura_layer = np.zeros((height, width, 4), dtype=np.uint8)  # RGBA
        
        # 樱花数量
        num_sakura = int(sakura_intensity * width * height / 800)
        
        for _ in range(num_sakura):
            # 随机位置
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            
            # 樱花大小
            size = np.random.randint(3, 8)
            
            # 樱花颜色（粉色系）
            pink_color = [
                np.random.randint(230, 255),  # R
                np.random.randint(180, 220),  # G
                np.random.randint(200, 240),  # B
                np.random.randint(150, 220)   # A
            ]
            
            # 绘制樱花（多个花瓣）
            for angle in range(0, 360, 72):
                rad = np.radians(angle)
                px = int(x + size * np.cos(rad))
                py = int(y + size * np.sin(rad))
                cv2.circle(sakura_layer, (px, py), size//2, pink_color, -1)
            
            # 花心
            cv2.circle(sakura_layer, (x, y), size//3, [255, 255, 200, 200], -1)
        
        # 模糊樱花层增加柔和感
        sakura_layer = cv2.GaussianBlur(sakura_layer, (3, 3), 0)
        
        # 分离RGBA通道
        sakura_rgb = sakura_layer[:, :, :3]
        sakura_alpha = sakura_layer[:, :, 3] / 255.0
        
        # 与原始图像混合
        result = image.copy().astype(np.float32)
        for c in range(3):
            result[:, :, c] = result[:, :, c] * (1 - sakura_alpha) + sakura_rgb[:, :, c] * sakura_alpha
        
        return result.astype(np.uint8)
    except Exception as e:
        st.error(f"樱花特效错误: {str(e)}")
        return image


def add_starry_night_effect(image, stars=100):
    """添加星空特效"""
    result = image.copy()
    height, width = image.shape[:2]
    
    # 添加不同大小的星星
    for _ in range(stars * 3):  # 增加星星数量
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        
        # 随机星星大小（1-4像素）
        radius = random.randint(1, 4)
        
        # 星星颜色（不同温度）
        color_choice = random.random()
        if color_choice < 0.6:  # 60% 白色星星
            brightness = random.randint(200, 255)
            color = (brightness, brightness, brightness)
        elif color_choice < 0.8:  # 20% 黄色星星
            brightness = random.randint(180, 230)
            color = (brightness, brightness, brightness // 2)
        else:  # 20% 蓝色星星
            brightness = random.randint(180, 220)
            color = (brightness, brightness - 30, brightness)
        
        # 绘制星星
        cv2.circle(result, (x, y), radius, color, -1)
        
        # 添加星光效果（更自然的形状）
        if random.random() > 0.5:  # 50%的星星有光芒
            # 四向光芒
            for dx, dy in [(2,0), (-2,0), (0,2), (0,-2)]:
                px = min(max(x + dx, 0), width-1)
                py = min(max(y + dy, 0), height-1)
                cv2.circle(result, (px, py), max(1, radius-1), color, -1)
            
            # 对角光芒
            if random.random() > 0.5:
                for dx, dy in [(2,2), (-2,2), (2,-2), (-2,-2)]:
                    px = min(max(x + dx, 0), width-1)
                    py = min(max(y + dy, 0), height-1)
                    cv2.circle(result, (px, py), 1, color, -1)
    
    # 添加高斯模糊使星星更柔和
    result = cv2.GaussianBlur(result, (3, 3), 0)
    
    # 添加一些特别亮的星星
    for _ in range(stars // 5):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        
        # 绘制亮星
        cv2.circle(result, (x, y), 2, (255, 255, 255), -1)
        
        # 添加光晕效果
        for r in range(3, 6):
            alpha = 0.5 * (1 - (r-3)/3)  # 光晕渐变
            color_with_alpha = tuple(int(255 * alpha) for _ in range(3))
            cv2.circle(result, (x, y), r, color_with_alpha, 1)
    
    return result

# 9. 图像绘画处理函数

def apply_oil_painting_effect(image, radius=3, intensity=30, enhance_color=True):
    """油画效果"""
    # 确保输入是uint8
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    
    try:
        oil_painting = cv2.xphoto.oilPainting(image, radius, intensity)
    except:
        # 如果xphoto不可用，使用替代方法
        oil_painting = cv2.stylization(image, sigma_s=60, sigma_r=0.6)
    
    if enhance_color:
        # 增强色彩饱和度
        hsv = cv2.cvtColor(oil_painting, cv2.COLOR_BGR2HSV)
        hsv = hsv.astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255)
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        oil_painting = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return oil_painting.astype(np.uint8)

def apply_pencil_sketch_effect(image, style="elegant", intensity=1.0):
    """素描效果"""
    # 确保输入是uint8
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    
    if style == "elegant":
        # 优雅风格 - 使用颜色减淡算法
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inverted, (21, 21), 3)
        
        # 避免除零错误
        denominator = 255 - blurred
        denominator[denominator == 0] = 1
        
        sketch = cv2.divide(gray, denominator, scale=256)
        sketch = cv2.convertScaleAbs(sketch, alpha=1.3 * intensity, beta=0)
        
        # 转换为彩色
        sketch_color = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        return sketch_color.astype(np.uint8)
    
    elif style == "artistic":
        # 艺术风格
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用Canny边缘检测和模糊混合
        edges = cv2.Canny(gray, 50, 150)
        blurred = cv2.GaussianBlur(gray, (5, 5), 2)
        
        # 混合边缘和模糊
        sketch = cv2.addWeighted(blurred, 0.8, edges, 0.2, 0)
        sketch = 255 - sketch  # 反相
        
        # 转换为彩色
        sketch_color = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        return sketch_color.astype(np.uint8)
    
    else:  # classic
        # 使用OpenCV内置函数
        try:
            _, sketch = cv2.pencilSketch(image, sigma_s=120, sigma_r=0.1)
            sketch = cv2.convertScaleAbs(sketch, alpha=1.4, beta=10)
            sketch_color = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
            return sketch_color.astype(np.uint8)
        except:
            # 备用方案
            return apply_pencil_sketch_effect(image, style="elegant", intensity=intensity)

def apply_ink_wash_painting_effect(image, ink_strength=0.4, paper_texture=True):
    """水墨画效果 - 简化版，避免复杂运算"""
    # 确保输入是uint8
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    
    try:
        # 转换为灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 增强对比度
        gray = cv2.equalizeHist(gray)
        
        # 双边滤波模拟水墨扩散
        filtered = cv2.bilateralFilter(gray, 9, 150, 150)
        
        # 高斯模糊创建晕染效果
        blurred = cv2.GaussianBlur(filtered, (15, 15), 5)
        
        # 边缘检测
        edges = cv2.adaptiveThreshold(filtered, 255,
                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, 25, 10)
        
        # 转换为彩色
        ink_color = cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)
        edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # 降低饱和度（创建水墨感）
        hsv = cv2.cvtColor(ink_color, cv2.COLOR_BGR2HSV)
        hsv = hsv.astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * 0.3  # 大幅降低饱和度
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        ink_color = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # 创建简单的边缘mask
        edges_float = edges.astype(np.float32) / 255.0
        
        # 直接应用边缘（简化版，避免复杂的mask操作）
        edges_expanded = np.stack([edges_float, edges_float, edges_float], axis=2)
        
        # 混合墨迹和边缘
        result = ink_color * (1 - edges_expanded * ink_strength) + edges_color * edges_expanded * ink_strength * 0.3
        
        # 添加轻微模糊
        result = cv2.GaussianBlur(result, (5, 5), 2)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    except Exception as e:
        # 如果出错，返回一个简单的灰度版本
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return result.astype(np.uint8)

def apply_comic_effect(image, edge_threshold=50, color_style="vibrant"):
    """漫画效果 - 简化版"""
    # 确保输入是uint8
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    
    try:
        # 1. 轻微模糊减少噪点
        smoothed = cv2.bilateralFilter(image, 7, 50, 50)
        
        # 2. 边缘检测
        gray = cv2.cvtColor(smoothed, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, edge_threshold, edge_threshold * 2)
        
        # 3. 根据风格处理颜色
        if color_style == "vibrant":
            # 鲜艳风格 - 增加对比度和饱和度
            lab = cv2.cvtColor(smoothed, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            lab = cv2.merge([l, a, b])
            color_enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            # 增加饱和度
            hsv = cv2.cvtColor(color_enhanced, cv2.COLOR_BGR2HSV)
            hsv = hsv.astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.5, 0, 255)
            hsv = np.clip(hsv, 0, 255).astype(np.uint8)
            color_enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
        elif color_style == "soft":
            # 柔和风格 - 使用stylization
            color_enhanced = cv2.stylization(smoothed, sigma_s=60, sigma_r=0.3)
            
        else:  # cel风格
            # 简单量化
            color_enhanced = cv2.stylization(smoothed, sigma_s=100, sigma_r=0.1)
        
        # 4. 创建边缘mask
        edges_float = edges.astype(np.float32) / 255.0
        edges_mask = np.stack([edges_float, edges_float, edges_float], axis=2)
        
        # 5. 描边颜色
        if color_style == "soft":
            outline_color = np.array([[[60, 60, 60]]], dtype=np.float32)
        else:
            outline_color = np.array([[[10, 10, 10]]], dtype=np.float32)
        
        # 6. 应用描边
        result = color_enhanced.astype(np.float32) * (1 - edges_mask) + outline_color * edges_mask
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    except Exception as e:
        # 备用方案
        return image.astype(np.uint8)

def apply_watercolor_effect(image, style="classic", texture_strength=0.3):
    """水彩画效果 - 简化版"""
    # 确保输入是uint8
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    
    try:
        if style == "classic":
            # 经典风格 - 使用stylization
            result = cv2.stylization(image, sigma_s=100, sigma_r=0.4)
            
            # 增加饱和度
            hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
            hsv = hsv.astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.3, 0, 255)
            hsv = np.clip(hsv, 0, 255).astype(np.uint8)
            result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
        else:  # modern
            # 现代风格 - detailEnhance
            result = cv2.detailEnhance(image, sigma_s=10, sigma_r=0.15)
            
            # 边缘保留模糊
            blurred = cv2.bilateralFilter(result, 7, 100, 100)
            result = cv2.addWeighted(result, 0.7, blurred, 0.3, 0)
        
        # 轻微模糊使效果更柔和
        result = cv2.GaussianBlur(result, (3, 3), 0.5)
        
        return result.astype(np.uint8)
    
    except Exception as e:
        # 备用方案
        return cv2.stylization(image, sigma_s=60, sigma_r=0.3).astype(np.uint8)

def apply_pop_art_effect(image, style="warhol", num_colors=8):
    """波普艺术效果 - 简化版"""
    # 确保输入是uint8
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    
    try:
        # 调整图像大小以提高处理速度
        height, width = image.shape[:2]
        if height * width > 800 * 600:
            scale = min(800 / width, 600 / height)
            small = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        else:
            small = image
        
        # 使用K-means进行颜色量化
        pixels = small.reshape((-1, 3))
        pixels = np.float32(pixels)
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        num_colors = min(num_colors, 12)
        
        _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # 转换为8位
        centers = np.uint8(centers)
        
        # 重塑图像
        quantized = centers[labels.flatten()]
        quantized = quantized.reshape(small.shape)
        
        # 增加对比度
        result = cv2.convertScaleAbs(quantized, alpha=1.2, beta=0)
        
        # 如果需要，调整回原始大小
        if height * width > 800 * 600:
            result = cv2.resize(result, (width, height), interpolation=cv2.INTER_NEAREST)
        
        return result.astype(np.uint8)
    
    except Exception as e:
        # 备用方案 - 简单的颜色量化
        Z = image.reshape((-1,3))
        Z = np.float32(Z)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = 8
        ret,label,center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        res = center[label.flatten()]
        result = res.reshape(image.shape)
        return result.astype(np.uint8)

def apply_impressionist_effect(image, brush_size=3):
    """印象派效果 - 简化版"""
    # 确保输入是uint8
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    
    try:
        # 创建模糊效果
        blurred1 = cv2.GaussianBlur(image, (brush_size*2+1, brush_size*2+1), 0)
        blurred2 = cv2.bilateralFilter(image, 9, 75, 75)
        
        # 混合效果
        result = cv2.addWeighted(blurred1, 0.5, blurred2, 0.5, 0)
        
        # 增强颜色
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
        hsv = hsv.astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255)
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return result.astype(np.uint8)
    
    except Exception as e:
        # 备用方案
        return cv2.GaussianBlur(image, (11, 11), 0).astype(np.uint8)

def apply_pastel_effect(image, softness=0.7):
    """粉彩画效果 - 简化版"""
    # 确保输入是uint8
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    
    try:
        # 深度模糊
        blurred = cv2.bilateralFilter(image, 9, 150, 150)
        
        # 提高亮度
        lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.add(l, 30)
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # 添加光晕效果
        bloom = cv2.GaussianBlur(result, (0, 0), 10)
        result = cv2.addWeighted(result, 0.9, bloom, 0.1, 0)
        
        return result.astype(np.uint8)
    
    except Exception as e:
        # 备用方案
        return cv2.bilateralFilter(image, 9, 150, 150).astype(np.uint8)



# 10. 风格迁移效果
def apply_van_gogh_style(image, twist_strength=0.001):
    """梵高风格（简化版）- 减小旋转程度"""
    height, width = image.shape[:2]
    
    # 1. 增强色彩饱和度
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:,:,1] = cv2.multiply(hsv[:,:,1], 1.5).clip(0, 255)
    vivid = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    # 2. 添加油画效果
    oil_painting = cv2.xphoto.oilPainting(vivid, 7, 30)
    
    # 3. 添加旋转扭曲（减小旋转强度）
    result = np.zeros_like(oil_painting, dtype=np.float32)
    center_x, center_y = width // 2, height // 2
    
    # 使用矢量操作加速
    y_coords, x_coords = np.mgrid[0:height, 0:width]
    dx = x_coords - center_x
    dy = y_coords - center_y
    distance = np.sqrt(dx*dx + dy*dy)
    
    # 使用较小的扭曲强度
    twist_angle = distance * twist_strength
    angle = np.arctan2(dy, dx) + twist_angle
    
    src_x = (center_x + distance * np.cos(angle)).astype(np.int32)
    src_y = (center_y + distance * np.sin(angle)).astype(np.int32)
    
    # 边界检查
    src_x = np.clip(src_x, 0, width-1)
    src_y = np.clip(src_y, 0, height-1)
    
    result = oil_painting[src_y, src_x]
    
    return result.astype(np.uint8)

def apply_starry_sky_style(image):
    """星空风格（梵高《星空》效果）- 优化"""
    # 1. 增强蓝色调和黄色调
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # 增加蓝色和黄色
    b = cv2.add(b, 25).clip(0, 255)
    a = cv2.add(a, 10).clip(0, 255)
    
    lab = cv2.merge([l, a, b])
    color_tone = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # 2. 应用梵高风格（使用更小的旋转）
    van_gogh_style = apply_van_gogh_style(color_tone, 0.0008)
    
    # 3. 添加旋涡效果
    height, width = van_gogh_style.shape[:2]
    result = van_gogh_style.copy()
    
    # 添加多个旋转中心
    centers = [
        (width//4, height//4),
        (width*3//4, height//4),
        (width//4, height*3//4),
        (width*3//4, height*3//4)
    ]
    
    for center_x, center_y in centers:
        for y in range(max(0, center_y-50), min(height, center_y+50)):
            for x in range(max(0, center_x-50), min(width, center_x+50)):
                dx = x - center_x
                dy = y - center_y
                distance = np.sqrt(dx*dx + dy*dy)
                
                if distance < 50:
                    # 轻微的旋涡效果
                    twist_angle = (50 - distance) * 0.01
                    src_x = int(center_x + distance * np.cos(np.arctan2(dy, dx) + twist_angle))
                    src_y = int(center_y + distance * np.sin(np.arctan2(dy, dx) + twist_angle))
                    
                    src_x = max(0, min(src_x, width-1))
                    src_y = max(0, min(src_y, height-1))
                    
                    result[y, x] = van_gogh_style[src_y, src_x]
    
    # 4. 添加星星
    for _ in range(150):
        x = random.randint(20, width-20)
        y = random.randint(20, height-20)
        
        # 梵高风格的星星（更自然的星芒效果）
        size = random.randint(1, 2)
        brightness = random.randint(220, 255)
        
        # 绘制星芒
        for angle in range(0, 360, 45):
            rad = np.deg2rad(angle)
            end_x = int(x + 6 * np.cos(rad))
            end_y = int(y + 6 * np.sin(rad))
            cv2.line(result, (x, y), (end_x, end_y), 
                    (brightness, brightness, brightness), 1)
        
        # 绘制中心光点
        cv2.circle(result, (x, y), size, 
                  (brightness, brightness, brightness), -1)
    
    return result

def apply_monet_style(image):
    """莫奈印象派风格"""
    height, width = image.shape[:2]
    
    # 1. 柔和的颜色模糊（印象派特点）
    blurred = cv2.bilateralFilter(image, 15, 80, 80)
    
    # 2. 添加笔触效果
    brush_strokes = np.zeros_like(blurred, dtype=np.float32)
    
    # 创建随机笔触
    brush_size = 10
    for y in range(0, height, brush_size):
        for x in range(0, width, brush_size):
            # 随机选择笔触方向
            angle = random.uniform(0, 2*np.pi)
            length = random.randint(brush_size, brush_size*2)
            
            end_x = int(x + length * np.cos(angle))
            end_y = int(y + length * np.sin(angle))
            
            end_x = max(0, min(end_x, width-1))
            end_y = max(0, min(end_y, height-1))
            
            # 使用线段颜色填充矩形区域
            color = blurred[y, x].astype(float)
            cv2.line(brush_strokes, (x, y), (end_x, end_y), color, brush_size)
    
    brush_strokes = brush_strokes.astype(np.uint8)
    
    # 3. 增强颜色（莫奈的鲜艳色彩）
    hsv = cv2.cvtColor(brush_strokes, cv2.COLOR_BGR2HSV)
    
    # 增加饱和度
    hsv[:,:,1] = cv2.multiply(hsv[:,:,1], 1.3).clip(0, 255)
    
    # 调整色调（偏向蓝色和紫色）
    hsv[:,:,0] = cv2.add(hsv[:,:,0], 10).clip(0, 255)
    
    # 轻微提高亮度
    hsv[:,:,2] = cv2.multiply(hsv[:,:,2], 1.1).clip(0, 255)
    
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    # 4. 添加光晕效果
    glow = cv2.GaussianBlur(result, (0, 0), 15)
    result = cv2.addWeighted(result, 0.7, glow, 0.3, 0)
    
    # 5. 添加画布纹理
    texture = np.random.randn(height, width) * 10 + 128
    texture = np.clip(texture, 100, 150).astype(np.uint8)
    texture_bgr = cv2.cvtColor(texture, cv2.COLOR_GRAY2BGR)
    
    result = cv2.addWeighted(result, 0.95, texture_bgr, 0.05, 0)
    
    return result

def apply_picasso_cubist_style(image):
    """毕加索立体主义风格"""
    height, width = image.shape[:2]
    
    # 1. 分割图像为多个几何区域
    result = np.zeros_like(image)
    
    # 创建网格分割
    grid_size = min(height, width) // 8
    
    for y in range(0, height, grid_size):
        for x in range(0, width, grid_size):
            # 随机变形网格
            offset_x = random.randint(-grid_size//2, grid_size//2)
            offset_y = random.randint(-grid_size//2, grid_size//2)
            
            end_x = min(x + grid_size + offset_x, width)
            end_y = min(y + grid_size + offset_y, height)
            
            # 获取区域平均颜色
            region = image[max(0, y):end_y, max(0, x):end_x]
            if region.size > 0:
                avg_color = cv2.mean(region)[:3]
                
                # 绘制几何形状
                shape_type = random.choice(['triangle', 'rectangle', 'polygon'])
                
                if shape_type == 'triangle':
                    # 绘制三角形
                    pts = np.array([
                        [x, y],
                        [x + grid_size, y],
                        [x + grid_size//2, y + grid_size]
                    ], np.int32)
                    cv2.fillPoly(result, [pts], avg_color)
                    
                elif shape_type == 'rectangle':
                    # 绘制矩形（可能旋转）
                    angle = random.uniform(-30, 30)
                    center = (x + grid_size//2, y + grid_size//2)
                    rect = ((x + grid_size//2, y + grid_size//2), 
                           (grid_size, grid_size), angle)
                    
                    box = cv2.boxPoints(rect)
                    # 修改这里：将 np.int0 改为 np.int32
                    box = np.int32(box)  # 或者 box.astype(np.int32)
                    cv2.fillPoly(result, [box], avg_color)
                    
                else:  # polygon
                    # 绘制多边形
                    num_sides = random.randint(3, 6)
                    radius = grid_size // 2
                    center = (x + grid_size//2, y + grid_size//2)
                    
                    pts = []
                    for i in range(num_sides):
                        angle = 2 * np.pi * i / num_sides + random.uniform(-0.2, 0.2)
                        px = center[0] + radius * np.cos(angle)
                        py = center[1] + radius * np.sin(angle)
                        pts.append([px, py])
                    
                    pts = np.array(pts, np.int32)
                    cv2.fillPoly(result, [pts], avg_color)
    
    # 2. 增强边缘（立体主义的特点）
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
    
    # 添加黑色轮廓
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    result = cv2.bitwise_and(result, cv2.bitwise_not(edges_bgr))
    
    # 3. 颜色简化（立体主义的有限色彩）
    pixels = result.reshape((-1, 3))
    pixels = np.float32(pixels)
    
    # 使用K-means减少颜色数量
    k = 8
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    centers = np.uint8(centers)
    simplified = centers[labels.flatten()]
    result = simplified.reshape(result.shape)
    
    # 4. 增强对比度
    lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # 增强亮度通道的对比度
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    lab = cv2.merge([l, a, b])
    result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    return result

def apply_anime_style(image):
    """动漫风格"""
    # 1. 边缘检测（用于描边）
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 双边滤波保留边缘
    filtered = cv2.bilateralFilter(image, 9, 75, 75)
    
    # 使用DoG边缘检测
    g1 = cv2.GaussianBlur(gray, (5, 5), 0.5)
    g2 = cv2.GaussianBlur(gray, (5, 5), 2.0)
    dog = g1 - g2
    
    # 二值化边缘
    _, edges = cv2.threshold(dog, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # 细化边缘
    edges = cv2.ximgproc.thinning(edges)
    
    # 2. 颜色平坦化（动漫的平坦着色）
    # 使用均值漂移减少颜色变化
    filtered_ms = cv2.pyrMeanShiftFiltering(filtered, 20, 50)
    
    # 3. 增强饱和度
    hsv = cv2.cvtColor(filtered_ms, cv2.COLOR_BGR2HSV)
    hsv[:,:,1] = cv2.multiply(hsv[:,:,1], 1.4).clip(0, 255)
    hsv[:,:,2] = cv2.multiply(hsv[:,:,2], 1.2).clip(0, 255)
    enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    # 4. 添加阴影效果
    height, width = enhanced.shape[:2]
    
    # 创建简单光源效果
    y_coords, x_coords = np.mgrid[0:height, 0:width]
    
    # 从左上角的光源
    light_source = np.sqrt((x_coords/width)**2 + (y_coords/height)**2)
    light_source = 1 - light_source * 0.3
    
    # 应用光照效果
    result = enhanced.astype(np.float32) * light_source[:,:,np.newaxis]
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    # 5. 添加黑色轮廓
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # 轮廓颜色可选（黑色或深色）
    outline_color = (30, 30, 30)
    edges_colored = cv2.bitwise_and(edges_bgr, outline_color)
    
    # 应用轮廓
    result = cv2.subtract(result, edges_colored)
    
    # 6. 添加高光效果
    # 在边缘区域添加高光
    highlight_mask = cv2.erode(edges, np.ones((2,2), np.uint8))
    
    # 添加白色高光
    result = cv2.addWeighted(result, 1.0, 
                           cv2.cvtColor(highlight_mask, cv2.COLOR_GRAY2BGR), 
                           0.1, 0)
    
    return result

# 11. 老照片上色
def colorize_old_photo(image, color_intensity=1.0, ai_assist=True):
    """
    真正的黑白照片上色函数
    将灰度图像智能上色为彩色
    
    参数:
    - image: 输入图像（BGR格式）
    - color_intensity: 色彩强度 (0.5-1.5)
    - ai_assist: 是否使用AI辅助（简化版）
    
    返回:
    - colorized: 上色后的图像
    """
    # 确保图像是BGR格式
    if len(image.shape) == 2:
        # 如果是灰度图，转换为3通道BGR
        gray = image.copy()
        image_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:
        # 如果是RGBA，转换为BGR
        image_bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    else:
        image_bgr = image.copy()
    
    # 确保是uint8类型
    if image_bgr.dtype != np.uint8:
        image_bgr = image_bgr.astype(np.uint8)
    
    # 1. 预处理：增强对比度，去除噪点
    # 转换为LAB颜色空间
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # 使用CLAHE增强亮度对比度
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    
    # 2. 智能区域检测（简化版AI辅助）
    gray_float = l_enhanced.astype(np.float32) / 255.0
    
    # 根据亮度创建区域掩码
    # 天空/高亮区域
    sky_mask = (gray_float > 0.7).astype(np.uint8) * 255
    
    # 地面/中等亮度区域
    ground_mask = ((gray_float > 0.3) & (gray_float <= 0.7)).astype(np.uint8) * 255
    
    # 植被区域（通过纹理检测）
    sobelx = cv2.Sobel(l_enhanced, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(l_enhanced, cv2.CV_64F, 0, 1, ksize=3)
    gradient = np.sqrt(sobelx**2 + sobely**2)
    texture_mask = (gradient > np.percentile(gradient, 70)).astype(np.uint8) * 255
    
    # 人物/建筑区域（通过边缘检测）
    edges = cv2.Canny(l_enhanced, 50, 150)
    
    # 3. 智能上色：为不同区域分配颜色
    # 初始化彩色通道（BGR顺序）
    colored_b = np.zeros_like(l_enhanced, dtype=np.float32)
    colored_g = np.zeros_like(l_enhanced, dtype=np.float32)
    colored_r = np.zeros_like(l_enhanced, dtype=np.float32)
    
    # 像素级智能上色
    height, width = l_enhanced.shape
    
    for i in range(height):
        for j in range(width):
            brightness = l_enhanced[i, j] / 255.0
            
            # 区域判断
            is_sky = sky_mask[i, j] > 0
            is_ground = ground_mask[i, j] > 0
            is_textured = texture_mask[i, j] > 0
            has_edge = edges[i, j] > 0
            
            # 智能上色规则
            if is_sky:
                # 天空：蓝色调，亮度越高越蓝
                blue_intensity = 0.7 + brightness * 0.3
                green_intensity = 0.5 + brightness * 0.2
                red_intensity = 0.3 + brightness * 0.2
            elif is_textured and not has_edge:
                # 植被：绿色调
                if brightness > 0.4:
                    green_intensity = 0.6 + brightness * 0.4
                    blue_intensity = 0.2 + brightness * 0.2
                    red_intensity = 0.1 + brightness * 0.2
                else:
                    # 深色植被
                    green_intensity = 0.3 + brightness * 0.3
                    blue_intensity = 0.1 + brightness * 0.2
                    red_intensity = 0.05 + brightness * 0.1
            elif has_edge and brightness > 0.5:
                # 建筑/人物边缘：暖色调
                red_intensity = 0.6 + brightness * 0.4
                green_intensity = 0.5 + brightness * 0.3
                blue_intensity = 0.3 + brightness * 0.2
            elif is_ground:
                # 地面：土黄色调
                red_intensity = 0.5 + brightness * 0.3
                green_intensity = 0.4 + brightness * 0.3
                blue_intensity = 0.2 + brightness * 0.2
            else:
                # 默认：根据亮度调整颜色
                if brightness > 0.7:
                    # 高亮区域：浅黄色
                    red_intensity = 0.8 + brightness * 0.2
                    green_intensity = 0.7 + brightness * 0.2
                    blue_intensity = 0.5 + brightness * 0.2
                elif brightness > 0.4:
                    # 中等亮度：中性色
                    red_intensity = 0.5 + brightness * 0.3
                    green_intensity = 0.5 + brightness * 0.3
                    blue_intensity = 0.5 + brightness * 0.3
                else:
                    # 暗部：冷色调
                    red_intensity = 0.2 + brightness * 0.2
                    green_intensity = 0.3 + brightness * 0.2
                    blue_intensity = 0.4 + brightness * 0.3
            
            # 应用颜色强度
            colored_r[i, j] = red_intensity * brightness * 255 * color_intensity
            colored_g[i, j] = green_intensity * brightness * 255 * color_intensity
            colored_b[i, j] = blue_intensity * brightness * 255 * color_intensity
    
    # 4. 合并彩色通道
    colored_r = np.clip(colored_r, 0, 255).astype(np.uint8)
    colored_g = np.clip(colored_g, 0, 255).astype(np.uint8)
    colored_b = np.clip(colored_b, 0, 255).astype(np.uint8)
    
    colorized = cv2.merge([colored_b, colored_g, colored_r])
    
    # 5. 后处理：颜色混合和增强
    # 将原始亮度与颜色混合
    colored_lab = cv2.cvtColor(colorized, cv2.COLOR_BGR2LAB)
    cl, ca, cb = cv2.split(colored_lab)
    
    # 保持原始亮度，只使用上色的色度信息
    result_lab = cv2.merge([l_enhanced, ca, cb])
    result = cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)
    
    # 6. 添加复古效果
    # 轻微暖色调滤镜
    warm_filter = np.array([
        [1.1, 0.0, 0.0],
        [0.0, 0.9, 0.0],
        [0.0, 0.0, 0.8]
    ], dtype=np.float32)
    
    warm_result = cv2.transform(result, warm_filter)
    warm_result = np.clip(warm_result, 0, 255).astype(np.uint8)
    
    # 混合：80%上色 + 20%怀旧暖色
    final = cv2.addWeighted(result, 0.8, warm_result, 0.2, 0)
    
    # 7. 颜色调整和增强
    hsv = cv2.cvtColor(final, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # 增加饱和度
    s_enhanced = cv2.multiply(s, color_intensity).clip(0, 255)
    
    # 稍微调整色调，使其更自然
    h_enhanced = h.copy()
    h_shift = 5  # 轻微色调偏移
    h_enhanced = (h_enhanced + h_shift) % 180
    
    # 合并HSV
    hsv_enhanced = cv2.merge([h_enhanced, s_enhanced, v])
    final_enhanced = cv2.cvtColor(hsv_enhanced, cv2.COLOR_HSV2BGR)
    
    # 8. 添加轻微胶片颗粒效果（可选）
    if ai_assist:
        # 添加轻微的噪点模拟胶片颗粒
        noise = np.random.normal(0, 2, final_enhanced.shape).astype(np.int16)
        final_with_noise = cv2.add(final_enhanced.astype(np.int16), noise)
        final_enhanced = np.clip(final_with_noise, 0, 255).astype(np.uint8)
    
    # 9. 最后轻微模糊，使颜色过渡更自然
    final_enhanced = cv2.GaussianBlur(final_enhanced, (3, 3), 0.5)
    
    return final_enhanced
def apply_deep_learning_colorization(image):
    """
    深度学习风格的上色（简化版）
    使用预训练的规则模拟深度学习效果
    """
    # 先使用基础的上色
    base_colorized = colorize_old_photo(image)
    
    # 增加颜色丰富度
    hsv = cv2.cvtColor(base_colorized, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # 深度学习风格通常颜色更鲜艳
    s = cv2.multiply(s, 1.3).clip(0, 255)
    
    # 稍微降低亮度，增加对比度
    v = cv2.convertScaleAbs(v, alpha=1.1, beta=-20)
    
    # 色调微调
    h_shifted = (h + 10) % 180  # 稍微调整色调
    
    hsv_enhanced = cv2.merge([h_shifted, s, v])
    result = cv2.cvtColor(hsv_enhanced, cv2.COLOR_HSV2BGR)
    
    return result

def apply_selective_colorization(image, focus_areas='auto'):
    """
    选择性焦点上色
    focus_areas: 'auto', 'center', 'faces', 'full'
    """
    base_colorized = colorize_old_photo(image)
    
    if focus_areas == 'full':
        return base_colorized
    
    # 创建灰度版本
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if len(gray.shape) == 2:
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    else:
        gray_bgr = gray
    
    # 创建焦点掩码
    height, width = image.shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    
    if focus_areas == 'center':
        # 中心区域上色
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 3
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
    elif focus_areas == 'auto':
        # 自动检测重要区域（基于边缘密度）
        edges = cv2.Canny(gray, 50, 150)
        
        # 使用形态学操作找到边缘密集区域
        kernel = np.ones((15, 15), np.uint8)
        edges_dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # 找到轮廓
        contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 绘制主要区域
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > (width * height * 0.01):  # 只处理足够大的区域
                cv2.drawContours(mask, [contour], -1, 255, -1)
    else:  # faces
        # 人脸检测（需要OpenCV的人脸检测器）
        try:
            # 转换为灰度进行人脸检测
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(mask, (x, y), (x+w, y+h), 255, -1)
        except:
            # 如果人脸检测失败，使用中心区域
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 4
            cv2.circle(mask, (center_x, center_y), radius, 255, -1)
    
    # 模糊掩码边缘，使过渡更平滑
    mask = cv2.GaussianBlur(mask, (31, 31), 0)
    mask = mask.astype(np.float32) / 255.0
    mask = cv2.merge([mask, mask, mask])
    
    # 混合彩色和灰度版本
    result = cv2.addWeighted(base_colorized.astype(np.float32), mask, 
                             gray_bgr.astype(np.float32), 1.0 - mask, 0)
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    return result

def apply_erosion(image, kernel_size=3):
    """腐蚀操作（增强版）"""
    # 使用椭圆核通常效果更好
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # 对于小物体去除，先进行腐蚀
    eroded = cv2.erode(image, kernel, iterations=1)
    
    # 如果图像是彩色的，对每个通道分别处理（可选）
    if len(image.shape) == 3:
        # 分离通道处理
        channels = cv2.split(eroded)
        processed_channels = []
        for channel in channels:
            # 对每个通道应用轻度腐蚀
            processed = cv2.erode(channel, kernel, iterations=1)
            processed_channels.append(processed)
        
        # 合并通道
        eroded = cv2.merge(processed_channels)
    
    return eroded

def apply_dilation(image, kernel_size=3):
    """膨胀操作（增强版）"""
    # 使用椭圆核效果更自然
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # 对于连接断裂，先进行膨胀
    dilated = cv2.dilate(image, kernel, iterations=1)
    
    # 如果图像是彩色的，可以增强边缘效果
    if len(image.shape) == 3:
        # 转换为HSV，增强V通道
        hsv = cv2.cvtColor(dilated, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # 对亮度通道进行额外膨胀（增强效果）
        v = cv2.dilate(v, kernel, iterations=1)
        
        # 合并并转换回BGR
        hsv = cv2.merge([h, s, v])
        dilated = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return dilated

def apply_opening(image, kernel_size=3):
    """开运算（增强版）- 去除小物体"""
    # 使用椭圆核，效果比矩形核更平滑
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # 标准开运算
    opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    
    # 如果图像是灰度图，可以添加对比度增强
    if len(image.shape) == 2:
        # 对开运算后的图像进行直方图均衡化
        opened = cv2.equalizeHist(opened)
    elif len(image.shape) == 3:
        # 对彩色图像，增强边缘对比度
        edges = cv2.Canny(opened, 50, 150)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # 将边缘叠加到开运算结果上
        opened = cv2.addWeighted(opened, 0.8, edges_colored, 0.2, 0)
    
    return opened

def apply_closing(image, kernel_size=3):
    """闭运算（增强版）- 填充小孔洞"""
    # 使用椭圆核
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # 标准闭运算
    closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    
    # 增强效果：如果图像是二值图，可以优化
    if len(image.shape) == 2:
        # 闭运算后可能还有小孔洞，进行填充
        contours, _ = cv2.findContours(closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 50:  # 填充小孔洞
                cv2.drawContours(closed, [contour], 0, 255, -1)
    
    return closed

def provide_download_button(image_rgb, filename, button_text, unique_key_suffix=""):
    """
    提供下载按钮 - 专门用于RGB图像
    
    Args:
        image_rgb: RGB格式的图像数组
        filename: 下载文件名
        button_text: 按钮文本
        unique_key_suffix: 唯一key后缀，防止重复ID
    """
    try:
        # 确保图像是RGB格式
        if len(image_rgb.shape) != 3 or image_rgb.shape[2] != 3:
            raise ValueError("图像必须是RGB格式 (H,W,3)")
        
        # 转换为PIL图像
        image_pil = Image.fromarray(image_rgb)
        
        # 保存到字节流
        buffered = io.BytesIO()
        image_pil.save(buffered, format="JPEG", quality=95)
        
        # 生成唯一key
        import time
        import hashlib
        timestamp = int(time.time() * 1000)
        
        # 使用图像内容哈希和当前时间生成唯一key
        image_hash = hashlib.md5(image_rgb.tobytes()).hexdigest()[:8]
        unique_key = f"download_{filename}_{image_hash}_{timestamp}_{unique_key_suffix}"
        
        # 下载按钮
        st.download_button(
            label=button_text,
            data=buffered.getvalue(),
            file_name=filename,
            mime="image/jpeg",
            use_container_width=True,
            key=unique_key
        )
        
    except Exception as e:
        st.error(f"下载功能出错: {str(e)}")
# ======================= 侧边栏渲染 =======================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; 
                    padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px;
                    box-shadow: 0 6px 12px rgba(220, 38, 38, 0.3); border: 2px solid #f59e0b;'>
            <h3 style='margin: 0;'>🔬 图像处理实验室</h3>
            <p style='margin: 10px 0 0 0;'>技术报国 · 创新发展 · 思政引领</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 快速导航
        st.markdown("### 🧭 快速导航")
        
        # 修复导航按钮
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("main.py")
        if st.button("🔬 图像处理实验室", use_container_width=True):
            st.switch_page("pages/1_🔬_图像处理实验室.py")
        if st.button("📚 学习资源中心", use_container_width=True):
            st.switch_page("pages/2_📚_学习资源中心.py")
        if st.button("📝 我的思政足迹", use_container_width=True):
            st.switch_page("pages/3_📝_我的思政足迹.py")
        if st.button("🏆 成果展示", use_container_width=True):
            st.switch_page("pages/4_🏆_成果展示.py")
        
        # 思政学习进度
        st.markdown("### 📚 思政学习进度")
        
        ideology_progress = [
            {"name": "工匠精神", "icon": "🔧", "progress": 85},
            {"name": "科学态度", "icon": "🔬", "progress": 78},
            {"name": "创新意识", "icon": "💡", "progress": 82},
            {"name": "责任担当", "icon": "⚖️", "progress": 88}
        ]
        
        for item in ideology_progress:
            st.markdown(f"**{item['icon']} {item['name']}**")
            st.progress(item['progress'] / 100)
        
        st.markdown("---")
        
        # 实验指南
        st.markdown("""
        <div class='info-card'>
            <h4>📚 实验指南</h4>
            <ol style='padding-left: 20px;'>
                <li>选择实验模块</li>
                <li>上传图像文件</li>
                <li>调整处理参数</li>
                <li>查看实时效果</li>
                <li>记录学习感悟</li>
            </ol>
            <p><strong>支持格式：</strong> JPG, PNG, JPEG, PDF, DOC, DOCX, ZIP</p>
        </div>
        """, unsafe_allow_html=True)
        # 思政理论学习
        st.markdown("### 🎯 思政理论学习")
        theory_topics = [
            "图像处理中的工匠精神",
            "科技创新与国家发展",
            "技术伦理与社会责任",
            "科学家精神传承"
        ]
        
        for topic in theory_topics:
            if st.button(f"📖 {topic}", key=f"theory_{topic}", use_container_width=True):
                st.info(f"开始学习：{topic}")
        
        st.markdown("---")
        # 思政教育提示
        st.markdown("""
        <div class='ideology-card'>
            <h5>💡 思政教育提示</h5>
            <p style='font-size: 0.9rem;'>在技术学习中培养：</p>
            <ul style='padding-left: 15px; font-size: 0.85rem;'>
                <li>🎯 精益求精的工匠精神</li>
                <li>🔬 实事求是的科学态度</li>
                <li>💡 创新发展的时代担当</li>
                <li>🇨🇳 科技报国的家国情怀</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)      
        # 系统信息
        st.markdown("---")
        st.markdown("**📊 系统信息**")
        st.text(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.text("状态: 🟢 正常运行")
        st.text("版本: v3.0.0")
        st.text(f"模块数: 13个")

# ======================= 主界面 =======================
# 实验室头部
st.markdown("""
<div class='lab-header'>
    <h1 class='lab-title'>🔬 数字图像处理实验室</h1>
    <p style='font-size: 1.3rem; opacity: 0.95;'>融合现代化图像处理实践平台 · 践行工匠精神 · 培养科学素养</p>
    <p style='font-size: 1.1rem; margin-top: 10px; opacity: 0.8;'>13大图像处理模块 · 思政融合教学</p>
</div>
""", unsafe_allow_html=True)

# 渲染侧边栏
render_sidebar()

# 创建13个选项卡
tab_names = [
    "🔬 图像增强", 
    "📐 边缘检测", 
    "🔄 线性变换", 
    "✨ 图像锐化",
    "📊 采样与量化",
    "🎨 彩色图像分割",
    "🌈 颜色通道分析",
    "🎭 特效处理",
    "🎨 图像绘画",
    "🌟 风格迁移",
    "🖼️ 老照片上色",
    "⚙️ 数字形态学",
    "📝 实验提交"
]

tabs = st.tabs(tab_names)

# 全局图像上传器
uploaded_file = None
if 'current_image' not in st.session_state:
    st.session_state.current_image = None

def load_and_display_image(uploaded_file, tab_key):
    """通用函数：加载并显示图像"""
    if uploaded_file is not None:
        try:
            # 读取图像文件
            image_bytes = uploaded_file.read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            
            # 使用OpenCV读取图像
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                st.error("无法读取图像文件，请确保是有效的图像格式")
                return None
            
            # 保存到session state
            st.session_state[f'image_{tab_key}'] = image
            
            # 转换为RGB用于显示（Streamlit使用RGB）
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            return image, image_rgb
            
        except Exception as e:
            st.error(f"加载图像时出错: {str(e)}")
            return None
    return None


# 1. 图像增强选项卡
with tabs[0]:
    st.markdown("### 🔬 图像增强处理")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：精益求精的工匠精神</h4>
        <p>
        图像增强技术体现了<strong style='color: #dc2626;'>精益求精</strong>的工匠精神，
        通过不断优化细节，追求更高质量的图像效果，这正体现了社会主义核心价值观中的<strong style='color: #dc2626;'>敬业</strong>精神。
        在技术学习中，我们要发扬这种一丝不苟、追求卓越的精神品质。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件", 
        type=["jpg", "jpeg", "png"], 
        key="tab1_upload"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        # 保存RGB版本用于显示
        image_rgb = np.array(pil_image)
        # 转换为BGR用于OpenCV处理
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # 初始化结果变量
        result_rgb = None
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            # 显示RGB版本（正确的颜色）
            st.image(image_rgb, caption="原始图像", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 增强方法选择
        enhancement_method = st.selectbox(
            "选择增强方法",
            ["直方图均衡化", "对比度调整", "伽马校正", "CLAHE增强"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if enhancement_method == "对比度调整":
                alpha = st.slider("对比度系数", 0.5, 3.0, 1.2, 0.1)
                beta = st.slider("亮度调整", -50, 50, 0)
                if st.button("应用对比度调整", use_container_width=True):
                    # 使用BGR版本进行处理
                    result_bgr = apply_contrast_adjustment(image_bgr, alpha, beta)
                    # 转换为RGB用于显示
                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
                    
            elif enhancement_method == "伽马校正":
                gamma = st.slider("伽马值", 0.1, 3.0, 1.0, 0.1)
                if st.button("应用伽马校正", use_container_width=True):
                    # 使用BGR版本进行处理
                    result_bgr = apply_gamma_correction(image_bgr, gamma)
                    # 转换为RGB用于显示
                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
                    
            elif enhancement_method == "CLAHE增强":
                clip_limit = st.slider("对比度限制", 1.0, 4.0, 2.0, 0.1)
                tile_size = st.slider("网格大小", 4, 16, 8, 2)
                if st.button("应用CLAHE增强", use_container_width=True):
                    # 使用BGR版本进行处理
                    result_bgr = apply_clahe(image_bgr, clip_limit, (tile_size, tile_size))
                    # 转换为RGB用于显示
                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
                    
            else:  # 直方图均衡化
                if st.button("应用直方图均衡化", use_container_width=True):
                    # 使用BGR版本进行处理
                    result_bgr = apply_histogram_equalization(image_bgr)
                    # 转换为RGB用于显示
                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        with col2:
            if result_rgb is not None:
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(result_rgb, caption=f"{enhancement_method}结果", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 下载时使用RGB版本
                provide_download_button(
                    result_rgb, 
                    f"enhanced_{enhancement_method}.jpg", 
                    "📥 下载增强结果",
                    unique_key_suffix="tab1_enhance"
                )
    else:
        st.info("请上传图像文件开始处理")

# 2. 边缘检测选项卡
with tabs[1]:
    st.markdown("### 📐 边缘检测算法比较")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：严谨的科学态度</h4>
        <p>
        边缘检测算法体现了<strong style='color: #dc2626;'>严谨求实</strong>的科学态度，
        不同算法各有优劣，需要根据实际需求选择，这体现了<strong style='color: #dc2626;'>实事求是</strong>的科学精神。
        在技术研究中，我们要保持严谨的态度，追求真理。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件", 
        type=["jpg", "jpeg", "png"], 
        key="tab2_upload"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        # 保存RGB版本用于显示
        image_rgb = np.array(pil_image)
        # 转换为BGR用于OpenCV处理
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # 初始化结果变量
        canny_result_rgb = None
        sobel_result_rgb = None
        laplacian_result_rgb = None
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Canny边缘检测")
            threshold1 = st.slider("低阈值", 0, 100, 10, key="canny1")
            threshold2 = st.slider("高阈值", 100, 300, 100, key="canny2")
            
            if st.button("应用Canny", key="btn_canny", use_container_width=True):
                canny_result_bgr = apply_canny_edge(image_bgr, threshold1, threshold2)
                # 转换为RGB用于显示和下载
                canny_result_rgb = cv2.cvtColor(canny_result_bgr, cv2.COLOR_BGR2RGB)
            
            if canny_result_rgb is not None:
                st.image(canny_result_rgb, use_container_width=True)
                provide_download_button(
                    canny_result_rgb, 
                    "edges_canny.jpg", 
                    "📥 下载Canny结果",
                    unique_key_suffix="tab2_canny"
                )
        
        with col2:
            st.markdown("### Sobel边缘检测")
            ksize = st.slider("核大小", 3, 17, 3, step=2, key="sobel")
            
            if st.button("应用Sobel", key="btn_sobel", use_container_width=True):
                sobel_result_bgr = apply_sobel_edge(image_bgr, ksize)
                # 转换为RGB用于显示和下载
                sobel_result_rgb = cv2.cvtColor(sobel_result_bgr, cv2.COLOR_BGR2RGB)
            
            if sobel_result_rgb is not None:
                st.image(sobel_result_rgb, use_container_width=True)
                provide_download_button(
                    sobel_result_rgb, 
                    "edges_sobel.jpg", 
                    "📥 下载Sobel结果",
                    unique_key_suffix="tab2_sobel"
                )
        
        with col3:
            st.markdown("### Laplacian边缘检测")
            
            # 添加Laplacian参数控制
            laplacian_ksize = st.slider("Laplacian核大小", 1, 7, 1, step=2, key="laplacian_ksize")
            laplacian_scale = st.slider("缩放因子", 0.1, 5.0, 1.0, 0.1, key="laplacian_scale")
            laplacian_delta = st.slider("亮度调整", 0, 100, 0, key="laplacian_delta")
            
            # 创建一个增强的Laplacian函数
            def apply_enhanced_laplacian(image, ksize=1, scale=1.0, delta=0):
                """增强的Laplacian边缘检测"""
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                else:
                    gray = image.copy()
                
                # 应用Laplacian
                laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=ksize)
                
                # 应用缩放和偏移
                laplacian = cv2.convertScaleAbs(laplacian, alpha=scale, beta=delta)
                
                # 转换为彩色图像用于显示
                return cv2.cvtColor(laplacian, cv2.COLOR_GRAY2BGR)
            
            if st.button("应用Laplacian", key="btn_laplacian", use_container_width=True):
                laplacian_result_bgr = apply_enhanced_laplacian(
                    image_bgr, 
                    ksize=laplacian_ksize,
                    scale=laplacian_scale,
                    delta=laplacian_delta
                )
                # 转换为RGB用于显示和下载
                laplacian_result_rgb = cv2.cvtColor(laplacian_result_bgr, cv2.COLOR_BGR2RGB)
            
            if laplacian_result_rgb is not None:
                st.image(laplacian_result_rgb, caption=f"Laplacian ksize={laplacian_ksize}", use_container_width=True)
                provide_download_button(
                    laplacian_result_rgb, 
                    "edges_laplacian.jpg", 
                    "📥 下载Laplacian结果",
                    unique_key_suffix="tab2_laplacian"
                )
        
        # 显示原始图像
        st.markdown("### 📷 原始图像参考")
        st.image(image_rgb, caption="原始图像", use_container_width=True)
    else:
        st.info("请上传图像文件开始处理")

# 3. 线性变换选项卡
with tabs[2]:
    st.markdown("### 🔄 线性变换处理")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：创新发展的思维</h4>
        <p>
        线性变换技术体现了<strong style='color: #dc2626;'>创新求变</strong>的思维模式，
        通过数学变换创造新的视角，这体现了<strong style='color: #dc2626;'>改革创新</strong>的时代精神。
        在技术发展中，我们要勇于创新，不断探索。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件", 
        type=["jpg", "jpeg", "png"], 
        key="tab3_upload"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        # 保存RGB版本用于显示
        image_rgb = np.array(pil_image)
        # 转换为BGR用于OpenCV处理
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # 初始化结果变量
        result_rgb = None
        
        transform_type = st.selectbox("选择变换类型", ["仿射变换", "透视变换"])
        
        if transform_type == "仿射变换":
            col1, col2 = st.columns(2)
            with col1:
                angle = st.slider("旋转角度", -180, 180, 0)
                scale = st.slider("缩放比例", 0.5, 2.0, 1.0, 0.1)
            with col2:
                tx = st.slider("水平平移", -100, 100, 0)
                ty = st.slider("垂直平移", -100, 100, 0)
            
            # 添加预览选项
            show_preview = st.checkbox("显示变换矩阵预览", value=True)
            
            if show_preview:
                # 计算并显示变换矩阵
                height, width = image_bgr.shape[:2]
                center = (width // 2, height // 2)
                matrix = cv2.getRotationMatrix2D(center, angle, scale)
                matrix[0, 2] += tx
                matrix[1, 2] += ty
                
                st.markdown("**仿射变换矩阵:**")
                st.code(f"""
                [ cosθ·s, -sinθ·s, tx ]
                [ sinθ·s,  cosθ·s, ty ]
                = 
                [{matrix[0,0]:.3f}, {matrix[0,1]:.3f}, {matrix[0,2]:.1f}]
                [{matrix[1,0]:.3f}, {matrix[1,1]:.3f}, {matrix[1,2]:.1f}]
                """)
            
            if st.button("应用仿射变换", use_container_width=True):
                result_bgr = apply_affine_transform(image_bgr, angle, scale, tx, ty)
                # 转换为RGB用于显示和下载
                result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        else:  # 透视变换
            st.markdown("### 透视变换参数")
            st.markdown("调整四个角的坐标来改变透视效果:")
            
            height, width = image_bgr.shape[:2]
            
            # 创建4个控制点
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**左上角**")
                tl_x = st.slider("TL X", 0, width//2, 50, key="tl_x")
                tl_y = st.slider("TL Y", 0, height//2, 50, key="tl_y")
                
                st.markdown("**右上角**")
                tr_x = st.slider("TR X", width//2, width, width-50, key="tr_x")
                tr_y = st.slider("TR Y", 0, height//2, 0, key="tr_y")
            
            with col2:
                st.markdown("**左下角**")
                bl_x = st.slider("BL X", 0, width//2, 0, key="bl_x")
                bl_y = st.slider("BL Y", height//2, height, height-50, key="bl_y")
                
                st.markdown("**右下角**")
                br_x = st.slider("BR X", width//2, width, width, key="br_x")
                br_y = st.slider("BR Y", height//2, height, height, key="br_y")
            
            # 更新透视变换函数
            def apply_custom_perspective_transform(image, src_points, dst_points):
                """自定义透视变换"""
                matrix = cv2.getPerspectiveTransform(src_points, dst_points)
                return cv2.warpPerspective(image, matrix, (width, height))
            
            # 定义原始点（图像的四个角）
            src_points = np.float32([
                [0, 0],           # 左上角
                [width, 0],       # 右上角
                [0, height],      # 左下角
                [width, height]   # 右下角
            ])
            
            # 定义目标点（根据滑块调整）
            dst_points = np.float32([
                [tl_x, tl_y],    # 左上角
                [tr_x, tr_y],    # 右上角
                [bl_x, bl_y],    # 左下角
                [br_x, br_y]     # 右下角
            ])
            
            # 显示透视变换预览
            st.markdown("### 变换效果预览")
            
            # 创建带有控制点的预览图像
            preview_image = image_rgb.copy()
            
            # 绘制原始点和目标点
            points_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
            points_labels = ['TL', 'TR', 'BL', 'BR']
            
            # 在预览图上绘制点
            for i, (src_pt, dst_pt, color, label) in enumerate(zip(src_points, dst_points, points_colors, points_labels)):
                # 绘制原始点（蓝色）
                cv2.circle(preview_image, (int(src_pt[0]), int(src_pt[1])), 8, color, -1)
                cv2.putText(preview_image, f'{label}_src', 
                          (int(src_pt[0])+10, int(src_pt[1])+10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # 绘制目标点（红色）
                cv2.circle(preview_image, (int(dst_pt[0]), int(dst_pt[1])), 8, color, 2)
                cv2.putText(preview_image, f'{label}_dst', 
                          (int(dst_pt[0])+10, int(dst_pt[1])+10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                
                # 绘制连接线
                cv2.line(preview_image, 
                        (int(src_pt[0]), int(src_pt[1])),
                        (int(dst_pt[0]), int(dst_pt[1])),
                        (128, 128, 128), 1, cv2.LINE_AA)
            
            # 显示预览图
            col1, col2 = st.columns(2)
            with col1:
                st.image(preview_image, caption="控制点预览（蓝色:原始, 红色:目标）", use_container_width=True)
            
            if st.button("应用透视变换", use_container_width=True):
                result_bgr = apply_custom_perspective_transform(image_bgr, src_points, dst_points)
                # 转换为RGB用于显示和下载
                result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        # 显示结果和下载（适用于两种变换）
        if result_rgb is not None:
            with col2:
                caption = ""
                if transform_type == "仿射变换":
                    caption = f"仿射变换结果\n旋转:{angle}°, 缩放:{scale}x"
                    st.image(result_rgb, caption=caption, use_container_width=True)
                else:  # 透视变换
                    caption = "透视变换结果"
                    st.image(result_rgb, caption=caption, use_container_width=True)
                    
                    # 显示变换矩阵
                    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
                    st.markdown("**透视变换矩阵:**")
                    st.code(f"""
                    [{matrix[0,0]:.6f}, {matrix[0,1]:.6f}, {matrix[0,2]:.6f}]
                    [{matrix[1,0]:.6f}, {matrix[1,1]:.6f}, {matrix[1,2]:.6f}]
                    [{matrix[2,0]:.6f}, {matrix[2,1]:.6f}, {matrix[2,2]:.6f}]
                    """)
            
            provide_download_button(
                result_rgb, 
                f"{transform_type}.jpg", 
                "📥 下载变换结果",
                unique_key_suffix=f"tab3_{transform_type}"
            )
    else:
        st.info("请上传图像文件开始处理")



# 4. 图像锐化选项卡
with tabs[3]:
    st.markdown("### ✨ 图像锐化处理")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：精益求精的态度</h4>
        <p>
        图像锐化技术体现了<strong style='color: #dc2626;'>精益求精</strong>的工作态度，
        通过增强细节展现更清晰的图像，这体现了<strong style='color: #dc2626;'>追求卓越</strong>的工匠精神。
        在技术工作中，我们要注重细节，追求完美。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加锐化原理说明
    with st.expander("📚 锐化原理说明", expanded=False):
        st.markdown("""
        ### 图像锐化技术原理
        
        1. **锐化滤波器** - 通过卷积核增强图像边缘
        2. **非锐化掩蔽** - 先模糊再与原图相减，增强高频细节
        3. **拉普拉斯锐化** - 使用拉普拉斯算子检测边缘
        4. **高频提升滤波** - 增强图像的高频分量
        5. **自适应锐化** - 仅在边缘区域应用锐化
        
        **灰度图像锐化的优势**:
        - 减少计算复杂度，提高处理速度
        - 避免彩色通道之间的干扰
        - 更专注于边缘和细节增强
        - 适合文本、文档、医学影像等处理
        
        **应用场景**:
        - 模糊照片的清晰化
        - 文档扫描件的增强
        - 医学图像的细节提取
        - 监控视频的清晰化
        """)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件", 
        type=["jpg", "jpeg", "png", "bmp", "webp"], 
        key="tab4_upload"
    )
    
    # 添加彩色/灰度选项
    processing_mode = st.radio(
        "选择处理模式",
        ["灰度图像锐化", "彩色图像锐化"],
        horizontal=True,
        index=0,
        key="sharpen_mode"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        
        # 根据处理模式转换图像
        if processing_mode == "灰度图像锐化":
            # 转换为灰度图像
            if pil_image.mode != 'L':
                pil_image = pil_image.convert('L')
            image_gray = np.array(pil_image)
            
            # 为兼容OpenCV处理，将灰度图转为3通道BGR格式
            image_bgr = cv2.cvtColor(image_gray, cv2.COLOR_GRAY2BGR)
            image_for_display = image_gray  # 显示用灰度图
        else:
            # 保持彩色图像
            image_rgb = np.array(pil_image)
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            image_for_display = image_rgb  # 显示用彩色图
        
        # 确保图像是uint8类型
        if image_bgr.dtype != np.uint8:
            image_bgr = image_bgr.astype(np.uint8)
        
        # 显示原始图像信息
        with st.expander("📊 原始图像信息", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("宽度", f"{image_for_display.shape[1]}px")
            with col2:
                st.metric("高度", f"{image_for_display.shape[0]}px")
            with col3:
                st.metric("模式", processing_mode)
                st.metric("格式", pil_image.format or "未知")
        
        # 显示原始图像
        st.markdown("### 📷 原始图像")
        if processing_mode == "灰度图像锐化":
            # 添加 width 参数控制显示大小
            st.image(image_for_display, use_container_width=False, width=400, 
                     caption=f"灰度图像 {image_for_display.shape[1]} × {image_for_display.shape[0]}",
                     clamp=True)
        else:
            st.image(image_for_display, use_container_width=False, width=400,
                     caption=f"彩色图像 {image_for_display.shape[1]} × {image_for_display.shape[0]}")
        
        # 选择锐化方法
        sharpen_method = st.selectbox(
            "选择锐化方法", 
            ["锐化滤波器", "非锐化掩蔽", "拉普拉斯锐化", "高频提升滤波", "自适应锐化"],
            key="sharpen_method_select"
        )
        
        # 结果变量
        result_image = None
        
        if sharpen_method == "锐化滤波器":
            st.markdown("#### 🔍 锐化滤波器设置")
            
            col1, col2 = st.columns(2)
            with col1:
                kernel_size = st.slider("滤波器大小", 3, 15, 3, step=2, key="sharpen_kernel")
            with col2:
                sharpen_strength = st.slider("锐化强度", 0.1, 3.0, 1.0, 0.1, key="sharpen_strength")
            
            if st.button("🔍 应用锐化滤波器", use_container_width=True, key="sharpen_filter_btn"):
                with st.spinner("正在应用锐化滤波器..."):
                    # 使用BGR图像处理
                    result_bgr = apply_sharpen_filter(image_bgr, kernel_size)
                    
                    # 调整锐化强度
                    if sharpen_strength != 1.0:
                        detail = cv2.subtract(result_bgr, image_bgr)
                        result_bgr = cv2.addWeighted(image_bgr, 1.0, detail, sharpen_strength, 0)
                    
                    # 根据处理模式转换结果
                    if processing_mode == "灰度图像锐化":
                        result_image = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2GRAY)
                    else:
                        result_image = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        elif sharpen_method == "非锐化掩蔽":
            st.markdown("#### 🎯 非锐化掩蔽设置")
            
            col1, col2 = st.columns(2)
            with col1:
                sigma = st.slider("模糊程度", 0.1, 5.0, 1.0, 0.1, key="unsharp_sigma")
            with col2:
                amount = st.slider("锐化强度", 0.1, 3.0, 1.0, 0.1, key="unsharp_amount")
            
            if st.button("🎯 应用非锐化掩蔽", use_container_width=True, key="unsharp_btn"):
                with st.spinner("正在应用非锐化掩蔽..."):
                    # 使用BGR图像处理
                    result_bgr = apply_unsharp_masking(image_bgr, sigma, amount)
                    
                    # 根据处理模式转换结果
                    if processing_mode == "灰度图像锐化":
                        result_image = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2GRAY)
                    else:
                        result_image = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        elif sharpen_method == "拉普拉斯锐化":
            st.markdown("#### ⚡ 拉普拉斯锐化设置")
            
            col1, col2 = st.columns(2)
            with col1:
                edge_strength = st.slider("边缘增强", 0.1, 2.0, 0.5, 0.1, key="laplace_strength")
            with col2:
                noise_reduction = st.checkbox("降噪处理", True, key="laplace_denoise")
            
            if st.button("⚡ 应用拉普拉斯锐化", use_container_width=True, key="laplace_btn"):
                with st.spinner("正在应用拉普拉斯锐化..."):
                    # 预处理：如果需要降噪
                    if noise_reduction:
                        image_processed = cv2.bilateralFilter(image_bgr, 5, 50, 50)
                    else:
                        image_processed = image_bgr
                    
                    # 应用拉普拉斯锐化
                    result_bgr = apply_laplacian_sharpening(image_processed)
                    
                    # 调整边缘强度
                    if edge_strength != 1.0:
                        detail = cv2.subtract(result_bgr, image_bgr)
                        result_bgr = cv2.addWeighted(image_bgr, 1.0, detail, edge_strength, 0)
                    
                    # 根据处理模式转换结果
                    if processing_mode == "灰度图像锐化":
                        result_image = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2GRAY)
                    else:
                        result_image = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        elif sharpen_method == "高频提升滤波":
            st.markdown("#### 🚀 高频提升滤波设置")
            
            col1, col2 = st.columns(2)
            with col1:
                boost_factor = st.slider("提升系数", 1.0, 3.0, 1.5, 0.1, key="boost_factor")
            with col2:
                blend_mode = st.selectbox("混合模式", ["直接混合", "边缘增强"], key="boost_blend")
            
            if st.button("🚀 应用高频提升滤波", use_container_width=True, key="boost_btn"):
                with st.spinner("正在应用高频提升滤波..."):
                    # 使用BGR图像处理
                    result_bgr = apply_high_boost_filter(image_bgr, boost_factor)
                    
                    # 根据处理模式转换结果
                    if processing_mode == "灰度图像锐化":
                        result_image = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2GRAY)
                    else:
                        result_image = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        else:  # 自适应锐化
            st.markdown("#### 🎨 自适应锐化设置")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                strength = st.slider("锐化强度", 0.1, 1.0, 0.5, 0.1, key="adaptive_strength")
            with col2:
                edge_threshold = st.slider("边缘阈值", 30, 200, 100, key="adaptive_threshold")
            with col3:
                smooth_edges = st.checkbox("平滑边缘", True, key="adaptive_smooth")
            
            if st.button("🎨 应用自适应锐化", use_container_width=True, key="adaptive_btn"):
                with st.spinner("正在应用自适应锐化..."):
                    # 使用BGR图像处理
                    result_bgr = apply_adaptive_sharpen(image_bgr, strength)
                    
                    # 根据处理模式转换结果
                    if processing_mode == "灰度图像锐化":
                        result_image = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2GRAY)
                    else:
                        result_image = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        # 显示结果和下载
        if result_image is not None:
            # 确保结果是uint8类型
            if result_image.dtype != np.uint8:
                result_image = result_image.astype(np.uint8)
            
            # 创建对比展示
            st.markdown("### 🖼️ 锐化效果对比")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📷 原始图像")
                if processing_mode == "灰度图像锐化":
                    st.image(image_for_display, use_container_width=True, 
                            caption=f"灰度图像 {image_for_display.shape[1]} × {image_for_display.shape[0]}",
                            clamp=True)
                else:
                    st.image(image_for_display, use_container_width=True, 
                            caption=f"彩色图像 {image_for_display.shape[1]} × {image_for_display.shape[0]}")
            
            with col2:
                st.markdown(f"#### ✨ {sharpen_method}")
                if processing_mode == "灰度图像锐化":
                    st.image(result_image, use_container_width=True, 
                            caption=f"锐化后灰度图 {result_image.shape[1]} × {result_image.shape[0]}",
                            clamp=True)
                else:
                    st.image(result_image, use_container_width=True, 
                            caption=f"锐化后彩色图 {result_image.shape[1]} × {result_image.shape[0]}")
            
            # 效果统计信息
            with st.expander("📊 锐化效果统计", expanded=False):
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                
                with col_stats1:
                    # 计算清晰度变化（基于梯度）
                    def calculate_sharpness(image):
                        """计算图像清晰度（基于梯度）"""
                        if len(image.shape) == 3:
                            # 彩色图像转为灰度
                            if image.shape[2] == 3:
                                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                            else:
                                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        else:
                            gray = image
                        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                        gradient = np.sqrt(sobelx**2 + sobely**2)
                        return np.mean(gradient)
                    
                    # 准备用于计算的图像
                    if processing_mode == "灰度图像锐化":
                        orig_for_calc = image_for_display
                        proc_for_calc = result_image
                    else:
                        orig_for_calc = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
                        proc_for_calc = cv2.cvtColor(cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
                    
                    orig_sharpness = calculate_sharpness(orig_for_calc)
                    proc_sharpness = calculate_sharpness(proc_for_calc)
                    improvement = (proc_sharpness - orig_sharpness) / orig_sharpness * 100
                    
                    st.metric("清晰度提升", f"{improvement:+.1f}%", 
                             f"{orig_sharpness:.1f} → {proc_sharpness:.1f}")
                
                with col_stats2:
                    # 亮度变化
                    if processing_mode == "灰度图像锐化":
                        orig_brightness = np.mean(image_for_display)
                        proc_brightness = np.mean(result_image)
                    else:
                        orig_brightness = np.mean(image_for_display)
                        proc_brightness = np.mean(result_image)
                    brightness_change = proc_brightness - orig_brightness
                    st.metric("亮度变化", f"{brightness_change:+.1f}",
                             f"{orig_brightness:.1f} → {proc_brightness:.1f}")
                
                with col_stats3:
                    # 对比度变化
                    if processing_mode == "灰度图像锐化":
                        orig_contrast = np.std(image_for_display)
                        proc_contrast = np.std(result_image)
                    else:
                        orig_contrast = np.std(image_for_display, axis=(0,1)).mean()
                        proc_contrast = np.std(result_image, axis=(0,1)).mean()
                    contrast_change = proc_contrast - orig_contrast
                    st.metric("对比度变化", f"{contrast_change:+.1f}",
                             f"{orig_contrast:.1f} → {proc_contrast:.1f}")
            
            # 分割线
            st.markdown("---")
            
            # 下载选项
            st.markdown("### 📥 下载锐化结果")
            
            # 将结果转换为PIL图像
            if processing_mode == "灰度图像锐化":
                result_pil = Image.fromarray(result_image, mode='L')
            else:
                result_pil = Image.fromarray(result_image)
            
            col_dl1, col_dl2, col_dl3 = st.columns(3)
            
            with col_dl1:
                # JPEG格式
                img_buffer = io.BytesIO()
                if processing_mode == "灰度图像锐化":
                    # JPEG不支持纯灰度模式，转换为RGB
                    result_pil.convert('RGB').save(img_buffer, format="JPEG", quality=95)
                else:
                    result_pil.save(img_buffer, format="JPEG", quality=95)
                img_buffer.seek(0)
                
                st.download_button(
                    label="💾 下载JPEG格式",
                    data=img_buffer,
                    file_name=f"锐化_{processing_mode}_{sharpen_method}.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
            
            with col_dl2:
                # PNG格式
                png_buffer = io.BytesIO()
                result_pil.save(png_buffer, format="PNG")
                png_buffer.seek(0)
                
                st.download_button(
                    label="🖼️ 下载PNG格式",
                    data=png_buffer,
                    file_name=f"锐化_{processing_mode}_{sharpen_method}.png",
                    mime="image/png",
                    use_container_width=True
                )
            
            with col_dl3:
                # 高质量版本
                high_buffer = io.BytesIO()
                if processing_mode == "灰度图像锐化":
                    result_pil.convert('RGB').save(high_buffer, format="JPEG", quality=100)
                else:
                    result_pil.save(high_buffer, format="JPEG", quality=100)
                high_buffer.seek(0)
                
                st.download_button(
                    label="🌟 最高质量",
                    data=high_buffer,
                    file_name=f"锐化_{processing_mode}_{sharpen_method}_高质量.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
            
            # 锐化预览
            st.markdown("### 🔍 锐化效果预览")
            preview_size = st.slider("预览区域大小", 100, 400, 200, key="preview_size")
            
            # 确保预览区域不超过图像尺寸
            max_height, max_width = image_for_display.shape[:2]
            preview_size = min(preview_size, max_height-200, max_width-200)
            
            # 选择预览区域
            col_preview1, col_preview2 = st.columns(2)
            
            with col_preview1:
                # 原始图像预览
                st.markdown("#### 原始图像局部")
                if len(image_for_display.shape) == 2:  # 灰度图
                    preview_orig = image_for_display[100:100+preview_size, 100:100+preview_size]
                else:  # 彩色图
                    preview_orig = image_for_display[100:100+preview_size, 100:100+preview_size, :]
                st.image(preview_orig, use_container_width=True, clamp=True)
            
            with col_preview2:
                # 锐化结果预览
                st.markdown("#### 锐化后局部")
                if len(result_image.shape) == 2:  # 灰度图
                    preview_sharp = result_image[100:100+preview_size, 100:100+preview_size]
                else:  # 彩色图
                    preview_sharp = result_image[100:100+preview_size, 100:100+preview_size, :]
                st.image(preview_sharp, use_container_width=True, clamp=True)
    
    else:
        # 没有上传文件时的界面
        st.info("📤 请上传图像文件开始处理")
        
        # 添加示例演示
        if st.checkbox("显示锐化示例", key="sharpen_demo"):
            # 创建示例图像
            st.markdown("### 📝 灰度图像锐化示例")
            
            # 创建灰度示例图像
            demo_image_gray = np.ones((300, 400), dtype=np.uint8) * 150
            cv2.putText(demo_image_gray, "Example Text", (80, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, 50, 3)
            
            # 应用模糊模拟需要锐化的图像
            demo_blurred = cv2.GaussianBlur(demo_image_gray, (5, 5), 2)
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(demo_blurred, caption="模糊的灰度图像", use_container_width=True, clamp=True)
            
            with col2:
                # 将灰度图转为3通道BGR用于处理
                demo_blurred_bgr = cv2.cvtColor(demo_blurred, cv2.COLOR_GRAY2BGR)
                
                # 应用锐化
                demo_sharp_bgr = apply_unsharp_masking(demo_blurred_bgr, 2.0, 1.5)
                demo_sharp_gray = cv2.cvtColor(demo_sharp_bgr, cv2.COLOR_BGR2GRAY)
                st.image(demo_sharp_gray, caption="锐化后的灰度图像", use_container_width=True, clamp=True)




# 5. 采样与量化选项卡
with tabs[4]:
    st.markdown("### 📊 采样与量化分析")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：实事求是的科学精神</h4>
        <p>
        采样与量化技术体现了<strong style='color: #dc2626;'>实事求是</strong>的科学精神，
        通过分析数据特征优化存储和传输，这体现了<strong style='color: #dc2626;'>务实高效</strong>的工作作风。
        在技术应用中，我们要注重实际效果，追求效率。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件", 
        type=["jpg", "jpeg", "png"], 
        key="tab5_upload"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        # 保存RGB版本用于显示
        image_rgb = np.array(pil_image)
        # 转换为BGR用于OpenCV处理
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # 初始化结果变量
        sampled_rgb = None
        quantized_rgb = None
        
        # 采样控制
        st.markdown("### 🔽 图像采样")
        sample_ratio = st.slider("采样比例", 2, 8, 2)
        
        if st.button("应用采样", key="sample_btn", use_container_width=True):
            # 使用BGR图像处理
            sampled_bgr = apply_sampling(image_bgr, sample_ratio)
            # 转换为RGB用于显示和下载
            sampled_rgb = cv2.cvtColor(sampled_bgr, cv2.COLOR_BGR2RGB)
        
        # 量化控制
        st.markdown("### 🎚️ 图像量化")
        quant_levels = st.slider("量化级别", 2, 256, 64)
        
        if st.button("应用量化", key="quant_btn", use_container_width=True):
            # 使用BGR图像处理
            quantized_bgr = apply_quantization(image_bgr, quant_levels)
            # 转换为RGB用于显示和下载
            quantized_rgb = cv2.cvtColor(quantized_bgr, cv2.COLOR_BGR2RGB)
        
        # 显示采样结果
        if sampled_rgb is not None:
            col1, col2 = st.columns(2)
            with col1:
                # 显示RGB原始图像
                st.image(image_rgb, caption=f"原始图像 {image_rgb.shape[1]}x{image_rgb.shape[0]}", use_container_width=True)
            with col2:
                # 显示RGB采样结果
                st.image(sampled_rgb, caption=f"采样后图像 {sampled_rgb.shape[1]}x{sampled_rgb.shape[0]}", use_container_width=True)
            
            provide_download_button(
                sampled_rgb, 
                f"sampled_{sample_ratio}x.jpg", 
                "📥 下载采样结果",
                unique_key_suffix="tab5_sampling"
            )
        
        # 显示量化结果
        if quantized_rgb is not None:
            col1, col2 = st.columns(2)
            with col1:
                # 显示RGB原始图像
                st.image(image_rgb, caption="原始图像", use_container_width=True)
            with col2:
                # 显示RGB量化结果
                st.image(quantized_rgb, caption=f"{quant_levels}级量化", use_container_width=True)
            
            provide_download_button(
                quantized_rgb, 
                f"quantized_{quant_levels}levels.jpg", 
                "📥 下载量化结果",
                unique_key_suffix="tab5_quantization"
            )
    else:
        st.info("请上传图像文件开始处理")

# 6. 彩色图像分割选项卡
with tabs[5]:
    st.markdown("### 🎨 彩色图像分割")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：精准分析的能力</h4>
        <p>
        彩色图像分割技术体现了<strong style='color: #dc2626;'>精准分析</strong>的能力，
        通过颜色特征识别不同区域，这体现了<strong style='color: #dc2626;'>科学分析</strong>的工作方法。
        在技术应用中，我们要培养精准分析的能力。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件", 
        type=["jpg", "jpeg", "png"], 
        key="tab6_upload"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        # 保存RGB版本用于显示
        image_rgb = np.array(pil_image)
        # 转换为BGR用于OpenCV处理
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # 初始化结果变量
        result_rgb = None
        
        color_space = st.selectbox("选择颜色空间", ["RGB颜色分割", "HSV颜色分割"])
        
        if color_space == "RGB颜色分割":
            st.markdown("### RGB颜色范围选择")
            col1, col2 = st.columns(2)
            with col1:
                r_min = st.slider("R最小值", 0, 255, 0)
                g_min = st.slider("G最小值", 0, 255, 0)
                b_min = st.slider("B最小值", 0, 255, 0)
            with col2:
                r_max = st.slider("R最大值", 0, 255, 255)
                g_max = st.slider("G最大值", 0, 255, 255)
                b_max = st.slider("B最大值", 0, 255, 255)
            
            # OpenCV使用BGR顺序，所以是[B, G, R]
            lower_color = np.array([b_min, g_min, r_min])
            upper_color = np.array([b_max, g_max, r_max])
        else:
            st.markdown("### HSV颜色范围选择")
            col1, col2 = st.columns(2)
            with col1:
                h_min = st.slider("H最小值", 0, 179, 0)
                s_min = st.slider("S最小值", 0, 255, 0)
                v_min = st.slider("V最小值", 0, 255, 0)
            with col2:
                h_max = st.slider("H最大值", 0, 179, 179)
                s_max = st.slider("S最大值", 0, 255, 255)
                v_max = st.slider("V最大值", 0, 255, 255)
            
            lower_color = np.array([h_min, s_min, v_min])
            upper_color = np.array([h_max, s_max, v_max])
        
        if st.button("应用颜色分割", use_container_width=True):
            if color_space == "RGB颜色分割":
                # 使用BGR图像处理
                result_bgr = apply_rgb_segmentation(image_bgr, lower_color, upper_color)
            else:
                # 使用BGR图像处理
                result_bgr = apply_hsv_segmentation(image_bgr, lower_color, upper_color)
            
            # 转换为RGB用于显示和下载
            result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        # 显示结果和下载
        if result_rgb is not None:
            col1, col2 = st.columns(2)
            with col1:
                # 显示RGB原始图像
                st.image(image_rgb, caption="原始图像", use_container_width=True)
            with col2:
                # 显示RGB分割结果
                st.image(result_rgb, caption=f"{color_space}结果", use_container_width=True)
            
            provide_download_button(
                result_rgb, 
                f"color_segmentation.jpg", 
                "📥 下载分割结果",
                unique_key_suffix="tab6_segmentation"
            )
    else:
        st.info("请上传图像文件开始处理")

# 7. 颜色通道分析选项卡
with tabs[6]:
    st.markdown("### 🌈 颜色通道分析")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：系统分析思维</h4>
        <p>
        颜色通道分析体现了<strong style='color: #dc2626;'>系统分析</strong>的思维方式，
        通过分解和重组理解图像结构，这体现了<strong style='color: #dc2626;'>全面分析</strong>的科学方法。
        在技术学习中，我们要培养系统思维。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件", 
        type=["jpg", "jpeg", "png"], 
        key="tab7_upload"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        # 保存RGB版本用于显示
        image_rgb = np.array(pil_image)
        # 转换为BGR用于OpenCV处理
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # 初始化结果变量
        channels_rgb = None
        result_rgb = None
        
        st.markdown("### 📊 RGB通道分离")
        if st.button("分离RGB通道", use_container_width=True):
            # 使用BGR图像处理
            channels_bgr = split_channels(image_bgr)
            
            # 将每个通道转换为RGB用于显示
            channels_rgb = []
            for channel_bgr in channels_bgr:
                channel_rgb = cv2.cvtColor(channel_bgr, cv2.COLOR_BGR2RGB)
                channels_rgb.append(channel_rgb)
        
        # 显示通道分离结果
        if channels_rgb is not None:
            cols = st.columns(4)
            with cols[0]:
                # 显示RGB原始图像
                st.image(image_rgb, caption="原始图像", use_container_width=True)
            with cols[1]:
                # 显示红色通道（BGR中的第2个通道）
                st.image(channels_rgb[0], caption="红色通道", use_container_width=True)
            with cols[2]:
                # 显示绿色通道（BGR中的第1个通道）
                st.image(channels_rgb[1], caption="绿色通道", use_container_width=True)
            with cols[3]:
                # 显示蓝色通道（BGR中的第0个通道）
                st.image(channels_rgb[2], caption="蓝色通道", use_container_width=True)
            
            # 提供通道分离结果下载
            st.markdown("### 📥 通道分离下载")
            col1, col2, col3 = st.columns(3)
            with col1:
                provide_download_button(
                    channels_rgb[0], 
                    "red_channel.jpg", 
                    "📥 下载红色通道",
                    unique_key_suffix="tab7_red"
                )
            with col2:
                provide_download_button(
                    channels_rgb[1], 
                    "green_channel.jpg", 
                    "📥 下载绿色通道",
                    unique_key_suffix="tab7_green"
                )
            with col3:
                provide_download_button(
                    channels_rgb[2], 
                    "blue_channel.jpg", 
                    "📥 下载蓝色通道",
                    unique_key_suffix="tab7_blue"
                )
        
        st.markdown("### 🎛️ 通道调整")
        channel_to_adjust = st.selectbox("选择调整通道", ["红色通道", "绿色通道", "蓝色通道"])
        adjustment_value = st.slider("调整值", -100, 100, 0)
        
        if st.button("应用通道调整", use_container_width=True):
            # 注意：BGR顺序，所以通道映射不同
            # BGR顺序：[蓝色, 绿色, 红色]
            channel_map = {
                "红色通道": 2,  # BGR中的第2个通道是红色
                "绿色通道": 1,  # BGR中的第1个通道是绿色
                "蓝色通道": 0   # BGR中的第0个通道是蓝色
            }
            
            # 使用BGR图像处理
            result_bgr = adjust_channel(image_bgr, channel_map[channel_to_adjust], adjustment_value)
            # 转换为RGB用于显示和下载
            result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        # 显示通道调整结果
        if result_rgb is not None:
            col1, col2 = st.columns(2)
            with col1:
                # 显示RGB原始图像
                st.image(image_rgb, caption="原始图像", use_container_width=True)
            with col2:
                # 显示RGB调整结果
                st.image(result_rgb, caption=f"调整{channel_to_adjust}", use_container_width=True)
            
            provide_download_button(
                result_rgb, 
                f"channel_adjusted.jpg", 
                "📥 下载调整结果",
                unique_key_suffix="tab7_adjusted"
            )
    else:
        st.info("请上传图像文件开始处理")

# 8. 特效处理选项卡
with tabs[7]:
    st.markdown("### 🎭 特效处理")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：创新实践能力</h4>
        <p>
        特效处理技术体现了<strong style='color: #dc2626;'>创新实践</strong>的能力，
        通过创造性思维实现视觉效果，这体现了<strong style='color: #dc2626;'>勇于创新</strong>的精神。
        在技术应用中，我们要敢于创新，勇于实践。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件", 
        type=["jpg", "jpeg", "png"], 
        key="tab8_upload"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        # 保存RGB版本用于显示
        image_rgb = np.array(pil_image)
        # 转换为BGR用于OpenCV处理
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        effect_type = st.selectbox("选择特效类型", 
                                  ["雨点特效", "雪花特效", "樱花特效", "星空特效"])
        
        # 初始化结果变量
        result_rgb = None
        result_bgr = None
        
        if effect_type == "雨点特效":
            col1, col2 = st.columns(2)
            with col1:
                intensity = st.slider("雨点密度", 50, 500, 150)
            with col2:
                opacity = st.slider("透明度", 0.1, 1.0, 0.5, 0.1)
            
            if st.button("添加雨点特效", use_container_width=True):
                # 使用BGR图像处理
                result_bgr = add_rain_effect(image_bgr, intensity, opacity)
                # 转换为RGB用于显示
                result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        elif effect_type == "雪花特效":
            col1, col2 = st.columns(2)
            with col1:
                intensity = st.slider("雪花密度", 100, 1000, 300)
            with col2:
                opacity = st.slider("透明度", 0.1, 1.0, 0.3, 0.1)
            
            if st.button("添加雪花特效", use_container_width=True):
                # 使用BGR图像处理
                result_bgr = add_snow_effect(image_bgr, intensity, opacity)
                # 转换为RGB用于显示
                result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        elif effect_type == "樱花特效":
            intensity = st.slider("樱花数量", 20, 200, 80)
            
            if st.button("添加樱花特效", use_container_width=True):
                # 使用BGR图像处理
                sakura_intensity = intensity / 100.0  # 转换为0.2-2.0的范围
                result_bgr = apply_sakura_effect(image_bgr, sakura_intensity)
                # 转换为RGB用于显示
                result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        else:  # 星空特效
            stars = st.slider("星星数量", 50, 500, 150)
            
            if st.button("添加星空特效", use_container_width=True):
                # 使用BGR图像处理
                result_bgr = add_starry_night_effect(image_bgr, stars)
                # 转换为RGB用于显示
                result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        # 显示结果和下载 - 使用result_rgb检查
        if result_rgb is not None:
            col1, col2 = st.columns(2)
            with col1:
                # 显示RGB原始图像
                st.image(image_rgb, caption="原始图像", use_container_width=True)
            with col2:
                # 显示RGB特效结果
                st.image(result_rgb, caption=f"{effect_type}结果", use_container_width=True)
            
            # 下载时传递RGB版本
            provide_download_button(
                result_rgb, 
                f"特效_{effect_type}.jpg", 
                "📥 下载特效结果",
                unique_key_suffix="tab8_effect"  # 添加唯一key后缀避免重复
            )
    else:
        st.info("请上传图像文件开始处理")
                
                
        

# 9. 图像绘画选项卡
with tabs[8]:
    st.markdown("### 🎨 图像绘画风格转换")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：艺术与科技融合</h4>
        <p>
        图像绘画技术体现了<strong style='color: #dc2626;'>艺术与科技</strong>的融合，
        通过技术手段实现艺术效果，这体现了<strong style='color: #dc2626;'>创新融合</strong>的发展理念。
        在技术发展中，我们要注重多学科融合，推动<strong style='color: #dc2626;'>文化创新</strong>和<strong style='color: #dc2626;'>科技进步</strong>。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件", 
        type=["jpg", "jpeg", "png"], 
        key="tab9_upload"
    )
    
    if uploaded_file is not None:
        try:
            # 读取图像
            pil_image = Image.open(uploaded_file)
            # 保存RGB版本用于显示
            image_rgb = np.array(pil_image)
            # 转换为BGR用于OpenCV处理
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            
            # 确保图像是uint8类型
            if image_bgr.dtype != np.uint8:
                image_bgr = image_bgr.astype(np.uint8)
            
            # 绘画风格选择 - 简化为基本风格
            painting_style = st.selectbox(
                "🎨 选择绘画风格", 
                [
                    "油画效果", 
                    "铅笔素描", 
                    "水墨画效果", 
                    "漫画风格",
                    "水彩画效果",
                    "波普艺术效果"
                ]
            )
            
            # 初始化结果变量
            result_rgb = None
            
            # 根据风格显示不同的控制参数
            if painting_style == "油画效果":
                col1, col2 = st.columns(2)
                with col1:
                    radius = st.slider("笔触半径", 1, 10, 3, key="oil_radius")
                with col2:
                    intensity = st.slider("油画强度", 10, 50, 25, key="oil_intensity")
                
                if st.button("🎨 生成油画效果", use_container_width=True, key="oil_btn"):
                    with st.spinner("正在绘制油画..."):
                        result_bgr = apply_oil_painting_effect(
                            image_bgr, 
                            radius=radius, 
                            intensity=intensity
                        )
                        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
            
            elif painting_style == "铅笔素描":
                col1, col2 = st.columns(2)
                with col1:
                    style_type = st.selectbox("素描类型", ["优雅", "艺术"], key="pencil_style")
                with col2:
                    intensity = st.slider("素描强度", 0.5, 2.0, 1.0, 0.1, key="pencil_intensity")
                
                if st.button("✏️ 生成铅笔素描", use_container_width=True, key="pencil_btn"):
                    with st.spinner("正在绘制素描..."):
                        if style_type == "优雅":
                            result_bgr = apply_pencil_sketch_effect(
                                image_bgr, 
                                style="elegant",
                                intensity=intensity
                            )
                        else:
                            result_bgr = apply_pencil_sketch_effect(
                                image_bgr,
                                style="artistic",
                                intensity=intensity
                            )
                        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
            
            elif painting_style == "水墨画效果":
                ink_strength = st.slider("墨迹浓度", 0.1, 0.8, 0.4, 0.1, key="ink_strength")
                
                if st.button("🖌️ 生成水墨画", use_container_width=True, key="ink_btn"):
                    with st.spinner("正在渲染水墨效果..."):
                        result_bgr = apply_ink_wash_painting_effect(
                            image_bgr, 
                            ink_strength=ink_strength
                        )
                        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
            
            elif painting_style == "漫画风格":
                col1, col2 = st.columns(2)
                with col1:
                    edge_threshold = st.slider("轮廓粗细", 30, 150, 50, key="comic_edge")
                with col2:
                    color_style = st.selectbox("颜色风格", ["鲜艳", "柔和"], key="comic_style")
                
                if st.button("🖼️ 生成漫画效果", use_container_width=True, key="comic_btn"):
                    with st.spinner("正在转换为漫画风格..."):
                        result_bgr = apply_comic_effect(
                            image_bgr,
                            edge_threshold=edge_threshold,
                            color_style="vibrant" if color_style == "鲜艳" else "soft"
                        )
                        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
            
            elif painting_style == "水彩画效果":
                col1, col2 = st.columns(2)
                with col1:
                    texture_strength = st.slider("纹理强度", 0.0, 0.5, 0.3, 0.05, key="watercolor_texture")
                with col2:
                    style_type = st.selectbox("风格类型", ["经典", "现代"], key="watercolor_style")
                
                if st.button("🎨 生成水彩画", use_container_width=True, key="watercolor_btn"):
                    with st.spinner("正在渲染水彩效果..."):
                        result_bgr = apply_watercolor_effect(
                            image_bgr,
                            style="classic" if style_type == "经典" else "modern",
                            texture_strength=texture_strength
                        )
                        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
            
            elif painting_style == "波普艺术效果":
                num_colors = st.slider("颜色数量", 3, 12, 6, key="popart_colors")
                
                if st.button("✨ 生成波普艺术", use_container_width=True, key="popart_btn"):
                    with st.spinner("正在创建波普艺术..."):
                        result_bgr = apply_pop_art_effect(
                            image_bgr,
                            num_colors=num_colors
                        )
                        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
            
            # 显示结果和下载
            if result_rgb is not None:
                # 确保结果是uint8类型
                if result_rgb.dtype != np.uint8:
                    result_rgb = result_rgb.astype(np.uint8)
                
                # 创建对比展示
                st.markdown("### 🖼️ 效果对比")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 📷 原始图像")
                    st.image(image_rgb, use_container_width=True)
                with col2:
                    st.markdown(f"#### 🎨 {painting_style}")
                    st.image(result_rgb, use_container_width=True)
                
                # 分割线
                st.markdown("---")
                
                # 简单的下载功能
                st.markdown("### 📥 下载处理结果")
                
                # 将结果转换为PIL图像
                result_pil = Image.fromarray(result_rgb)
                
                # 将图像保存到字节流
                img_buffer = io.BytesIO()
                result_pil.save(img_buffer, format="JPEG", quality=90)
                img_buffer.seek(0)
                
                # 创建下载按钮
                st.download_button(
                    label="💾 下载处理结果",
                    data=img_buffer,
                    file_name=f"绘画_{painting_style}.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
                
                # 其他格式选项
                st.markdown("##### 其他格式选项")
                col1, col2 = st.columns(2)
                
                with col1:
                    # PNG格式
                    png_buffer = io.BytesIO()
                    result_pil.save(png_buffer, format="PNG")
                    png_buffer.seek(0)
                    
                    st.download_button(
                        label="🖼️ 下载PNG格式",
                        data=png_buffer,
                        file_name=f"绘画_{painting_style}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                with col2:
                    # 高质量JPEG
                    jpeg_high_buffer = io.BytesIO()
                    result_pil.save(jpeg_high_buffer, format="JPEG", quality=100)
                    jpeg_high_buffer.seek(0)
                    
                    st.download_button(
                        label="🌟 最高质量",
                        data=jpeg_high_buffer,
                        file_name=f"绘画_{painting_style}_高质量.jpg",
                        mime="image/jpeg",
                        use_container_width=True
                    )
        
        except Exception as e:
            st.error(f"处理图像时发生错误: {str(e)}")
            st.info("请尝试上传其他图像或选择不同的处理选项。")
    
    else:
        # 没有上传文件时的界面
        st.info("📤 请上传图像文件开始处理")
        
        # 显示示例效果
        with st.expander("🎨 查看各种风格效果示例", expanded=False):
            st.markdown("""
            ### 各种绘画风格示例
            
            1. **油画效果** - 模拟传统油画的厚重笔触
            2. **铅笔素描** - 精细线条的黑白素描
            3. **水墨画** - 中国传统文化的水墨风格
            4. **漫画风格** - 动漫风格的鲜艳色彩
            5. **水彩画** - 柔和的水彩晕染效果
            6. **波普艺术** - 鲜艳的色彩和色块
            
            **提示**: 上传您的图像后，可以选择不同的风格，获得个性化的艺术效果！
            """)
# 10. 风格迁移选项卡
with tabs[9]:
    st.markdown("### 🌟 风格迁移与艺术化")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：文化传承与创新</h4>
        <p>
        风格迁移技术体现了<strong style='color: #dc2626;'>文化传承与创新</strong>，
        通过现代技术重现经典艺术风格，这体现了<strong style='color: #dc2626;'>文化自信</strong>。
        在技术应用中，我们要注重文化传承。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件", 
        type=["jpg", "jpeg", "png"], 
        key="tab10_upload"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        # 保存RGB版本用于显示
        image_rgb = np.array(pil_image)
        # 转换为BGR用于OpenCV处理
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # 初始化结果变量
        result_rgb = None
        
        style_type = st.selectbox("选择艺术风格", 
                                  ["梵高风格", "星空风格", "莫奈印象派", 
                                   "毕加索立体主义", "动漫风格"])
        
        if style_type == "梵高风格":
            col1, col2 = st.columns(2)
            with col1:
                twist_strength = st.slider("扭曲强度", 0.0005, 0.002, 0.001, 0.0001, 
                                          key="vangogh_twist")
            with col2:
                color_intensity = st.slider("色彩强度", 0.5, 2.0, 1.5, 0.1, 
                                           key="vangogh_color")
            
            if st.button("🎨 应用梵高风格", use_container_width=True, key="vangogh_btn"):
                with st.spinner("正在创作梵高风格..."):
                    # 临时调整颜色强度
                    if color_intensity != 1.0:
                        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
                        hsv[:,:,1] = cv2.multiply(hsv[:,:,1], color_intensity).clip(0, 255)
                        temp_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                        result_bgr = apply_van_gogh_style(temp_image, twist_strength)
                    else:
                        result_bgr = apply_van_gogh_style(image_bgr, twist_strength)
                    
                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        elif style_type == "星空风格":
            col1, col2 = st.columns(2)
            with col1:
                star_density = st.slider("星星密度", 50, 300, 150, key="starry_stars")
            with col2:
                blue_intensity = st.slider("蓝色强度", 0.5, 2.0, 1.2, 0.1, key="starry_blue")
            
            if st.button("🌌 应用星空风格", use_container_width=True, key="starry_btn"):
                with st.spinner("正在绘制星空..."):
                    # 调整蓝色强度
                    if blue_intensity != 1.0:
                        lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
                        l, a, b = cv2.split(lab)
                        b = cv2.multiply(b, blue_intensity).clip(0, 255)
                        lab = cv2.merge([l, a, b])
                        temp_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                        result_bgr = apply_starry_sky_style(temp_image)
                    else:
                        result_bgr = apply_starry_sky_style(image_bgr)
                    
                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        elif style_type == "莫奈印象派":
            col1, col2 = st.columns(2)
            with col1:
                brush_size = st.slider("笔触大小", 5, 20, 10, key="monet_brush")
            with col2:
                color_vivid = st.slider("色彩鲜艳度", 0.5, 2.0, 1.3, 0.1, key="monet_color")
            
            if st.button("🌸 应用莫奈风格", use_container_width=True, key="monet_btn"):
                with st.spinner("正在创作印象派..."):
                    result_bgr = apply_monet_style(image_bgr)
                    
                    # 调整笔触和色彩
                    if brush_size != 10 or color_vivid != 1.3:
                        # 重新调整颜色
                        hsv = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2HSV)
                        hsv[:,:,1] = cv2.multiply(hsv[:,:,1], color_vivid).clip(0, 255)
                        result_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                    
                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        elif style_type == "毕加索立体主义":
            col1, col2 = st.columns(2)
            with col1:
                grid_size = st.slider("几何块大小", 10, 50, 30, key="picasso_grid")
            with col2:
                color_simplify = st.slider("颜色简化度", 4, 16, 8, key="picasso_colors")
            
            if st.button("🔷 应用立体主义风格", use_container_width=True, key="picasso_btn"):
                with st.spinner("正在创作立体主义作品..."):
                    result_bgr = apply_picasso_cubist_style(image_bgr)
                    
                    # 调整颜色简化度
                    if color_simplify != 8:
                        pixels = result_bgr.reshape((-1, 3))
                        pixels = np.float32(pixels)
                        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
                        _, labels, centers = cv2.kmeans(pixels, color_simplify, None, 
                                                        criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
                        centers = np.uint8(centers)
                        simplified = centers[labels.flatten()]
                        result_bgr = simplified.reshape(result_bgr.shape)
                    
                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        else:  # 动漫风格
            col1, col2 = st.columns(2)
            with col1:
                edge_thickness = st.slider("轮廓粗细", 1, 5, 2, key="anime_edge")
            with col2:
                flatness = st.slider("色彩平坦度", 0.5, 2.0, 1.4, 0.1, key="anime_flat")
            
            if st.button("🎭 应用动漫风格", use_container_width=True, key="anime_btn"):
                with st.spinner("正在转换为动漫风格..."):
                    result_bgr = apply_anime_style(image_bgr)
                    
                    # 调整轮廓粗细
                    if edge_thickness != 2:
                        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
                        g1 = cv2.GaussianBlur(gray, (5, 5), 0.5)
                        g2 = cv2.GaussianBlur(gray, (5, 5), 2.0)
                        dog = g1 - g2
                        _, edges = cv2.threshold(dog, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                        edges = cv2.ximgproc.thinning(edges)
                        
                        # 根据厚度调整轮廓
                        kernel_size = edge_thickness * 2 + 1
                        kernel = np.ones((kernel_size, kernel_size), np.uint8)
                        edges_thick = cv2.dilate(edges, kernel)
                        
                        # 应用新的轮廓
                        edges_bgr = cv2.cvtColor(edges_thick, cv2.COLOR_GRAY2BGR)
                        outline_color = (30, 30, 30)
                        edges_colored = cv2.bitwise_and(edges_bgr, outline_color)
                        result_bgr = cv2.subtract(result_bgr, edges_colored)
                    
                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        # 显示结果和下载
        if result_rgb is not None:
            # 艺术信息卡片
            with st.expander("🎨 艺术风格介绍", expanded=False):
                if style_type == "梵高风格":
                    st.markdown("""
                    **文森特·梵高** - 荷兰后印象派画家
                    - 特点：强烈的色彩、旋转的笔触、情感表达
                    - 代表作：《星空》、《向日葵》
                    """)
                elif style_type == "星空风格":
                    st.markdown("""
                    **梵高《星空》风格**
                    - 特点：旋涡状的天空、明亮的星星、蓝色基调
                    - 技术：油画技法和独特的视角
                    """)
                elif style_type == "莫奈印象派":
                    st.markdown("""
                    **克劳德·莫奈** - 法国印象派创始人
                    - 特点：捕捉光影变化、柔和的色彩、笔触明显
                    - 代表作：《睡莲》、《日出·印象》
                    """)
                elif style_type == "毕加索立体主义":
                    st.markdown("""
                    **巴勃罗·毕加索** - 西班牙立体主义画家
                    - 特点：几何分解、多视角融合、色彩简化
                    - 代表作：《亚威农少女》、《格尔尼卡》
                    """)
                else:  # 动漫风格
                    st.markdown("""
                    **动漫艺术风格**
                    - 特点：平坦着色、黑色轮廓、夸张的表情
                    - 技术：赛璐珞动画风格、线条清晰
                    """)
            
            # 效果对比展示
            st.markdown("### 🖼️ 艺术效果对比")
            
            col1, col2 = st.columns(2)
            with col1:
                # 原始图像
                st.markdown("#### 📷 原始图像")
                st.image(image_rgb, use_container_width=True)
                
                # 添加艺术处理建议
                with st.expander("💡 艺术处理建议", expanded=False):
                    st.write("""
                    1. **人像照片**：适合动漫风格、莫奈风格
                    2. **风景照片**：适合梵高风格、星空风格
                    3. **建筑照片**：适合毕加索立体主义风格
                    4. **色彩丰富**：适合所有艺术风格
                    """)
            
            with col2:
                # 艺术结果
                st.markdown(f"#### 🎨 {style_type}")
                st.image(result_rgb, use_container_width=True)
                
                # 艺术效果分析
                with st.expander("📊 艺术效果分析", expanded=False):
                    # 计算一些艺术特征
                    brightness = np.mean(result_rgb)
                    contrast = np.std(result_rgb)
                    
                    # 颜色丰富度
                    unique_colors = len(np.unique(result_rgb.reshape(-1, 3), axis=0))
                    
                    st.write(f"亮度: {brightness:.1f}")
                    st.write(f"对比度: {contrast:.1f}")
                    st.write(f"颜色数量: {unique_colors}")
                    
                    # 风格评估
                    if style_type == "动漫风格":
                        edge_pixels = np.sum(cv2.Canny(cv2.cvtColor(result_rgb, cv2.COLOR_RGB2GRAY), 50, 150) > 0)
                        st.write(f"轮廓强度: {edge_pixels/(result_rgb.shape[0]*result_rgb.shape[1]):.2%}")
            
            # 分割线
            st.markdown("---")
            
            # 艺术创作选项
            st.markdown("### 🎨 艺术创作选项")
            
            # 增强效果选项
            col1, col2, col3 = st.columns(3)
            with col1:
                enhance_style = st.selectbox("增强效果", 
                                           ["无", "增强对比度", "添加画框", "添加签名"],
                                           key="enhance_style")
            
            if enhance_style == "增强对比度":
                with col2:
                    contrast_level = st.slider("对比度级别", 0.5, 2.0, 1.2, 0.1, key="art_contrast")
            elif enhance_style == "添加画框":
                with col2:
                    frame_type = st.selectbox("画框类型", ["古典", "现代", "简约"], key="frame_type")
            
            # 处理增强
            if st.button("✨ 应用增强效果", use_container_width=True, key="enhance_btn"):
                enhanced_rgb = result_rgb.copy()
                
                if enhance_style == "增强对比度":
                    enhanced_rgb = cv2.convertScaleAbs(enhanced_rgb, alpha=contrast_level)
                elif enhance_style == "添加画框":
                    # 添加简单的画框效果
                    h, w = enhanced_rgb.shape[:2]
                    frame_color = (50, 50, 50) if frame_type == "简约" else \
                                 (139, 69, 19) if frame_type == "古典" else \
                                 (200, 200, 200)
                    
                    frame_size = 20
                    enhanced_rgb[:frame_size, :] = frame_color
                    enhanced_rgb[-frame_size:, :] = frame_color
                    enhanced_rgb[:, :frame_size] = frame_color
                    enhanced_rgb[:, -frame_size:] = frame_color
                
                result_rgb = enhanced_rgb
                st.success("增强效果已应用！")
            
            # 下载选项
            st.markdown("### 📥 艺术创作下载")
            
            download_cols = st.columns(4)
            with download_cols[0]:
                provide_download_button(
                    result_rgb, 
                    f"艺术_{style_type}.jpg", 
                    "🎨 下载艺术作品",
                    unique_key_suffix="art_main"
                )
            
            with download_cols[1]:
                # 缩略图版本
                thumbnail = cv2.resize(result_rgb, (400, 400))
                provide_download_button(
                    thumbnail, 
                    f"艺术_{style_type}_缩略图.jpg", 
                    "🖼️ 下载缩略图",
                    unique_key_suffix="art_thumb"
                )
            
            with download_cols[2]:
                # 社交媒体版本
                social_size = (1080, 1080)
                social_img = cv2.resize(result_rgb, social_size)
                provide_download_button(
                    social_img, 
                    f"艺术_{style_type}_社交媒体.jpg",  # 修改这里：styleType -> style_type
                    "📱 社交媒体版",
                    unique_key_suffix="art_social"
                )
            
            with download_cols[3]:
                # 打印版本（高分辨率）
                if result_rgb.shape[0] > 1000:
                    print_img = result_rgb
                else:
                    print_img = cv2.resize(result_rgb, 
                                          (result_rgb.shape[1]*2, result_rgb.shape[0]*2))
                provide_download_button(
                    print_img, 
                    f"艺术_{style_type}_打印版.jpg", 
                    "🖨️ 打印版本",
                    unique_key_suffix="art_print"
                )
            
            # 艺术画廊展示
            with st.expander("🖼️ 其他风格预览", expanded=False):
                preview_cols = st.columns(5)
                preview_styles = ["梵高风格", "星空风格", "莫奈印象派", 
                                 "毕加索立体主义", "动漫风格"]
                
                for idx, (col, preview_style) in enumerate(zip(preview_cols, preview_styles)):
                    with col:
                        st.caption(preview_style)
                        
                        # 创建小预览
                        preview_size = (120, 120)
                        
                        if preview_style == "梵高风格":
                            preview_img = apply_van_gogh_style(image_bgr[:100, :100], 0.001)
                            preview_rgb = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
                        elif preview_style == "星空风格":
                            preview_img = apply_starry_sky_style(image_bgr[:100, :100])
                            preview_rgb = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
                        elif preview_style == "莫奈印象派":
                            preview_img = apply_monet_style(image_bgr[:100, :100])
                            preview_rgb = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
                        elif preview_style == "毕加索立体主义":
                            preview_img = apply_picasso_cubist_style(image_bgr[:100, :100])
                            preview_rgb = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
                        else:  # 动漫风格
                            preview_img = apply_anime_style(image_bgr[:100, :100])
                            preview_rgb = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
                        
                        st.image(cv2.resize(preview_rgb, preview_size), 
                                use_container_width=True)
    else:
        st.info("📤 请上传图像文件开始艺术创作")
        
# 11. 老照片上色选项卡
with tabs[10]:
    st.markdown("### 🖼️ 老照片上色与修复")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：历史传承与记忆</h4>
        <p>
        老照片上色技术体现了<strong style='color: #dc2626;'>历史传承</strong>的意义，
        通过技术手段重现历史色彩，这体现了<strong style='color: #dc2626;'>记忆传承</strong>的价值。
        在技术应用中，我们要尊重历史，传承文化。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择黑白或老旧照片", 
        type=["jpg", "jpeg", "png"], 
        key="tab11_upload"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        # 保存RGB版本用于显示
        image_rgb = np.array(pil_image)
        # 转换为BGR用于OpenCV处理
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # 显示原始图像
        col1, col2 = st.columns(2)
        with col1:
            st.image(image_rgb, caption="原始照片", use_container_width=True)
        
        # 检查图像是否是黑白的
        is_colorful = True
        if len(image_rgb.shape) == 3:
            # 计算颜色差异
            r_channel = image_rgb[:,:,0]
            g_channel = image_rgb[:,:,1]
            b_channel = image_rgb[:,:,2]
            
            # 如果三个通道非常相似，可能是黑白图像
            diff_rg = np.abs(r_channel.astype(float) - g_channel.astype(float)).mean()
            diff_rb = np.abs(r_channel.astype(float) - b_channel.astype(float)).mean()
            diff_gb = np.abs(g_channel.astype(float) - b_channel.astype(float)).mean()
            
            # 如果平均差异很小，可能是黑白图像
            avg_diff = (diff_rg + diff_rb + diff_gb) / 3
            is_colorful = avg_diff > 15  # 稍微提高阈值
            
            with col2:
                st.markdown("### 🔍 图像分析")
                st.info(f"颜色差异度: {avg_diff:.2f}")
                
                if avg_diff < 10:
                    st.success("✅ 检测到黑白/灰度图像")
                elif avg_diff < 15:
                    st.warning("⚠️ 检测到近灰度图像，上色效果较好")
                else:
                    st.warning("⚠️ 检测到彩色图像，上色效果可能不明显")
        
        # 添加颜色调整参数
        st.markdown("### 🎨 上色参数设置")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 选择上色模式
            colorize_mode = st.selectbox(
                "上色模式",
                ["智能上色", "复古色调", "鲜艳色调", "自然色调", "AI增强上色"],
                help="选择不同的上色风格"
            )
            
            # 是否强制去色
            force_grayscale = st.checkbox(
                "强制转换为黑白图像", 
                value=not is_colorful,
                help="如果原始图像已经是彩色，可以强制转换为黑白再上色"
            )
            
        with col2:
            # 颜色增强参数
            saturation = st.slider("饱和度", 0.5, 3.0, 1.2, 0.1,
                                  help="调整颜色的鲜艳程度")
            
            brightness = st.slider("亮度", -30, 30, 0,
                                  help="调整图像的整体亮度")
            
            color_intensity = st.slider("色彩强度", 0.5, 1.5, 1.0, 0.1,
                                       help="控制上色的强度")
            
        with col3:
            # 对比度参数
            contrast = st.slider("对比度", 0.5, 2.0, 1.0, 0.1,
                                help="调整图像的对比度")
            
            # 降噪强度
            denoise_strength = st.slider("降噪强度", 0, 10, 3,
                                        help="去除图像噪点")
            
            # AI辅助
            ai_assist = st.checkbox("启用AI智能识别", True,
                                   help="使用智能算法识别图像内容")
        
        # 如果需要强制去色
        process_image = image_bgr.copy()
        if force_grayscale and is_colorful:
            # 转换为灰度图
            gray = cv2.cvtColor(process_image, cv2.COLOR_BGR2GRAY)
            # 将灰度图转换为三通道BGR
            process_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # 使用新的老照片上色函数
        def enhanced_colorize_old_photo(image, mode="智能上色", color_intensity=1.0, 
                                       saturation=1.2, brightness=0, contrast=1.0, 
                                       denoise=3, ai_assist=True):
            """增强版老照片上色，真正实现黑白转彩色"""
            # 根据模式选择不同的上色方法
            if mode == "AI增强上色":
                # 使用我提供的完整AI上色函数
                result = colorize_old_photo(image, color_intensity, ai_assist)
                
            elif mode == "智能上色":
                # 使用优化的智能上色
                result = smart_colorize_photo(image, color_intensity)
                
            elif mode == "复古色调":
                # 先上色，然后添加复古滤镜
                base_colored = smart_colorize_photo(image, color_intensity)
                result = apply_vintage_filter(base_colored)
                
            elif mode == "鲜艳色调":
                # 鲜艳风格上色
                base_colored = smart_colorize_photo(image, color_intensity)
                result = enhance_color_vibrance(base_colored, saturation * 1.5)
                
            else:  # 自然色调
                # 自然风格上色
                base_colored = smart_colorize_photo(image, color_intensity * 0.8)
                result = apply_natural_tones(base_colored)
            
            # 应用饱和度调整
            hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
            hsv[:,:,1] = cv2.multiply(hsv[:,:,1], saturation).clip(0, 255)
            
            # 应用亮度和对比度调整
            hsv[:,:,2] = cv2.addWeighted(
                hsv[:,:,2], contrast, 
                np.zeros_like(hsv[:,:,2]), 0, 
                brightness
            ).clip(0, 255)
            
            result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            # 应用降噪
            if denoise > 0:
                result = cv2.bilateralFilter(result, 9, denoise*25, denoise*25)
            
            return result
        
        # 辅助函数
        def smart_colorize_photo(image, color_intensity=1.0):
            """优化的智能上色函数"""
            # 如果是彩色图像且需要上色，先转换为灰度再处理
            if len(image.shape) == 3:
                # 检查是否是真正的彩色图
                b, g, r = cv2.split(image)
                diff = np.abs(b.astype(float) - g.astype(float)).mean() + \
                      np.abs(b.astype(float) - r.astype(float)).mean() + \
                      np.abs(g.astype(float) - r.astype(float)).mean()
                
                if diff > 15:  # 彩色图像
                    # 转换为灰度再上色
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            # 基础的上色处理
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # 增强亮度对比度
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_enhanced = clahe.apply(l)
            
            # 智能添加颜色
            height, width = l_enhanced.shape
            
            # 根据亮度区域智能上色
            for i in range(height):
                for j in range(width):
                    brightness = l_enhanced[i, j] / 255.0
                    
                    # 智能上色规则
                    if brightness > 0.8:  # 高亮区域（天空/云）
                        a[i, j] = 128 + int(64 * brightness)  # 偏青色
                        b[i, j] = 128 + int(96 * brightness)  # 偏蓝色
                    elif brightness > 0.6:  # 中等偏亮（皮肤/墙壁）
                        a[i, j] = 140 + int(40 * brightness)  # 偏暖色
                        b[i, j] = 100 + int(30 * brightness)  # 偏黄色
                    elif brightness > 0.4:  # 中等亮度（植被）
                        a[i, j] = 90 + int(70 * brightness)   # 偏绿色
                        b[i, j] = 120 + int(40 * brightness)  # 偏黄色
                    elif brightness > 0.2:  # 暗部（土地/阴影）
                        a[i, j] = 110 + int(30 * brightness)  # 偏棕色
                        b[i, j] = 80 + int(20 * brightness)   # 偏蓝色
                    else:  # 很暗的区域
                        a[i, j] = 128
                        b[i, j] = 128
            
            # 应用颜色强度
            a_center = 128
            b_center = 128
            a = ((a - a_center) * color_intensity + a_center).clip(0, 255).astype(np.uint8)
            b = ((b - b_center) * color_intensity + b_center).clip(0, 255).astype(np.uint8)
            
            lab_colored = cv2.merge([l_enhanced, a, b])
            result = cv2.cvtColor(lab_colored, cv2.COLOR_LAB2BGR)
            
            return result
        
        def apply_vintage_filter(image):
            """应用复古滤镜"""
            # 添加棕褐色调
            sepia_filter = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ], dtype=np.float32)
            
            vintage = cv2.transform(image, sepia_filter)
            vintage = np.clip(vintage, 0, 255).astype(np.uint8)
            
            # 添加轻微噪点
            noise = np.random.normal(0, 3, vintage.shape).astype(np.int16)
            vintage = cv2.add(vintage.astype(np.int16), noise)
            vintage = np.clip(vintage, 0, 255).astype(np.uint8)
            
            return vintage
        
        def enhance_color_vibrance(image, saturation_factor=1.5):
            """增强颜色鲜艳度"""
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hsv[:,:,1] = cv2.multiply(hsv[:,:,1], saturation_factor).clip(0, 255)
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        def apply_natural_tones(image):
            """应用自然色调"""
            # 轻微降低饱和度，使颜色更自然
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hsv[:,:,1] = cv2.multiply(hsv[:,:,1], 0.8).clip(0, 255)
            
            # 增加一点暖色调
            hsv[:,:,0] = (hsv[:,:,0] + 5) % 180
            
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # 添加预览按钮
        st.markdown("---")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🎨 应用上色效果", use_container_width=True):
                with st.spinner("正在智能上色中..."):
                    # 使用BGR图像处理
                    result_bgr = enhanced_colorize_old_photo(
                        process_image, 
                        mode=colorize_mode,
                        color_intensity=color_intensity,
                        saturation=saturation,
                        brightness=brightness,
                        contrast=contrast,
                        denoise=denoise_strength,
                        ai_assist=ai_assist
                    )
                    # 转换为RGB用于显示
                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
                    
                    # 存储结果
                    st.session_state.colorize_result_rgb = result_rgb
                    st.session_state.colorize_result_bgr = result_bgr
                    
                    st.success("✅ 上色完成！")
        
        with col_btn2:
            if st.button("🔄 重置参数", use_container_width=True):
                # 重置所有参数到默认值
                st.rerun()
        
        # 显示结果
        if 'colorize_result_rgb' in st.session_state:
            st.markdown("### 🎉 上色结果对比")
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(image_rgb, caption="原始照片", use_container_width=True)
                
                # 显示原始图像信息
                with st.expander("📊 原始图像信息", expanded=False):
                    st.write(f"尺寸: {image_rgb.shape[1]} × {image_rgb.shape[0]}")
                    st.write(f"亮度: {np.mean(image_rgb):.1f}")
                    st.write(f"对比度: {np.std(image_rgb):.1f}")
            
            with col2:
                result_rgb = st.session_state.colorize_result_rgb
                st.image(result_rgb, 
                        caption=f"上色结果 ({colorize_mode})", 
                        use_container_width=True)
                
                # 显示处理后的图像信息
                with st.expander("📊 上色后图像信息", expanded=False):
                    st.write(f"尺寸: {result_rgb.shape[1]} × {result_rgb.shape[0]}")
                    st.write(f"亮度: {np.mean(result_rgb):.1f}")
                    st.write(f"对比度: {np.std(result_rgb):.1f}")
                    
                    # 计算颜色丰富度
                    unique_colors = len(np.unique(result_rgb.reshape(-1, 3), axis=0))
                    st.write(f"颜色数量: {unique_colors}")
                    
                    # 计算饱和度变化
                    if len(image_rgb.shape) == 3:
                        # 计算原始图像饱和度
                        hsv_orig = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
                        sat_orig = np.mean(hsv_orig[:,:,1])
                        
                        # 计算处理后饱和度
                        hsv_result = cv2.cvtColor(result_rgb, cv2.COLOR_RGB2HSV)
                        sat_result = np.mean(hsv_result[:,:,1])
                        
                        sat_change = ((sat_result - sat_orig) / sat_orig * 100) if sat_orig > 0 else 0
                        st.write(f"饱和度变化: {sat_change:+.1f}%")
            
            # 分割线
            st.markdown("---")
            
            # 下载选项
            st.markdown("### 📥 下载上色结果")
            
            col_dl1, col_dl2, col_dl3 = st.columns(3)
            
            with col_dl1:
                provide_download_button(
                    result_rgb, 
                    f"colorized_{colorize_mode}.jpg", 
                    "💾 下载JPEG格式",
                    unique_key_suffix="colorize_jpg"
                )
            
            with col_dl2:
                # PNG格式
                png_buffer = io.BytesIO()
                result_pil = Image.fromarray(result_rgb)
                result_pil.save(png_buffer, format="PNG")
                png_buffer.seek(0)
                
                st.download_button(
                    label="🖼️ 下载PNG格式",
                    data=png_buffer,
                    file_name=f"colorized_{colorize_mode}.png",
                    mime="image/png",
                    use_container_width=True
                )
            
            with col_dl3:
                # 高质量版本
                high_buffer = io.BytesIO()
                result_pil.save(high_buffer, format="JPEG", quality=100)
                high_buffer.seek(0)
                
                st.download_button(
                    label="🌟 最高质量",
                    data=high_buffer,
                    file_name=f"colorized_{colorize_mode}_高质量.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
            
            # 添加处理建议
            st.markdown("### 💡 上色处理建议")
            
            tips_cols = st.columns(2)
            with tips_cols[0]:
                st.markdown("""
                **👤 人像照片建议:**
                - 使用 **自然色调** 或 **智能上色**
                - 饱和度: 1.0-1.3
                - 色彩强度: 0.8-1.0
                - 启用AI智能识别
                """)
            
            with tips_cols[1]:
                st.markdown("""
                **🏞️ 风景照片建议:**
                - 使用 **鲜艳色调** 或 **AI增强上色**
                - 饱和度: 1.2-1.5
                - 色彩强度: 1.0-1.3
                - 对比度: 1.1-1.3
                """)
    else:
        # 没有上传文件时的界面
        st.info("📤 请上传黑白或老旧照片开始上色")
        
        # 显示示例
        if st.checkbox("显示上色示例", key="colorize_demo"):
            st.markdown("### 📝 老照片上色示例")
            
            # 创建示例黑白图像
            demo_image_gray = np.ones((300, 400), dtype=np.uint8) * 150
            cv2.putText(demo_image_gray, "Old Photo", (120, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, 100, 3)
            
            # 转换为彩色用于显示
            demo_gray_bgr = cv2.cvtColor(demo_image_gray, cv2.COLOR_GRAY2BGR)
            demo_gray_rgb = cv2.cvtColor(demo_gray_bgr, cv2.COLOR_BGR2RGB)
            
            # 应用简单上色
            demo_lab = cv2.cvtColor(demo_gray_bgr, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(demo_lab)
            
            # 添加颜色
            a = np.full_like(a, 140)
            b = np.full_like(b, 120)
            
            demo_colored_lab = cv2.merge([l, a, b])
            demo_colored_bgr = cv2.cvtColor(demo_colored_lab, cv2.COLOR_LAB2BGR)
            demo_colored_rgb = cv2.cvtColor(demo_colored_bgr, cv2.COLOR_BGR2RGB)
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(demo_gray_rgb, caption="示例黑白照片", use_container_width=True)
            with col2:
                st.image(demo_colored_rgb, caption="上色后效果", use_container_width=True)    




# 12. 数字形态学选项卡
with tabs[11]:
    st.markdown("### ⚙️ 数字形态学转换")
    
    st.markdown("""
    <div class='ideology-card'>
        <h4>🎯 思政关联：结构化思维</h4>
        <p>
        数字形态学技术体现了<strong style='color: #dc2626;'>结构化</strong>思维，
        通过数学形态处理图像结构，这体现了<strong style='color: #dc2626;'>系统化</strong>的工作方法。
        在技术学习中，我们要培养结构化思维。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 选择图像文件（推荐二值图像）", 
        type=["jpg", "jpeg", "png"], 
        key="tab12_upload"
    )
    
    if uploaded_file is not None:
        # 读取图像
        pil_image = Image.open(uploaded_file)
        # 保存RGB版本用于显示
        image_rgb = np.array(pil_image)
        
        # 转换为BGR用于OpenCV处理
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # 如果图像不是二值图，先转换为灰度再二值化
        if len(image_bgr.shape) == 3:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            # 将二值图像转换为BGR三通道
            image_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            # 同时更新用于显示的RGB版本
            image_rgb = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
        
        operation = st.selectbox("选择形态学操作", 
                                ["腐蚀", "膨胀", "开运算", "闭运算"])
        
        kernel_size = st.slider("核大小", 3, 15, 5, step=2)
        
        if operation == "腐蚀":
            result_bgr = apply_erosion(image_bgr, kernel_size)
        elif operation == "膨胀":
            result_bgr = apply_dilation(image_bgr, kernel_size)
        elif operation == "开运算":
            result_bgr = apply_opening(image_bgr, kernel_size)
        else:  # 闭运算
            result_bgr = apply_closing(image_bgr, kernel_size)
        
        # 转换为RGB用于显示和下载
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        col1, col2 = st.columns(2)
        with col1:
            # 显示RGB原始图像
            st.image(image_rgb, caption="原始图像（已二值化）", use_container_width=True)
        with col2:
            # 显示RGB处理结果
            st.image(result_rgb, caption=f"{operation}结果", use_container_width=True)
        
        # 下载时传递RGB版本
        provide_download_button(result_rgb, f"morphology_{operation}.jpg", "📥 下载结果")
    else:
        st.info("请上传图像文件开始处理")

# 13. 实验提交选项卡
with tabs[12]:
    st.markdown("### 📝 实验提交中心")
    
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
        
        experiment_title = get_experiment_title(experiment_number)
        
        st.markdown(f"### {experiment_title}")
        st.markdown(get_experiment_description(experiment_number))
        
        # 提交内容
        submission_content = st.text_area(
            "实验报告内容",
            placeholder="请详细描述您的实验过程、结果分析、遇到的问题及解决方案...",
            height=300
        )
        
        # 文件上传
        uploaded_files = st.file_uploader(
            "上传实验文件（代码、结果图像、报告文档等）",
            type=['py', 'jpg', 'png', 'zip', 'pdf', 'doc', 'docx', 'txt', 'cpp', 'c', 'java'],
            accept_multiple_files=True,
            help="支持多种文件格式：代码文件(.py, .java, .cpp, .c)、图像文件(.jpg, .png)、文档(.pdf, .doc, .docx)、压缩包(.zip)等"
        )
        
        # 显示已选择的文件
        if uploaded_files:
            st.markdown("**已选择的文件:**")
            for file in uploaded_files:
                st.markdown(f"""
                <div class='file-item'>
                    <span>📎 {file.name}</span>
                    <span style='color: #666; font-size: 0.9rem;'>{file.size / 1024:.1f} KB</span>
                </div>
                """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📤 提交实验", use_container_width=True):
                if submission_content.strip():
                    # 确保用户已登录
                    if 'username' not in st.session_state:
                        st.session_state.username = "demo_student"
                    
                    success, message, submission_id = submit_experiment(
                        st.session_state.username,
                        experiment_number,
                        experiment_title,
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
                        st.session_state.show_my_submissions = True
                        
                        # 添加延迟刷新
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("请填写实验报告内容")
        
        with col2:
            if st.button("🔄 查看我的提交", use_container_width=True):
                st.session_state.show_my_submissions = True
        
        # 显示我的提交记录
        if st.session_state.get('show_my_submissions', False):
            st.markdown("---")
            st.markdown("### 📋 我的实验提交记录")
            
            # 确保用户已登录
            if 'username' not in st.session_state:
                st.session_state.username = "demo_student"
            
            submissions = get_student_experiments(st.session_state.username)
            
            if submissions:
                # 统计信息
                total_submissions = len(submissions)
                graded_submissions = len([s for s in submissions if s[6] == 'graded'])
                pending_submissions = len([s for s in submissions if s[6] == 'pending'])
                average_score = sum([s[8] for s in submissions if s[6] == 'graded']) / graded_submissions if graded_submissions > 0 else 0
                
                # 显示统计卡片
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown("""
                    <div class='stats-card'>
                        <div>📊 总提交</div>
                        <div class='stats-number'>{}</div>
                        <div class='stats-label'>实验总数</div>
                    </div>
                    """.format(total_submissions), unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class='stats-card'>
                        <div>✅ 已批改</div>
                        <div class='stats-number'>{}</div>
                        <div class='stats-label'>完成评分</div>
                    </div>
                    """.format(graded_submissions), unsafe_allow_html=True)
                with col3:
                    st.markdown("""
                    <div class='stats-card'>
                        <div>⏳ 待批改</div>
                        <div class='stats-number'>{}</div>
                        <div class='stats-label'>等待评分</div>
                    </div>
                    """.format(pending_submissions), unsafe_allow_html=True)
                with col4:
                    st.markdown("""
                    <div class='stats-card'>
                        <div>🎯 平均分</div>
                        <div class='stats-number'>{:.1f}</div>
                        <div class='stats-label'>当前成绩</div>
                    </div>
                    """.format(average_score), unsafe_allow_html=True)
                
                # 显示详细提交记录
                st.markdown("### 详细提交记录")
                for sub in submissions:
                    status_info = {
                        'pending': ('⏳ 待批改', 'status-pending'),
                        'graded': ('✅ 已评分', 'status-graded'),
                        'returned': ('🔙 已退回', 'status-returned')
                    }.get(sub[6], ('⚪ 未知', ''))
                    
                    with st.expander(f"{status_info[0]} - 实验{sub[2]}: {sub[3]} - {sub[5]}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown("**📝 提交内容:**")
                            st.text_area("内容", sub[4], height=150, key=f"content_{sub[0]}", disabled=True)
                            
                            # 显示提交的文件 - 简化版本，只显示文件名
                            if len(sub) > 10 and sub[10]:  # file_names字段
                                file_list = sub[10].split(',') if sub[10] else []
                                if file_list:
                                    st.markdown("**📎 提交的文件:**")
                                    for filename in file_list:
                                        if filename.strip():
                                            st.markdown(f"- {filename}")
                                    
                                    # 提供打包下载
                                    zip_path = create_zip_file(sub[0], st.session_state.username)
                                    if zip_path and os.path.exists(zip_path):
                                        with open(zip_path, "rb") as zip_file:
                                            zip_data = zip_file.read()
                                            st.download_button(
                                                label="📦 下载所有文件(ZIP)",
                                                data=zip_data,
                                                file_name=f"实验{sub[2]}_提交文件.zip",
                                                mime="application/zip",
                                                key=f"zip_{sub[0]}",
                                                use_container_width=True
                                            )
                            
                            # 显示分数和反馈（如果已评分且允许查看）
                            if sub[6] == 'graded' and sub[9]:  # 已评分且允许查看
                                st.markdown(f"""
                                <div class='score-badge'>
                                    🎯 得分: {sub[8]}/100
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if sub[7]:  # 教师反馈
                                    st.markdown("**💬 教师反馈:**")
                                    st.info(sub[7])
                        
                        with col2:
                            st.markdown(f"**📊 状态:**")
                            st.markdown(f"<span class='{status_info[1]} status-badge'>{status_info[0]}</span>", unsafe_allow_html=True)
                            st.markdown(f"**🕒 提交时间:** {sub[5]}")
                            st.markdown(f"**🔢 提交ID:** `{sub[0]}`")

                            # 添加分数显示（美观版本）
                            if sub[6] == 'graded' and sub[9]:  # 已评分且允许查看
                                score_color = "#10b981" if sub[8] >= 80 else "#f59e0b" if sub[8] >= 60 else "#ef4444"
                                st.markdown(f"""
                                <div style='background: {score_color}; color: white; padding: 8px 16px; border-radius: 20px; 
                                            font-weight: bold; text-align: center; margin: 10px 0;'>
                                    🎯 得分: {sub[8]}/100
                                </div>
                                """, unsafe_allow_html=True)
                            elif sub[6] == 'graded' and not sub[9]:  # 已评分但不允许查看
                                st.markdown("""
                                <div style='background: #6b7280; color: white; padding: 8px 16px; border-radius: 20px; 
                                            font-weight: bold; text-align: center; margin: 10px 0;'>
                                    🔒 得分暂不可查看
                                </div>
                                """, unsafe_allow_html=True)
                            else:  # 待批改状态
                                st.markdown("""
                                <div style='background: #f59e0b; color: white; padding: 8px 16px; border-radius: 20px; 
                                            font-weight: bold; text-align: center; margin: 10px 0;'>
                                    ⏳ 得分待批改
                                </div>
                                """, unsafe_allow_html=True)

                            if sub[6] == 'pending':
                                if st.button("撤回", key=f"withdraw_{sub[0]}", use_container_width=True):
                                    success, msg = withdraw_experiment(sub[0], st.session_state.username)
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
            else:
                st.info("暂无提交记录，请先提交实验报告")
    
    elif st.session_state.get('role') == 'teacher':
        # 教师端：实验管理界面
        st.markdown("#### 👨‍🏫 教师实验管理")
        
        # 获取所有学生的实验提交
        all_submissions = get_all_experiments()
        
        if all_submissions:
            # 教师端统计信息
            total_submissions = len(all_submissions)
            pending_submissions = len([s for s in all_submissions if s[6] == 'pending'])
            graded_submissions = len([s for s in all_submissions if s[6] == 'graded'])
            average_score = sum([s[8] for s in all_submissions if s[6] == 'graded']) / graded_submissions if graded_submissions > 0 else 0
            
            # 显示统计卡片
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("""
                <div class='stats-card'>
                    <div>📊 总提交</div>
                    <div class='stats-number'>{}</div>
                    <div class='stats-label'>所有实验</div>
                </div>
                """.format(total_submissions), unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div class='stats-card'>
                    <div>⏳ 待批改</div>
                    <div class='stats-number'>{}</div>
                    <div class='stats-label'>等待评分</div>
                </div>
                """.format(pending_submissions), unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div class='stats-card'>
                    <div>✅ 已批改</div>
                    <div class='stats-number'>{}</div>
                    <div class='stats-label'>完成评分</div>
                </div>
                """.format(graded_submissions), unsafe_allow_html=True)
            with col4:
                st.markdown("""
                <div class='stats-card'>
                    <div>🎯 平均分</div>
                    <div class='stats-number'>{:.1f}</div>
                    <div class='stats-label'>班级平均</div>
                </div>
                """.format(average_score), unsafe_allow_html=True)
            
            # 按状态筛选
            st.markdown("### 🔍 筛选提交")
            filter_status = st.selectbox(
                "筛选状态",
                ["全部", "待批改", "已评分", "已退回"]
            )
            
            filtered_submissions = all_submissions
            if filter_status == "待批改":
                filtered_submissions = [s for s in all_submissions if s[6] == 'pending']
            elif filter_status == "已评分":
                filtered_submissions = [s for s in all_submissions if s[6] == 'graded']
            elif filter_status == "已退回":
                filtered_submissions = [s for s in all_submissions if s[6] == 'returned']
            
            st.markdown(f"**找到 {len(filtered_submissions)} 个提交**")
            
            # 显示提交列表
            for sub in filtered_submissions:
                status_info = {
                    'pending': ('⏳ 待批改', 'status-pending'),
                    'graded': ('✅ 已评分', 'status-graded'),
                    'returned': ('🔙 已退回', 'status-returned')
                }.get(sub[6], ('⚪ 未知', ''))
                
                with st.expander(f"{sub[1]} - 实验{sub[2]}: {sub[3]} - {status_info[0]} - {sub[5]}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown("**👤 学生:**")
                        st.info(f"**{sub[1]}**")
                        
                        st.markdown("**📝 提交内容:**")
                        st.text_area("内容", sub[4], height=150, key=f"teacher_content_{sub[0]}", disabled=True)
                        
                        # 显示提交的文件 - 简化版本
                        if len(sub) > 10 and sub[10]:
                            file_list = sub[10].split(',') if sub[10] else []
                            if file_list:
                                st.markdown("**📎 提交的文件:**")
                                for filename in file_list:
                                    if filename.strip():
                                        st.markdown(f"- {filename}")
                                
                                # 提供打包下载
                                zip_path = create_zip_file(sub[0], sub[1])
                                if zip_path and os.path.exists(zip_path):
                                    with open(zip_path, "rb") as zip_file:
                                        zip_data = zip_file.read()
                                        st.download_button(
                                            label="📦 下载所有文件(ZIP)",
                                            data=zip_data,
                                            file_name=f"{sub[1]}_实验{sub[2]}_提交文件.zip",
                                            mime="application/zip",
                                            key=f"teacher_zip_{sub[0]}",
                                            use_container_width=True
                                        )
                        
                        # 显示现有评分和反馈
                        if sub[6] == 'graded':
                            st.markdown(f"""
                            <div class='score-badge'>
                                🎯 当前得分: {sub[8]}/100
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if sub[7]:
                                st.markdown("**💬 当前反馈:**")
                                st.info(sub[7])
                    
                    with col2:
                        st.markdown(f"**📊 状态:**")
                        st.markdown(f"<span class='{status_info[1]} status-badge'>{status_info[0]}</span>", unsafe_allow_html=True)
                        st.markdown(f"**🕒 提交时间:** {sub[5]}")
                        st.markdown(f"**🔢 提交ID:** `{sub[0]}`")
                        
                        # 评分和反馈表单
                        st.markdown("---")
                        st.markdown("**📝 评分与反馈**")
                        
                        with st.form(key=f"grade_form_{sub[0]}"):
                            score = st.slider("评分", 0, 100, sub[8] if sub[8] else 60, key=f"score_{sub[0]}")
                            feedback = st.text_area("教师反馈", sub[7] if sub[7] else "", 
                                                  placeholder="请输入对学生的反馈意见...", 
                                                  key=f"feedback_{sub[0]}")
                            can_view_score = st.checkbox("允许学生查看分数", value=bool(sub[9]), key=f"view_{sub[0]}")
                            status = st.selectbox("状态", 
                                                ["pending", "graded", "returned"], 
                                                index=["pending", "graded", "returned"].index(sub[6]) if sub[6] in ["pending", "graded", "returned"] else 0,
                                                key=f"status_{sub[0]}")
                            
                            submitted = st.form_submit_button("💾 保存评分", use_container_width=True)
                            if submitted:
                                success, message = update_experiment_score(sub[0], score, feedback, can_view_score, status)
                                if success:
                                    st.success("✅ " + message)
                                    st.rerun()
                                else:
                                    st.error("❌ " + message)
        else:
            st.info("暂无学生提交的实验报告")
    
    else:
        # 未登录用户提示
        st.warning("请先登录以访问实验提交功能")



# 底部思政总结
st.markdown("---")
st.markdown("""
<div class='ideology-card'>
    <h3>🌟 思政学习总结</h3>
    <p style='text-align: center; font-size: 1.1rem;'>
    通过13个图像处理模块的学习与实践，我们不仅掌握了先进技术，更重要的是培养了
    <strong style='color: #dc2626;'>工匠精神、科学态度、创新意识、责任担当、系统思维、文化传承</strong>
    等综合素质。将个人成长与国家发展紧密结合，为实现科技强国目标贡献力量。
    </p>
</div>
""", unsafe_allow_html=True)

# 底部信息
st.markdown("""
<div style='text-align: center; margin-top: 40px; color: #666; font-size: 0.9rem;'>
    <p>🔬 数字图像处理实验室 v3.0 | 融合思政教育 | 培养创新人才</p>
    <p>© 2025 图像处理融思政平台 | 技术支持：OpenCV, Streamlit, NumPy</p>
</div>
""", unsafe_allow_html=True)
