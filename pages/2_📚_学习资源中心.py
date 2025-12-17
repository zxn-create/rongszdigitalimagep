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
    }
    </style>
    """, unsafe_allow_html=True)

# 图像处理工具函数（保持不变）
def apply_edge_detection(image, operator):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if operator == "Roberts":
        kernelx = np.array([[1, 0], [0, -1]])
        kernely = np.array([[0, 1], [-1, 0]])
        robertsx = cv2.filter2D(gray.astype(np.float32), -1, kernelx)
        robertsy = cv2.filter2D(gray.astype(np.float32), -1, kernely)
        edge = cv2.magnitude(robertsx, robertsy).astype(np.uint8)
    elif operator == "Sobel":
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edge = cv2.magnitude(sobelx, sobely).astype(np.uint8)
    elif operator == "Prewitt":
        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        prewittx = cv2.filter2D(gray.astype(np.float32), -1, kernelx)
        prewitty = cv2.filter2D(gray.astype(np.float32), -1, kernely)
        edge = cv2.magnitude(prewittx, prewitty).astype(np.uint8)
    elif operator == "Laplacian":
        edge = cv2.Laplacian(gray, cv2.CV_64F).astype(np.uint8)
    elif operator == "LoG":
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edge = cv2.Laplacian(blurred, cv2.CV_64F).astype(np.uint8)
    
    # 确保返回的是3通道图像用于显示
    if len(edge.shape) == 2:
        edge = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
    return edge

def apply_filter(image, filter_type, kernel_size):
    if image is None or image.size == 0:
        raise ValueError("输入图像无效")
    
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    kernel_size = max(3, min(15, kernel_size))
    
    try:
        if filter_type == "中值滤波":
            filtered = cv2.medianBlur(image, kernel_size)
        elif filter_type == "均值滤波":
            filtered = cv2.blur(image, (kernel_size, kernel_size))
        elif filter_type == "高斯滤波":
            if kernel_size < 1:
                kernel_size = 3
            filtered = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        else:
            filtered = image.copy()
        return filtered
    except Exception as e:
        st.error(f"滤波处理失败: {str(e)}")
        return image.copy()

def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img = Image.fromarray(img)
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/jpeg;base64,{img_str}" download="{filename}" style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; margin-top: 10px;">{text}</a>'
    return href

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
        st.text("版本: v2.1.0")

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
        if st.session_state.role == "管理员":
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
                    

                # 资源卡片 - 修改版本
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
                    if is_owner or st.session_state.role == "管理员":
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🇨🇳 思政资源", "🔬 技术资源", "🛠️ 实践工具", "📤 资源上传", "💾 资源下载"])

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

        # 理论知识部分（保持不变）
        # ... [保持原有的理论知识部分代码不变]

    with tab3:
        st.markdown('<div class="section-title">🛠️ 在线实践工具</div>', unsafe_allow_html=True)

        # 边缘检测工具
        with st.expander("🔍 边缘检测工具", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                uploaded_file = st.file_uploader("上传图像", type=["jpg", "jpeg", "png"], key="edge_detector")
                operator = st.selectbox("选择边缘检测算子", ["Roberts", "Sobel", "Prewitt", "Laplacian", "LoG"],
                                        key="edge_op")

                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    image_np = np.array(image)
                    if len(image_np.shape) == 3:
                        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                    st.image(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB), caption="原始图像", use_container_width=True)

                    if st.button("执行边缘检测", key="edge_btn", use_container_width=True):
                        with st.spinner("正在处理..."):
                            try:
                                result = apply_edge_detection(image_np, operator)
                                st.session_state['edge_result'] = result
                            except Exception as e:
                                st.error(f"处理出错: {str(e)}")

            with col2:
                if uploaded_file is not None and 'edge_result' in st.session_state:
                    display_result = cv2.cvtColor(st.session_state['edge_result'], cv2.COLOR_BGR2RGB)
                    st.image(display_result, caption=f"{operator}边缘检测结果", use_container_width=True)
                    st.markdown(get_image_download_link(
                        st.session_state['edge_result'],
                        f"edge_detection_{operator}.jpg",
                        "📥 下载结果图像"
                    ), unsafe_allow_html=True)
                else:
                    st.info("👆 请上传图像并点击处理按钮")

        # 图像滤波工具
        with st.expander("🔄 图像滤波工具"):
            col1, col2 = st.columns(2)

            with col1:
                uploaded_file = st.file_uploader("上传图像", type=["jpg", "jpeg", "png"], key="filter_upload")
                filter_type = st.selectbox("选择滤波器类型", ["中值滤波", "均值滤波", "高斯滤波"], key="filter_type")
                kernel_size = st.slider("核大小", 3, 15, 3, 2, key="kernel_size")

                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    image_np = np.array(image)
                    if len(image_np.shape) == 3:
                        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                    st.image(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB), caption="原始图像", use_container_width=True)

                    if st.button("执行滤波处理", key="filter_btn", use_container_width=True):
                        with st.spinner("正在处理..."):
                            try:
                                result = apply_filter(image_np, filter_type, kernel_size)
                                st.session_state['filter_result'] = result
                            except Exception as e:
                                st.error(f"处理出错: {str(e)}")

            with col2:
                if uploaded_file is not None and 'filter_result' in st.session_state:
                    display_result = cv2.cvtColor(st.session_state['filter_result'], cv2.COLOR_BGR2RGB)
                    st.image(display_result, caption=f"{filter_type}结果", use_container_width=True)
                    st.markdown(get_image_download_link(
                        st.session_state['filter_result'],
                        f"{filter_type}_{kernel_size}x{kernel_size}.jpg",
                        "📥 下载结果图像"
                    ), unsafe_allow_html=True)
                else:
                    st.info("👆 请上传图像并点击处理按钮")

    with tab4:
        # 资源上传页面
        render_resource_upload()

    with tab5:
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
