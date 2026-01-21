import streamlit as st
import webbrowser
import pandas as pd
from datetime import datetime

# 页面配置（必须放在最前面）
st.set_page_config(
    page_title="智能图像处理",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 目标链接
TARGET_URL = "https://29phcdb33h.coze.site/"

# 现代化米色思政主题CSS
st.markdown("""
<style>
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

.resource-card.ai {
    border-left: 5px solid #8b5cf6;
}

.resource-card.tech {
    border-left: 5px solid #3b82f6;
}

.resource-card.tutorial {
    border-left: 5px solid #10b981;
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

.badge.ai {
    background: linear-gradient(135deg, #8b5cf6, #6d28d9);
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

/* 图像容器样式 */
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
</style>
""", unsafe_allow_html=True)

# 链接按钮创建函数
def create_link_button(url, text):
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

# 渲染侧边栏
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; 
            padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px;
            box-shadow: 0 6px 12px rgba(220, 38, 38, 0.3);'>
            <h3>🤖 智能处理导航</h3>
            <p style='margin: 10px 0 0 0; font-size: 1rem;'>智能创新 · 技术融合 · 思政引领</p>
        </div>
        """, unsafe_allow_html=True)

        # 快速导航
        st.markdown("### 🧭 快速导航")
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("main.py")
        if st.button("🔬 图像处理实验室", use_container_width=True):
            st.switch_page("pages/1_🔬_图像处理实验室.py")
        if st.button("🤖 智能图像处理", use_container_width=True):
            # 使用JavaScript在新标签页打开链接
            st.switch_page("pages/智能与传统图片处理.py")
        if st.button("📚 学习资源中心", use_container_width=True):
            st.switch_page("pages/2_📚_学习资源中心.py")
        if st.button("📝 我的思政足迹", use_container_width=True):
            st.switch_page("pages/3_📝_我的思政足迹.py")
        if st.button("🏆 成果展示", use_container_width=True):
            st.switch_page("pages/4_🏆_成果展示.py")


def main():
    render_sidebar()
    st.markdown("""
 <div class='modern-header'>
      <h1>🤖 智能图像处理</h1>
      <p class='subtitle'>🇨🇳 智能与传统创新的学习平台 · 培养德才兼备的新时代技术人才</p>
  </div>
    """, unsafe_allow_html=True)
    TARGET_URL = "https://29phcdb33h.coze.site/"
    # 主要跳转按钮
    if st.button("🚀 点击进入智能与传统图片处理", use_container_width=True):
        webbrowser.open_new_tab(TARGET_URL)
    st.markdown("---")
    st.subheader("📎 直接链接")
    st.markdown(f'<a href="{TARGET_URL}" target="_blank"><button style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">点击跳转到处理页面</button></a>', unsafe_allow_html=True)
       

        

if __name__ == "__main__":
    main()
