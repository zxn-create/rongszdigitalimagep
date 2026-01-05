import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import base64
import pandas as pd
from datetime import datetime
import webbrowser  # 保留导入，但使用新的实现方式
import matplotlib.pyplot as plt

# 页面配置
st.set_page_config(
    page_title="学习资源中心",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 目标链接（统一配置）
TARGET_URL = "https://www.yuketang.cn/"

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
    """
    应用图像滤波处理
    
    参数:
        image: 输入图像 (BGR格式)
        filter_type: 滤波类型 ["中值滤波", "均值滤波", "高斯滤波"]
        kernel_size: 核大小 (3-15之间的奇数)
    
    返回:
        filtered: 滤波后的图像
    """
    # 输入验证
    if image is None or image.size == 0:
        raise ValueError("输入图像无效")
    
    # 确保核大小为奇数且在有效范围内
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # 限制核大小范围
    kernel_size = max(3, min(15, kernel_size))
    
    try:
        if filter_type == "中值滤波":
            # 中值滤波：对彩色图像的每个通道分别处理
            filtered = cv2.medianBlur(image, kernel_size)
            
        elif filter_type == "均值滤波":
            # 均值滤波：简单的平均滤波
            filtered = cv2.blur(image, (kernel_size, kernel_size))
            
        elif filter_type == "高斯滤波":
            # 高斯滤波：使用高斯核进行加权平均
            # 高斯滤波的核大小必须是正奇数
            if kernel_size < 1:
                kernel_size = 3
            filtered = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
            
        else:
            # 未知滤波类型，返回原图
            filtered = image.copy()
            
        return filtered
        
    except Exception as e:
        # 如果滤波失败，返回原图并抛出错误
        st.error(f"滤波处理失败: {str(e)}")
        return image.copy()

def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img = Image.fromarray(img)
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/jpeg;base64,{img_str}" download="{filename}" style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; margin-top: 10px;">{text}</a>'
    return href

# 新的链接打开函数 - 使用HTML方式
def create_link_button(url, text, key=None):
    """创建HTML链接按钮"""
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


# 渲染侧边栏（修改链接打开方式）
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

        # 快速导航（保持原跳转逻辑，不修改）
        st.markdown("### 🧭 快速导航")
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("main.py")
        if st.button("🔬 图像处理实验室", use_container_width=True):
            st.switch_page("pages/1_🔬_图像处理实验室.py")
        if st.button("📝 智能与传统图片处理", use_container_width=True):
            # 使用JavaScript在新标签页打开链接
            js = """<script>window.open("https://29phcdb33h.coze.site", "_blank");</script>"""
            st.components.v1.html(js, height=0)
        if st.button("📚 学习资源中心", use_container_width=True):
            st.switch_page("pages/2_📚_学习资源中心.py")
        if st.button("📝 我的思政足迹", use_container_width=True):
            st.switch_page("pages/3_📝_我的思政足迹.py")
        if st.button("🏆 成果展示", use_container_width=True):
            st.switch_page("pages/4_🏆_成果展示.py")

        # 学习进度（保持不变）
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

        # 思政理论学习（修改为HTML链接方式）
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

        # 实验指南（保持不变）
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

        # 思政教育提示（保持不变）
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fee2e2, #fecaca); padding: 20px; 
                    border-radius: 12px; border: 2px solid #dc2626; margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);'>
            <h5 style='color: #dc2626;'>💡 思政教育提示</h5>
            <p style='font-size: 0.9rem; color: #7f1d1d;'>在技术学习中培养：</p>
            <ul style='padding-left: 15px; font-size: 0.85rem; color: #7f1d1d;'>
                <li style='color: #dc2626;'>🎯 精益求精的工匠精神</li>
                <li style='color: #dc2626;'>🔬 实事求是的科学态度</li>
                <li style='color: #dc2626;'>💡 创新发展的时代担当</li>
                <li style='color: #dc2626;'>🇨🇳 科技报国的家国情怀</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 系统信息（保持不变）
        st.markdown("---")
        st.markdown("**📊 系统信息**")
        st.text(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.text("状态: 🟢 正常运行")
        st.text("版本: v2.1.0")


# 主页面内容（修改链接打开方式）
def main():
    # 应用CSS样式
    apply_modern_css()

    # 页面标题（保持不变）
    st.markdown("""
    <div class='modern-header'>
        <h1>📚 学习资源中心</h1>
        <p class='subtitle'>🇨🇳 思政教育与专业技术融合学习平台 · 培养德才兼备的新时代技术人才</p>
    </div>
    """, unsafe_allow_html=True)

    # 渲染侧边栏
    render_sidebar()

    # 使用标签页组织内容
    tab1, tab2, tab3, tab4 = st.tabs(["🇨🇳 思政资源", "🔬 技术资源", "🛠️ 实践工具", "💾 资源下载"])

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

                # 修改为HTML链接方式
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

                # 修改为HTML链接方式
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

            # 修改为HTML链接方式
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

            # 修改为HTML链接方式
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

                # 修改为HTML链接方式
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

                # 修改为HTML链接方式
                button_html = create_link_button(
                    "https://www.bilibili.com/video/BV1Fo4y1d7JL/", 
                    "开始学习"
                )
                st.markdown(button_html, unsafe_allow_html=True)

        # 理论知识部分（保持不变）
        with st.expander("第1章 绪论", expanded=True):
            st.markdown("""
            **1.1 图像的基本概念**
            - 数字图像的定义：由像素组成的二维矩阵
            - 基本术语：像素、分辨率、邻域、连接性
            - 图像类型：二值图像、灰度图像、彩色图像
            - 图像质量评价指标

            **1.2 图像的数字化及描述**
            - 采样过程：空间坐标的离散化
            - 量化过程：灰度值的离散化
            - 数字图像的数学表示方法
            - 图像文件格式：BMP、JPEG、PNG等

            **1.3 图像处理的基本知识**
            - 图像处理系统的组成
            - 数字图像处理的基本步骤
            - 图像处理的主要研究内容

            **1.4 数字图像处理的应用和发展**
            - 应用领域：医学影像、遥感、工业检测、安防监控等
            - 发展趋势：深度学习、实时处理、三维图像处理等
            """)

        with st.expander("第2章 数字图像处理基础"):
            st.markdown("""
            **2.1 图像的点运算**
            - 灰度变换：线性变换、非线性变换（对数、指数）
            - 对比度拉伸：分段线性变换
            - 直方图修正：直方图均衡化、直方图规定化
            - 应用场景：图像增强、对比度调整

            **2.2 图像的代数运算**
            - 图像加法：图像平均去噪、图像叠加
            - 图像减法：背景消除、运动检测
            - 图像乘法：掩模操作、感兴趣区域提取
            - 图像除法：比值处理、阴影校正

            **2.3 图像的几何变换**
            - 基本变换：平移、旋转、缩放、镜像
            - 仿射变换：保持平行性的线性变换
            - 投影变换：透视变换
            - 插值方法：最近邻、双线性、双三次插值

            **2.4 图像卷积操作**
            - 卷积的基本概念和原理
            - 卷积核的设计与应用
            - 边界处理方法：补零、镜像、复制
            """)

        with st.expander("第3章 彩色图像处理"):
            st.markdown("""
            **3.1 彩色图像的颜色空间**
            - RGB颜色模型：加色混合原理
            - HSI颜色模型：色调、饱和度、亮度
            - CMYK颜色模型：减色混合原理
            - YUV/YIQ颜色模型：电视传输标准
            - 颜色空间转换算法和实现

            **3.2 伪彩色图像处理**
            - 灰度图像的伪彩色增强
            - 密度分割法
            - 灰度级-彩色变换法
            - 频率域伪彩色处理

            **3.3 基于彩色图像的分割**
            - 彩色图像分割的特殊性
            - 基于颜色聚类的分割方法
            - 彩色边缘检测技术
            - 彩色区域生长算法

            **3.4 彩色图像灰度化**
            - 常用灰度化方法：平均值法、加权平均法
            - 基于亮度信息的灰度化
            - 灰度化质量评价
            - 应用场景：特征提取、图像压缩
            """)

        with st.expander("第4章 空间滤波"):
            st.markdown("""
            **4.1 空间滤波基础**
            - 空间滤波的基本原理
            - 滤波器分类：线性滤波、非线性滤波
            - 相关与卷积的关系
            - 滤波器设计原则

            **4.2 图像噪声**
            - 噪声模型：高斯噪声、椒盐噪声、泊松噪声
            - 噪声特性分析
            - 噪声对图像质量的影响
            - 噪声估计方法

            **4.3 图像平滑**
            - 均值滤波：算法原理和实现
            - 中值滤波：非线性滤波，有效去除椒盐噪声
            - 高斯滤波：加权平均，保持边缘信息
            - 自适应滤波：根据局部特性调整参数

            **4.4 图像锐化**
            - 一阶微分算子：Roberts、Sobel、Prewitt算子
            - 二阶微分算子：Laplacian算子
            - 梯度模版的设计和应用
            - 反锐化掩模技术
            - 高频增强滤波
            """)

        with st.expander("第5章 图像的数学形态学处理"):
            st.markdown("""
            **5.1 二值图像形态学处理**
            - 基本运算：腐蚀、膨胀
            - 组合运算：开运算、闭运算
            - 击中与击不中变换
            - 形态学应用：边界提取、区域填充、骨架提取

            **5.2 灰度图像形态学处理**
            - 灰度腐蚀和膨胀
            - 灰度开运算和闭运算
            - 形态学梯度
            - 顶帽变换和底帽变换
            - 应用：纹理分割、背景校正
            """)

        with st.expander("第6章 图像特征提取"):
            st.markdown("""
            **6.1 图像颜色特征提取**
            - 颜色直方图：全局颜色分布
            - 颜色矩：均值、方差、偏度
            - 颜色相关图：空间颜色关系
            - 颜色聚合向量
            - 颜色集表示

            **6.2 图像纹理特征提取**
            - 统计纹理特征：对比度、相关性、能量、均匀性
            - 结构纹理特征：基于纹理基元的描述
            - 频谱纹理特征：傅里叶频谱、小波变换
            - 局部二值模式（LBP）
            - Gabor滤波器组

            **6.3 图像形状特征提取**
            - 边界特征：链码、傅里叶描述子
            - 区域特征：几何矩、不变矩
            - 形状上下文
            - 骨架描述方法
            """)

        with st.expander("第7章 图像分割"):
            st.markdown("""
            **7.1 图像分割概述**
            - 图像分割的定义和意义
            - 分割方法分类：基于边界、基于区域、结合方法
            - 分割质量评价标准

            **7.2 边缘检测**
            - 边缘模型：阶跃边缘、屋顶边缘
            - 经典边缘检测算子：Canny、Sobel、Laplacian
            - 边缘连接技术
            - 多尺度边缘检测

            **7.3 线检测**
            - Hough变换原理
            - 直线检测算法
            - 曲线检测扩展
            - 随机Hough变换

            **7.4 区域分割**
            - 阈值分割：全局阈值、局部阈值、自适应阈值
            - 区域生长：种子点选择、生长准则
            - 分裂合并算法
            - 基于聚类的分割：K-means、Mean Shift
            - 分水岭算法
            """)

        with st.expander("第8章 图像压缩"):
            st.markdown("""
            **8.1 图像压缩简介**
            - 图像压缩的必要性
            - 压缩分类：无损压缩、有损压缩
            - 压缩性能评价：压缩比、保真度
            - 信息论基础：熵、互信息

            **8.2 熵编码技术**
            - 哈夫曼编码：变长编码，基于概率统计
            - 算术编码：将整个消息编码为一个分数
            - 游程编码：适用于连续相同像素的图像
            - LZW编码：字典-based编码方法

            **8.3 K-L变换**
            - K-L变换的数学原理
            - 主成分分析在图像压缩中的应用
            - 变换系数的选择和量化
            - 能量集中特性

            **8.4 JPEG编码**
            - JPEG标准的基本框架
            - 离散余弦变换（DCT）
            - 量化表设计
            - 之字形扫描和熵编码
            - 渐进式编码模式
            """)

    with tab3:
        st.markdown('<div class="section-title">🛠️ 在线实践工具</div>', unsafe_allow_html=True)

        # 边缘检测工具（保持不变）
        with st.expander("🔍 边缘检测工具", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                uploaded_file = st.file_uploader("上传图像", type=["jpg", "jpeg", "png"], key="edge_detector")
                operator = st.selectbox("选择边缘检测算子", ["Roberts", "Sobel", "Prewitt", "Laplacian", "LoG"],
                                        key="edge_op")

                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    image_np = np.array(image)
                    # 确保图像是BGR格式（OpenCV标准）
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
                    # 转换回RGB格式用于显示
                    display_result = cv2.cvtColor(st.session_state['edge_result'], cv2.COLOR_BGR2RGB)
                    st.image(display_result, caption=f"{operator}边缘检测结果", use_container_width=True)
                    st.markdown(get_image_download_link(
                        st.session_state['edge_result'],
                        f"edge_detection_{operator}.jpg",
                        "📥 下载结果图像"
                    ), unsafe_allow_html=True)
                else:
                    st.info("👆 请上传图像并点击处理按钮")

        # 图像滤波工具（保持不变）
        with st.expander("🔄 图像滤波工具"):
            col1, col2 = st.columns(2)

            with col1:
                uploaded_file = st.file_uploader("上传图像", type=["jpg", "jpeg", "png"], key="filter_upload")
                filter_type = st.selectbox("选择滤波器类型", ["中值滤波", "均值滤波", "高斯滤波"], key="filter_type")
                kernel_size = st.slider("核大小", 3, 15, 3, 2, key="kernel_size")

                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    image_np = np.array(image)
                    # 确保图像是BGR格式
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
                    # 转换回RGB格式用于显示
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
                        # 修改为HTML链接方式
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
                        # 修改为HTML链接方式
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
                    # 修改为HTML链接方式
                    button_html = create_link_button(code['url'], "下载")
                    st.markdown(button_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
