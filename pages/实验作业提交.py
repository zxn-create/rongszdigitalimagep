import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from datetime import datetime, timedelta
import os
import zipfile
import tempfile
import shutil
import time
import pandas as pd
import random
from scipy import ndimage
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
import warnings
import re
import unicodedata
warnings.filterwarnings('ignore')

# ==================== Supabase 相关导入 ====================
from supabase import create_client, Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from email.utils import formataddr
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="作业提交台",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 现代化实验室CSS（增强版）- 保持原有CSS不变
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

# ==================== 增强的文件名清理工具函数 ====================

def sanitize_filename(filename):
    """
    清理文件名，确保只包含ASCII字符，适合Supabase Storage
    
    Args:
        filename: 原始文件名
    
    Returns:
        清理后的安全文件名（只包含字母、数字、点、下划线、连字符）
    """
    # 首先，将Unicode字符（包括中文）转换为ASCII表示或删除
    # 使用NFKD规范化，将Unicode字符分解为基本字符+组合标记
    normalized = unicodedata.normalize('NFKD', filename)
    # 只保留ASCII字符，其他都转换为下划线
    ascii_only = []
    for char in normalized:
        if ord(char) < 128:  # ASCII字符
            ascii_only.append(char)
        else:
            # 非ASCII字符（如中文）转换为下划线
            ascii_only.append('_')
    
    safe_name = ''.join(ascii_only)
    
    # 替换不安全的字符
    # 只允许字母、数字、点、下划线、连字符
    safe_name = re.sub(r'[^\w\s\.\-]', '_', safe_name)
    # 将空格替换为下划线
    safe_name = safe_name.replace(' ', '_')
    # 移除连续的多个下划线
    safe_name = re.sub(r'_+', '_', safe_name)
    # 移除开头和结尾的下划线
    safe_name = safe_name.strip('_')
    
    # 如果文件名为空，使用时间戳
    if not safe_name:
        safe_name = f"file_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 处理文件扩展名
    # 查找最后一个点，确保有扩展名
    parts = safe_name.rsplit('.', 1)
    if len(parts) > 1:
        base_name = parts[0]
        ext = parts[1]
        # 清理扩展名部分，只保留字母和数字
        ext = re.sub(r'[^a-zA-Z0-9]', '', ext)
        if ext:
            # 确保基本名称不为空
            if not base_name:
                base_name = f"file_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            safe_name = f"{base_name}.{ext}"
        else:
            safe_name = base_name
    else:
        safe_name = parts[0]
    
    # 再次确保名称不为空
    if not safe_name:
        safe_name = f"file_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return safe_name

def sanitize_path_component(component):
    """
    清理路径组件，确保用于构建存储路径的部分是安全的（只包含ASCII字符）
    
    Args:
        component: 路径组件（如用户名、作业ID等）
    
    Returns:
        清理后的安全组件
    """
    # 将组件转换为字符串
    str_component = str(component)
    
    # 将Unicode字符转换为ASCII或下划线
    normalized = unicodedata.normalize('NFKD', str_component)
    ascii_only = []
    for char in normalized:
        if ord(char) < 128:
            ascii_only.append(char)
        else:
            ascii_only.append('_')
    
    safe_component = ''.join(ascii_only)
    
    # 只保留字母、数字和下划线
    safe_component = re.sub(r'[^\w]', '_', safe_component)
    # 移除连续的多个下划线
    safe_component = re.sub(r'_+', '_', safe_component)
    # 移除开头和结尾的下划线
    safe_component = safe_component.strip('_')
    
    # 如果为空，返回一个默认值
    if not safe_component:
        safe_component = f"component_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return safe_component

def create_safe_storage_path(username, assignment_id, original_filename):
    """
    创建安全的存储路径（只包含ASCII字符）
    
    Args:
        username: 用户名
        assignment_id: 作业ID
        original_filename: 原始文件名
    
    Returns:
        安全的存储路径字符串
    """
    # 清理各个组件
    safe_username = sanitize_path_component(username)
    safe_assignment_id = sanitize_path_component(assignment_id)
    safe_filename = sanitize_filename(original_filename)
    
    # 添加时间戳确保唯一性
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # 构建路径：username_assignmentid_timestamp_filename
    # 使用下划线连接所有部分，确保没有中文字符
    storage_path = f"{safe_username}_{safe_assignment_id}_{timestamp}_{safe_filename}"
    
    # 最后检查一次，确保没有中文字符
    # 如果还有任何非ASCII字符，全部替换为下划线
    final_path = []
    for char in storage_path:
        if ord(char) < 128:
            final_path.append(char)
        else:
            final_path.append('_')
    
    storage_path = ''.join(final_path)
    
    # 再次清理可能产生的多个连续下划线
    storage_path = re.sub(r'_+', '_', storage_path)
    
    return storage_path

def validate_ascii_only(text):
    """
    验证字符串是否只包含ASCII字符
    
    Args:
        text: 要验证的字符串
    
    Returns:
        (bool, str) - 是否只包含ASCII，以及清理后的字符串
    """
    cleaned = []
    has_non_ascii = False
    
    for char in text:
        if ord(char) < 128:
            cleaned.append(char)
        else:
            cleaned.append('_')
            has_non_ascii = True
    
    cleaned_text = ''.join(cleaned)
    return not has_non_ascii, cleaned_text

# ==================== Supabase 初始化 ====================
@st.cache_resource
def init_supabase():
    """初始化 Supabase 客户端"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

# ==================== 存储桶名称定义 ====================
BUCKET_ASSIGNMENTS = "assignment_files"
BUCKET_EXPERIMENT_CARDS = "experiment_cards"
BUCKET_TEACHER_MATERIALS = "teacher_materials"

# ==================== 检查并创建存储桶 ====================
def ensure_storage_buckets():
    """确保存储桶可用 - 简化版"""
    required_buckets = [BUCKET_ASSIGNMENTS, BUCKET_EXPERIMENT_CARDS, BUCKET_TEACHER_MATERIALS]
    
    for bucket_name in required_buckets:
        try:
            # 尝试列出存储桶中的文件（测试访问权限）
            supabase.storage.from_(bucket_name).list()
            print(f"存储桶 {bucket_name} 可访问")
        except Exception as e:
            # 如果访问失败，尝试创建
            try:
                supabase.storage.create_bucket(
                    bucket_name,
                    options={
                        "public": True,
                        "allowed_mime_types": ["*/*"],
                        "file_size_limit": 104857600
                    }
                )
                print(f"成功创建存储桶: {bucket_name}")
            except Exception as create_error:
                # 静默失败，不显示警告
                print(f"存储桶 {bucket_name} 不可用: {create_error}")

# 执行存储桶检查
ensure_storage_buckets()

# ==================== Supabase 表初始化 ====================
def init_supabase_tables():
    """初始化 Supabase 表结构（如果不存在）"""
    try:
        # 检查 assignments 表是否存在
        try:
            supabase.table("assignments").select("*").limit(1).execute()
        except Exception as e:
            # 表不存在，需要手动在 Supabase SQL 编辑器创建
            st.warning("请在 Supabase SQL 编辑器中执行以下 SQL 创建表：")
            st.code("""
-- 创建 assignments 表
CREATE TABLE assignments (
    id BIGSERIAL PRIMARY KEY,
    assignment_type TEXT NOT NULL,
    assignment_number INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    deadline TEXT,
    max_score INTEGER DEFAULT 100,
    created_at TEXT NOT NULL,
    teacher_username TEXT,
    experiment_card TEXT,
    experiment_materials TEXT
);

-- 创建 experiment_submissions 表
CREATE TABLE experiment_submissions (
    id BIGSERIAL PRIMARY KEY,
    student_username TEXT NOT NULL,
    experiment_number INTEGER,
    experiment_title TEXT,
    submission_content TEXT,
    submission_time TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    teacher_feedback TEXT,
    score INTEGER,
    resubmission_count INTEGER DEFAULT 0,
    allow_view_score BOOLEAN DEFAULT FALSE,
    assignment_type TEXT DEFAULT 'experiment',
    file_paths TEXT[] DEFAULT '{}'  -- 存储文件路径数组
);
            """)
        
        # 检查 submissions 表是否存在
        try:
            supabase.table("experiment_submissions").select("*").limit(1).execute()
        except:
            pass
            
    except Exception as e:
        st.error(f"Supabase 初始化检查失败: {e}")

# 执行初始化检查
init_supabase_tables()

# ==================== Supabase Storage 文件操作函数 ====================

def upload_file_to_storage(file, bucket_name, storage_path):
    """上传文件到 Supabase Storage"""
    try:
        # 读取文件内容
        file_bytes = file.getbuffer()
        
        # 验证存储路径是否只包含ASCII字符
        is_ascii, cleaned_path = validate_ascii_only(storage_path)
        if not is_ascii:
            print(f"警告：存储路径包含非ASCII字符，已清理: {storage_path} -> {cleaned_path}")
            storage_path = cleaned_path
        
        print(f"最终存储路径: {storage_path}")
        
        # 上传到 Storage
        response = supabase.storage.from_(bucket_name).upload(
            path=storage_path,
            file=file_bytes.tobytes(),
            file_options={"content-type": file.type if file.type else "application/octet-stream"}
        )
        
        # 获取公共URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
        return True, public_url, storage_path
    except Exception as e:
        error_msg = str(e)
        print(f"上传失败详细错误: {error_msg}")
        return False, error_msg, None

def download_file_from_storage(bucket_name, storage_path):
    """从 Supabase Storage 下载文件"""
    try:
        file_data = supabase.storage.from_(bucket_name).download(storage_path)
        return True, file_data
    except Exception as e:
        return False, str(e)

def delete_file_from_storage(bucket_name, storage_path):
    """从 Supabase Storage 删除文件"""
    try:
        supabase.storage.from_(bucket_name).remove([storage_path])
        return True, "删除成功"
    except Exception as e:
        return False, str(e)

def list_files_in_storage(bucket_name, folder_path):
    """列出存储桶中的文件"""
    try:
        files = supabase.storage.from_(bucket_name).list(folder_path)
        return True, files
    except Exception as e:
        return False, str(e)

def save_uploaded_files_to_storage(uploaded_files, student_username, assignment_id):
    """保存上传的文件到 Supabase Storage"""
    saved_files = []
    file_paths = []
    public_urls = []
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # 使用安全路径创建函数生成存储路径
            storage_path = create_safe_storage_path(
                student_username, 
                assignment_id, 
                uploaded_file.name
            )
            
            print(f"上传文件: {uploaded_file.name}")
            print(f"原始文件名中的字符: {[ord(c) for c in uploaded_file.name]}")
            print(f"生成的存储路径: {storage_path}")
            
            # 上传文件
            success, result, path = upload_file_to_storage(
                uploaded_file, 
                BUCKET_ASSIGNMENTS, 
                storage_path
            )
            
            if success:
                saved_files.append(uploaded_file.name)
                file_paths.append(storage_path)
                public_urls.append(result)
                print(f"文件已上传: {storage_path}")
            else:
                st.error(f"文件 {uploaded_file.name} 上传失败: {result}")
                print(f"上传失败详情: {result}")
    
    return saved_files, file_paths, public_urls

def save_teacher_files_to_storage(uploaded_files, teacher_username, assignment_id, file_type="experiment_cards"):
    """保存教师上传的文件到 Supabase Storage"""
    saved_files = []
    file_paths = []
    public_urls = []
    
    bucket_name = BUCKET_EXPERIMENT_CARDS if file_type == "experiment_cards" else BUCKET_TEACHER_MATERIALS
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # 使用安全路径创建函数生成存储路径
            storage_path = create_safe_storage_path(
                teacher_username, 
                assignment_id, 
                uploaded_file.name
            )
            
            print(f"上传文件: {uploaded_file.name}")
            print(f"生成的存储路径: {storage_path}")
            
            success, result, path = upload_file_to_storage(
                uploaded_file, 
                bucket_name, 
                storage_path
            )
            
            if success:
                saved_files.append(uploaded_file.name)
                file_paths.append(storage_path)
                public_urls.append(result)
                print(f"文件上传成功: {storage_path}")
            else:
                st.error(f"文件 {uploaded_file.name} 上传失败: {result}")
                print(f"上传失败详情: {result}")
    
    return saved_files, file_paths, public_urls

def download_assignment_files_as_zip(student_username, assignment_id, file_paths):
    """从 Storage 下载文件并打包成 ZIP"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
            zip_path = tmp_zip.name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.filename_encoding = 'utf-8'
            
            for i, storage_path in enumerate(file_paths):
                # 从 Storage 下载文件
                success, file_data = download_file_from_storage(BUCKET_ASSIGNMENTS, storage_path)
                
                if success:
                    # 获取原始文件名（从存储路径中提取）
                    original_filename = storage_path.split('_')[-1] if '_' in storage_path else f"file_{i+1}"
                    
                    # 写入 zip
                    zipf.writestr(original_filename, file_data)
        
        if os.path.getsize(zip_path) == 0:
            st.error("创建的压缩包为空")
            os.remove(zip_path)
            return None
            
        return zip_path
    except Exception as e:
        st.error(f"创建压缩包失败: {str(e)}")
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)
        return None

def download_teacher_files_as_zip(teacher_username, assignment_id, file_paths, bucket_name="experiment_cards"):
    """下载教师文件并打包成 ZIP"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
            zip_path = tmp_zip.name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.filename_encoding = 'utf-8'
            
            for i, storage_path in enumerate(file_paths):
                success, file_data = download_file_from_storage(bucket_name, storage_path)
                
                if success:
                    original_filename = storage_path.split('_')[-1] if '_' in storage_path else f"file_{i+1}"
                    zipf.writestr(original_filename, file_data)
        
        return zip_path
    except Exception as e:
        st.error(f"创建压缩包失败: {str(e)}")
        return None

def get_file_preview_from_storage(storage_path, bucket_name=BUCKET_ASSIGNMENTS):
    """从 Storage 获取文件预览"""
    try:
        success, file_data = download_file_from_storage(bucket_name, storage_path)
        
        if not success:
            return None, f"文件下载失败: {file_data}"
        
        # 确定文件类型
        file_ext = os.path.splitext(storage_path)[1].lower()
        
        # 图像文件
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            try:
                image = Image.open(io.BytesIO(file_data))
                return image, "image"
            except Exception as e:
                return f"图片预览失败: {str(e)}", "info"
        
        # 文本文件
        elif file_ext in ['.txt', '.py', '.java', '.cpp', '.c', '.h', '.html', '.css', '.js', '.md', '.json', '.xml']:
            try:
                # 尝试多种编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
                for encoding in encodings:
                    try:
                        content = file_data.decode(encoding)
                        if len(content) > 10000:
                            content = content[:10000] + "\n\n... (文件较大，仅显示前10000字符)"
                        return content, "text"
                    except UnicodeDecodeError:
                        continue
                return f"无法解码文本文件，文件大小: {len(file_data)} 字节", "info"
            except Exception as e:
                return f"文本预览失败: {str(e)}", "info"
        
        # PDF文件
        elif file_ext == '.pdf':
            return f"PDF文档\n大小: {len(file_data)} 字节\n请下载查看完整内容", "info"
        
        # 其他文件
        else:
            return f"文件类型: {file_ext}\n大小: {len(file_data)} 字节", "info"
            
    except Exception as e:
        return None, f"预览失败: {str(e)}"

# ==================== 工具函数 ====================
def get_beijing_time():
    utc_now = datetime.utcnow()
    beijing_time = utc_now + timedelta(hours=8)
    return beijing_time

def send_file_to_email(uploaded_files, username, assignment_name):
    """
    发送用户上传的文件到你的邮箱
    """
    # 从Secrets读取邮箱配置
    MY_EMAIL = st.secrets["EMAIL"]["address"]
    MY_PWD = st.secrets["EMAIL"]["password"]
    SMTP_SERVER = "smtp.qq.com"
    SMTP_PORT = 465

    try:
        # 构建邮件内容
        msg = MIMEMultipart()
        msg['From'] = formataddr(("作业提交系统", MY_EMAIL))
        msg['To'] = MY_EMAIL
        msg['Subject'] = f"[{username}] 提交{assignment_name}作业"

        # 添加上传的文件作为邮件附件
        for file in uploaded_files:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.getbuffer())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{file.name}"')
            msg.attach(part)

        # 发送邮件
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(MY_EMAIL, MY_PWD)
        server.sendmail(MY_EMAIL, [MY_EMAIL], msg.as_string())
        server.quit()
        return True, "邮件发送成功"
    except Exception as e:
        return False, f"邮件发送失败: {str(e)}"

def init_default_assignments():
    """初始化默认作业到 Supabase"""
    try:
        # 检查是否已有作业
        response = supabase.table("assignments").select("*", count="exact").execute()
        
        if response.count == 0:
            current_time = get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')
            
            # 实验作业
            experiments = [
                (1, "图像灰度化处理", "将彩色图像转换为灰度图像，比较不同转换方法的优劣"),
                (2, "图像边缘检测", "使用Sobel、Canny等算子进行边缘检测"),
                (3, "图像滤波处理", "实现均值滤波、高斯滤波等去噪方法"),
                (4, "图像形态学操作", "实现腐蚀、膨胀、开运算、闭运算"),
                (5, "图像分割技术", "使用阈值分割、区域生长等方法"),
                (6, "特征提取与匹配", "提取SIFT、ORB等特征并进行匹配"),
                (7, "图像增强技术", "实现直方图均衡化、对比度增强"),
                (8, "图像几何变换", "实现旋转、缩放、仿射变换等")
            ]
            
            for i, (num, title, desc) in enumerate(experiments):
                deadline = (get_beijing_time() + timedelta(days=14+i*7)).strftime('%Y-%m-%d')
                supabase.table("assignments").insert({
                    "assignment_type": "experiment",
                    "assignment_number": num,
                    "title": title,
                    "description": desc,
                    "deadline": deadline,
                    "created_at": current_time
                }).execute()
            
            # 期中作业
            midterm_deadline = (get_beijing_time() + timedelta(days=60)).strftime('%Y-%m-%d')
            supabase.table("assignments").insert({
                "assignment_type": "midterm",
                "assignment_number": 1,
                "title": "图像处理综合应用",
                "description": "设计并实现一个完整的图像处理应用系统",
                "deadline": midterm_deadline,
                "created_at": current_time
            }).execute()
            
            # 期末作业
            final_deadline = (get_beijing_time() + timedelta(days=120)).strftime('%Y-%m-%d')
            supabase.table("assignments").insert({
                "assignment_type": "final",
                "assignment_number": 1,
                "title": "图像处理项目开发",
                "description": "开发一个完整的图像处理项目，包含GUI界面和多种处理功能",
                "deadline": final_deadline,
                "created_at": current_time
            }).execute()
    except Exception as e:
        st.error(f"初始化默认作业失败: {e}")

# 初始化默认作业
init_default_assignments()

def get_assignment_by_id(assignment_id):
    """通过ID获取作业信息"""
    try:
        response = supabase.table("assignments").select("*").eq("id", assignment_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"获取作业信息失败：{str(e)}")
        return None

def get_assignments_by_type(assignment_type):
    """按类型获取作业列表"""
    try:
        response = supabase.table("assignments").select("*").eq("assignment_type", assignment_type).order("assignment_number").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"获取作业列表失败：{str(e)}")
        return []

def get_all_assignments():
    """获取所有作业"""
    try:
        response = supabase.table("assignments").select("*").order("assignment_type").order("assignment_number").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"获取所有作业失败：{str(e)}")
        return []

def get_assignment_by_type(assignment_type):
    """根据类型获取作业"""
    return get_assignments_by_type(assignment_type)

def get_assignment_id_by_type_and_number(assignment_type, assignment_number):
    """根据作业类型和编号获取作业ID"""
    try:
        response = supabase.table("assignments").select("id").eq("assignment_type", assignment_type).eq("assignment_number", assignment_number).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
        return None
    except Exception as e:
        st.error(f"获取作业ID失败：{str(e)}")
        return None

def get_student_submissions(student_username, assignment_type=None):
    """获取学生的提交记录"""
    try:
        query = supabase.table("experiment_submissions").select("*").eq("student_username", student_username)
        
        if assignment_type:
            query = query.eq("assignment_type", assignment_type)
        
        response = query.order("submission_time", desc=True).execute()
        
        submissions = response.data if response.data else []
        
        # 获取作业标题
        for sub in submissions:
            exp_num = sub.get("experiment_number")
            sub_type = sub.get("assignment_type")
            if exp_num and sub_type:
                assign_response = supabase.table("assignments").select("title, description, deadline").eq("assignment_type", sub_type).eq("assignment_number", exp_num).execute()
                if assign_response.data and len(assign_response.data) > 0:
                    assign = assign_response.data[0]
                    sub["title"] = assign.get("title", "")
                    sub["description"] = assign.get("description", "")
                    sub["deadline"] = assign.get("deadline", "")
        
        return submissions
    except Exception as e:
        st.error(f"获取提交记录失败：{str(e)}")
        return []

def submit_assignment(student_username, student_name, assignment_id, assignment_type, content, uploaded_files):
    """提交作业 - 使用 Storage 保存文件"""
    try:
        assignment = get_assignment_by_id(assignment_id)
        if not assignment:
            return False, "找不到对应的作业", None
        
        assignment_number = assignment.get("assignment_number")
        assignment_title = assignment.get("title")
        
        # 检查是否已有提交
        response = supabase.table("experiment_submissions").select("id, resubmission_count, file_paths").eq("student_username", student_username).eq("experiment_number", assignment_number).eq("assignment_type", assignment_type).execute()
        existing = response.data if response.data else []
        
        submission_time = get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存文件到 Storage
        saved_files, file_paths, public_urls = save_uploaded_files_to_storage(
            uploaded_files, student_username, assignment_id
        )
        
        file_names_str = ','.join(saved_files) if saved_files else ''
        
        if existing:
            submission_id = existing[0]["id"]
            resubmission_count = existing[0]["resubmission_count"] + 1
            
            # 获取原有的文件路径
            old_file_paths = existing[0].get("file_paths", [])
            
            # 合并新旧文件路径
            all_file_paths = old_file_paths + file_paths if old_file_paths else file_paths
            
            supabase.table("experiment_submissions").update({
                "submission_content": content + "\n\n提交文件: " + file_names_str,
                "submission_time": submission_time,
                "status": "pending",
                "resubmission_count": resubmission_count,
                "assignment_type": assignment_type,
                "file_paths": all_file_paths
            }).eq("id", submission_id).execute()
            
            message = f"作业重新提交成功！这是第{resubmission_count}次提交"
        else:
            insert_response = supabase.table("experiment_submissions").insert({
                "student_username": student_username,
                "experiment_number": assignment_number,
                "experiment_title": assignment_title,
                "submission_content": content + "\n\n提交文件: " + file_names_str,
                "submission_time": submission_time,
                "status": "pending",
                "resubmission_count": 0,
                "assignment_type": assignment_type,
                "allow_view_score": False,
                "file_paths": file_paths
            }).execute()
            
            submission_id = insert_response.data[0]["id"] if insert_response.data else None
            message = "作业提交成功！"
        
        return True, message, submission_id
    except Exception as e:
        return False, f"提交失败：{str(e)}", None

def get_all_submissions(assignment_type=None):
    """获取所有学生的提交（教师端）"""
    try:
        query = supabase.table("experiment_submissions").select("*")
        
        if assignment_type:
            query = query.eq("assignment_type", assignment_type)
        
        response = query.order("submission_time", desc=True).execute()
        
        submissions = response.data if response.data else []
        
        # 获取作业标题和类型信息
        for sub in submissions:
            exp_num = sub.get("experiment_number")
            sub_type = sub.get("assignment_type")
            if exp_num and sub_type:
                assign_response = supabase.table("assignments").select("title, assignment_type, assignment_number").eq("assignment_type", sub_type).eq("assignment_number", exp_num).execute()
                if assign_response.data and len(assign_response.data) > 0:
                    assign = assign_response.data[0]
                    sub["title"] = assign.get("title", "")
                    sub["assignment_type"] = assign.get("assignment_type", "")
                    sub["assignment_number"] = assign.get("assignment_number", "")
        
        return submissions
    except Exception as e:
        st.error(f"获取所有提交失败：{str(e)}")
        return []

def update_submission_score(submission_id, score, feedback, can_view_score, status):
    """更新作业评分"""
    try:
        supabase.table("experiment_submissions").update({
            "score": score,
            "teacher_feedback": feedback,
            "allow_view_score": can_view_score,
            "status": status
        }).eq("id", submission_id).execute()
        
        return True, "评分更新成功！"
    except Exception as e:
        return False, f"更新失败：{str(e)}"

def get_submission_stats():
    """获取提交统计信息"""
    try:
        response = supabase.table("experiment_submissions").select("*").execute()
        submissions = response.data if response.data else []
        
        total = len(submissions)
        
        status_stats = {}
        for sub in submissions:
            status = sub.get("status", "unknown")
            status_stats[status] = status_stats.get(status, 0) + 1
        
        graded_scores = [sub.get("score", 0) for sub in submissions if sub.get("status") == "graded" and sub.get("score") is not None]
        avg_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
        
        return {
            'total': total,
            'status': status_stats,
            'avg_score': avg_score
        }
    except Exception as e:
        st.error(f"获取统计信息失败：{str(e)}")
        return {'total': 0, 'status': {}, 'avg_score': 0}

def get_experiment_title(experiment_number):
    """获取实验标题"""
    try:
        response = supabase.table("assignments").select("title").eq("assignment_number", experiment_number).eq("assignment_type", "experiment").execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["title"]
    except:
        pass
    
    titles = {
        1: "实验一",
        2: "实验二",
        3: "实验三",
        4: "实验四",
        5: "实验五",
        6: "实验六",
        7: "实验七",
        8: "实验八"
    }
    return titles.get(experiment_number, f"实验{experiment_number}")

def get_experiment_description(experiment_number):
    """获取实验描述"""
    try:
        response = supabase.table("assignments").select("description").eq("assignment_number", experiment_number).eq("assignment_type", "experiment").execute()
        if response.data and len(response.data) > 0 and response.data[0].get("description"):
            return response.data[0]["description"]
    except:
        pass
    
    descriptions = {
        1: "**实验要求：\n**提交内容：** 实验报告、源代码、一定包含图像。",
        2: "**实验要求：\n**提交内容：** 实验报告、源代码、一定包含图像。",
        3: "**实验要求：\n**提交内容：** 实验报告、源代码、一定包含图像。",
        4: "**实验要求：\n**提交内容：** 实验报告、源代码、一定包含图像。",
        5: "**实验要求：\n**提交内容：** 实验报告、源代码、一定包含图像。",
        6: "**实验要求：\n**提交内容：** 实验报告、源代码、一定包含图像。",
        7: "**实验要求：\n**提交内容：** 实验报告、源代码、一定包含图像。",
        8: "**实验要求：\n**提交内容：** 实验报告、源代码、一定包含图像。"
    }
    return descriptions.get(experiment_number, "")

def save_experiment_card(assignment_id, teacher_username, card_content, uploaded_files):
    """保存实验卡 - 使用 Storage"""
    try:
        saved_files = []
        file_paths = []
        
        if uploaded_files:
            saved_files, file_paths, _ = save_teacher_files_to_storage(
                uploaded_files, teacher_username, assignment_id, "experiment_cards"
            )
        
        experiment_card_content = card_content
        if saved_files:
            experiment_card_content += "\n\n附件文件: " + ', '.join(saved_files)
            experiment_card_content += "\n\n文件路径: " + ', '.join(file_paths)
        
        supabase.table("assignments").update({
            "teacher_username": teacher_username,
            "experiment_card": experiment_card_content
        }).eq("id", assignment_id).execute()
        
        return True, "实验卡上传成功！"
    except Exception as e:
        return False, f"上传失败：{str(e)}"

def save_experiment_materials(assignment_id, teacher_username, materials_content, uploaded_files):
    """保存实验文档/资料 - 使用 Storage"""
    try:
        saved_files = []
        file_paths = []
        
        if uploaded_files:
            saved_files, file_paths, _ = save_teacher_files_to_storage(
                uploaded_files, teacher_username, assignment_id, "teacher_materials"
            )
        
        experiment_materials_content = materials_content
        if saved_files:
            experiment_materials_content += "\n\n附件文件: " + ', '.join(saved_files)
            experiment_materials_content += "\n\n文件路径: " + ', '.join(file_paths)
        
        supabase.table("assignments").update({
            "teacher_username": teacher_username,
            "experiment_materials": experiment_materials_content
        }).eq("id", assignment_id).execute()
        
        return True, "实验文档上传成功！"
    except Exception as e:
        return False, f"上传失败：{str(e)}"

def get_experiment_materials(assignment_id):
    """获取实验文档/资料"""
    try:
        response = supabase.table("assignments").select("experiment_materials").eq("id", assignment_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0].get("experiment_materials", "")
        return ""
    except Exception as e:
        st.error(f"获取实验文档失败：{str(e)}")
        return ""

def download_experiment_card(assignment_id):
    """下载实验卡 - 从 Storage 下载"""
    try:
        response = supabase.table("assignments").select("experiment_card, teacher_username, assignment_number").eq("id", assignment_id).execute()
        
        if not response.data or len(response.data) == 0:
            return None, "找不到实验卡内容"
            
        card_data = response.data[0]
        card_content = card_data.get("experiment_card", "")
        teacher_username = card_data.get("teacher_username", "")
        assignment_number = card_data.get("assignment_number", "")
        
        temp_dir = tempfile.mkdtemp()
        
        zip_filename = f"实验卡_实验{assignment_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.filename_encoding = 'utf-8'
            
            # 添加实验卡内容
            card_filename = f"实验{assignment_number}_实验卡内容.txt"
            card_path = os.path.join(temp_dir, card_filename)
            
            with open(card_path, "w", encoding="utf-8") as f:
                f.write(card_content)
            
            zipf.write(card_path, card_filename)
            
            # 解析文件路径并下载附件
            if "文件路径:" in card_content:
                file_paths_part = card_content.split("文件路径:")[-1].strip().split(',')
                for storage_path in file_paths_part:
                    storage_path = storage_path.strip()
                    if storage_path:
                        success, file_data = download_file_from_storage(BUCKET_EXPERIMENT_CARDS, storage_path)
                        if success:
                            original_filename = storage_path.split('_')[-1] if '_' in storage_path else f"file_{i+1}"
                            zipf.writestr(os.path.join("附件", original_filename), file_data)
        
        return zip_path, None
    except Exception as e:
        return None, f"下载失败：{str(e)}"

def download_student_files(student_username, assignment_id, file_paths):
    """下载学生提交的文件"""
    if not student_username or not assignment_id or not file_paths:
        st.error("缺少必要参数")
        return None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
            zip_path = tmp_zip.name
            
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.filename_encoding = 'utf-8'
            
            for i, storage_path in enumerate(file_paths):
                success, file_data = download_file_from_storage(BUCKET_ASSIGNMENTS, storage_path)
                
                if success:
                    # 从存储路径提取原始文件名
                    original_filename = storage_path.split('_')[-1] if '_' in storage_path else f"file_{i+1}"
                    zipf.writestr(original_filename, file_data)
        
        if os.path.getsize(zip_path) == 0:
            st.error("创建的压缩包为空")
            os.remove(zip_path)
            return None
            
        return zip_path
    except Exception as e:
        st.error(f"创建压缩包失败: {str(e)}")
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)
        return None

def download_single_submission(submission_id, student_username, assignment_type, assignment_number):
    """下载单次提交的文件"""
    try:
        # 获取提交记录
        response = supabase.table("experiment_submissions").select("file_paths").eq("id", submission_id).execute()
        if not response.data or len(response.data) == 0:
            return None, None, "找不到提交记录"
        
        file_paths = response.data[0].get("file_paths", [])
        
        assignment_id = get_assignment_id_by_type_and_number(assignment_type, assignment_number)
        if not assignment_id:
            return None, None, "找不到对应的作业"
        
        zip_path = download_student_files(student_username, assignment_id, file_paths)
        if not zip_path:
            return None, None, "没有找到提交的文件"
        
        filename = f"{student_username}_{assignment_type}_{assignment_number}_submission_{submission_id}.zip"
        return zip_path, filename, None
        
    except Exception as e:
        return None, None, f"下载失败: {str(e)}"

def get_all_students():
    """获取所有学生的用户名"""
    try:
        response = supabase.table("experiment_submissions").select("student_username").execute()
        if response.data:
            return list(set([row["student_username"] for row in response.data if row.get("student_username")]))
        return []
    except Exception as e:
        st.error(f"获取学生列表失败：{str(e)}")
        return []

def export_experiment_scores_to_excel(student_filter=None):
    """导出实验成绩到Excel文件"""
    try:
        exp_submissions = supabase.table("experiment_submissions").select("*").eq("assignment_type", "experiment").execute()
        submissions = exp_submissions.data if exp_submissions.data else []
        
        if student_filter:
            submissions = [s for s in submissions if s.get("student_username") == student_filter]
        
        data = []
        for sub in submissions:
            assign_response = supabase.table("assignments").select("title, assignment_number").eq("assignment_type", "experiment").eq("assignment_number", sub.get("experiment_number")).execute()
            if assign_response.data and len(assign_response.data) > 0:
                assign = assign_response.data[0]
                data.append({
                    "student_username": sub.get("student_username"),
                    "assignment_number": assign.get("assignment_number"),
                    "title": assign.get("title"),
                    "score": sub.get("score"),
                    "status": sub.get("status"),
                    "submission_time": sub.get("submission_time"),
                    "teacher_feedback": sub.get("teacher_feedback")
                })
        
        if not data:
            return None, "没有找到实验成绩数据"
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='实验成绩详情', index=False)
            
            if not student_filter:
                summary_df = df.groupby('student_username').agg({
                    'score': ['count', 'mean', 'max', 'min'],
                    'status': lambda x: (x == 'graded').sum()
                }).round(2)
                
                summary_df.columns = ['提交次数', '平均分', '最高分', '最低分', '已批改数量']
                summary_df = summary_df.reset_index()
                summary_df.to_excel(writer, sheet_name='学生汇总', index=False)
                
                experiment_stats = df.groupby(['assignment_number', 'title']).agg({
                    'score': ['count', 'mean', 'max', 'min', 'std']
                }).round(2)
                
                experiment_stats.columns = ['提交人数', '平均分', '最高分', '最低分', '标准差']
                experiment_stats = experiment_stats.reset_index()
                experiment_stats.to_excel(writer, sheet_name='实验统计', index=False)
        
        output.seek(0)
        return output, None
    except Exception as e:
        return None, f"导出失败：{str(e)}"

def export_midterm_scores_to_excel(student_filter=None):
    """导出期中成绩到Excel文件"""
    try:
        mid_submissions = supabase.table("experiment_submissions").select("*").eq("assignment_type", "midterm").execute()
        submissions = mid_submissions.data if mid_submissions.data else []
        
        if student_filter:
            submissions = [s for s in submissions if s.get("student_username") == student_filter]
        
        data = []
        for sub in submissions:
            assign_response = supabase.table("assignments").select("title").eq("assignment_type", "midterm").eq("assignment_number", sub.get("experiment_number")).execute()
            if assign_response.data and len(assign_response.data) > 0:
                assign = assign_response.data[0]
                data.append({
                    "student_username": sub.get("student_username"),
                    "title": assign.get("title"),
                    "score": sub.get("score"),
                    "status": sub.get("status"),
                    "submission_time": sub.get("submission_time"),
                    "teacher_feedback": sub.get("teacher_feedback"),
                    "resubmission_count": sub.get("resubmission_count", 0)
                })
        
        if not data:
            return None, "没有找到期中成绩数据"
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='期中成绩详情', index=False)
            
            if not student_filter:
                summary_df = df.groupby('student_username').agg({
                    'score': 'last',
                    'submission_time': 'last',
                    'resubmission_count': 'max'
                }).round(2)
                
                summary_df = summary_df.reset_index()
                summary_df = summary_df.rename(columns={
                    'score': '最终得分',
                    'submission_time': '最后提交时间',
                    'resubmission_count': '提交次数'
                })
                summary_df.to_excel(writer, sheet_name='学生汇总', index=False)
                
                stats_data = {
                    '统计项': ['总提交人数', '平均分', '最高分', '最低分', '标准差'],
                    '数值': [
                        len(summary_df),
                        summary_df['最终得分'].mean() if not summary_df.empty else 0,
                        summary_df['最终得分'].max() if not summary_df.empty else 0,
                        summary_df['最终得分'].min() if not summary_df.empty else 0,
                        summary_df['最终得分'].std() if not summary_df.empty else 0
                    ]
                }
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='统计信息', index=False)
        
        output.seek(0)
        return output, None
    except Exception as e:
        return None, f"导出失败：{str(e)}"

def export_final_scores_to_excel(student_filter=None):
    """导出期末成绩到Excel文件"""
    try:
        final_submissions = supabase.table("experiment_submissions").select("*").eq("assignment_type", "final").execute()
        submissions = final_submissions.data if final_submissions.data else []
        
        if student_filter:
            submissions = [s for s in submissions if s.get("student_username") == student_filter]
        
        data = []
        for sub in submissions:
            assign_response = supabase.table("assignments").select("title").eq("assignment_type", "final").eq("assignment_number", sub.get("experiment_number")).execute()
            if assign_response.data and len(assign_response.data) > 0:
                assign = assign_response.data[0]
                data.append({
                    "student_username": sub.get("student_username"),
                    "title": assign.get("title"),
                    "score": sub.get("score"),
                    "status": sub.get("status"),
                    "submission_time": sub.get("submission_time"),
                    "teacher_feedback": sub.get("teacher_feedback"),
                    "resubmission_count": sub.get("resubmission_count", 0)
                })
        
        if not data:
            return None, "没有找到期末成绩数据"
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='期末成绩详情', index=False)
            
            if not student_filter:
                summary_df = df.groupby('student_username').agg({
                    'score': 'last',
                    'submission_time': 'last',
                    'resubmission_count': 'max'
                }).round(2)
                
                summary_df = summary_df.reset_index()
                summary_df = summary_df.rename(columns={
                    'score': '最终得分',
                    'submission_time': '最后提交时间',
                    'resubmission_count': '提交次数'
                })
                summary_df.to_excel(writer, sheet_name='学生汇总', index=False)
                
                stats_data = {
                    '统计项': ['总提交人数', '平均分', '最高分', '最低分', '标准差', '优秀(≥90)', '良好(≥80)', '及格(≥60)', '不及格(<60)'],
                    '数值': [
                        len(summary_df),
                        summary_df['最终得分'].mean() if not summary_df.empty else 0,
                        summary_df['最终得分'].max() if not summary_df.empty else 0,
                        summary_df['最终得分'].min() if not summary_df.empty else 0,
                        summary_df['最终得分'].std() if not summary_df.empty else 0,
                        len(summary_df[summary_df['最终得分'] >= 90]) if not summary_df.empty else 0,
                        len(summary_df[(summary_df['最终得分'] >= 80) & (summary_df['最终得分'] < 90)]) if not summary_df.empty else 0,
                        len(summary_df[(summary_df['最终得分'] >= 60) & (summary_df['最终得分'] < 80)]) if not summary_df.empty else 0,
                        len(summary_df[summary_df['最终得分'] < 60]) if not summary_df.empty else 0
                    ]
                }
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='统计信息', index=False)
        
        output.seek(0)
        return output, None
    except Exception as e:
        return None, f"导出失败：{str(e)}"

def export_all_scores_to_excel(student_filter=None):
    """导出所有成绩（实验、期中、期末）到Excel文件"""
    try:
        if student_filter:
            students = [student_filter]
        else:
            students = get_all_students()
        
        all_data = []
        
        for student in students:
            exp_submissions = supabase.table("experiment_submissions").select("*").eq("student_username", student).eq("assignment_type", "experiment").order("experiment_number").execute()
            exp_scores_data = exp_submissions.data if exp_submissions.data else []
            
            mid_submissions = supabase.table("experiment_submissions").select("*").eq("student_username", student).eq("assignment_type", "midterm").order("submission_time", desc=True).execute()
            mid_scores_data = mid_submissions.data if mid_submissions.data else []
            
            final_submissions = supabase.table("experiment_submissions").select("*").eq("student_username", student).eq("assignment_type", "final").order("submission_time", desc=True).execute()
            final_scores_data = final_submissions.data if final_submissions.data else []
            
            exp_scores = []
            for sub in exp_scores_data:
                if sub.get("score") is not None:
                    exp_scores.append(sub.get("score"))
            
            exp_avg = sum(exp_scores) / len(exp_scores) if exp_scores else None
            mid_score = mid_scores_data[0].get("score") if mid_scores_data and mid_scores_data[0].get("score") is not None else None
            final_score = final_scores_data[0].get("score") if final_scores_data and final_scores_data[0].get("score") is not None else None
            
            student_data = {
                '学号/用户名': student,
                '实验平均分': round(exp_avg, 2) if exp_avg else '未评分',
                '期中成绩': round(mid_score, 2) if mid_score else '未评分',
                '期末成绩': round(final_score, 2) if final_score else '未评分',
                '总评成绩': '待计算'
            }
            all_data.append(student_data)
        
        if not all_data:
            return None, "没有找到成绩数据"
        
        df = pd.DataFrame(all_data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='综合成绩', index=False)
            
            if not student_filter:
                exp_detail_data = []
                exp_subs = supabase.table("experiment_submissions").select("*").eq("assignment_type", "experiment").execute()
                if exp_subs.data:
                    for sub in exp_subs.data:
                        assign_resp = supabase.table("assignments").select("title, assignment_number").eq("assignment_type", "experiment").eq("assignment_number", sub.get("experiment_number")).execute()
                        if assign_resp.data and len(assign_resp.data) > 0:
                            assign = assign_resp.data[0]
                            exp_detail_data.append({
                                "student_username": sub.get("student_username"),
                                "assignment_number": assign.get("assignment_number"),
                                "title": assign.get("title"),
                                "score": sub.get("score"),
                                "status": sub.get("status"),
                                "submission_time": sub.get("submission_time")
                            })
                
                if exp_detail_data:
                    exp_detail_df = pd.DataFrame(exp_detail_data)
                    exp_detail_df.to_excel(writer, sheet_name='实验详细成绩', index=False)
            
            if not student_filter:
                mid_final_data = []
                mf_subs = supabase.table("experiment_submissions").select("*").in_("assignment_type", ["midterm", "final"]).execute()
                if mf_subs.data:
                    for sub in mf_subs.data:
                        assign_resp = supabase.table("assignments").select("title").eq("assignment_type", sub.get("assignment_type")).eq("assignment_number", sub.get("experiment_number")).execute()
                        if assign_resp.data and len(assign_resp.data) > 0:
                            assign = assign_resp.data[0]
                            mid_final_data.append({
                                "student_username": sub.get("student_username"),
                                "assignment_type": sub.get("assignment_type"),
                                "title": assign.get("title"),
                                "score": sub.get("score"),
                                "status": sub.get("status"),
                                "submission_time": sub.get("submission_time")
                            })
                
                if mid_final_data:
                    mid_final_df = pd.DataFrame(mid_final_data)
                    mid_final_df.to_excel(writer, sheet_name='期中期末成绩', index=False)
        
        output.seek(0)
        return output, None
    except Exception as e:
        return None, f"导出失败：{str(e)}"

# ==================== 渲染侧边栏 ====================
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

        st.markdown("### 🧭 快速导航")
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("main.py")
        if st.button("🔬 图像处理实验室", use_container_width=True):
            st.switch_page("pages/1_🔬_图像处理实验室.py")
        if st.button("📝 智能与传统图片处理", use_container_width=True):
            st.switch_page("pages/智能与传统图片处理.py")
        if st.button("📤 实验作业提交", use_container_width=True):
            st.switch_page("pages/实验作业提交.py")
        if st.button("📚 学习资源中心", use_container_width=True):
            st.switch_page("pages/2_📚_学习资源中心.py")
        if st.button("📝 我的思政足迹", use_container_width=True):
            st.switch_page("pages/3_📝_我的思政足迹.py")
        if st.button("🏆 成果展示", use_container_width=True):
            st.switch_page("pages/4_🏆_成果展示.py")

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

        st.markdown("### 🎯 思政理论学习")
        
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

        st.markdown("---")
        st.markdown("**📊 系统信息**")
        st.text(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.text("状态: 🟢 正常运行")
        st.text("版本: v3.0.0 (Supabase Storage with enhanced sanitization)")

render_sidebar()

# ==================== 检查登录状态 ====================
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["🧪 实验作业", "📊 期中作业", "🎓 期末作业", "👨‍🏫 教师管理"])
    
    # 实验作业选项卡
    with tab1:
        st.markdown("### 📚 实验卡资源")
        assignments = get_assignments_by_type('experiment')
        if assignments:
            for assignment in assignments:
                assignment_id = assignment.get("id")
                assignment_number = assignment.get("assignment_number")
                title = assignment.get("title")
                description = assignment.get("description")
                experiment_card = assignment.get("experiment_card")
                
                with st.expander(f"实验{assignment_number}: {title}", expanded=False):
                    st.markdown(description)
                    
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
                                        zip_data = f.read()
                                        st.download_button(
                                            label="✅ 点击下载",
                                            data=zip_data,
                                            file_name=f"实验{assignment_number}_实验卡_{datetime.now().strftime('%Y%m%d')}.zip",
                                            mime="application/zip",
                                            key=f"student_card_download_{assignment_id}",
                                            use_container_width=True
                                        )
                                    try:
                                        os.remove(zip_path)
                                        shutil.rmtree(os.path.dirname(zip_path))
                                    except:
                                        pass
                                elif error:
                                    st.error(error)
                                else:
                                    st.warning("该实验暂无实验卡")
        else:
            st.info("暂无实验卡资源")

        st.markdown("### 📝 实验作业提交中心")
        
        if st.session_state.get('role') == 'student':
            st.markdown("#### 🎓 学生实验提交")
            
            experiment_number = st.selectbox(
                "选择实验",
                options=[1, 2, 3, 4, 5, 6, 7, 8],
                format_func=lambda x: f"实验{x}"
            )
            
            experiment_title = get_experiment_title(experiment_number)
            
            st.markdown(f"### {experiment_title}")
            
            st.markdown(get_experiment_description(experiment_number))
            
            assignments = get_assignment_by_type('experiment')
            assignment_id = None
            for assignment in assignments:
                if assignment.get("assignment_number") == experiment_number:
                    assignment_id = assignment.get("id")
                    break
            
            if assignment_id:
                experiment_materials = get_experiment_materials(assignment_id)
                if experiment_materials:
                    with st.expander("📖 查看实验文档/资料", expanded=False):
                        st.markdown(experiment_materials)
            
            submission_content = st.text_area(
                "实验报告内容",
                placeholder="请详细描述您的实验过程、结果分析、遇到的问题及解决方案...",
                height=300,
                key=f"exp_content_{experiment_number}"
            )
            
            uploaded_files = st.file_uploader(
                "上传实验文件（代码、结果图像、报告文档等）",
                type=['py', 'jpg', 'png', 'zip', 'rar', 'pdf', 'ppt', 'pptx', 'doc', 'docx', 'txt', 'cpp', 'c', 'java'],
                accept_multiple_files=True,
                help="支持多种文件格式：代码文件(.py, .java, .cpp, .c)、图像文件(.jpg, .png)、文档(.pdf, .doc, .docx)、演示文稿(.ppt, .pptx)、压缩包(.zip, .rar)等",
                key=f"exp_files_{experiment_number}"
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
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("📤 提交实验", use_container_width=True, type="primary", key=f"submit_exp_{experiment_number}"):
                    if submission_content.strip():
                        assignments = get_assignment_by_type('experiment')
                        assignment_id = None
                        for assignment in assignments:
                            if assignment.get("assignment_number") == experiment_number:
                                assignment_id = assignment.get("id")
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
                                
                                st.balloons()
                                st.snow()
                                
                                st.success("✅ 实验提交成功！")
                                
                                st.session_state.show_my_experiments = True
                                
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
            
            if st.session_state.get('show_my_experiments', False):
                st.markdown("---")
                st.markdown("### 📋 我的实验提交记录")
                
                submissions = get_student_submissions(st.session_state.username, 'experiment')
                
                if submissions:
                    total_submissions = len(submissions)
                    graded_submissions = len([s for s in submissions if s.get("status") == 'graded'])
                    pending_submissions = len([s for s in submissions if s.get("status") == 'pending'])
                    graded_scores = [s.get("score") for s in submissions if s.get("status") == 'graded' and s.get("score") is not None]
                    average_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
                    
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
                    
                    st.markdown("### 详细提交记录")
                    for sub_idx, sub in enumerate(submissions):
                        submission_id = sub.get("id")
                        student_username = sub.get("student_username")
                        experiment_number = sub.get("experiment_number")
                        experiment_title = sub.get("experiment_title") or f"实验{experiment_number}"
                        submission_content = sub.get("submission_content", "")
                        submission_time = sub.get("submission_time", "")
                        status = sub.get("status", "pending")
                        teacher_feedback = sub.get("teacher_feedback")
                        score = sub.get("score")
                        resubmission_count = sub.get("resubmission_count", 0)
                        allow_view_score = sub.get("allow_view_score", False)
                        file_paths = sub.get("file_paths", [])
                        
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
                                
                                if "提交文件:" in submission_content:
                                    file_section = submission_content.split("提交文件:")[-1].strip()
                                    if file_section:
                                        st.markdown("**📎 提交的文件:**")
                                        files = []
                                        for filename in file_section.split(','):
                                            if filename.strip():
                                                files.append(filename.strip())
                                                st.markdown(f"- {filename}")
                                        
                                        if files and file_paths:
                                            assignment_id = None
                                            assignments = get_assignment_by_type('experiment')
                                            for assignment in assignments:
                                                if assignment.get("assignment_number") == experiment_number:
                                                    assignment_id = assignment.get("id")
                                                    break
                                            
                                            if assignment_id:
                                                zip_path = download_student_files(student_username, assignment_id, file_paths)
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
                                                
                                                st.markdown("**🔍 文件预览:**")
                                                for file_idx, (filename, storage_path) in enumerate(zip(files, file_paths)):
                                                    file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                    with file_preview_col1:
                                                        with st.expander(f"📄 {filename}", expanded=False):
                                                            preview_result, preview_type = get_file_preview_from_storage(storage_path)
                                                            if preview_result:
                                                                if preview_type == "image":
                                                                    st.image(preview_result, caption=filename)
                                                                elif preview_type == "text":
                                                                    st.code(preview_result, language='text')
                                                                else:
                                                                    st.info(preview_result)
                                                    with file_preview_col2:
                                                        success, file_data = download_file_from_storage(BUCKET_ASSIGNMENTS, storage_path)
                                                        if success:
                                                            st.download_button(
                                                                label="📥 下载",
                                                                data=file_data,
                                                                file_name=filename,
                                                                mime="application/octet-stream",
                                                                key=f"single_file_{submission_id}_{experiment_number}_{file_idx}"
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
                                st.markdown(f"**🔢 提交ID:** `{submission_id}`")
                                st.markdown(f"**🔄 提交次数:** {resubmission_count}")

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
                                else:
                                    st.markdown("""
                                    <div style='background: #f59e0b; color: white; padding: 15px; border-radius: 10px; 
                                                font-weight: bold; text-align: center; margin: 10px 0; font-size: 1.2rem;'>
                                        ⏳ 得分待批改
                                    </div>
                                    """, unsafe_allow_html=True)

                                if status == 'pending':
                                    if st.button("撤回", key=f"withdraw_{submission_id}_{experiment_number}_{sub_idx}", use_container_width=True):
                                        try:
                                            # 获取文件路径并删除
                                            sub_data = supabase.table("experiment_submissions").select("file_paths").eq("id", submission_id).execute()
                                            if sub_data.data and sub_data.data[0].get("file_paths"):
                                                for fp in sub_data.data[0]["file_paths"]:
                                                    delete_file_from_storage(BUCKET_ASSIGNMENTS, fp)
                                            
                                            supabase.table("experiment_submissions").delete().eq("id", submission_id).eq("student_username", st.session_state.username).execute()
                                            
                                            st.success("提交已撤回！")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"撤回失败: {e}")
                else:
                    st.info("暂无实验提交记录，请先提交实验报告")
        
        elif st.session_state.get('role') == 'teacher':
            st.markdown("#### 👨‍🏫 教师实验管理")
            
            st.markdown("### 📋 实验卡管理")
            experiment_number = st.selectbox(
                "选择实验",
                options=[1, 2, 3, 4, 5, 6, 7, 8],
                format_func=lambda x: f"实验{x}",
                key="teacher_experiment_select"
            )
            
            assignments = get_assignment_by_type('experiment')
            assignment_id = None
            current_card = ""
            for assignment in assignments:
                if assignment.get("assignment_number") == experiment_number:
                    assignment_id = assignment.get("id")
                    current_card = assignment.get("experiment_card", "")
                    break
            
            if assignment_id:
                if current_card:
                    st.markdown("#### 当前实验卡内容：")
                    st.text_area("实验卡内容", current_card, height=200, disabled=True, key=f"current_card_{assignment_id}")
                
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
                                        try:
                                            os.remove(zip_path)
                                            shutil.rmtree(os.path.dirname(zip_path))
                                        except:
                                            pass
                                    elif error:
                                        st.error(error)
                                    else:
                                        st.warning("该实验暂无实验卡")
            
            st.markdown("### 📝 学生作业批改")
            experiment_submissions = get_all_submissions('experiment')
            
            if experiment_submissions:
                total_submissions = len(experiment_submissions)
                pending_submissions = len([s for s in experiment_submissions if s.get("status") == 'pending'])
                graded_submissions = len([s for s in experiment_submissions if s.get("status") == 'graded'])
                graded_scores = [s.get("score") for s in experiment_submissions if s.get("status") == 'graded' and s.get("score") is not None]
                average_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
                
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
                
                st.markdown("### 🔍 筛选提交")
                filter_status = st.selectbox(
                    "筛选状态",
                    ["全部", "待批改", "已评分", "已退回"],
                    key="teacher_filter_status"
                )
                
                filtered_submissions = experiment_submissions
                if filter_status == "待批改":
                    filtered_submissions = [s for s in experiment_submissions if s.get("status") == 'pending']
                elif filter_status == "已评分":
                    filtered_submissions = [s for s in experiment_submissions if s.get("status") == 'graded']
                elif filter_status == "已退回":
                    filtered_submissions = [s for s in experiment_submissions if s.get("status") == 'returned']
                
                st.markdown(f"**找到 {len(filtered_submissions)} 个提交**")
                
                for sub_idx, sub in enumerate(filtered_submissions):
                    submission_id = sub.get("id")
                    student_username = sub.get("student_username")
                    experiment_number = sub.get("experiment_number")
                    submission_content = sub.get("submission_content", "")
                    submission_time = sub.get("submission_time", "")
                    status = sub.get("status", "pending")
                    teacher_feedback = sub.get("teacher_feedback")
                    score = sub.get("score")
                    resubmission_count = sub.get("resubmission_count", 0)
                    allow_view_score = sub.get("allow_view_score", False)
                    file_paths = sub.get("file_paths", [])
                    
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
                            
                            if "提交文件:" in submission_content:
                                file_section = submission_content.split("提交文件:")[-1].strip()
                                if file_section:
                                    st.markdown("**📎 提交的文件:**")
                                    files = []
                                    for filename in file_section.split(','):
                                        if filename.strip():
                                            files.append(filename.strip())
                                            st.markdown(f"- {filename}")
                                    
                                    if files and file_paths:
                                        assignment_id = get_assignment_id_by_type_and_number('experiment', experiment_number)
                                        if assignment_id:
                                            zip_path = download_student_files(student_username, assignment_id, file_paths)
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
                                            
                                            st.markdown("**🔍 文件预览:**")
                                            for file_idx, (filename, storage_path) in enumerate(zip(files, file_paths)):
                                                file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                with file_preview_col1:
                                                    with st.expander(f"📄 {filename}", expanded=False):
                                                        preview_result, preview_type = get_file_preview_from_storage(storage_path)
                                                        if preview_result:
                                                            if preview_type == "image":
                                                                st.image(preview_result, caption=filename)
                                                            elif preview_type == "text":
                                                                st.code(preview_result, language='python' if filename.endswith('.py') else 'text')
                                                            else:
                                                                st.info(preview_result)
                                                with file_preview_col2:
                                                    success, file_data = download_file_from_storage(BUCKET_ASSIGNMENTS, storage_path)
                                                    if success:
                                                        st.download_button(
                                                            label="📥 单独下载",
                                                            data=file_data,
                                                            file_name=filename,
                                                            mime="application/octet-stream",
                                                            key=f"teacher_single_file_{submission_id}_{experiment_number}_{student_username}_{file_idx}"
                                                        )
                            
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
            st.warning("此功能仅对学生和教师开放")
    
    with tab2:
        st.markdown("### 📊 期中作业提交中心")
        
        midterm_assignments = get_assignment_by_type('midterm')
        
        if midterm_assignments:
            for assignment in midterm_assignments:
                assignment_id = assignment.get("id")
                title = assignment.get("title")
                description = assignment.get("description")
                experiment_card = assignment.get("experiment_card")
                
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
                
                if experiment_card and st.session_state.get('role') == 'student':
                    st.markdown("---")
                    with st.expander("📋 期中作业要求", expanded=False):
                        st.markdown(experiment_card)
                        
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
                                    try:
                                        os.remove(zip_path)
                                        shutil.rmtree(os.path.dirname(zip_path))
                                    except:
                                        pass
                                elif error:
                                    st.error(error)
                                else:
                                    st.warning("暂无作业要求")
                
                if st.session_state.get('role') == 'student':
                    st.markdown("---")
                    st.markdown("#### 🎓 期中作业提交")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        student_name = st.text_input("姓名", value=st.session_state.get('student_name', ''), key="midterm_name")
                    with col2:
                        student_id = st.text_input("学号", value=st.session_state.username, key="midterm_id")
                    
                    content = st.text_area(
                        "项目报告/说明文档",
                        placeholder="请详细描述您的项目设计思路、实现过程、功能说明、遇到的问题及解决方案...",
                        height=200,
                        key="midterm_content"
                    )
                    
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
                    
                    if st.session_state.get('show_my_midterm', False):
                        st.markdown("---")
                        st.markdown("### 📋 我的期中作业提交")
                        
                        submissions = get_student_submissions(st.session_state.username, 'midterm')
                        
                        if submissions:
                            for sub_idx, sub in enumerate(submissions):
                                submission_id = sub.get("id")
                                student_username = sub.get("student_username")
                                submission_content = sub.get("submission_content", "")
                                submission_time = sub.get("submission_time", "")
                                status = sub.get("status", "pending")
                                teacher_feedback = sub.get("teacher_feedback")
                                score = sub.get("score")
                                resubmission_count = sub.get("resubmission_count", 0)
                                allow_view_score = sub.get("allow_view_score", False)
                                file_paths = sub.get("file_paths", [])
                                
                                status_info = {
                                    'pending': ('⏳ 待批改', 'status-pending'),
                                    'graded': ('✅ 已评分', 'status-graded'),
                                    'returned': ('🔙 已退回', 'status-returned')
                                }.get(status, ('⚪ 未知', ''))
                                
                                with st.expander(f"{status_info[0]} - 期中作业 - {submission_time}", expanded=False):
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
                                                
                                                if files and file_paths:
                                                    assignment_id = None
                                                    assignments = get_assignment_by_type('midterm')
                                                    for assignment in assignments:
                                                        if assignment.get("assignment_number") == 1:
                                                            assignment_id = assignment.get("id")
                                                            break
                                                    
                                                    if assignment_id:
                                                        zip_path = download_student_files(student_username, assignment_id, file_paths)
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
                                                        
                                                        st.markdown("**🔍 文件预览:**")
                                                        for file_idx, (filename, storage_path) in enumerate(zip(files, file_paths)):
                                                            file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                            with file_preview_col1:
                                                                with st.expander(f"📄 {filename}", expanded=False):
                                                                    preview_result, preview_type = get_file_preview_from_storage(storage_path)
                                                                    if preview_result:
                                                                        if preview_type == "image":
                                                                            st.image(preview_result, caption=filename)
                                                                        elif preview_type == "text":
                                                                            st.code(preview_result, language='text')
                                                                        else:
                                                                            st.info(preview_result)
                                                            with file_preview_col2:
                                                                success, file_data = download_file_from_storage(BUCKET_ASSIGNMENTS, storage_path)
                                                                if success:
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
        
        final_assignments = get_assignment_by_type('final')
        
        if final_assignments:
            for assignment in final_assignments:
                assignment_id = assignment.get("id")
                title = assignment.get("title")
                description = assignment.get("description")
                experiment_card = assignment.get("experiment_card")
                
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
                
                if experiment_card and st.session_state.get('role') == 'student':
                    st.markdown("---")
                    with st.expander("📋 期末作业要求", expanded=False):
                        st.markdown(experiment_card)
                        
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
                                    try:
                                        os.remove(zip_path)
                                        shutil.rmtree(os.path.dirname(zip_path))
                                    except:
                                        pass
                                elif error:
                                    st.error(error)
                                else:
                                    st.warning("暂无作业要求")

                if st.session_state.get('role') == 'student':
                    st.markdown("---")
                    st.markdown("#### 🎓 期末作业提交")

                    col1, col2 = st.columns(2)
                    with col1:
                        student_name = st.text_input("姓名", value=st.session_state.get('student_name', ''),
                                                     key="final_name")
                    with col2:
                        student_id = st.text_input("学号", value=st.session_state.username, key="final_id")

                    content = st.text_area(
                        "项目报告/设计文档",
                        placeholder="请详细描述您的项目：\n1. 项目背景与意义\n2. 需求分析\n3. 系统设计\n4. 实现过程\n5. 测试结果\n6. 总结与展望...",
                        height=250,
                        key="final_content"
                    )

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

                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if st.button("🎓 提交期末作业", key="submit_final", use_container_width=True,
                                     type="primary"):
                            if content.strip():
                                with st.spinner("正在提交作业..."):
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

                    if st.session_state.get('show_my_final', False):
                        st.markdown("---")
                        st.markdown("### 📋 我的期末作业提交")
                        
                        submissions = get_student_submissions(st.session_state.username, 'final')
                        
                        if submissions:
                            for sub_idx, sub in enumerate(submissions):
                                submission_id = sub.get("id")
                                student_username = sub.get("student_username")
                                submission_content = sub.get("submission_content", "")
                                submission_time = sub.get("submission_time", "")
                                status = sub.get("status", "pending")
                                teacher_feedback = sub.get("teacher_feedback")
                                score = sub.get("score")
                                resubmission_count = sub.get("resubmission_count", 0)
                                allow_view_score = sub.get("allow_view_score", False)
                                file_paths = sub.get("file_paths", [])
                                
                                status_info = {
                                    'pending': ('⏳ 待评审', 'status-pending'),
                                    'graded': ('✅ 已评分', 'status-graded'),
                                    'returned': ('🔙 需修改', 'status-returned')
                                }.get(status, ('⚪ 未知', ''))
                                
                                with st.expander(f"{status_info[0]} - 期末作业 - {submission_time}", expanded=False):
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
                                                
                                                if files and file_paths:
                                                    assignment_id = None
                                                    assignments = get_assignment_by_type('final')
                                                    for assignment in assignments:
                                                        if assignment.get("assignment_number") == 1:
                                                            assignment_id = assignment.get("id")
                                                            break
                                                    
                                                    if assignment_id:
                                                        zip_path = download_student_files(student_username, assignment_id, file_paths)
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
                                                        
                                                        st.markdown("**🔍 文件预览:**")
                                                        for file_idx, (filename, storage_path) in enumerate(zip(files, file_paths)):
                                                            file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                            with file_preview_col1:
                                                                with st.expander(f"📄 {filename}", expanded=False):
                                                                    preview_result, preview_type = get_file_preview_from_storage(storage_path)
                                                                    if preview_result:
                                                                        if preview_type == "image":
                                                                            st.image(preview_result, caption=filename)
                                                                        elif preview_type == "text":
                                                                            st.code(preview_result, language='text')
                                                                        else:
                                                                            st.info(preview_result)
                                                            with file_preview_col2:
                                                                success, file_data = download_file_from_storage(BUCKET_ASSIGNMENTS, storage_path)
                                                                if success:
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
                        else:
                            st.info("暂无期末作业提交记录")
                elif st.session_state.get('role') == 'teacher':
                    st.markdown(f"**📊去教师管理进行批改和管理**")
    
    with tab4:
        st.markdown("### 👨‍🏫 教师管理中心")
        
        if st.session_state.get('role') != 'teacher':
            st.warning("❌ 此功能仅对教师开放")
        else:
            teacher_sub_tab1, teacher_sub_tab2, teacher_sub_tab3, teacher_sub_tab4 = st.tabs([
                "🧪 实验作业管理", "📊 期中作业管理", "🎓 期末作业管理", "📊 成绩导出"
            ])
            
            with teacher_sub_tab1:
                st.markdown("#### 实验作业管理")
                
                st.markdown("### 📋 实验卡管理")
                experiment_number = st.selectbox(
                    "选择实验",
                    options=[1, 2, 3, 4, 5, 6, 7, 8],
                    format_func=lambda x: f"实验{x}",
                    key="teacher_tab_experiment_select"
                )
                
                assignments = get_assignment_by_type('experiment')
                assignment_id = None
                current_card = ""
                for assignment in assignments:
                    if assignment.get("assignment_number") == experiment_number:
                        assignment_id = assignment.get("id")
                        current_card = assignment.get("experiment_card", "")
                        break
                
                if assignment_id:
                    if current_card:
                        st.markdown("#### 当前实验卡内容：")
                        st.text_area("实验卡内容", current_card, height=200, disabled=True, key=f"teacher_current_card_{assignment_id}")
                    
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
                                            try:
                                                os.remove(zip_path)
                                                shutil.rmtree(os.path.dirname(zip_path))
                                            except:
                                                pass
                                        elif error:
                                            st.error(error)
                                        else:
                                            st.warning("该实验暂无实验卡")
                
                st.markdown("### 📝 学生实验提交管理")
                experiment_submissions = get_all_submissions('experiment')
                
                if experiment_submissions:
                    total_submissions = len(experiment_submissions)
                    pending_submissions = len([s for s in experiment_submissions if s.get("status") == 'pending'])
                    graded_submissions = len([s for s in experiment_submissions if s.get("status") == 'graded'])
                    graded_scores = [s.get("score") for s in experiment_submissions if s.get("status") == 'graded' and s.get("score") is not None]
                    average_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown('<div class="stats-card"><div>📊 总提交</div><div class="stats-number">{}</div><div class="stats-label">所有实验</div></div>'.format(total_submissions), unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="stats-card"><div>⏳ 待批改</div><div class="stats-number">{}</div><div class="stats-label">等待评分</div></div>'.format(pending_submissions), unsafe_allow_html=True)
                    with col3:
                        st.markdown('<div class="stats-card"><div>✅ 已批改</div><div class="stats-number">{}</div><div class="stats-label">完成评分</div></div>'.format(graded_submissions), unsafe_allow_html=True)
                    with col4:
                        st.markdown('<div class="stats-card"><div>🎯 平均分</div><div class="stats-number">{}</div><div class="stats-label">班级平均</div></div>'.format(int(average_score)), unsafe_allow_html=True)
                    
                    st.markdown("### 🔍 筛选提交")
                    filter_status = st.selectbox(
                        "筛选状态",
                        ["全部", "待批改", "已评分", "已退回"],
                        key="teacher_tab_filter_status"
                    )
                    
                    filtered_submissions = experiment_submissions
                    if filter_status == "待批改":
                        filtered_submissions = [s for s in experiment_submissions if s.get("status") == 'pending']
                    elif filter_status == "已评分":
                        filtered_submissions = [s for s in experiment_submissions if s.get("status") == 'graded']
                    elif filter_status == "已退回":
                        filtered_submissions = [s for s in experiment_submissions if s.get("status") == 'returned']
                    
                    st.markdown(f"**找到 {len(filtered_submissions)} 个提交**")
                    
                    for sub_idx, sub in enumerate(filtered_submissions):
                        submission_id = sub.get("id")
                        student_username = sub.get("student_username")
                        experiment_number = sub.get("experiment_number")
                        submission_content = sub.get("submission_content", "")
                        submission_time = sub.get("submission_time", "")
                        status = sub.get("status", "pending")
                        teacher_feedback = sub.get("teacher_feedback")
                        score = sub.get("score")
                        resubmission_count = sub.get("resubmission_count", 0)
                        allow_view_score = sub.get("allow_view_score", False)
                        file_paths = sub.get("file_paths", [])
                        
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
                                
                                if "提交文件:" in submission_content:
                                    file_section = submission_content.split("提交文件:")[-1].strip()
                                    if file_section:
                                        st.markdown("**📎 提交的文件:**")
                                        files = []
                                        for filename in file_section.split(','):
                                            if filename.strip():
                                                files.append(filename.strip())
                                                st.markdown(f"- {filename}")
                                        
                                        if files and file_paths:
                                            assignment_id = get_assignment_id_by_type_and_number('experiment', experiment_number)
                                            if assignment_id:
                                                zip_path = download_student_files(student_username, assignment_id, file_paths)
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
                                                
                                                st.markdown("**🔍 文件预览:**")
                                                for file_idx, (filename, storage_path) in enumerate(zip(files, file_paths)):
                                                    file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                    with file_preview_col1:
                                                        with st.expander(f"📄 {filename}", expanded=False):
                                                            preview_result, preview_type = get_file_preview_from_storage(storage_path)
                                                            if preview_result:
                                                                if preview_type == "image":
                                                                    st.image(preview_result, caption=filename)
                                                                elif preview_type == "text":
                                                                    st.code(preview_result, language='python' if filename.endswith('.py') else 'text')
                                                                else:
                                                                    st.info(preview_result)
                                                    with file_preview_col2:
                                                        success, file_data = download_file_from_storage(BUCKET_ASSIGNMENTS, storage_path)
                                                        if success:
                                                            st.download_button(
                                                                label="📥 单独下载",
                                                                data=file_data,
                                                                file_name=filename,
                                                                mime="application/octet-stream",
                                                                key=f"teacher_tab_single_file_{submission_id}_{experiment_number}_{student_username}_{file_idx}"
                                                            )
                                
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
                
                midterm_assignments = get_assignment_by_type('midterm')
                
                if midterm_assignments:
                    for assignment in midterm_assignments:
                        assignment_id = assignment.get("id")
                        title = assignment.get("title")
                        description = assignment.get("description")
                        deadline = assignment.get("deadline")
                        experiment_card = assignment.get("experiment_card")
                        
                        st.markdown(f"""
                        <div class='assignment-card assignment-midterm'>
                            <div class='assignment-icon'>📊</div>
                            <div class='assignment-title'>{title}</div>
                            <div style='color: #666; margin-bottom: 10px;'>期中作业</div>
                            <div style='margin-bottom: 15px;'>{description}</div>
                            <div class='assignment-deadline'>⏰ 截止日期: {deadline}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if experiment_card:
                        st.markdown("#### 当前期中作业要求：")
                        st.text_area("作业要求", experiment_card, height=200, disabled=True, key=f"teacher_midterm_current_card_{assignment_id}")
                    
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
                                            try:
                                                os.remove(zip_path)
                                                shutil.rmtree(os.path.dirname(zip_path))
                                            except:
                                                pass
                                        elif error:
                                            st.error(error)
                                        else:
                                            st.warning("该作业暂无要求")
                    
                    st.markdown("### 📝 期中作业提交管理")
                    midterm_submissions = get_all_submissions('midterm')
                    
                    if midterm_submissions:
                        total_submissions = len(midterm_submissions)
                        pending_submissions = len([s for s in midterm_submissions if s.get("status") == 'pending'])
                        graded_submissions = len([s for s in midterm_submissions if s.get("status") == 'graded'])
                        graded_scores = [s.get("score") for s in midterm_submissions if s.get("status") == 'graded' and s.get("score") is not None]
                        average_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown('<div class="stats-card"><div>📊 总提交</div><div class="stats-number">{}</div><div class="stats-label">期中作业</div></div>'.format(total_submissions), unsafe_allow_html=True)
                        with col2:
                            st.markdown('<div class="stats-card"><div>⏳ 待批改</div><div class="stats-number">{}</div><div class="stats-label">等待评分</div></div>'.format(pending_submissions), unsafe_allow_html=True)
                        with col3:
                            st.markdown('<div class="stats-card"><div>✅ 已批改</div><div class="stats-number">{}</div><div class="stats-label">完成评分</div></div>'.format(graded_submissions), unsafe_allow_html=True)
                        with col4:
                            st.markdown('<div class="stats-card"><div>🎯 平均分</div><div class="stats-number">{}</div><div class="stats-label">班级平均</div></div>'.format(int(average_score)), unsafe_allow_html=True)
                    
                    for sub_idx, sub in enumerate(midterm_submissions):
                        submission_id = sub.get("id")
                        student_username = sub.get("student_username")
                        submission_content = sub.get("submission_content", "")
                        submission_time = sub.get("submission_time", "")
                        status = sub.get("status", "pending")
                        teacher_feedback = sub.get("teacher_feedback")
                        score = sub.get("score")
                        resubmission_count = sub.get("resubmission_count", 0)
                        allow_view_score = sub.get("allow_view_score", False)
                        file_paths = sub.get("file_paths", [])
                        
                        status_info = {
                            'pending': ('⏳ 待批改', 'status-pending'),
                            'graded': ('✅ 已评分', 'status-graded'),
                            'returned': ('🔙 已退回', 'status-returned')
                        }.get(status, ('⚪ 未知', ''))
                        
                        with st.expander(f"{student_username} - 期中作业 - {status_info[0]} - {submission_time}", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown("**👤 学生:**")
                                st.info(f"**{student_username}**")
                                
                                st.markdown("**📝 提交内容:**")
                                st.text_area("内容", submission_content, height=150, 
                                           key=f"teacher_midterm_content_{submission_id}_{student_username}_{sub_idx}", 
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
                                        
                                        if files and file_paths:
                                            assignment_id = get_assignment_id_by_type_and_number('midterm', 1)
                                            if assignment_id:
                                                zip_path = download_student_files(student_username, assignment_id, file_paths)
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
                                                
                                                st.markdown("**🔍 文件预览:**")
                                                for file_idx, (filename, storage_path) in enumerate(zip(files, file_paths)):
                                                    file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                    with file_preview_col1:
                                                        with st.expander(f"📄 {filename}", expanded=False):
                                                            preview_result, preview_type = get_file_preview_from_storage(storage_path)
                                                            if preview_result:
                                                                if preview_type == "image":
                                                                    st.image(preview_result, caption=filename)
                                                                elif preview_type == "text":
                                                                    st.code(preview_result, language='text')
                                                                else:
                                                                    st.info(preview_result)
                                                    with file_preview_col2:
                                                        success, file_data = download_file_from_storage(BUCKET_ASSIGNMENTS, storage_path)
                                                        if success:
                                                            st.download_button(
                                                                label="📥 单独下载",
                                                                data=file_data,
                                                                file_name=filename,
                                                                mime="application/octet-stream",
                                                                key=f"teacher_midterm_single_file_{submission_id}_{student_username}_{file_idx}"
                                                            )
                                
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
                
                final_assignments = get_assignment_by_type('final')
                
                if final_assignments:
                    for assignment in final_assignments:
                        assignment_id = assignment.get("id")
                        title = assignment.get("title")
                        description = assignment.get("description")
                        deadline = assignment.get("deadline")
                        experiment_card = assignment.get("experiment_card")
                        
                        st.markdown(f"""
                        <div class='assignment-card assignment-final'>
                            <div class='assignment-icon'>🎓</div>
                            <div class='assignment-title'>{title}</div>
                            <div style='color: #666; margin-bottom: 10px;'>期末大作业</div>
                            <div style='margin-bottom: 15px;'>{description}</div>
                            <div class='assignment-deadline'>⏰ 截止日期: {deadline}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if experiment_card:
                        st.markdown("#### 当前期末作业要求：")
                        st.text_area("作业要求", experiment_card, height=200, disabled=True, key=f"teacher_final_current_card_{assignment_id}")
                    
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
                                            try:
                                                os.remove(zip_path)
                                                shutil.rmtree(os.path.dirname(zip_path))
                                            except:
                                                pass
                                        elif error:
                                            st.error(error)
                                        else:
                                            st.warning("该作业暂无要求")
                    
                    st.markdown("### 📝 期末作业提交管理")
                    final_submissions = get_all_submissions('final')
                    
                    if final_submissions:
                        total_submissions = len(final_submissions)
                        pending_submissions = len([s for s in final_submissions if s.get("status") == 'pending'])
                        graded_submissions = len([s for s in final_submissions if s.get("status") == 'graded'])
                        graded_scores = [s.get("score") for s in final_submissions if s.get("status") == 'graded' and s.get("score") is not None]
                        average_score = sum(graded_scores) / len(graded_scores) if graded_scores else 0
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown('<div class="stats-card"><div>📊 总提交</div><div class="stats-number">{}</div><div class="stats-label">期末作业</div></div>'.format(total_submissions), unsafe_allow_html=True)
                        with col2:
                            st.markdown('<div class="stats-card"><div>⏳ 待批改</div><div class="stats-number">{}</div><div class="stats-label">等待评分</div></div>'.format(pending_submissions), unsafe_allow_html=True)
                        with col3:
                            st.markdown('<div class="stats-card"><div>✅ 已批改</div><div class="stats-number">{}</div><div class="stats-label">完成评分</div></div>'.format(graded_submissions), unsafe_allow_html=True)
                        with col4:
                            st.markdown('<div class="stats-card"><div>🎯 平均分</div><div class="stats-number">{}</div><div class="stats-label">班级平均</div></div>'.format(int(average_score)), unsafe_allow_html=True)
                    
                    for sub_idx, sub in enumerate(final_submissions):
                        submission_id = sub.get("id")
                        student_username = sub.get("student_username")
                        submission_content = sub.get("submission_content", "")
                        submission_time = sub.get("submission_time", "")
                        status = sub.get("status", "pending")
                        teacher_feedback = sub.get("teacher_feedback")
                        score = sub.get("score")
                        resubmission_count = sub.get("resubmission_count", 0)
                        allow_view_score = sub.get("allow_view_score", False)
                        file_paths = sub.get("file_paths", [])
                        
                        status_info = {
                            'pending': ('⏳ 待评审', 'status-pending'),
                            'graded': ('✅ 已评分', 'status-graded'),
                            'returned': ('🔙 需修改', 'status-returned')
                        }.get(status, ('⚪ 未知', ''))
                        
                        with st.expander(f"{student_username} - 期末作业 - {status_info[0]} - {submission_time}", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown("**👤 学生:**")
                                st.info(f"**{student_username}**")
                                
                                st.markdown("**📝 提交内容:**")
                                st.text_area("内容", submission_content, height=150, 
                                           key=f"teacher_final_content_{submission_id}_{student_username}_{sub_idx}", 
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
                                        
                                        if files and file_paths:
                                            assignment_id = get_assignment_id_by_type_and_number('final', 1)
                                            if assignment_id:
                                                zip_path = download_student_files(student_username, assignment_id, file_paths)
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
                                                
                                                st.markdown("**🔍 文件预览:**")
                                                for file_idx, (filename, storage_path) in enumerate(zip(files, file_paths)):
                                                    file_preview_col1, file_preview_col2 = st.columns([3, 1])
                                                    with file_preview_col1:
                                                        with st.expander(f"📄 {filename}", expanded=False):
                                                            preview_result, preview_type = get_file_preview_from_storage(storage_path)
                                                            if preview_result:
                                                                if preview_type == "image":
                                                                    st.image(preview_result, caption=filename)
                                                                elif preview_type == "text":
                                                                    st.code(preview_result, language='text')
                                                                else:
                                                                    st.info(preview_result)
                                                    with file_preview_col2:
                                                        success, file_data = download_file_from_storage(BUCKET_ASSIGNMENTS, storage_path)
                                                        if success:
                                                            st.download_button(
                                                                label="📥 单独下载",
                                                                data=file_data,
                                                                file_name=filename,
                                                                mime="application/octet-stream",
                                                                key=f"teacher_final_single_file_{submission_id}_{student_username}_{file_idx}"
                                                            )
                                
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
                st.markdown("### 📊 成绩导出中心")
                
                students = get_all_students()
                
                if students:
                    st.markdown("#### 🔍 学生筛选")
                    selected_student = st.selectbox(
                        "选择学生（可选，不选则导出所有学生）",
                        options=["全部学生"] + students,
                        index=0,
                        key="export_student_select"
                    )
                    
                    student_filter = None if selected_student == "全部学生" else selected_student
                    
                    st.markdown("#### 📈 导出选项")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📋 实验成绩导出", use_container_width=True, type="primary"):
                            with st.spinner("正在生成实验成绩Excel文件..."):
                                excel_data, error = export_experiment_scores_to_excel(student_filter)
                                if excel_data:
                                    filename = f"实验成绩_{selected_student}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                                    st.download_button(
                                        label="📥 下载实验成绩Excel",
                                        data=excel_data,
                                        file_name=filename,
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key="download_experiment_scores"
                                    )
                                    st.success("✅ 实验成绩Excel文件已生成！")
                                else:
                                    st.error(f"❌ {error}")
                    
                    with col2:
                        if st.button("📊 期中成绩导出", use_container_width=True, type="primary"):
                            with st.spinner("正在生成期中成绩Excel文件..."):
                                excel_data, error = export_midterm_scores_to_excel(student_filter)
                                if excel_data:
                                    filename = f"期中成绩_{selected_student}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                                    st.download_button(
                                        label="📥 下载期中成绩Excel",
                                        data=excel_data,
                                        file_name=filename,
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key="download_midterm_scores"
                                    )
                                    st.success("✅ 期中成绩Excel文件已生成！")
                                else:
                                    st.error(f"❌ {error}")
                    
                    with col3:
                        if st.button("🎓 期末成绩导出", use_container_width=True, type="primary"):
                            with st.spinner("正在生成期末成绩Excel文件..."):
                                excel_data, error = export_final_scores_to_excel(student_filter)
                                if excel_data:
                                    filename = f"期末成绩_{selected_student}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                                    st.download_button(
                                        label="📥 下载期末成绩Excel",
                                        data=excel_data,
                                        file_name=filename,
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key="download_final_scores"
                                    )
                                    st.success("✅ 期末成绩Excel文件已生成！")
                                else:
                                    st.error(f"❌ {error}")
                    
                    if student_filter:
                        st.info(f"当前筛选学生: **{student_filter}**")
                        
                        st.markdown("#### 📊 学生成绩概览")
                        
                        submissions = get_student_submissions(student_filter)
                        
                        if submissions:
                            experiment_scores = [s.get("score") for s in submissions if s.get("assignment_type") == 'experiment' and s.get("score") is not None]
                            midterm_scores = [s.get("score") for s in submissions if s.get("assignment_type") == 'midterm' and s.get("score") is not None]
                            final_scores = [s.get("score") for s in submissions if s.get("assignment_type") == 'final' and s.get("score") is not None]
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("实验提交次数", len([s for s in submissions if s.get("assignment_type") == 'experiment']))
                            with col2:
                                if experiment_scores:
                                    st.metric("实验平均分", f"{sum(experiment_scores)/len(experiment_scores):.1f}")
                                else:
                                    st.metric("实验平均分", "未评分")
                            with col3:
                                if midterm_scores:
                                    st.metric("期中成绩", f"{midterm_scores[0]:.1f}")
                                else:
                                    st.metric("期中成绩", "未提交")
                            with col4:
                                if final_scores:
                                    st.metric("期末成绩", f"{final_scores[0]:.1f}")
                                else:
                                    st.metric("期末成绩", "未提交")
                        else:
                            st.info("该学生暂无提交记录")
                    else:
                        st.info("当前导出所有学生成绩")
                        
                        st.markdown("#### 📈 总体统计")
                        
                        all_submissions = get_all_submissions()
                        
                        if all_submissions:
                            total_students = len(set([s.get("student_username") for s in all_submissions]))
                            total_submissions = len(all_submissions)
                            graded_submissions = len([s for s in all_submissions if s.get("status") == 'graded'])
                            graded_scores = [s.get("score") for s in all_submissions if s.get("status") == 'graded' and s.get("score") is not None]
                            avg_score = sum(graded_scores)/len(graded_scores) if graded_scores else 0
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("总学生数", total_students)
                            with col2:
                                st.metric("总提交数", total_submissions)
                            with col3:
                                st.metric("已批改数", graded_submissions)
                            with col4:
                                st.metric("平均分", f"{avg_score:.1f}")
                else:
                    st.info("暂无学生提交记录，无法导出成绩")