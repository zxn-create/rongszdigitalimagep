import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import base64
import pandas as pd
from datetime import datetime
import webbrowser
import matplotlib.pyplot as plt
import os
import json
import uuid
import shutil
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="学习资源中心",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 目标链接（统一配置）
TARGET_URL = "https://www.yuketang.cn/"

# 检查登录状态
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""

# 资源上传相关配置
UPLOAD_DIR = "uploaded_resources"
RESOURCES_FILE = "resources_data.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 实践项目库配置
PROJECTS_DIR = "projects_library"
PROJECTS_FILE = "projects_data.json"
os.makedirs(PROJECTS_DIR, exist_ok=True)

def load_resources():
    """加载已上传的资源"""
    if os.path.exists(RESOURCES_FILE):
        with open(RESOURCES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_resources(resources):
    """保存资源数据"""
    with open(RESOURCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(resources, f, ensure_ascii=False, indent=2)

def load_projects():
    """加载实践项目"""
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_projects(projects):
    """保存项目数据"""
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

# 现代化米色思政主题CSS
def apply_modern_css():
    st.markdown("""
    <style>
    /* 现代化米色主题变量 */
    :root {
        --primary-red: #dc2626;
        --dark-red: #b91c1c;
        --accent-red: #ef4444;
        --beige-light: #fefaf0;
        --beige-medium: #fdf6e3;
        --beige-dark: #faf0d9;
        --gold: #d4af37;
        --light-gold: #fef3c7;
        --dark-text: #1f2937;
        --light-text: #6b7280;
        --card-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        --hover-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
    }

    /* 整体页面背景 - 米色渐变 */
    .stApp {
        background: linear-gradient(135deg, #fefaf0 0%, #fdf6e3 50%, #faf0d9 100%);
    }

    /* 主容器 */
    .main-container {
        background: linear-gradient(135deg, #fefaf0 0%, #fdf6e3 50%, #faf0d9 100%);
        min-height: 100vh;
    }

    /* 现代化头部 */
    .modern-header {
        background: linear-gradient(135deg, var(--primary-red) 0%, var(--dark-red) 100%);
        color: white;
        padding: 40px;
        text-align: center;
        border-radius: 24px;
        margin: 20px 0 40px 0;
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .main-title {
        font-size: 2.5rem;
        margin-bottom: 15px;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        background: linear-gradient(135deg, #fff, #fef3c7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }

    .subtitle {
        font-size: 1.3rem;
        opacity: 0.95;
        line-height: 1.6;
        max-width: 800px;
        margin: 0 auto;
        font-weight: 300;
        position: relative;
        text-align: center;
    }

    /* 资源卡片样式 */
    .resource-card {
        background: linear-gradient(135deg, #fff, var(--beige-light));
        padding: 30px;
        border-radius: 20px;
        border-left: 5px solid var(--primary-red);
        margin: 20px 0;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
        border: 1px solid #e5e7eb;
    }

    .resource-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--hover-shadow);
    }

    .resource-card.tech {
        border-left: 5px solid #3b82f6;
    }

    .resource-card.tutorial {
        border-left: 5px solid #10b981;
    }

    .resource-card.tool {
        border-left: 5px solid #f59e0b;
    }

    .resource-card.upload {
        border-left: 5px solid #8b5cf6;
    }

    .resource-card.project {
        border-left: 5px solid #059669;
    }

    .section-title {
        color: var(--primary-red);
        font-size: 2rem;
        margin: 30px 0 20px 0;
        border-bottom: 3px solid #e5e7eb;
        padding-bottom: 10px;
        font-weight: 700;
    }

    /* 现代化按钮 - 红白渐变悬浮效果 */
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
    }

    /* 删除按钮样式 */
    .stButton button.delete-btn {
        border: 2px solid #ef4444;
        color: #ef4444;
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
    }
    
    .stButton button.delete-btn:hover {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        border-color: #ef4444;
    }

    /* 项目卡片样式 */
    .project-card {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        padding: 25px;
        border-radius: 18px;
        border-left: 5px solid #059669;
        margin: 15px 0;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
        border: 1px solid #bbf7d0;
    }

    .project-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--hover-shadow);
    }

    .project-card.student {
        border-left: 5px solid #3b82f6;
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
    }

    .project-status {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
    }

    .status-completed {
        background: linear-gradient(135deg, #10b981, #047857);
        color: white;
    }

    .status-in-progress {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }

    .status-new {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
    }

    /* 文件卡片 */
    .file-card {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #8b5cf6;
        transition: all 0.2s ease;
    }

    .file-card:hover {
        background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
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

    .css-1d391kg {
        background: linear-gradient(135deg, #fdf6e3 0%, #faf0d9 50%, #f5e6c8 100%) !important;
    }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-red);
        color: white;
    }

    /* 进度条样式 */
    .progress-container {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }

    .progress-bar {
        background: linear-gradient(135deg, var(--primary-red), var(--accent-red));
        height: 8px;
        border-radius: 4px;
        margin-top: 5px;
    }

    /* 徽章样式 */
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary-red), var(--accent-red));
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }

    .badge.blue {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    }

    .badge.green {
        background: linear-gradient(135deg, #10b981, #047857);
    }

    .badge.yellow {
        background: linear-gradient(135deg, #f59e0b, #d97706);
    }

    .badge.purple {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
    }

    .badge.teal {
        background: linear-gradient(135deg, #059669, #047857);
    }

    /* 资源上传卡片 */
    .uploaded-resource-card {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #8b5cf6;
        margin: 15px 0;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
    }

    .uploaded-resource-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--hover-shadow);
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .subtitle {
            font-size: 1.1rem;
        }
        .resource-card {
            padding: 20px;
        }
        .project-card {
            padding: 20px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ================== 重新设计的图像处理工具函数 ==================

def apply_edge_detection(image, operator):
    """
    应用边缘检测算子
    Args:
        image: 输入的BGR图像
        operator: 算子类型（Roberts, Sobel, Prewitt, Laplacian, LoG）
    Returns:
        edge_image: 边缘检测结果（3通道BGR图像）
    """
    if image is None or image.size == 0:
        raise ValueError("输入图像无效")
    
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 根据算子类型进行处理
    if operator == "Roberts":
        # Roberts算子
        kernelx = np.array([[1, 0], [0, -1]], dtype=np.float32)
        kernely = np.array([[0, 1], [-1, 0]], dtype=np.float32)
        robertsx = cv2.filter2D(gray, cv2.CV_32F, kernelx)
        robertsy = cv2.filter2D(gray, cv2.CV_32F, kernely)
        edge_magnitude = np.sqrt(np.square(robertsx) + np.square(robertsy))
        edge_magnitude = np.uint8(np.clip(edge_magnitude, 0, 255))
    
    elif operator == "Sobel":
        # Sobel算子
        sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        edge_magnitude = np.sqrt(np.square(sobelx) + np.square(sobely))
        edge_magnitude = np.uint8(np.clip(edge_magnitude, 0, 255))
    
    elif operator == "Prewitt":
        # Prewitt算子
        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
        prewittx = cv2.filter2D(gray, cv2.CV_32F, kernelx)
        prewitty = cv2.filter2D(gray, cv2.CV_32F, kernely)
        edge_magnitude = np.sqrt(np.square(prewittx) + np.square(prewitty))
        edge_magnitude = np.uint8(np.clip(edge_magnitude, 0, 255))
    
    elif operator == "Laplacian":
        # Laplacian算子
        laplacian = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
        edge_magnitude = np.uint8(np.clip(np.abs(laplacian), 0, 255))
    
    elif operator == "LoG":
        # LoG算子（Laplacian of Gaussian）
        blurred = cv2.GaussianBlur(gray, (5, 5), 1)
        laplacian = cv2.Laplacian(blurred, cv2.CV_32F, ksize=3)
        edge_magnitude = np.uint8(np.clip(np.abs(laplacian), 0, 255))
    
    else:
        # 默认返回原图
        edge_magnitude = gray
    
    # 转换为3通道图像以便显示
    edge_image = cv2.cvtColor(edge_magnitude, cv2.COLOR_GRAY2BGR)
    
    # 增强边缘效果
    edge_image = cv2.convertScaleAbs(edge_image, alpha=1.2, beta=20)
    
    return edge_image

def apply_filter(image, filter_type, kernel_size):
    """
    应用图像滤波器
    Args:
        image: 输入的BGR图像
        filter_type: 滤波器类型（中值滤波, 均值滤波, 高斯滤波）
        kernel_size: 核大小（必须为奇数）
    Returns:
        filtered_image: 滤波后的图像
    """
    if image is None or image.size == 0:
        raise ValueError("输入图像无效")
    
    # 确保核大小为奇数
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    kernel_size = max(3, min(15, kernel_size))
    
    try:
        if filter_type == "中值滤波":
            filtered = cv2.medianBlur(image, kernel_size)
        
        elif filter_type == "均值滤波":
            filtered = cv2.blur(image, (kernel_size, kernel_size))
        
        elif filter_type == "高斯滤波":
            filtered = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        
        else:
            filtered = image.copy()
        
        return filtered
    
    except Exception as e:
        st.error(f"滤波处理失败: {str(e)}")
        return image.copy()

def get_image_download_link(img, filename, text):
    """
    生成图像下载链接
    Args:
        img: numpy数组图像（BGR格式）
        filename: 下载文件名
        text: 链接显示文本
    Returns:
        HTML下载链接
    """
    # 转换为RGB格式
    if len(img.shape) == 3 and img.shape[2] == 3:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        img_rgb = img
    
    # 转换为PIL图像
    pil_img = Image.fromarray(img_rgb)
    
    # 保存到缓冲区
    buffered = io.BytesIO()
    pil_img.save(buffered, format="JPEG", quality=95)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # 生成下载链接
    href = f'''
    <a href="data:image/jpeg;base64,{img_str}" download="{filename}" 
       style="display: inline-block; 
              background: linear-gradient(135deg, #dc2626, #b91c1c); 
              color: white; 
              padding: 12px 24px; 
              border-radius: 50px;
              text-decoration: none;
              font-weight: 600;
              margin-top: 10px;
              box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
              transition: all 0.3s ease;">
       {text}
    </a>
    '''
    return href

def display_image_comparison(original_img, processed_img, original_title="原始图像", processed_title="处理结果"):
    """
    并排显示原始图像和处理结果
    Args:
        original_img: 原始图像
        processed_img: 处理后的图像
        original_title: 原始图像标题
        processed_title: 处理结果标题
    """
    col1, col2 = st.columns(2)
    
    with col1:
        # 显示原始图像
        if len(original_img.shape) == 3:
            display_original = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        else:
            display_original = original_img
        
        st.image(display_original, caption=f"📷 {original_title}", use_container_width=True)
        
        # 显示图像信息
        st.caption(f"""
        **图像信息:**
        - 尺寸: {original_img.shape[1]}×{original_img.shape[0]}
        - 通道数: {original_img.shape[2] if len(original_img.shape) == 3 else 1}
        - 数据类型: {original_img.dtype}
        """)
    
    with col2:
        # 显示处理结果
        if len(processed_img.shape) == 3:
            display_processed = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
        else:
            display_processed = processed_img
        
        st.image(display_processed, caption=f"✨ {processed_title}", use_container_width=True)
        
        # 显示处理信息
        st.caption(f"""
        **处理信息:**
        - 输出尺寸: {processed_img.shape[1]}×{processed_img.shape[0]}
        - 输出通道: {processed_img.shape[2] if len(processed_img.shape) == 3 else 1}
        - 数据范围: [{processed_img.min()}, {processed_img.max()}]
        """)

# 新的链接打开函数
def create_link_button(url, text, key=None):
    button_html = f'''
    <a href="{url}" target="_blank" style="
        display: inline-block;
        width: 100%;
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
        text-decoration: none;
        text-align: center;
        cursor: pointer;
        margin: 5px 0;
    " onmouseover="this.style.background='linear-gradient(135deg, #dc2626, #b91c1c)'; this.style.color='white'; this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 25px rgba(220, 38, 38, 0.4)';" 
    onmouseout="this.style.background='linear-gradient(135deg, #ffffff, #fef2f2)'; this.style.color='#dc2626'; this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 15px rgba(220, 38, 38, 0.2)';">
        {text}
    </a>
    '''
    return button_html

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
        if st.button("📤 实验作业提交", use_container_width=True):
            st.switch_page("pages/实验作业提交.py")
        if st.button("📚 学习资源中心", use_container_width=True):
            st.switch_page("pages/2_📚_学习资源中心.py")
        if st.button("📝 我的思政足迹", use_container_width=True):
            st.switch_page("pages/3_📝_我的思政足迹.py")
        if st.button("🏆 成果展示", use_container_width=True):
            st.switch_page("pages/4_🏆_成果展示.py")

        # 用户信息显示
        if st.session_state.logged_in:
            st.markdown("### 👤 用户信息")
            st.info(f"**用户名:** {st.session_state.username}")
            st.info(f"**身份:** {st.session_state.role}")
            if st.session_state.student_name:
                st.info(f"**姓名:** {st.session_state.student_name}")
            
            if st.button("🚪 退出登录", use_container_width=True):
                for key in ['logged_in', 'username', 'role', 'student_name']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        # 学习进度
        st.markdown("### 📊 学习进度")
        progress_data = {
            "章节": ["图像处理基础", "图像增强", "边缘检测", "图像分割", "特征提取"],
            "进度": [100, 80, 60, 40, 20]
        }
        df = pd.DataFrame(progress_data)

        for _, row in df.iterrows():
            st.markdown(f"**{row['章节']}**")
            st.progress(row['进度'] / 100)

        st.markdown("---")

        # 思政理论学习
        st.markdown("### 🎯 思政理论学习")
        
        theory_links = [
            ("图像处理中的工匠精神", "https://www.sxjrzyxy.edu.cn/Article.aspx?ID=33094&Mid=869"),
            ("科技创新与国家发展", "https://www.bilibili.com/video/BV13K4y1a7Xv/"),
            ("技术伦理与社会责任", "https://www.bilibili.com/video/BV18T4y137Ku/"),
            ("科学家精神传承", "https://www.bilibili.com/video/BV13DVgzKEoz/")
        ]
        
        for topic, url in theory_links:
            button_html = create_link_button(url, f"📖 {topic}")
            st.markdown(button_html, unsafe_allow_html=True)

        st.markdown("---")

        # 实验指南
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fee2e2, #fecaca); padding: 20px; 
                    border-radius: 12px; border-left: 4px solid #dc2626; margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);'>
            <h4 style='color: #dc2626;'>📚 学习指南</h4>
            <ol style='padding-left: 20px; color: #7f1d1d;'>
                <li style='color: #dc2626;'>选择学习模块</li>
                <li style='color: #dc2626;'>阅读理论知识</li>
                <li style='color: #dc2626;'>完成实践练习</li>
                <li style='color: #dc2626;'>记录学习心得</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        # 系统信息
        st.markdown("---")
        st.markdown("**📊 系统信息**")
        st.text(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.text("状态: 🟢 正常运行")
        st.text("版本: v2.2.0")

# 资源上传页面
def render_resource_upload():
    """渲染资源上传页面"""
    st.markdown('<div class="section-title">📤 资源上传与共享</div>', unsafe_allow_html=True)
    
    # 检查登录状态
    if not st.session_state.logged_in:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fef2f2, #fee2e2); padding: 30px; 
                    border-radius: 15px; border: 2px solid #dc2626; margin: 20px 0;
                    text-align: center;'>
            <h3 style='color: #dc2626;'>🔒 访问受限</h3>
            <p style='color: #7f1d1d; font-size: 1.1rem;'>请先登录系统以访问资源上传功能</p>
            <p style='color: #7f1d1d;'>请在主页面点击右上角的"登录/注册"按钮进行登录</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("main.py")
        return
    
    st.markdown(f"""
    <div class='resource-card upload'>
        <h3>👋 欢迎，{st.session_state.username}！</h3>
        <p>在这里，您可以上传学习资源与其他同学分享。</p>
        <div style="margin: 15px 0;">
            <span class="badge purple">上传</span>
            <span class="badge purple">分享</span>
            <span class="badge purple">协作</span>
        </div>
        <p><strong>📝 使用说明：</strong></p>
        <ul>
            <li>支持上传文档、图片、代码等学习资源</li>
            <li>上传的资源对所有用户可见</li>
            <li>可以对自己上传的资源进行撤销</li>
            <li>鼓励分享优质学习资源</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 用户信息显示
    user_col1, user_col2, user_col3 = st.columns(3)
    with user_col1:
        st.info(f"👤 用户: {st.session_state.username}")
    with user_col2:
        st.info(f"🎓 身份: {st.session_state.role}")
    with user_col3:
        if st.session_state.student_name:
            st.info(f"📝 姓名: {st.session_state.student_name}")
        else:
            st.info("📝 姓名: 未设置")
    
    st.markdown("---")
    
    # 上传资源表单
    st.markdown("### 📤 上传新资源")
    
    with st.form("resource_upload_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            resource_name = st.text_input("资源名称 *", placeholder="例如：图像处理实验报告")
            resource_type = st.selectbox("资源类型 *", 
                ["文档", "代码", "图片", "视频", "音频", "数据集", "其他"])
            description = st.text_area("资源描述", 
                placeholder="请简要描述资源内容...", height=100)
        
        with col2:
            upload_file = st.file_uploader("选择文件 *", 
                type=["pdf", "doc", "docx", "txt", "py", "java", "c", "cpp", 
                      "jpg", "jpeg", "png", "gif", "mp4", "avi", "mp3", "wav",
                      "zip", "rar", "7z", "csv", "xlsx", "json"],
                help="支持多种文件格式，最大100MB")
            
            tags = st.text_input("标签（用逗号分隔）", 
                placeholder="例如：图像处理,OpenCV,实验报告")
            is_public = st.checkbox("公开分享给所有用户", value=True)
        
        submitted = st.form_submit_button("📤 上传资源", use_container_width=True)
        
        if submitted:
            if not resource_name:
                st.error("请填写资源名称！")
            elif not upload_file:
                st.error("请选择要上传的文件！")
            else:
                try:
                    # 生成唯一ID
                    resource_id = str(uuid.uuid4())[:8]
                    
                    # 保存文件
                    file_ext = upload_file.name.split('.')[-1]
                    filename = f"{resource_id}_{upload_file.name}"
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(upload_file.getbuffer())
                    
                    # 获取文件大小
                    file_size = upload_file.size
                    file_size_str = f"{file_size/1024:.1f}KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f}MB"
                    
                    # 创建资源记录
                    resource_data = {
                        "id": resource_id,
                        "name": resource_name,
                        "type": resource_type,
                        "description": description,
                        "filename": filename,
                        "original_filename": upload_file.name,
                        "file_size": file_size_str,
                        "file_ext": file_ext,
                        "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                        "uploader": st.session_state.username,
                        "uploader_role": st.session_state.role,
                        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "is_public": is_public,
                        "download_count": 0
                    }
                    
                    # 保存到资源列表
                    resources = load_resources()
                    resources.append(resource_data)
                    save_resources(resources)
                    
                    st.success(f"✅ 资源 '{resource_name}' 上传成功！")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"上传失败: {str(e)}")
    
    st.markdown("---")
    
    # 显示已上传的资源
    st.markdown("### 📋 已上传的资源")
    
    resources = load_resources()
    
    if not resources:
        st.info("📭 暂无上传的资源")
    else:
        # 过滤资源：如果是普通用户，只能看到公开资源和自己上传的；管理员可以看到所有
        if st.session_state.role == "admin" or st.session_state.role == "teacher":
            filtered_resources = resources
        else:
            filtered_resources = [
                r for r in resources 
                if r.get("is_public", True) or r.get("uploader") == st.session_state.username
            ]
        
        if not filtered_resources:
            st.info("📭 暂无可见的资源")
        else:
            for resource in filtered_resources:
                is_owner = resource.get("uploader") == st.session_state.username
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # 资源类型图标
                    type_icons = {
                        "文档": "📄", "代码": "💻", "图片": "🖼️", 
                        "视频": "🎬", "音频": "🎵", "数据集": "📊", "其他": "📎"
                    }
                    icon = type_icons.get(resource["type"], "📎")
                    
                    # 资源卡片
                    html_parts = []

                    # 第一部分：卡片头部
                    header = f"""
                        <div class='uploaded-resource-card'>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #1f2937;">{icon} {resource['name']}</h4>
                            <div>
                    """

                    # 处理所有者和隐私标签
                    owner_tag = '<span style="color: #dc2626; font-weight: bold;">👤 我的</span>' if is_owner else ''
                    privacy_tag = '' if resource.get('is_public', True) else '<span style="color: #6b7280; font-weight: bold;">🔒 私密</span>'

                    # 第二部分：描述
                    description = f"<p style='color: #6b7280; margin: 8px 0;'>{resource['description'] or '无描述'}</p>"
        
                    # 第三部分：信息
                    info = f"""
                    <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                        <div>
                            <span style="color: #6b7280; font-size: 0.9rem;">👤 {resource['uploader']} ({resource['uploader_role']})</span>
                            <span style="color: #6b7280; font-size: 0.9rem; margin-left: 15px;">🕒 {resource['upload_time']}</span>
                        </div>
                        <div>
                            <span style="color: #6b7280; font-size: 0.9rem;">📦 {resource['file_size']}</span>
                            <span style="color: #6b7280; font-size: 0.9rem; margin-left: 15px;">📥 下载: {resource.get('download_count', 0)}</span>
                        </div>
                    </div>
                    """

                    # 第四部分：标签
                    tags_section = ""
                    if resource.get('tags'):
                        tags_list = []
                        for tag in resource.get('tags', []):
                            tags_list.append(f'<span class="badge purple" style="font-size: 0.8rem;">{tag}</span>')
                        tags_html = ' '.join(tags_list)
                        tags_section = f"<div style='margin-top: 10px;'>{tags_html}</div>"

                    # 组合所有部分
                    final_html = f"""{header}{owner_tag}{privacy_tag}</div></div>
                    {description}
                    {info}
                    {tags_section}
                    </div>"""

                    st.markdown(final_html, unsafe_allow_html=True)
                with col2:
                    # 下载按钮
                    filepath = os.path.join(UPLOAD_DIR, resource["filename"])
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as f:
                            file_data = f.read()
                        
                        st.download_button(
                            label="📥 下载",
                            data=file_data,
                            file_name=resource["original_filename"],
                            mime="application/octet-stream",
                            use_container_width=True,
                            key=f"download_{resource['id']}"
                        )
                    
                    # 删除按钮（仅资源所有者或管理员可见）
                    if is_owner or st.session_state.role in ["admin", "teacher"]:
                        if st.button("🗑️ 撤销", 
                                   key=f"delete_{resource['id']}",
                                   use_container_width=True,
                                   type="secondary"):
                            # 删除文件
                            try:
                                if os.path.exists(filepath):
                                    os.remove(filepath)
                            except:
                                pass
                            
                            # 从资源列表中移除
                            resources = [r for r in resources if r["id"] != resource["id"]]
                            save_resources(resources)
                            st.success("✅ 资源已撤销")
                            st.rerun()

# 实践项目库模块
def render_project_library():
    """渲染实践项目库页面"""
    st.markdown('<div class="section-title">🏗️ 实践项目库</div>', unsafe_allow_html=True)
    
    # 检查登录状态
    if not st.session_state.logged_in:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fef2f2, #fee2e2); padding: 30px; 
                    border-radius: 15px; border: 2px solid #dc2626; margin: 20px 0;
                    text-align: center;'>
            <h3 style='color: #dc2626;'>🔒 访问受限</h3>
            <p style='color: #7f1d1d; font-size: 1.1rem;'>请先登录系统以访问实践项目库</p>
            <p style='color: #7f1d1d;'>请在主页面点击右上角的"登录/注册"按钮进行登录</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("main.py")
        return
    
    st.markdown(f"""
    <div class='resource-card project'>
        <h3>🏗️ 实践项目库</h3>
        <p>这里是历届学生的实践项目存档中心，包含选题文档、数据集和代码。</p>
        <div style="margin: 15px 0;">
            <span class="badge teal">教师端</span>
            <span class="badge teal">学生端</span>
            <span class="badge teal">项目</span>
            <span class="badge teal">代码</span>
        </div>
        <p><strong>📝 功能说明：</strong></p>
        <ul>
            <li><strong>教师端：</strong>上传和管理历届学生选题文档和数据集</li>
            <li><strong>学生端：</strong>下载选题文档和数据集，上传和下载代码</li>
            <li><strong>权限控制：</strong>不同角色拥有不同的操作权限</li>
            <li><strong>文件管理：</strong>支持文件的上传、下载和删除</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 用户信息显示
    user_col1, user_col2 = st.columns(2)
    with user_col1:
        st.info(f"👤 当前用户: {st.session_state.username}")
    with user_col2:
        st.info(f"🎓 当前身份: {st.session_state.role}")
    
    st.markdown("---")
    
    # 加载项目数据
    projects = load_projects()
    
    # 根据用户角色显示不同的界面
    if st.session_state.role == "teacher" or st.session_state.role == "admin":
        render_teacher_project_interface(projects)
    else:
        render_student_project_interface(projects)

def render_teacher_project_interface(projects):
    """渲染教师端项目界面"""
    st.markdown("### 👨‍🏫 教师端功能")
    
    # 教师功能标签页
    teacher_tab1, teacher_tab2 = st.tabs(["📤 上传新项目", "📋 管理现有项目"])
    
    with teacher_tab1:
        st.markdown("#### 📤 上传新的实践项目")
        
        with st.form("project_upload_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                project_name = st.text_input("项目名称 *", placeholder="例如：基于OpenCV的人脸识别系统")
                student_name = st.text_input("学生姓名", placeholder="例如：张三")
                student_id = st.text_input("学号", placeholder="例如：20210001")
                academic_year = st.selectbox("学年", ["2021-2022", "2022-2023", "2023-2024", "2024-2025"])
                project_type = st.selectbox("项目类型", ["课程设计", "毕业设计", "创新项目", "实验项目"])
                description = st.text_area("项目描述", placeholder="请简要描述项目内容和技术要点...", height=120)
            
            with col2:
                # 选题文档上传
                proposal_file = st.file_uploader("选题文档 *", 
                    type=["pdf", "doc", "docx", "txt"],
                    help="请上传项目的选题报告或开题报告")
                
                # 数据集上传
                dataset_files = st.file_uploader("数据集文件", 
                    type=["zip", "rar", "7z", "csv", "json", "jpg", "png", "npy"],
                    help="可上传多个数据集文件（支持压缩包格式）",
                    accept_multiple_files=True)
                
                # 初始代码上传
                initial_code = st.file_uploader("初始代码（可选）", 
                    type=["py", "java", "c", "cpp", "ipynb", "zip", "rar"],
                    help="可上传项目的基础代码或框架代码")
                
                difficulty = st.select_slider("项目难度", 
                    options=["简单", "中等", "较难", "困难", "挑战"],
                    value="中等")
            
            submitted = st.form_submit_button("🚀 创建新项目", use_container_width=True)
            
            if submitted:
                if not project_name:
                    st.error("请填写项目名称！")
                elif not proposal_file:
                    st.error("请上传选题文档！")
                else:
                    try:
                        # 生成项目ID
                        project_id = str(uuid.uuid4())[:8]
                        project_dir = os.path.join(PROJECTS_DIR, project_id)
                        os.makedirs(project_dir, exist_ok=True)
                        
                        # 保存选题文档
                        proposal_ext = proposal_file.name.split('.')[-1]
                        proposal_filename = f"proposal_{project_id}.{proposal_ext}"
                        proposal_path = os.path.join(project_dir, proposal_filename)
                        
                        with open(proposal_path, "wb") as f:
                            f.write(proposal_file.getbuffer())
                        
                        # 保存数据集文件
                        dataset_files_info = []
                        if dataset_files:
                            dataset_dir = os.path.join(project_dir, "datasets")
                            os.makedirs(dataset_dir, exist_ok=True)
                            
                            for dataset_file in dataset_files:
                                dataset_filename = f"dataset_{dataset_file.name}"
                                dataset_path = os.path.join(dataset_dir, dataset_filename)
                                
                                with open(dataset_path, "wb") as f:
                                    f.write(dataset_file.getbuffer())
                                
                                file_size = dataset_file.size
                                file_size_str = f"{file_size/1024:.1f}KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f}MB"
                                
                                dataset_files_info.append({
                                    "filename": dataset_filename,
                                    "original_name": dataset_file.name,
                                    "size": file_size_str,
                                    "type": dataset_file.name.split('.')[-1]
                                })
                        
                        # 保存初始代码
                        initial_code_info = None
                        if initial_code:
                            code_ext = initial_code.name.split('.')[-1]
                            code_filename = f"initial_code_{project_id}.{code_ext}"
                            code_path = os.path.join(project_dir, code_filename)
                            
                            with open(code_path, "wb") as f:
                                f.write(initial_code.getbuffer())
                            
                            file_size = initial_code.size
                            file_size_str = f"{file_size/1024:.1f}KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f}MB"
                            
                            initial_code_info = {
                                "filename": code_filename,
                                "original_name": initial_code.name,
                                "size": file_size_str,
                                "type": code_ext
                            }
                        
                        # 创建项目记录
                        project_data = {
                            "id": project_id,
                            "name": project_name,
                            "student_name": student_name,
                            "student_id": student_id,
                            "academic_year": academic_year,
                            "type": project_type,
                            "difficulty": difficulty,
                            "description": description,
                            "proposal_file": {
                                "filename": proposal_filename,
                                "original_name": proposal_file.name,
                                "size": f"{proposal_file.size/1024:.1f}KB" if proposal_file.size < 1024*1024 else f"{proposal_file.size/(1024*1024):.1f}MB",
                                "type": proposal_ext
                            },
                            "datasets": dataset_files_info,
                            "initial_code": initial_code_info,
                            "student_codes": [],  # 学生上传的代码
                            "created_by": st.session_state.username,
                            "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "updated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "download_count": 0
                        }
                        
                        # 保存项目数据
                        projects.append(project_data)
                        save_projects(projects)
                        
                        st.success(f"✅ 项目 '{project_name}' 创建成功！")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"创建项目失败: {str(e)}")
    
    with teacher_tab2:
        st.markdown("#### 📋 项目管理")
        
        if not projects:
            st.info("📭 暂无实践项目")
        else:
            # 项目筛选
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_year = st.selectbox("按学年筛选", ["全部"] + list(set(p["academic_year"] for p in projects)))
            with col2:
                filter_type = st.selectbox("按类型筛选", ["全部"] + list(set(p["type"] for p in projects)))
            with col3:
                filter_difficulty = st.selectbox("按难度筛选", ["全部", "简单", "中等", "较难", "困难", "挑战"])
            
            # 过滤项目
            filtered_projects = projects
            if filter_year != "全部":
                filtered_projects = [p for p in filtered_projects if p["academic_year"] == filter_year]
            if filter_type != "全部":
                filtered_projects = [p for p in filtered_projects if p["type"] == filter_type]
            if filter_difficulty != "全部":
                filtered_projects = [p for p in filtered_projects if p["difficulty"] == filter_difficulty]
            
            if not filtered_projects:
                st.info("📭 没有符合条件的项目")

            else:
                for project in filtered_projects:
                    # 项目卡片
                    st.markdown(f"""
                    <div class='project-card'>
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4 style="margin: 0; color: #1f2937;">🏗️ {project['name']}</h4>
                                <p style="color: #6b7280; margin: 5px 0; font-size: 0.95rem;">
                                    👤 {project['student_name'] or '未指定'} | 🎓 {project['student_id'] or '未指定'} | 📅 {project['academic_year']}
                                </p>
                            </div>
                            <div>
                                <span class="project-status status-{'completed' if project.get('status') == 'completed' else 'in-progress'}">
                                    {project.get('status', '进行中')}
                                </span>
                                <span style="color: #dc2626; font-weight: bold;">{project['difficulty']}</span>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    
                    st.markdown(f"""    
                        <p style="color: #4b5563; margin: 10px 0; font-size: 0.95rem;">{project['description']}</p>""", unsafe_allow_html=True)
                    st.markdown(f"""                      
                        <div style="margin-top: 15px;">
                            <span class="badge teal">{project['type']}</span>
                            <span class="badge teal">📅 {project['academic_year']}</span>
                            <span class="badge teal">👨‍🏫 {project['created_by']}</span>
                        </div>""", unsafe_allow_html=True)
                    st.markdown(f"""                        
                        <div style="margin-top: 15px; background: #f8fafc; padding: 15px; border-radius: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <p style="margin: 5px 0; color: #4b5563; font-size: 0.9rem;">
                                        <strong>📄 选题文档:</strong> {project['proposal_file']['original_name']} ({project['proposal_file']['size']})
                                    </p>
                                    <p style="margin: 5px 0; color: #4b5563; font-size: 0.9rem;">
                                        <strong>📊 数据集:</strong> {len(project.get('datasets', []))}个文件
                                    </p>
                                    <p style="margin: 5px 0; color: #4b5563; font-size: 0.9rem;">
                                        <strong>💻 学生代码:</strong> {len(project.get('student_codes', []))}个版本
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 操作按钮
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        # 下载选题文档
                        proposal_path = os.path.join(PROJECTS_DIR, project['id'], project['proposal_file']['filename'])
                        if os.path.exists(proposal_path):
                            with open(proposal_path, "rb") as f:
                                proposal_data = f.read()
                            
                            st.download_button(
                                label="📥 下载选题文档",
                                data=proposal_data,
                                file_name=project['proposal_file']['original_name'],
                                mime="application/octet-stream",
                                key=f"download_proposal_{project['id']}",
                                use_container_width=True
                            )
                    
                    with col2:
                        # 查看数据集
                        if project.get('datasets'):
                            if st.button("📊 查看数据集", key=f"view_dataset_{project['id']}", use_container_width=True):
                                # 显示数据集文件列表
                                st.session_state[f"show_dataset_{project['id']}"] = not st.session_state.get(f"show_dataset_{project['id']}", False)
                        
                        if st.session_state.get(f"show_dataset_{project['id']}", False) and project.get('datasets'):
                            for dataset in project['datasets']:
                                dataset_path = os.path.join(PROJECTS_DIR, project['id'], "datasets", dataset['filename'])
                                if os.path.exists(dataset_path):
                                    with open(dataset_path, "rb") as f:
                                        dataset_data = f.read()
                                    
                                    col_a, col_b = st.columns([3, 1])
                                    with col_a:
                                        st.write(f"📁 {dataset['original_name']} ({dataset['size']})")
                                    with col_b:
                                        st.download_button(
                                            label="下载",
                                            data=dataset_data,
                                            file_name=dataset['original_name'],
                                            mime="application/octet-stream",
                                            key=f"download_dataset_{project['id']}_{dataset['filename']}",
                                            use_container_width=True
                                        )
                    
                    with col3:
                        # 查看学生代码
                        if project.get('student_codes'):
                            if st.button("💻 查看代码", key=f"view_code_{project['id']}", use_container_width=True):
                                st.session_state[f"show_code_{project['id']}"] = not st.session_state.get(f"show_code_{project['id']}", False)
                        
                        if st.session_state.get(f"show_code_{project['id']}", False) and project.get('student_codes'):
                            for code in project['student_codes']:
                                code_path = os.path.join(PROJECTS_DIR, project['id'], "student_codes", code['filename'])
                                if os.path.exists(code_path):
                                    with open(code_path, "rb") as f:
                                        code_data = f.read()
                                    
                                    col_a, col_b = st.columns([3, 1])
                                    with col_a:
                                        st.write(f"📝 {code['original_name']} ({code['size']})")
                                        st.caption(f"上传者: {code['uploader']} | 时间: {code['upload_time']}")
                                    with col_b:
                                        st.download_button(
                                            label="下载",
                                            data=code_data,
                                            file_name=code['original_name'],
                                            mime="application/octet-stream",
                                            key=f"download_code_{project['id']}_{code['filename']}",
                                            use_container_width=True
                                        )
                    
                    with col4:
                        # 删除项目（仅创建者或管理员）
                        if project['created_by'] == st.session_state.username or st.session_state.role in ["admin", "teacher"]:
                            if st.button("🗑️ 删除", key=f"delete_project_{project['id']}", use_container_width=True, type="secondary"):
                                # 删除项目目录
                                project_dir = os.path.join(PROJECTS_DIR, project['id'])
                                if os.path.exists(project_dir):
                                    shutil.rmtree(project_dir)
                                
                                # 从项目列表中移除
                                projects = [p for p in projects if p['id'] != project['id']]
                                save_projects(projects)
                                
                                st.success("✅ 项目已删除")
                                st.rerun()
                    
                    st.markdown("---")

def render_student_project_interface(projects):
    """渲染学生端项目界面"""
    st.markdown("### 👨‍🎓 学生端功能")
    
    if not projects:
        st.info("📭 暂无可用的实践项目")
        return
    
    # 学生功能标签页
    student_tab1, student_tab2 = st.tabs(["📚 浏览项目", "💻 我的代码"])
    
    with student_tab1:
        st.markdown("#### 📚 可参与的项目")
        
        # 项目筛选
        col1, col2 = st.columns(2)
        with col1:
            filter_difficulty = st.selectbox("按难度筛选", ["全部", "简单", "中等", "较难", "困难", "挑战"])
        with col2:
            filter_type = st.selectbox("按类型筛选", ["全部"] + list(set(p["type"] for p in projects)))
        
        # 过滤项目
        filtered_projects = projects
        if filter_difficulty != "全部":
            filtered_projects = [p for p in filtered_projects if p["difficulty"] == filter_difficulty]
        if filter_type != "全部":
            filtered_projects = [p for p in filtered_projects if p["type"] == filter_type]
        
        if not filtered_projects:
            st.info("📭 没有符合条件的项目")
        else:
            for project in filtered_projects:
                # 项目卡片
                st.markdown(f"""
                <div class='project-card student'>
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0; color: #1f2937;">🏗️ {project['name']}</h4>
                            <p style="color: #6b7280; margin: 5px 0; font-size: 0.95rem;">
                                👤 {project['student_name'] or '未指定'} | 🎓 {project['student_id'] or '未指定'} | 📅 {project['academic_year']}
                            </p>
                        </div>
                        <div>
                            <span style="color: #dc2626; font-weight: bold;">{project['difficulty']}</span>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""  
                    <p style="color: #4b5563; margin: 10px 0; font-size: 0.95rem;">{project['description']}</p>
                 """, unsafe_allow_html=True)
                st.markdown(f"""  
                    <div style="margin-top: 15px;">
                        <span class="badge blue">{project['type']}</span>
                        <span class="badge blue">📅 {project['academic_year']}</span>
                        <span class="badge blue">📊 {len(project.get('datasets', []))}个数据集</span>
                        <span class="badge blue">💻 {len(project.get('student_codes', []))}个代码版本</span>
                    </div>
                
                """, unsafe_allow_html=True)
                
                # 操作按钮
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # 下载选题文档
                    proposal_path = os.path.join(PROJECTS_DIR, project['id'], project['proposal_file']['filename'])
                    if os.path.exists(proposal_path):
                        with open(proposal_path, "rb") as f:
                            proposal_data = f.read()
                        
                        st.download_button(
                            label="📄 下载选题文档",
                            data=proposal_data,
                            file_name=project['proposal_file']['original_name'],
                            mime="application/octet-stream",
                            key=f"student_download_proposal_{project['id']}",
                            use_container_width=True
                        )
                
                with col2:
                    # 下载数据集
                    if project.get('datasets'):
                        if st.button("📊 下载数据集", key=f"student_download_dataset_{project['id']}", use_container_width=True):
                            # 如果是单个文件，直接下载；如果是多个文件，打包下载
                            if len(project['datasets']) == 1:
                                dataset = project['datasets'][0]
                                dataset_path = os.path.join(PROJECTS_DIR, project['id'], "datasets", dataset['filename'])
                                if os.path.exists(dataset_path):
                                    with open(dataset_path, "rb") as f:
                                        dataset_data = f.read()
                                    
                                    st.download_button(
                                        label=f"下载 {dataset['original_name']}",
                                        data=dataset_data,
                                        file_name=dataset['original_name'],
                                        mime="application/octet-stream",
                                        key=f"student_single_dataset_{project['id']}"
                                    )
                            else:
                                # 创建压缩包
                                import zipfile
                                import tempfile
                                
                                with tempfile.TemporaryDirectory() as tmpdir:
                                    zip_path = os.path.join(tmpdir, f"{project['id']}_datasets.zip")
                                    
                                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                                        for dataset in project['datasets']:
                                            dataset_path = os.path.join(PROJECTS_DIR, project['id'], "datasets", dataset['filename'])
                                            if os.path.exists(dataset_path):
                                                zipf.write(dataset_path, dataset['original_name'])
                                    
                                    with open(zip_path, "rb") as f:
                                        zip_data = f.read()
                                    
                                    st.download_button(
                                        label="📦 下载全部数据集",
                                        data=zip_data,
                                        file_name=f"{project['id']}_datasets.zip",
                                        mime="application/zip",
                                        key=f"student_zip_dataset_{project['id']}"
                                    )
                
                with col3:
                    # 上传我的代码
                    if st.button("💻 上传代码", key=f"student_upload_code_{project['id']}", use_container_width=True):
                        st.session_state[f"show_upload_{project['id']}"] = not st.session_state.get(f"show_upload_{project['id']}", False)
                
                # 代码上传表单
                if st.session_state.get(f"show_upload_{project['id']}", False):
                    with st.form(f"upload_code_form_{project['id']}", clear_on_submit=True):
                        code_file = st.file_uploader("选择代码文件", 
                            type=["py", "java", "c", "cpp", "ipynb", "zip", "rar", "7z"],
                            key=f"code_file_{project['id']}",
                            help="可以上传单个代码文件或整个项目的压缩包")
                        
                        code_description = st.text_area("代码说明", 
                            placeholder="请简要描述代码功能和修改内容...",
                            key=f"code_desc_{project['id']}",
                            height=80)
                        
                        submitted = st.form_submit_button("🚀 上传代码", use_container_width=True)
                        
                        if submitted:
                            if not code_file:
                                st.error("请选择要上传的代码文件！")
                            else:
                                try:
                                    # 确保学生代码目录存在
                                    code_dir = os.path.join(PROJECTS_DIR, project['id'], "student_codes")
                                    os.makedirs(code_dir, exist_ok=True)
                                    
                                    # 生成代码版本ID
                                    code_id = str(uuid.uuid4())[:8]
                                    code_ext = code_file.name.split('.')[-1]
                                    code_filename = f"code_{st.session_state.username}_{code_id}.{code_ext}"
                                    code_path = os.path.join(code_dir, code_filename)
                                    
                                    # 保存代码文件
                                    with open(code_path, "wb") as f:
                                        f.write(code_file.getbuffer())
                                    
                                    # 更新项目数据
                                    for p in projects:
                                        if p['id'] == project['id']:
                                            if 'student_codes' not in p:
                                                p['student_codes'] = []
                                            
                                            code_data = {
                                                "id": code_id,
                                                "filename": code_filename,
                                                "original_name": code_file.name,
                                                "size": f"{code_file.size/1024:.1f}KB" if code_file.size < 1024*1024 else f"{code_file.size/(1024*1024):.1f}MB",
                                                "type": code_ext,
                                                "uploader": st.session_state.username,
                                                "description": code_description,
                                                "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            }
                                            
                                            p['student_codes'].append(code_data)
                                            p['updated_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            break
                                    
                                    save_projects(projects)
                                    
                                    st.success("✅ 代码上传成功！")
                                    st.balloons()
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"上传失败: {str(e)}")
                
                st.markdown("---")
    
    with student_tab2:
        st.markdown("#### 💻 我上传的代码")
        
        # 查找当前学生上传的代码
        student_codes = []
        for project in projects:
            if 'student_codes' in project:
                for code in project['student_codes']:
                    if code['uploader'] == st.session_state.username:
                        code['project_name'] = project['name']
                        code['project_id'] = project['id']
                        student_codes.append(code)
        
        if not student_codes:
            st.info("📭 您还没有上传过代码")
        else:
            # 按上传时间排序
            student_codes.sort(key=lambda x: x['upload_time'], reverse=True)
            
            for code in student_codes:
                # 在页面开头添加自定义CSS
                st.markdown("""
                    <style>
                    .file-card {
                        padding: 15px;
                        border-radius: 10px;
                        border: 1px solid #e5e7eb;
                        margin: 10px 0;
                        background-color: white;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                        }
                    .file-card h5 {
                       margin: 0 0 10px 0;
                        color: #1f2937;
                    }
                    .file-card p {
                        margin: 5px 0;
                        color: #6b7280;
                        font-size: 0.9rem;
    }
                    </style>
                """, unsafe_allow_html=True)

                # 然后在需要的地方
                st.markdown(f"""
                    <div class='file-card'>
                        <h5>📝 {code['original_name']}</h5>
                        <p><strong>所属项目:</strong> {code['project_name']}</p>
                        <p><strong>上传时间:</strong> {code['upload_time']} | <strong>文件大小:</strong> {code['size']}</p>
                        {f'<p><strong>说明:</strong> {code["description"]}</p>' if code.get('description') else ''}
                    </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # 下载代码
                    code_path = os.path.join(PROJECTS_DIR, code['project_id'], "student_codes", code['filename'])
                    if os.path.exists(code_path):
                        with open(code_path, "rb") as f:
                            code_data = f.read()
                        
                        st.download_button(
                            label="📥 下载代码",
                            data=code_data,
                            file_name=code['original_name'],
                            mime="application/octet-stream",
                            key=f"download_my_code_{code['id']}",
                            use_container_width=True
                        )
                
                with col2:
                    # 删除代码（仅上传者可删除）
                    if st.button("🗑️ 删除", key=f"delete_my_code_{code['id']}", use_container_width=True, type="secondary"):
                        try:
                            # 删除文件
                            if os.path.exists(code_path):
                                os.remove(code_path)
                            
                            # 从项目数据中移除
                            for project in projects:
                                if project['id'] == code['project_id'] and 'student_codes' in project:
                                    project['student_codes'] = [c for c in project['student_codes'] if c['id'] != code['id']]
                                    break
                            
                            save_projects(projects)
                            st.success("✅ 代码已删除")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"删除失败: {str(e)}")
                
                st.markdown("---")

# ================== 重新设计的在线实践工具页面 ==================

def render_online_tools():
    """渲染在线实践工具页面"""
    st.markdown('<div class="section-title">🛠️ 在线实践工具</div>', unsafe_allow_html=True)
    
    # 创建工具标签页
    tool_tab1, tool_tab2 = st.tabs(["🔍 边缘检测工具", "🔄 图像滤波工具"])
    
    with tool_tab1:
        st.markdown("""
        <div class='resource-card tool'>
            <h3>🔍 边缘检测工具</h3>
            <p>使用不同的边缘检测算子提取图像中的边缘信息。</p>
            <div style="margin: 15px 0;">
                <span class="badge yellow">图像处理</span>
                <span class="badge yellow">特征提取</span>
                <span class="badge yellow">实时处理</span>
            </div>
            <p><strong>支持的算子：</strong></p>
            <ul>
                <li><strong>Roberts算子：</strong>简单的2×2算子，对噪声敏感</li>
                <li><strong>Sobel算子：</strong>经典的3×3算子，具有平滑效果</li>
                <li><strong>Prewitt算子：</strong>类似Sobel，但权值不同</li>
                <li><strong>Laplacian算子：</strong>二阶微分算子，能检测过零点</li>
                <li><strong>LoG算子：</strong>高斯-拉普拉斯算子，抗噪性强</li>
                <li><strong>Canny算子：</strong>多阶段边缘检测算法</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 边缘检测工具界面 - 使用三列布局
        col1, col2, col3 = st.columns([1, 1.2, 0.8])
        
        with col1:
            # 控制面板
            st.markdown("### ⚙️ 参数设置")
            
            # 上传图像
            uploaded_file = st.file_uploader(
                "上传图像", 
                type=["jpg", "jpeg", "png", "bmp"],
                key="edge_uploader",
                help="支持JPG、PNG、BMP格式的图像文件"
            )
            
            if uploaded_file is not None:
                # 图像预览
                image = Image.open(uploaded_file)
                st.image(image, caption="📷 上传的图像预览", use_container_width=True)
                
                # 参数设置
                operator = st.selectbox(
                    "选择边缘检测算子",
                    ["Roberts", "Sobel", "Prewitt", "Laplacian", "LoG", "Canny"],
                    key="edge_operator_select",
                    help="不同的算子适用于不同的场景"
                )
                
                # 算子说明
                operator_descriptions = {
                    "Roberts": "简单的2×2算子，计算速度快但对噪声敏感",
                    "Sobel": "经典的3×3算子，具有平滑效果，常用",
                    "Prewitt": "类似Sobel，权值不同，边缘定位准确",
                    "Laplacian": "二阶微分算子，能检测过零点",
                    "LoG": "高斯-拉普拉斯算子，抗噪性强但计算复杂",
                    "Canny": "多阶段算法，包含高斯平滑、梯度计算、非极大值抑制和双阈值检测"
                }
                st.info(f"**{operator}算子：** {operator_descriptions[operator]}")
                
                # 算子参数设置区域
                st.markdown("#### 🔧 算子参数")
                
                # 初始化参数字典
                edge_params = {}
                
                # 通用参数：边缘强度阈值
                edge_threshold = st.slider(
                    "边缘强度阈值",
                    min_value=0,
                    max_value=255,
                    value=30,
                    key="edge_threshold_slider",
                    help="值越大，检测到的边缘越少"
                )
                edge_params['threshold'] = edge_threshold
                
                # 根据选择的算子显示不同的参数控制
                if operator in ["Sobel", "Prewitt"]:
                    # Sobel和Prewitt的核大小
                    kernel_size = st.selectbox(
                        "核大小",
                        [3, 5, 7],
                        index=0,
                        key=f"{operator.lower()}_kernel_select",
                        help="核大小越大，检测的边缘越粗，但计算量也越大"
                    )
                    edge_params['kernel_size'] = kernel_size
                    
                    # 是否显示梯度方向
                    show_direction = st.checkbox("显示梯度方向图", value=False, 
                                                 key=f"{operator.lower()}_direction_check")
                    edge_params['show_direction'] = show_direction
                    
                elif operator == "LoG":
                    # LoG的高斯核大小
                    log_kernel = st.slider(
                        "高斯核大小",
                        min_value=3,
                        max_value=15,
                        value=5,
                        step=2,
                        key="log_kernel_slider",
                        help="高斯核的大小，必须是奇数"
                    )
                    edge_params['log_kernel'] = log_kernel
                    
                    # LoG的标准差
                    log_sigma = st.slider(
                        "高斯标准差 (σ)",
                        min_value=0.5,
                        max_value=5.0,
                        value=1.0,
                        step=0.1,
                        key="log_sigma_slider",
                        help="σ值越大，平滑效果越强"
                    )
                    edge_params['sigma'] = log_sigma
                    
                elif operator == "Laplacian":
                    # Laplacian的核大小
                    laplacian_kernel = st.selectbox(
                        "核大小",
                        [3, 5],
                        index=0,
                        key="laplacian_kernel_select",
                        help="Laplacian算子的核大小"
                    )
                    edge_params['kernel_size'] = laplacian_kernel
                    
                elif operator == "Canny":
                    # Canny算子的阈值
                    col_th1, col_th2 = st.columns(2)
                    with col_th1:
                        canny_threshold1 = st.slider(
                            "低阈值",
                            min_value=0,
                            max_value=255,
                            value=50,
                            key="canny_threshold1_slider",
                            help="低于此阈值的边缘将被丢弃"
                        )
                    with col_th2:
                        canny_threshold2 = st.slider(
                            "高阈值",
                            min_value=0,
                            max_value=255,
                            value=150,
                            key="canny_threshold2_slider",
                            help="高于此阈值的边缘将被保留为强边缘"
                        )
                    edge_params['threshold1'] = canny_threshold1
                    edge_params['threshold2'] = canny_threshold2
                    
                    # Canny的高斯核大小（用于平滑）
                    canny_blur_kernel = st.slider(
                        "高斯平滑核大小",
                        min_value=3,
                        max_value=9,
                        value=5,
                        step=2,
                        key="canny_blur_slider",
                        help="Canny算法中高斯平滑的核大小"
                    )
                    edge_params['blur_kernel'] = canny_blur_kernel
                
                # 添加噪声选项（用于演示）
                add_noise = st.checkbox("添加随机噪声（用于演示）", value=False, key="edge_noise_check")
                noise_level = 0
                if add_noise:
                    noise_level = st.slider("噪声强度", 10, 50, 20, key="edge_noise_level_slider")
                    edge_params['noise_level'] = noise_level
                
                # 处理按钮
                if st.button("🚀 执行边缘检测", key="edge_detect_btn", type="primary", use_container_width=True):
                    try:
                        # 转换图像为numpy数组
                        image_np = np.array(image)
                        
                        # 灰度处理
                        gray = None
                        if len(image_np.shape) == 3:
                            if image_np.shape[2] == 4:
                                gray = cv2.cvtColor(image_np, cv2.COLOR_RGBA2GRAY)
                            elif image_np.shape[2] == 3:
                                gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
                        else:
                            gray = image_np.copy()
                        
                        # 添加噪声（如果选择了）
                        if add_noise and noise_level > 0:
                            noise = np.random.randint(-noise_level, noise_level, gray.shape)
                            gray = np.clip(gray.astype(np.int16) + noise, 0, 255).astype(np.uint8)
                        
                        # 执行边缘检测
                        with st.spinner(f"正在应用{operator}算子..."):
                            result_dict = apply_edge_detection_with_params(gray, operator, edge_params)
                        
                        # 保存结果到session_state
                        st.session_state['edge_original'] = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR) if len(image_np.shape) == 3 else image_np
                        st.session_state['edge_gray'] = gray
                        st.session_state['edge_result'] = result_dict['edges']
                        st.session_state['edge_operator'] = operator
                        st.session_state['edge_params'] = edge_params
                        
                        if 'grad_x' in result_dict:
                            st.session_state['edge_grad_x'] = result_dict['grad_x']
                        if 'grad_y' in result_dict:
                            st.session_state['edge_grad_y'] = result_dict['grad_y']
                        if 'direction' in result_dict:
                            st.session_state['edge_direction'] = result_dict['direction']
                        
                        # 计算边缘强度分布
                        edges = result_dict['edges']
                        st.session_state['edge_hist'] = np.histogram(edges.flatten(), bins=50, range=(0, 255))[0]
                        
                        st.success(f"✅ {operator}边缘检测完成！")
                        
                    except Exception as e:
                        st.error(f"边缘检测失败: {str(e)}")
                        st.exception(e)
            
            else:
                st.info("👆 请先上传图像文件")
                
                # 示例图像
                if st.button("📸 使用示例图像", key="edge_example_btn", use_container_width=True):
                    # 创建示例图像（带有不同边缘的测试图案）
                    example_img = np.zeros((300, 400), dtype=np.uint8)
                    
                    # 添加不同方向的边缘
                    cv2.rectangle(example_img, (100, 50), (150, 100), 255, -1)  # 方形边缘
                    cv2.rectangle(example_img, (200, 150), (250, 200), 128, -1)  # 较弱的边缘
                    
                    # 添加对角线边缘
                    for i in range(100, 200):
                        example_img[i, i] = 255
                        example_img[i, 400-i] = 255
                    
                    # 添加圆形边缘
                    cv2.circle(example_img, (300, 100), 30, 200, -1)
                    
                    # 添加高斯模糊模拟真实图像
                    example_img = cv2.GaussianBlur(example_img, (3, 3), 1)
                    
                    # 保存到session_state
                    st.session_state['edge_original'] = cv2.cvtColor(example_img, cv2.COLOR_GRAY2BGR)
                    st.session_state['edge_gray'] = example_img
                    
                    # 应用Sobel算子作为示例
                    params = {'threshold': 30, 'kernel_size': 3}
                    result_dict = apply_edge_detection_with_params(example_img, "Sobel", params)
                    st.session_state['edge_result'] = result_dict['edges']
                    st.session_state['edge_operator'] = "Sobel"
                    st.session_state['edge_params'] = params
                    st.session_state['using_example'] = True
                    
                    # 保存梯度信息
                    st.session_state['edge_grad_x'] = result_dict.get('grad_x', None)
                    st.session_state['edge_grad_y'] = result_dict.get('grad_y', None)
                    
                    st.success("✅ 已加载示例图像")
        
        with col2:
            # 主要结果显示区域
            st.markdown("### 📊 边缘检测结果")
            
            if 'edge_original' in st.session_state and 'edge_result' in st.session_state:
                operator = st.session_state.get('edge_operator', '边缘检测')
                params = st.session_state.get('edge_params', {})
                
                # 显示原始图像和处理结果对比
                if 'edge_gray' in st.session_state:
                    # 显示灰度图和边缘图对比
                    col_gray, col_edge = st.columns(2)
                    
                    with col_gray:
                        gray_img = st.session_state['edge_gray']
                        if len(gray_img.shape) == 2:
                            st.image(gray_img, caption="🎨 灰度图像", use_container_width=True, 
                                    clamp=True, channels="GRAY")
                        else:
                            st.image(gray_img, caption="🎨 灰度图像", use_container_width=True)
                    
                    with col_edge:
                        edge_img = st.session_state['edge_result']
                        if len(edge_img.shape) == 2:
                            st.image(edge_img, caption=f"🔍 {operator}边缘检测", 
                                    use_container_width=True, clamp=True, channels="GRAY")
                        else:
                            st.image(edge_img, caption=f"🔍 {operator}边缘检测", 
                                    use_container_width=True)
                
                # 显示梯度分量（对于Sobel/Prewitt算子）
                if operator in ["Sobel", "Prewitt"] and 'edge_grad_x' in st.session_state:
                    st.markdown("#### 📐 梯度分量")
                    col_gx, col_gy = st.columns(2)
                    
                    with col_gx:
                        grad_x = st.session_state['edge_grad_x']
                        # 归一化显示
                        grad_x_norm = cv2.normalize(np.abs(grad_x), None, 0, 255, cv2.NORM_MINMAX)
                        st.image(grad_x_norm.astype(np.uint8), caption="X方向梯度 (Gx)", 
                                use_container_width=True, clamp=True, channels="GRAY")
                    
                    with col_gy:
                        grad_y = st.session_state['edge_grad_y']
                        # 归一化显示
                        grad_y_norm = cv2.normalize(np.abs(grad_y), None, 0, 255, cv2.NORM_MINMAX)
                        st.image(grad_y_norm.astype(np.uint8), caption="Y方向梯度 (Gy)", 
                                use_container_width=True, clamp=True, channels="GRAY")
                
                # 显示梯度方向图（如果启用了）
                if operator in ["Sobel", "Prewitt"] and params.get('show_direction', False) and 'edge_direction' in st.session_state:
                    st.markdown("#### 🧭 梯度方向可视化")
                    
                    direction_img = st.session_state['edge_direction']
                    edge_strength = st.session_state['edge_result']
                    
                    # 创建方向彩色图
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
                    
                    # 左图：方向分布直方图
                    angles_deg = np.degrees(direction_img.flatten())
                    ax1.hist(angles_deg, bins=36, range=(0, 360), alpha=0.7, color='skyblue', edgecolor='black')
                    ax1.set_xlabel('梯度方向 (度)')
                    ax1.set_ylabel('像素数量')
                    ax1.set_title('梯度方向分布')
                    ax1.grid(True, alpha=0.3)
                    ax1.set_xlim(0, 360)
                    
                    # 右图：方向彩色图
                    hsv = np.zeros((direction_img.shape[0], direction_img.shape[1], 3), dtype=np.uint8)
                    hsv[..., 0] = ((direction_img + np.pi) * 180 / (2 * np.pi)).astype(np.uint8)  # 0-180度
                    hsv[..., 1] = 200
                    hsv[..., 2] = np.clip(edge_strength, 50, 255).astype(np.uint8)
                    
                    direction_color = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
                    ax2.imshow(direction_color)
                    ax2.set_title('梯度方向彩色图')
                    ax2.axis('off')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # 添加方向图例
                    st.markdown("""
                    <div style='text-align: center; margin: 10px 0;'>
                        <div style='background: linear-gradient(90deg, red, yellow, lime, cyan, blue, magenta, red); 
                                    height: 20px; border-radius: 10px;'></div>
                        <p style='font-size: 0.8em; color: #666;'>
                        方向图例：0°(红) → 45°(黄) → 90°(绿) → 135°(青) → 180°(蓝) → 225°(品红) → 270°(红)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col3:
            # 详细分析和统计区域
            st.markdown("### 🔬 详细分析")
            
            if 'edge_original' in st.session_state and 'edge_result' in st.session_state:
                operator = st.session_state.get('edge_operator', '')
                params = st.session_state.get('edge_params', {})
                
                # 显示参数设置
                st.markdown("#### 📝 参数设置")
                param_text = f"""
                **算子:** {operator}  
                **边缘阈值:** {params.get('threshold', 30)}
                """
                
                if operator in ["Sobel", "Prewitt"]:
                    param_text += f"  \n**核大小:** {params.get('kernel_size', 3)}×{params.get('kernel_size', 3)}"
                elif operator == "LoG":
                    param_text += f"  \n**高斯核:** {params.get('log_kernel', 5)}×{params.get('log_kernel', 5)}"
                    param_text += f"  \n**标准差σ:** {params.get('sigma', 1.0)}"
                elif operator == "Laplacian":
                    param_text += f"  \n**核大小:** {params.get('kernel_size', 3)}×{params.get('kernel_size', 3)}"
                elif operator == "Canny":
                    param_text += f"  \n**低阈值:** {params.get('threshold1', 50)}"
                    param_text += f"  \n**高阈值:** {params.get('threshold2', 150)}"
                    param_text += f"  \n**平滑核:** {params.get('blur_kernel', 5)}×{params.get('blur_kernel', 5)}"
                
                if params.get('noise_level', 0) > 0:
                    param_text += f"  \n**添加噪声:** {params.get('noise_level', 0)}"
                
                st.info(param_text)
                
                # 边缘统计信息
                st.markdown("#### 📈 边缘统计")
                
                edge_result = st.session_state['edge_result']
                edge_threshold = params.get('threshold', 30)
                
                # 计算统计信息
                edge_pixels = np.sum(edge_result > edge_threshold)
                total_pixels = edge_result.shape[0] * edge_result.shape[1]
                edge_ratio = (edge_pixels / total_pixels) * 100
                
                # 边缘强度统计
                edge_strength_mean = np.mean(edge_result)
                edge_strength_std = np.std(edge_result)
                edge_strength_max = np.max(edge_result)
                edge_strength_min = np.min(edge_result)
                
                # 显示统计指标
                col_stats1, col_stats2 = st.columns(2)
                with col_stats1:
                    st.metric("边缘像素数", f"{edge_pixels:,}")
                    st.metric("平均强度", f"{edge_strength_mean:.1f}")
                with col_stats2:
                    st.metric("边缘占比", f"{edge_ratio:.1f}%")
                    st.metric("强度标准差", f"{edge_strength_std:.1f}")
                
                # 边缘强度直方图
                st.markdown("#### 📊 边缘强度分布")
                
                # 创建直方图
                fig, ax = plt.subplots(figsize=(5, 3))
                n, bins, patches = ax.hist(edge_result.flatten(), bins=50, alpha=0.7, 
                                          color='skyblue', edgecolor='black')
                
                # 标记阈值
                threshold = params.get('threshold', 30)
                ax.axvline(x=threshold, color='red', linestyle='--', linewidth=2, 
                          label=f'阈值={threshold}')
                
                # 填充超过阈值的区域
                bin_centers = 0.5 * (bins[:-1] + bins[1:])
                over_threshold = bin_centers > threshold
                for patch, over in zip(patches, over_threshold):
                    if over:
                        patch.set_facecolor('lightcoral')
                        patch.set_alpha(0.8)
                
                ax.set_xlabel('边缘强度')
                ax.set_ylabel('像素数量')
                ax.set_title('边缘强度直方图')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                st.pyplot(fig)
                
                # 下载按钮
                st.markdown("---")
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    # 下载原始图像
                    original_filename = "original_image.jpg"
                    st.markdown(get_image_download_link(
                        st.session_state['edge_original'],
                        original_filename,
                        "📥 原始图像"
                    ), unsafe_allow_html=True)
                
                with col_dl2:
                    # 下载处理结果
                    result_filename = f"edge_detection_{operator}.jpg"
                    st.markdown(get_image_download_link(
                        st.session_state['edge_result'],
                        result_filename,
                        "📥 边缘结果"
                    ), unsafe_allow_html=True)
                
                # 额外下载梯度图
                if operator in ["Sobel", "Prewitt"] and 'edge_grad_x' in st.session_state:
                    st.markdown(get_image_download_link(
                        cv2.normalize(np.abs(st.session_state['edge_grad_x']), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
                        f"gradient_x_{operator}.jpg",
                        "📥 X方向梯度"
                    ), unsafe_allow_html=True)
            
            else:
                st.info("👈 请先在左侧上传图像并点击处理按钮")
                
                # 显示算子比较说明
                st.markdown("""
                <div style='background: linear-gradient(135deg, #e0f2fe, #bae6fd); 
                            padding: 15px; border-radius: 10px; margin-top: 20px;'>
                    <h4>🔍 各算子特点对比</h4>
                    <table style="width:100%; font-size:0.85em; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #4b5563; color: white;">
                                <th style="padding: 8px; text-align: left;">算子</th>
                                <th style="padding: 8px; text-align: left;">优点</th>
                                <th style="padding: 8px; text-align: left;">缺点</th>
                                <th style="padding: 8px; text-align: left;">适用场景</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 8px;"><strong>Roberts</strong></td>
                                <td style="padding: 8px;">计算简单快速</td>
                                <td style="padding: 8px;">对噪声敏感</td>
                                <td style="padding: 8px;">实时应用</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 8px;"><strong>Sobel</strong></td>
                                <td style="padding: 8px;">抗噪声较好</td>
                                <td style="padding: 8px;">边缘较粗</td>
                                <td style="padding: 8px;">一般应用</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 8px;"><strong>Prewitt</strong></td>
                                <td style="padding: 8px;">边缘定位准确</td>
                                <td style="padding: 8px;">抗噪声一般</td>
                                <td style="padding: 8px;">精确边缘</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 8px;"><strong>Laplacian</strong></td>
                                <td style="padding: 8px;">检测过零点</td>
                                <td style="padding: 8px;">对噪声敏感</td>
                                <td style="padding: 8px;">精细边缘</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 8px;"><strong>LoG</strong></td>
                                <td style="padding: 8px;">抗噪性强</td>
                                <td style="padding: 8px;">计算复杂</td>
                                <td style="padding: 8px;">高质量检测</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px;"><strong>Canny</strong></td>
                                <td style="padding: 8px;">精度高，抗噪</td>
                                <td style="padding: 8px;">计算复杂</td>
                                <td style="padding: 8px;">高精度应用</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)
    
    # 工具标签页2的代码保持不变   
    with tool_tab2:
        st.markdown("""
        <div class='resource-card tool'>
            <h3>🔄 图像滤波工具</h3>
            <p>使用不同的滤波器对图像进行平滑处理或降噪。</p>
            <div style="margin: 15px 0;">
                <span class="badge yellow">图像增强</span>
                <span class="badge yellow">噪声消除</span>
                <span class="badge yellow">平滑处理</span>
            </div>
            <p><strong>支持的滤波器：</strong></p>
            <ul>
                <li><strong>中值滤波：</strong>非线性滤波器，有效去除椒盐噪声</li>
                <li><strong>均值滤波：</strong>线性滤波器，简单的平滑处理</li>
                <li><strong>高斯滤波：</strong>线性滤波器，保留边缘的平滑</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 图像滤波工具界面
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # 控制面板
            st.markdown("### ⚙️ 参数设置")
            
            # 上传图像
            uploaded_file = st.file_uploader(
                "上传图像", 
                type=["jpg", "jpeg", "png", "bmp"],
                key="filter_uploader",
                help="支持JPG、PNG、BMP格式的图像文件"
            )
            
            if uploaded_file is not None:
                # 图像预览
                image = Image.open(uploaded_file)
                st.image(image, caption="📷 上传的图像预览", use_container_width=True)
                
                # 滤波器类型选择
                filter_type = st.selectbox(
                    "选择滤波器类型",
                    ["中值滤波", "均值滤波", "高斯滤波"],
                    key="filter_type_select",
                    help="不同类型的滤波器有不同的应用场景"
                )
                
                # 滤波器说明
                filter_descriptions = {
                    "中值滤波": "非线性滤波器，用邻域中值替代中心像素，有效去除椒盐噪声",
                    "均值滤波": "线性滤波器，用邻域均值替代中心像素，简单平滑",
                    "高斯滤波": "线性滤波器，用高斯权重计算邻域加权均值，保留边缘"
                }
                st.info(f"**{filter_type}：** {filter_descriptions[filter_type]}")
                
                # 核大小选择
                kernel_size = st.slider(
                    "核大小",
                    min_value=3,
                    max_value=15,
                    value=5,
                    step=2,
                    key="kernel_size_slider",
                    help="核大小必须是奇数，值越大平滑效果越强"
                )
                
                # 显示核大小说明
                if kernel_size == 3:
                    st.caption("小核：轻微平滑，保留细节")
                elif kernel_size == 5:
                    st.caption("中等核：适中平滑，平衡细节与降噪")
                elif kernel_size == 7:
                    st.caption("大核：强平滑，可能模糊细节")
                else:
                    st.caption("超大核：极强平滑，适用于严重噪声")
                
                # 添加噪声选项（用于演示）
                add_noise = st.checkbox("添加随机噪声（用于演示）", value=False)
                noise_level = 0
                if add_noise:
                    noise_level = st.slider("噪声强度", 10, 50, 20, key="noise_level")
                
                # 处理按钮
                if st.button("🚀 执行滤波处理", key="filter_btn", use_container_width=True):
                    try:
                        # 转换图像为numpy数组
                        image_np = np.array(image)
                        
                        # 确保是3通道图像
                        if len(image_np.shape) == 2:
                            # 灰度图转BGR
                            image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)
                        elif image_np.shape[2] == 4:
                            # RGBA转BGR
                            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)
                        elif image_np.shape[2] == 3:
                            # RGB转BGR
                            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                        
                        # 添加噪声（如果选择了）
                        noisy_img = image_np.copy()
                        if add_noise and noise_level > 0:
                            noise = np.random.randint(-noise_level, noise_level, image_np.shape)
                            noisy_img = np.clip(image_np.astype(np.int16) + noise, 0, 255).astype(np.uint8)
                        
                        # 执行滤波处理
                        with st.spinner(f"正在应用{filter_type}..."):
                            filter_result = apply_filter(noisy_img, filter_type, kernel_size)
                        
                        # 保存结果到session_state
                        st.session_state['filter_original'] = image_np
                        st.session_state['filter_noisy'] = noisy_img if add_noise else None
                        st.session_state['filter_result'] = filter_result
                        st.session_state['filter_type'] = filter_type
                        st.session_state['filter_kernel'] = kernel_size
                        
                        st.success(f"✅ {filter_type}完成！")
                        
                    except Exception as e:
                        st.error(f"滤波处理失败: {str(e)}")
            
            else:
                st.info("👆 请先上传图像文件")
                
                # 示例图像
                if st.button("📸 使用示例图像", key="filter_example_btn", use_container_width=True):
                    # 创建示例图像（带纹理的渐变）
                    example_img = np.zeros((200, 300, 3), dtype=np.uint8)
                    
                    # 创建渐变
                    for i in range(3):
                        example_img[:, :, i] = np.linspace(0, 255, 300).astype(np.uint8)
                    
                    # 添加一些纹理
                    example_img = example_img.astype(np.float32)
                    example_img += np.random.randn(200, 300, 3) * 30
                    example_img = np.clip(example_img, 0, 255).astype(np.uint8)
                    
                    # 保存到session_state
                    st.session_state['filter_original'] = example_img
                    st.session_state['filter_result'] = apply_filter(example_img, "高斯滤波", 5)
                    st.session_state['filter_type'] = "高斯滤波"
                    st.session_state['filter_kernel'] = 5
                    st.session_state['using_example_filter'] = True
                    
                    st.success("✅ 已加载示例图像")
        
        with col2:
            # 结果显示区域
            st.markdown("### 📊 处理结果")
            
            if 'filter_original' in st.session_state and 'filter_result' in st.session_state:
                # 显示对比结果
                filter_type = st.session_state.get('filter_type', '滤波')
                kernel_size = st.session_state.get('filter_kernel', 3)
                
                # 如果有噪声图像，显示噪声图像和滤波结果对比
                if 'filter_noisy' in st.session_state and st.session_state['filter_noisy'] is not None:
                    # 显示噪声图像和滤波结果
                    col_noisy, col_filtered = st.columns(2)
                    
                    with col_noisy:
                        noisy_img = st.session_state['filter_noisy']
                        if len(noisy_img.shape) == 3:
                            display_noisy = cv2.cvtColor(noisy_img, cv2.COLOR_BGR2RGB)
                        else:
                            display_noisy = noisy_img
                        st.image(display_noisy, caption="📈 添加噪声后的图像", use_container_width=True)
                    
                    with col_filtered:
                        filter_img = st.session_state['filter_result']
                        if len(filter_img.shape) == 3:
                            display_filtered = cv2.cvtColor(filter_img, cv2.COLOR_BGR2RGB)
                        else:
                            display_filtered = filter_img
                        st.image(display_filtered, 
                                caption=f"✨ {filter_type}结果 ({kernel_size}×{kernel_size})", 
                                use_container_width=True)
                
                else:
                    # 显示原始图像和滤波结果对比
                    display_image_comparison(
                        st.session_state['filter_original'],
                        st.session_state['filter_result'],
                        original_title="原始图像",
                        processed_title=f"{filter_type}结果 ({kernel_size}×{kernel_size})"
                    )
                
                # 下载按钮
                col_a, col_b = st.columns(2)
                with col_a:
                    # 下载原始图像
                    original_filename = "original_image.jpg"
                    st.markdown(get_image_download_link(
                        st.session_state['filter_original'],
                        original_filename,
                        "📥 下载原始图像"
                    ), unsafe_allow_html=True)
                
                with col_b:
                    # 下载处理结果
                    result_filename = f"filter_{filter_type}_{kernel_size}x{kernel_size}.jpg"
                    st.markdown(get_image_download_link(
                        st.session_state['filter_result'],
                        result_filename,
                        "📥 下载处理结果"
                    ), unsafe_allow_html=True)
                
                # 技术指标
                st.markdown("### 📈 技术指标")
                col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
                
                with col_metrics1:
                    original_img = st.session_state['filter_original']
                    result_img = st.session_state['filter_result']
                    
                    # 计算PSNR（峰值信噪比）
                    if original_img.shape == result_img.shape:
                        mse = np.mean((original_img.astype(float) - result_img.astype(float)) ** 2)
                        if mse == 0:
                            psnr = 99.99
                        else:
                            psnr = 20 * np.log10(255.0 / np.sqrt(mse))
                        st.metric("PSNR", f"{psnr:.2f} dB")
                    else:
                        st.metric("图像尺寸", "不匹配")
                
                with col_metrics2:
                    # 计算平滑度
                    original_grad = np.gradient(original_img.astype(float))
                    result_grad = np.gradient(result_img.astype(float))
                    
                    original_var = np.var(original_grad[0]) + np.var(original_grad[1])
                    result_var = np.var(result_grad[0]) + np.var(result_grad[1])
                    
                    smoothness = ((original_var - result_var) / original_var) * 100
                    st.metric("平滑度提升", f"{smoothness:.1f}%")
                
                with col_metrics3:
                    # 计算处理时间（模拟）
                    processing_time = kernel_size * 0.5 + 0.1
                    st.metric("估计处理时间", f"{processing_time:.1f} ms")
            
            else:
                st.info("👈 请先在左侧上传图像并点击处理按钮")
                
                # 显示示例说明
                st.markdown("""
                <div style='background: linear-gradient(135deg, #fef3c7, #fde68a); 
                            padding: 20px; border-radius: 12px; margin-top: 20px;'>
                    <h4>💡 使用说明</h4>
                    <ol>
                        <li>在左侧上传或选择一张图像</li>
                        <li>选择滤波器类型和核大小</li>
                        <li>可以选择添加噪声以观察滤波效果</li>
                        <li>点击"执行滤波处理"按钮</li>
                        <li>查看并比较处理前后的图像</li>
                        <li>可以下载处理结果</li>
                    </ol>
                    <p><strong>教学提示：</strong>不同滤波器和核大小对图像平滑效果的影响，
                    尝试调整参数观察效果变化。</p>
                </div>
                """, unsafe_allow_html=True)     

def apply_edge_detection_with_params(image, operator, params):
    """
    应用带参数的边缘检测算子
    """
    # 确保输入是灰度图
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    threshold = params.get('threshold', 30)
    result_dict = {}
    
    try:
        if operator == "Roberts":
            # Roberts算子 - 固定2×2
            kernel_x = np.array([[1, 0], [0, -1]])
            kernel_y = np.array([[0, 1], [-1, 0]])
            roberts_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
            roberts_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)
            edges = np.sqrt(roberts_x**2 + roberts_y**2)
            edges = np.clip(edges, 0, 255).astype(np.uint8)
            result_dict['edges'] = edges
            result_dict['grad_x'] = roberts_x
            result_dict['grad_y'] = roberts_y
        
        elif operator == "Sobel":
            # Sobel算子
            kernel_size = params.get('kernel_size', 3)
            sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=kernel_size)
            sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=kernel_size)
            edges = cv2.magnitude(sobelx, sobely)
            edges = np.clip(edges, 0, 255).astype(np.uint8)
            result_dict['edges'] = edges
            result_dict['grad_x'] = sobelx
            result_dict['grad_y'] = sobely
            
            # 计算梯度方向
            if params.get('show_direction', False):
                with np.errstate(divide='ignore', invalid='ignore'):
                    direction = np.arctan2(sobely, sobelx)
                    direction = np.nan_to_num(direction, nan=0.0)
                result_dict['direction'] = direction
        
        elif operator == "Prewitt":
            # Prewitt算子
            kernel_size = 3  # Prewitt通常是3×3
            kernel_x = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
            kernel_y = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
            prewitt_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
            prewitt_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)
            edges = cv2.magnitude(prewitt_x, prewitt_y)
            edges = np.clip(edges, 0, 255).astype(np.uint8)
            result_dict['edges'] = edges
            result_dict['grad_x'] = prewitt_x
            result_dict['grad_y'] = prewitt_y
            
            # 计算梯度方向
            if params.get('show_direction', False):
                with np.errstate(divide='ignore', invalid='ignore'):
                    direction = np.arctan2(prewitt_y, prewitt_x)
                    direction = np.nan_to_num(direction, nan=0.0)
                result_dict['direction'] = direction
        
        elif operator == "Laplacian":
            # Laplacian算子
            kernel_size = params.get('kernel_size', 3)
            # 根据核大小选择适当的Laplacian
            if kernel_size == 3:
                edges = cv2.Laplacian(image, cv2.CV_64F, ksize=3)
            else:
                edges = cv2.Laplacian(image, cv2.CV_64F, ksize=5)
            edges = np.abs(edges)
            edges = np.clip(edges, 0, 255).astype(np.uint8)
            result_dict['edges'] = edges
        
        elif operator == "LoG":
            # LoG算子（高斯-拉普拉斯）
            kernel_size = params.get('log_kernel', 5)
            sigma = params.get('sigma', 1.0)
            blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
            edges = cv2.Laplacian(blurred, cv2.CV_64F)
            edges = np.abs(edges)
            edges = np.clip(edges, 0, 255).astype(np.uint8)
            result_dict['edges'] = edges
        
        elif operator == "Canny":
            # Canny算子
            threshold1 = params.get('threshold1', 50)
            threshold2 = params.get('threshold2', 150)
            blur_kernel = params.get('blur_kernel', 5)
            
            # 先进行高斯平滑
            blurred = cv2.GaussianBlur(image, (blur_kernel, blur_kernel), 0)
            edges = cv2.Canny(blurred, threshold1, threshold2)
            result_dict['edges'] = edges
        
        else:
            result_dict['edges'] = image
        
        # 应用阈值（对于非Canny算子）
        if operator != "Canny":
            edges = result_dict['edges']
            # 创建二值化边缘图
            _, binary_edges = cv2.threshold(edges, threshold, 255, cv2.THRESH_BINARY)
            result_dict['edges'] = binary_edges
    
    except Exception as e:
        st.error(f"应用{operator}算子时出错: {str(e)}")
        # 返回原始图像作为fallback
        result_dict['edges'] = image
    
    return result_dict

# 主页面内容
def main():
    # 应用CSS样式
    apply_modern_css()

    # 页面标题
    st.markdown("""
    <div class='modern-header'>
        <h1>📚 学习资源中心</h1>
        <p class='subtitle'>🇨🇳 思政教育与专业技术融合学习平台 · 培养德才兼备的新时代技术人才</p>
    </div>
    """, unsafe_allow_html=True)

    # 渲染侧边栏
    render_sidebar()

    # 使用标签页组织内容
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🇨🇳 思政资源", "🔬 技术资源", "🛠️ 在线实践工具", "📤 资源上传", "🏗️ 实践项目库", "💾 资源下载"])

    with tab1:
        st.markdown('<div class="section-title">🇨🇳 思政教育资源</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                st.markdown("""
                <div class='resource-card'>
                    <h3>🎯 《数字图像处理中的工匠精神》</h3>
                    <p>深入探讨如何在图像处理技术中培养和践行精益求精的工匠精神。</p>
                    <div style="margin: 15px 0;">
                        <span class="badge">工匠精神</span>
                        <span class="badge">技术伦理</span>
                        <span class="badge">职业素养</span>
                    </div>
                    <ul>
                        <li>工匠精神的内涵与时代价值</li>
                        <li>图像处理中的精度追求</li>
                        <li>典型案例分析</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                button_html = create_link_button(
                    "https://www.sxjrzyxy.edu.cn/Article.aspx?ID=33094&Mid=869", 
                    "开始学习"
                )
                st.markdown(button_html, unsafe_allow_html=True)

        with col2:
            with st.container():
                st.markdown("""
                <div class='resource-card'>
                    <h3>🔬 《科技报国：中国科学家故事》</h3>
                    <p>学习钱学森、袁隆平等科学家的爱国精神和创新事迹。</p>
                    <div style="margin: 15px 0;">
                        <span class="badge">科学家精神</span>
                        <span class="badge">爱国主义</span>
                        <span class="badge">创新精神</span>
                    </div>
                    <ul>
                        <li>科学家成长历程</li>
                        <li>重大科技突破</li>
                        <li>爱国主义教育</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                button_html = create_link_button(
                    "https://www.bilibili.com/video/BV13K4y1a7Xv/", 
                    "开始学习"
                )
                st.markdown(button_html, unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("""
            <div class='resource-card'>
                <h3>📹 工匠精神与技术创新</h3>
                <p>探讨如何在技术实践中培养工匠精神。</p>
                <div style='background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; margin: 15px 0;'>
                    <p>🎬 视频时长: 45分钟</p>
                    <p><em>点击下方按钮观看视频</em></p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            button_html = create_link_button(
                "https://www.bilibili.com/video/BV13DVgzKEoz/", 
                "观看视频"
            )
            st.markdown(button_html, unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div class='resource-card'>
                <h3>💡 科技伦理与责任</h3>
                <p>讨论技术发展中的伦理问题和责任担当。</p>
                <div style='background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; margin: 15px 0;'>
                    <p>🎬 视频时长: 38分钟</p>
                    <p><em>点击下方按钮观看视频</em></p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            button_html = create_link_button(
                "https://www.bilibili.com/video/BV18T4y137Ku/", 
                "观看视频"
            )
            st.markdown(button_html, unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-title">🔬 技术学习资源</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                st.markdown("""
                <div class='resource-card tech'>
                    <h3>📖 OpenCV官方文档</h3>
                    <p>完整的OpenCV库文档和API参考，包含丰富的示例代码。</p>
                    <div style="margin: 15px 0;">
                        <span class="badge blue">OpenCV</span>
                        <span class="badge blue">文档</span>
                        <span class="badge blue">API</span>
                    </div>
                    <ul>
                        <li>图像处理基础</li>
                        <li>计算机视觉算法</li>
                        <li>实战项目案例</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                button_html = create_link_button(
                    "https://woshicver.com/", 
                    "查看文档"
                )
                st.markdown(button_html, unsafe_allow_html=True)

        with col2:
            with st.container():
                st.markdown("""
                <div class='resource-card tech'>
                    <h3>🎓 Python图像处理实战</h3>
                    <p>从基础到高级的Python图像处理教程，包含大量实践项目。</p>
                    <div style="margin: 15px 0;">
                        <span class="badge green">Python</span>
                        <span class="badge green">实战</span>
                        <span class="badge green">项目</span>
                    </div>
                    <ul>
                        <li>NumPy图像处理</li>
                        <li>OpenCV实战</li>
                        <li>项目开发指导</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                button_html = create_link_button(
                    "https://www.bilibili.com/video/BV1Fo4y1d7JL/", 
                    "开始学习"
                )
                st.markdown(button_html, unsafe_allow_html=True)

    with tab3:
        # 在线实践工具页面
        render_online_tools()

    with tab4:
        # 资源上传页面
        render_resource_upload()

    with tab5:
        # 实践项目库页面
        render_project_library()

    with tab6:
        st.markdown('<div class="section-title">💾 学习资源下载</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class='resource-card'>
                <h3>📘 教材与讲义</h3>
                <div style="margin: 15px 0;">
                    <span class="badge">PDF</span>
                    <span class="badge">教程</span>
                    <span class="badge">课件</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            resources = [
                {"name": "《数字图像处理（第三版）》- Gonzalez", "format": "PDF", "size": "15.2MB", "url": "https://wenku.so.com/s?q=%E6%95%B0%E5%AD%97%E5%9B%BE%E5%83%8F%E5%A4%84%E7%90%86(%E7%AC%AC%E4%B8%89%E7%89%88)"},
                {"name": "《OpenCV入门到精通》- 中文教程", "format": "PDF+代码", "size": "8.7MB", "url": "https://github.com/search?q=OpenCV"},
                {"name": "《计算机视觉：算法与应用》", "format": "课件", "size": "12.3MB", "url": "https://www.scidb.cn/s/mqABbi"}
            ]

            for resource in resources:
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"**{resource['name']}**")
                        st.caption(f"{resource['format']} · {resource['size']}")
                    with col_b:
                        button_html = create_link_button(resource['url'], "下载")
                        st.markdown(button_html, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class='resource-card'>
                <h3>📊 数据集资源</h3>
                <div style="margin: 15px 0;">
                    <span class="badge blue">图像集</span>
                    <span class="badge blue">标注数据</span>
                    <span class="badge blue">测试集</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            datasets = [
                {"name": "标准测试图像集（50张）", "format": "JPG", "size": "25.1MB", "url": "https://www.scidb.cn/s/mqABbi"},
                {"name": "医学影像数据集", "format": "DICOM", "size": "156.8MB", "url": "https://www.scidb.cn/s/mqABbi"},
                {"name": "自然场景图像库", "format": "JPG+标注", "size": "89.3MB", "url": "https://www.scidb.cn/s/mqABbi"}
            ]

            for dataset in datasets:
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"**{dataset['name']}**")
                        st.caption(f"{dataset['format']} · {dataset['size']}")
                    with col_b:
                        button_html = create_link_button(dataset['url'], "下载")
                        st.markdown(button_html, unsafe_allow_html=True)

        # 代码资源
        st.markdown("""
        <div class='resource-card'>
            <h3>💻 代码资源库</h3>
            <div style="margin: 15px 0;">
                <span class="badge green">Python</span>
                <span class="badge green">OpenCV</span>
                <span class="badge green">MATLAB</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        code_resources = [
            {"name": "图像处理算法库（Python）", "language": "Python", "size": "4.2MB", "url": "https://github.com/search?q=OpenCV"},
            {"name": "OpenCV实战项目", "language": "C++/Python", "size": "7.8MB", "url": "https://github.com/search?q=OpenCV"},
            {"name": "MATLAB图像处理工具箱", "language": "MATLAB", "size": "3.5MB", "url": "https://github.com/search?q=OpenCV"}
        ]

        for code in code_resources:
            with st.container():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.write(f"**{code['name']}**")
                with col_b:
                    st.caption(f"语言: {code['language']}")
                with col_c:
                    button_html = create_link_button(code['url'], "下载")
                    st.markdown(button_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
