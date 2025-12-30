import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import sqlite3
import json
import os
import zipfile
import tempfile
import shutil
import csv
import io
import base64
import requests
from github import Github, GithubException
import time

st.set_page_config(
    page_title="思政成果展示", 
    page_icon="🏆", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# GitHub配置 - 添加错误处理
GITHUB_USERNAME = "zxn-create"
GITHUB_REPO_NAME = "rongszdigitalimagep"

# 安全的获取 GitHub Token 方法
def get_github_token():
    """安全地获取 GitHub Token"""
    try:
        # 首先尝试从 Streamlit secrets 获取
        return st.secrets.get("GITHUB_TOKEN", "")
    except Exception as e:
        # 如果在本地运行且没有 secrets.toml 文件
        try:
            # 尝试从环境变量获取
            return os.environ.get("GITHUB_TOKEN", "")
        except:
            # 最后返回空字符串
            print(f"警告: 无法获取 GitHub Token: {e}")
            return ""

GITHUB_TOKEN = get_github_token()

# 设置时区为北京时间
def get_beijing_time():
    """获取北京时间"""
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))

def format_beijing_time(timestamp):
    """格式化时间为北京时间字符串"""
    if timestamp is None:
        return ""
    
    if isinstance(timestamp, str):
        try:
            # 尝试解析字符串时间
            if 'T' in timestamp:
                dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                # 尝试多种时间格式
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                    try:
                        dt = datetime.datetime.strptime(timestamp, fmt)
                        break
                    except:
                        continue
                else:
                    return timestamp
            
            # 转换为北京时间
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            beijing_tz = datetime.timezone(datetime.timedelta(hours=8))
            return dt.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp
    
    elif isinstance(timestamp, datetime.datetime):
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
        beijing_tz = datetime.timezone(datetime.timedelta(hours=8))
        return timestamp.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    return str(timestamp)

# GitHub存储类 - 增强错误处理
class GitHubStorage:
    def __init__(self):
        self.token = GITHUB_TOKEN
        self.username = GITHUB_USERNAME
        self.repo_name = GITHUB_REPO_NAME
        self.repo = None
        self.connected = False
        self.error_message = ""
        
    def connect(self):
        """连接到GitHub仓库"""
        try:
            if not self.token:
                self.error_message = "GitHub Token未配置"
                return False
            
            g = Github(self.token)
            self.repo = g.get_user().get_repo(self.repo_name)
            self.connected = True
            self.error_message = ""
            return True
        except GithubException as e:
            if e.status == 404:
                self.error_message = f"GitHub仓库 '{self.repo_name}' 不存在"
            elif e.status == 401:
                self.error_message = "GitHub Token无效或过期"
            else:
                self.error_message = f"GitHub连接失败: {str(e)}"
            return False
        except Exception as e:
            self.error_message = f"连接到GitHub失败: {str(e)}"
            return False
    
    def save_file_to_github(self, file_content, file_path, commit_message=None):
        """保存文件到GitHub"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            # 检查文件是否存在
            try:
                contents = self.repo.get_contents(file_path)
                # 文件存在，更新
                self.repo.update_file(
                    file_path,
                    commit_message or f"更新文件 {os.path.basename(file_path)}",
                    file_content,
                    contents.sha
                )
            except:
                # 文件不存在，创建
                self.repo.create_file(
                    file_path,
                    commit_message or f"创建文件 {os.path.basename(file_path)}",
                    file_content
                )
            return True
        except Exception as e:
            self.error_message = f"保存到GitHub失败: {str(e)}"
            return False
    
    def save_binary_file(self, file_data, file_path, commit_message=None):
        """保存二进制文件到GitHub"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            # 将二进制文件转换为base64
            content = base64.b64encode(file_data).decode('utf-8')
            
            # 检查文件是否存在
            try:
                contents = self.repo.get_contents(file_path)
                # 文件存在，更新
                self.repo.update_file(
                    file_path,
                    commit_message or f"更新文件 {os.path.basename(file_path)}",
                    content,
                    contents.sha
                )
            except:
                # 文件不存在，创建
                self.repo.create_file(
                    file_path,
                    commit_message or f"创建文件 {os.path.basename(file_path)}",
                    content
                )
            return True
        except Exception as e:
            self.error_message = f"保存二进制文件到GitHub失败: {str(e)}"
            return False
    
    def get_file_from_github(self, file_path):
        """从GitHub获取文件"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            contents = self.repo.get_contents(file_path)
            return contents.decoded_content
        except:
            return None
    
    def list_files(self, folder_path=""):
        """列出GitHub仓库中的文件"""
        if not self.connected:
            if not self.connect():
                return []
        
        try:
            contents = self.repo.get_contents(folder_path)
            files = []
            for content in contents:
                files.append({
                    'name': content.name,
                    'path': content.path,
                    'type': content.type,
                    'size': content.size,
                    'sha': content.sha,
                    'url': content.html_url
                })
            return files
        except:
            return []

# 创建GitHub存储实例
github_storage = GitHubStorage()

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
    
    .achievement-card {
        background: linear-gradient(135deg, #fff, var(--beige-light));
        padding: 30px;
        border-radius: 20px;
        border-left: 5px solid var(--primary-red);
        margin: 20px 0;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
        border: 1px solid #e5e7eb;
    }
    
    .achievement-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--hover-shadow);
    }
    
    .project-card {
        background: linear-gradient(135deg, #fff, var(--beige-light));
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .project-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--hover-shadow);
    }
    
    .project-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(135deg, var(--primary-red), var(--accent-red));
    }
    
    .ideology-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary-red), var(--accent-red));
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }
    
    .ideology-badge.blue {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    }
    
    .ideology-badge.green {
        background: linear-gradient(135deg, #10b981, #047857);
    }
    
    .ideology-badge.yellow {
        background: linear-gradient(135deg, #f59e0b, #d97706);
    }
    
    .ideology-badge.purple {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
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
    
    /* 审核状态标签样式 */
    .status-pending {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .status-approved {
        background: linear-gradient(135deg, #10b981, #047857);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .status-rejected {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* GitHub存储状态 */
    .github-status {
        background: linear-gradient(135deg, #24292e, #2d333b);
        color: white;
        padding: 10px;
        border-radius: 10px;
        font-size: 0.9rem;
        margin: 10px 0;
        text-align: center;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化数据库 - 修复版本
def init_database():
    """初始化数据库表 - 修复FOREIGN KEY错误"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 检查 submitted_projects 表是否存在并获取其列信息
        c.execute("PRAGMA table_info(submitted_projects)")
        existing_columns = [column[1] for column in c.fetchall()]
        
        # 如果表不存在，创建完整的表结构（不带外键约束）
        if not existing_columns:
            c.execute('''
                CREATE TABLE submitted_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    author_name TEXT NOT NULL,
                    project_desc TEXT NOT NULL,
                    submit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    files TEXT,
                    file_paths TEXT,
                    status TEXT DEFAULT '待审核',
                    review_notes TEXT,
                    review_time TIMESTAMP,
                    reviewer TEXT,
                    user_id INTEGER,
                    github_paths TEXT  -- 新增：GitHub存储路径
                )
            ''')
        else:
            # 检查并添加缺失的字段
            columns_to_add = [
                ('file_paths', 'TEXT'),
                ('reviewer', 'TEXT'),
                ('user_id', 'INTEGER'),
                ('github_paths', 'TEXT')
            ]
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        c.execute(f'ALTER TABLE submitted_projects ADD COLUMN {column_name} {column_type}')
                    except:
                        pass
        
        # 创建意见反馈表
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_content TEXT NOT NULL,
                submit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                github_synced BOOLEAN DEFAULT 0  -- 新增：GitHub同步状态
            )
        ''')
        
        # 创建用户表（如果不存在）
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建GitHub同步记录表
        c.execute('''
            CREATE TABLE IF NOT EXISTS github_sync (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                github_path TEXT NOT NULL,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(table_name, record_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"数据库初始化失败：{str(e)}")
        return False

# 渲染侧边栏 - 修复版本
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; 
            padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px;
            box-shadow: 0 6px 12px rgba(220, 38, 38, 0.3);'>
            <h3>🏆 思政成果展示</h3>
            <p style='margin: 10px 0 0 0; font-size: 1rem;'>技术报国 · 思想引领 · 创新发展</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示GitHub存储状态
        if github_storage.connect():
            st.markdown("""
            <div class='github-status'>
                ✅ GitHub存储已连接<br>
                <small>数据永久保存</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='github-status'>
                ⚠️ GitHub存储未连接<br>
                <small>{github_storage.error_message or '本地运行模式'}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # 快速导航
        st.markdown("### 🧭 快速导航")
        
        if st.button("🏠 返回首页", width='stretch'):
            st.switch_page("main.py")
        if st.button("🔬 图像处理实验室", width='stretch'):
            st.switch_page("pages/1_🔬_图像处理实验室.py")
        if st.button("🏫加入班级与在线签到", use_container_width=True):
            st.switch_page("pages/分班和在线签到.py")
        if st.button("📤 实验作业提交", width='stretch'):
            st.switch_page("pages/实验作业提交.py")            
        if st.button("📚 学习资源中心", width='stretch'):
            st.switch_page("pages/2_📚_学习资源中心.py")
        if st.button("📝 我的思政足迹", width='stretch'):
            st.switch_page("pages/3_📝_我的思政足迹.py")
        if st.button("🏆 成果展示", width='stretch'):
            st.switch_page("pages/4_🏆_成果展示.py")
        
        # 用户提交记录查看
        if "logged_in" in st.session_state and st.session_state.logged_in:
            st.markdown("---")
            if st.button("📋 我的提交记录", width='stretch'):
                st.session_state.show_my_projects = True
                st.rerun()
        
        # 检查是否为教师，显示管理员入口
        if "logged_in" in st.session_state and st.session_state.logged_in:
            if verify_teacher_role(st.session_state.username):
                st.markdown("---")
                if st.button("🔧 进入教师后台", width='stretch', type="primary"):
                    st.session_state.show_admin = True
                    st.rerun()
        
        # 思政学习进度
        st.markdown("### 📚 思政学习进度")
        
        ideology_progress = [
            {"name": "工匠精神", "icon": "🔧", "progress": 90},
            {"name": "家国情怀", "icon": "🇨🇳", "progress": 85},
            {"name": "科学态度", "icon": "🔬", "progress": 78},
            {"name": "创新意识", "icon": "💡", "progress": 82},
            {"name": "责任担当", "icon": "⚖️", "progress": 88},
            {"name": "团队合作", "icon": "🤝", "progress": 80}
        ]
        
        for item in ideology_progress:
            st.markdown(f"**{item['icon']} {item['name']}**")
            st.progress(item['progress'] / 100)
        
        st.markdown("---")
        
        # 思政理论学习
        st.markdown("### 🎯 思政理论学习")
        theory_topics = [
            "新时代工匠精神的内涵与实践",
            "科技创新与国家发展战略",
            "社会主义核心价值观与技术伦理",
            "科学家精神与家国情怀",
            "数字时代的责任与担当"
        ]
        
        for topic in theory_topics:
            if st.button(f"📖 {topic}", key=f"theory_{topic}", width='stretch'):
                st.info(f"开始学习：{topic}")
        
        st.markdown("---")
        
        # 思政学习提醒
        st.markdown("### 💫 思政学习提醒")
        st.success("""
        🎯 **本周思政重点：**
        - 学习科学家精神
        - 践行工匠精神
        - 培养家国情怀
        - 强化责任担当
        """)

# 生成优秀作品数据
def generate_projects_data():
    projects = [
        {
            "title": "智能图像增强系统",
            "author": "李天龙、陈曦、王语嫣（团队）",
            "tech_highlight": "基于进化算法的CNN自适应图像增强技术",
            "ideology": ["工匠精神", "创新意识"],
            "description": "团队在魏培阳、甘建红老师指导下，优化CNN模型架构，结合进化算法实现复杂场景下的图像去噪、超分辨率重建，解决传统算法细节丢失问题，每一个参数调整都历经上百次测试，体现了精益求精的技术追求和算法创新突破。",
            "achievement": "第17届中国大学生计算机设计大赛全国二等奖",
            "impact": "可应用于气象雷达图像、安防监控画面优化，已为2家气象观测站提供数据处理支持，提升图像分析准确率25%",
            "date": "2024-08-11"
        },
        {
            "title": "细胞智绘—基于超分辨的AI细胞图像分析系统",
            "author": "吴欣遥、刘馨宇、赵彬宇（团队）",
            "tech_highlight": "超分辨成像+神经元细胞精准定位算法",
            "ideology": ["科学态度", "责任担当"],
            "description": "在杨昊、周航老师指导下，针对脑神经元细胞标注难题，研发超分辨图像分析技术，通过算法拉开紧密接触的细胞间距，实现精准定位标注，减少科研人员手动标注工作量，体现了用技术解决医学研究痛点的责任担当和严谨科学态度。",
            "achievement": "第17届中国大学生计算机设计大赛全国三等奖",
            "impact": "已辅助脑科学研究团队提升数据处理效率40%，降低科研资源消耗30%，为神经科学研究提供技术支撑",
            "date": "2024-08-20"
        },
        {
            "title": "传承'徽'煌数学—传统文化数字图像处理平台",
            "author": "王佳艺、王欣钰（团队）",
            "tech_highlight": "PS图像处理+Illustrator矢量绘图融合技术",
            "ideology": ["文化自信", "传承创新"],
            "description": "团队在范晶、刘雪峰老师指导下，运用专业图像处理工具，将刘徽数学思想与徽派文化元素通过图像可视化呈现，每一处视觉细节都经过反复雕琢，实现艺术与技术的完美融合，体现了对传统文化的传承与数字技术创新的结合。",
            "achievement": "第17届中国大学生计算机设计大赛全国三等奖",
            "impact": "已应用于3所中学传统文化教学，帮助学生通过视觉化方式理解古代数学成就，覆盖师生2000余人",
            "date": "2024-08-20"
        }
    ]
    return projects

# 生成统计数据
def generate_stats_data():
    """生成用于图表的数据"""
    # 思政元素分布数据
    ideology_data = {
        '思政元素': ['工匠精神', '家国情怀', '创新意识', '责任担当', '科学态度', '团队合作'],
        '作品数量': [35, 28, 22, 25, 20, 18]
    }
    
    # 项目类型分布数据
    project_type_data = {
        '项目类型': ['技术创新类', '社会服务类', '文化传承类', '国家战略类'],
        '数量': [45, 30, 15, 10]
    }
    
    return pd.DataFrame(ideology_data), pd.DataFrame(project_type_data)

# 校验用户是否为教师角色
def verify_teacher_role(username):
    """校验用户是否为教师角色"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()
        return result is not None and result[0] == "teacher"
    except:
        return False

def get_user_id(username):
    """获取用户ID"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

def sync_data_to_github(table_name, record_id, data):
    """同步数据到GitHub"""
    try:
        if not github_storage.connect():
            return False, "GitHub连接失败"
            
        timestamp = get_beijing_time().strftime('%Y%m%d_%H%M%S')
        github_path = f"data/{table_name}/{timestamp}_{record_id}.json"
        
        # 将数据转换为JSON格式
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        # 保存到GitHub
        if github_storage.save_file_to_github(json_data, github_path, f"同步{table_name}数据_{record_id}"):
            # 更新数据库中的GitHub路径
            conn = sqlite3.connect('image_processing_platform.db')
            c = conn.cursor()
            
            if table_name == 'submitted_projects':
                c.execute('''UPDATE submitted_projects SET github_paths = ? WHERE id = ?''', 
                         (github_path, record_id))
            elif table_name == 'feedback':
                c.execute('''UPDATE feedback SET github_synced = 1 WHERE id = ?''', (record_id,))
            
            # 记录同步历史
            c.execute('''INSERT OR REPLACE INTO github_sync (table_name, record_id, github_path) 
                        VALUES (?, ?, ?)''', (table_name, record_id, github_path))
            
            conn.commit()
            conn.close()
            return True, "同步成功"
        else:
            return False, github_storage.error_message
    except Exception as e:
        return False, f"同步到GitHub失败：{str(e)}"

def sync_file_to_github(file_data, file_name, project_name, author_name):
    """同步文件到GitHub"""
    try:
        if not github_storage.connect():
            return None
            
        timestamp = get_beijing_time().strftime('%Y%m%d_%H%M%S')
        safe_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_author_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        github_path = f"uploads/{safe_project_name}_{safe_author_name}/{timestamp}_{file_name}"
        
        # 保存到GitHub
        if github_storage.save_binary_file(file_data, github_path, f"上传文件：{file_name}"):
            return github_path
        else:
            return None
    except Exception as e:
        print(f"同步文件到GitHub失败：{str(e)}")
        return None

def get_feedback_data():
    """从数据库读取意见反馈数据"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        c.execute('''
            SELECT id, feedback_content, submit_time, ip_address, user_agent, github_synced
            FROM feedback
            ORDER BY submit_time DESC
        ''')
        
        feedback_list = []
        for row in c.fetchall():
            feedback_list.append({
                "序号": row[0],
                "反馈内容": row[1],
                "提交时间": format_beijing_time(row[2]),
                "IP地址": row[3] if row[3] else "未知",
                "用户代理": row[4] if row[4] else "未知",
                "GitHub同步": "✅" if row[5] else "❌"
            })
        
        conn.close()
        return feedback_list
    except Exception as e:
        st.error(f"读取反馈数据失败：{str(e)}")
        return []

def save_feedback_to_db(feedback_content):
    """保存反馈到数据库并同步到GitHub"""
    try:
        import socket
        import streamlit as st
        
        # 获取IP地址
        try:
            ip_address = st.experimental_connection("client_ip").query().to_dict()['ip_address']
        except:
            ip_address = "127.0.0.1"
        
        # 获取用户代理
        try:
            user_agent = st.experimental_connection("client_headers").query().to_dict().get('user-agent', '未知')
        except:
            user_agent = "未知"
        
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO feedback (feedback_content, ip_address, user_agent)
            VALUES (?, ?, ?)
        ''', (feedback_content, ip_address, user_agent))
        
        record_id = c.lastrowid
        
        conn.commit()
        conn.close()
        
        # 同步到GitHub
        feedback_data = {
            "content": feedback_content,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "submit_time": get_beijing_time().isoformat(),
            "record_id": record_id
        }
        
        success, message = sync_data_to_github('feedback', record_id, feedback_data)
        if success:
            return True, "已保存并同步到GitHub"
        else:
            return True, f"已保存到本地（GitHub同步失败：{message}）"
        
    except Exception as e:
        return False, f"保存失败：{str(e)}"

def save_uploaded_files(uploaded_files, project_name, author_name):
    """保存上传的文件到服务器和GitHub"""
    try:
        # 创建上传目录
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 创建项目目录
        safe_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_author_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        project_dir = os.path.join(upload_dir, f"{safe_project_name}_{safe_author_name}")
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        saved_files = []
        file_paths = []
        github_paths = []
        
        for uploaded_file in uploaded_files:
            # 生成唯一文件名
            file_ext = os.path.splitext(uploaded_file.name)[1]
            unique_filename = f"{get_beijing_time().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
            local_file_path = os.path.join(project_dir, unique_filename)
            
            # 保存文件到本地
            with open(local_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 同步到GitHub
            github_path = None
            if github_storage.connect():
                file_data = uploaded_file.getvalue()
                github_path = sync_file_to_github(file_data, uploaded_file.name, project_name, author_name)
            
            saved_files.append(uploaded_file.name)
            file_paths.append(local_file_path)
            github_paths.append(github_path if github_path else "")
        
        return saved_files, file_paths, github_paths
    except Exception as e:
        st.error(f"保存文件失败：{str(e)}")
        return [], [], []

def save_submitted_project(project_data, uploaded_files=None):
    """保存提交的作品到数据库并同步到GitHub"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 获取用户ID
        user_id = None
        if "logged_in" in st.session_state and st.session_state.logged_in:
            user_id = get_user_id(st.session_state.username)
        
        files_str = json.dumps(project_data.get('files', []))
        file_paths_str = json.dumps(project_data.get('file_paths', []))
        github_paths_str = json.dumps(project_data.get('github_paths', []))
        
        c.execute('''
            INSERT INTO submitted_projects (project_name, author_name, project_desc, files, file_paths, user_id, github_paths)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (project_data['project_name'], project_data['author_name'], 
              project_data['project_desc'], files_str, file_paths_str, user_id, github_paths_str))
        
        record_id = c.lastrowid
        
        conn.commit()
        conn.close()
        
        # 同步完整数据到GitHub
        project_full_data = {
            **project_data,
            "record_id": record_id,
            "user_id": user_id,
            "submit_time": get_beijing_time().isoformat(),
            "status": "待审核"
        }
        
        success, message = sync_data_to_github('submitted_projects', record_id, project_full_data)
        if success:
            return True, "已保存并同步到GitHub"
        else:
            return True, f"已保存到本地（GitHub同步失败：{message}）"
        
    except Exception as e:
        return False, f"保存作品失败：{str(e)}"

def get_submitted_projects(user_id=None):
    """获取所有提交的作品"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        if user_id:
            # 获取特定用户的作品
            c.execute('''
                SELECT id, project_name, author_name, project_desc, 
                       submit_time, files, file_paths, status, review_notes, review_time, reviewer, github_paths
                FROM submitted_projects
                WHERE user_id = ?
                ORDER BY submit_time DESC
            ''', (user_id,))
        else:
            # 获取所有作品
            c.execute('''
                SELECT id, project_name, author_name, project_desc, 
                       submit_time, files, file_paths, status, review_notes, review_time, reviewer, github_paths
                FROM submitted_projects
                ORDER BY submit_time DESC
            ''')
        
        projects = []
        for row in c.fetchall():
            files = json.loads(row[5]) if row[5] else []
            file_paths = json.loads(row[6]) if row[6] else []
            github_paths = json.loads(row[11]) if row[11] else []
            projects.append({
                "id": row[0],
                "project_name": row[1],
                "author_name": row[2],
                "project_desc": row[3],
                "submit_time": format_beijing_time(row[4]),
                "files": files,
                "file_paths": file_paths,
                "github_paths": github_paths,
                "status": row[7],
                "review_notes": row[8],
                "review_time": format_beijing_time(row[9]),
                "reviewer": row[10]
            })
        
        conn.close()
        return projects
    except Exception as e:
        st.error(f"获取作品失败：{str(e)}")
        return []

def update_project_status(project_id, status, review_notes=""):
    """更新作品审核状态并同步到GitHub"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        c.execute('''
            UPDATE submitted_projects 
            SET status = ?, review_notes = ?, review_time = CURRENT_TIMESTAMP, reviewer = ?
            WHERE id = ?
        ''', (status, review_notes, st.session_state.username, project_id))
        
        # 获取更新后的数据
        c.execute('SELECT github_paths FROM submitted_projects WHERE id = ?', (project_id,))
        github_paths = c.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        # 同步更新到GitHub（如果已连接）
        if github_paths and github_storage.connect():
            try:
                github_paths_list = json.loads(github_paths)
                for github_path in github_paths_list:
                    if github_path:
                        # 获取原始数据
                        data_json = github_storage.get_file_from_github(github_path)
                        if data_json:
                            data = json.loads(data_json)
                            # 更新状态
                            data["status"] = status
                            data["review_notes"] = review_notes
                            data["reviewer"] = st.session_state.username
                            data["review_time"] = get_beijing_time().isoformat()
                            
                            # 保存回GitHub
                            github_storage.save_file_to_github(
                                json.dumps(data, ensure_ascii=False, indent=2),
                                github_path,
                                f"更新审核状态为{status}"
                            )
            except:
                pass
        
        return True
    except Exception as e:
        st.error(f"更新作品状态失败：{str(e)}")
        return False

def download_project_files(project):
    """下载项目文件 - 增强版本，确保用户可下载自己的文件"""
    try:
        # 首先尝试从GitHub下载
        github_files = []
        if project.get('github_paths') and github_storage.connect():
            for i, github_path in enumerate(project['github_paths']):
                if github_path:
                    file_data = github_storage.get_file_from_github(github_path)
                    if file_data:
                        original_filename = project['files'][i] if i < len(project['files']) else f"file_{i+1}"
                        github_files.append((original_filename, file_data))
        
        # 如果GitHub没有文件，尝试本地文件
        if not github_files and project.get('file_paths'):
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, f"{project['project_name']}_files.zip")
            
            # 创建ZIP文件
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, file_path in enumerate(project['file_paths']):
                    if os.path.exists(file_path):
                        original_filename = project['files'][i] if i < len(project['files']) else f"file_{i+1}"
                        zipf.write(file_path, original_filename)
            
            # 读取ZIP文件内容
            with open(zip_path, 'rb') as f:
                zip_data = f.read()
            
            # 清理临时文件
            shutil.rmtree(temp_dir)
            
            return zip_data
        
        # 如果有GitHub文件，创建ZIP
        if github_files:
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, f"{project['project_name']}_files.zip")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename, filedata in github_files:
                    # 将文件数据写入临时文件
                    temp_file_path = os.path.join(temp_dir, filename)
                    with open(temp_file_path, 'wb') as f:
                        f.write(filedata)
                    zipf.write(temp_file_path, filename)
            
            with open(zip_path, 'rb') as f:
                zip_data = f.read()
            
            shutil.rmtree(temp_dir)
            return zip_data
        
        return None
    except Exception as e:
        st.error(f"下载文件失败：{str(e)}")
        return None

def render_my_projects():
    """渲染用户提交记录 - 增强下载功能"""
    st.markdown("<h1 style='color:#dc2626; font-size:2rem;'>📋 我的提交记录</h1>", unsafe_allow_html=True)
    
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.error("🔒 请先登录查看提交记录")
        return
    
    # 返回按钮
    if st.button("← 返回成果展示", width='content'):
        st.session_state.show_my_projects = False
        st.rerun()
    
    # 获取用户ID
    user_id = get_user_id(st.session_state.username)
    if not user_id:
        st.error("无法获取用户信息")
        return
    
    # 获取用户提交的作品
    my_projects = get_submitted_projects(user_id)
    
    if my_projects:
        st.markdown(f"### 📊 提交统计：共提交了 {len(my_projects)} 个作品")
        
        # 统计不同状态的作品数量
        status_counts = {}
        for project in my_projects:
            status = project['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 显示状态统计
        cols = st.columns(3)
        status_labels = {
            "待审核": ("⏳", "orange"),
            "已通过": ("✅", "green"),
            "已拒绝": ("❌", "red")
        }
        
        for idx, (status, count) in enumerate(status_counts.items()):
            with cols[idx % 3]:
                icon, color = status_labels.get(status, ("📌", "blue"))
                st.metric(f"{icon} {status}", count)
        
        st.divider()
        
        # 显示作品列表
        for project in my_projects:
            with st.expander(f"📄 {project['project_name']} - 提交时间：{project['submit_time']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**作者：** {project['author_name']}")
                    st.markdown(f"**作品描述：**")
                    st.info(project['project_desc'])
                    
                    if project['files']:
                        st.markdown(f"**上传文件：**")
                        for i, file in enumerate(project['files']):
                            github_status = "✅" if (project.get('github_paths') and i < len(project['github_paths']) and project['github_paths'][i]) else "❌"
                            st.markdown(f"- 📎 {file} {github_status}")
                
                with col2:
                    # 显示状态
                    status_color = ""
                    if project['status'] == "待审核":
                        status_color = "orange"
                        st.markdown(f"**审核状态：** :{status_color}[{project['status']}]")
                        st.info("您的作品正在等待老师审核，请耐心等待~")
                    elif project['status'] == "已通过":
                        status_color = "green"
                        st.markdown(f"**审核状态：** :{status_color}[{project['status']}]")
                        st.success("🎉 恭喜！您的作品已通过审核！")
                    else:
                        status_color = "red"
                        st.markdown(f"**审核状态：** :{status_color}[{project['status']}]")
                        st.warning("您的作品未通过审核")
                    
                    # 显示审核意见
                    if project['review_notes']:
                        st.markdown(f"**审核意见：**")
                        st.warning(project['review_notes'])
                    
                    if project['review_time']:
                        st.markdown(f"**审核时间：** {project['review_time']}")
                    
                    if project['reviewer']:
                        st.markdown(f"**审核老师：** {project['reviewer']}")
                
                # 下载按钮 - 无论状态如何，用户都可以下载自己提交的文件
                if project['files']:
                    zip_data = download_project_files(project)
                    if zip_data:
                        st.download_button(
                            label="📥 下载我的作品文件",
                            data=zip_data,
                            file_name=f"{project['project_name']}_作品文件.zip",
                            mime="application/zip",
                            key=f"download_{project['id']}"
                        )
                        st.info("💡 您可以随时下载您提交的文件")
    else:
        st.info("📭 您还没有提交过作品，快去【作品征集】页面提交您的第一个作品吧！")

def export_feedback_to_csv(feedback_data):
    """导出反馈数据到CSV - 修复编码问题"""
    try:
        if not feedback_data:
            return None
        
        # 创建StringIO对象
        output = io.StringIO()
        
        # 定义CSV字段
        fieldnames = ["序号", "反馈内容", "提交时间", "IP地址", "用户代理", "GitHub同步"]
        
        # 创建CSV writer，确保正确处理中文
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        # 写入表头
        writer.writeheader()
        
        # 写入数据
        for feedback in feedback_data:
            writer.writerow(feedback)
        
        # 获取CSV字符串并编码为GB18030（兼容GBK和UTF-8）
        csv_str = output.getvalue()
        output.close()
        
        # 编码为GB18030，确保中文正确显示
        csv_bytes = csv_str.encode('gb18030', errors='ignore')
        
        return csv_bytes
    except Exception as e:
        st.error(f"导出CSV失败：{str(e)}")
        return None

def render_admin_dashboard():
    """渲染管理员后台内容"""
    # 页面标题与用户信息
    st.markdown("<h1 style='color:#dc2626; font-size:2rem;'>🔧 管理员后台</h1>", unsafe_allow_html=True)
    st.markdown(f"### 👤 当前登录教师：{st.session_state.username}")
    
    st.markdown("---")
    
    # 返回普通视图按钮
    if st.button("← 返回成果展示", width='content'):
        st.session_state.show_admin = False
        st.rerun()
    
    # 手动同步按钮
    if st.button("🔄 手动同步所有数据到GitHub", type="primary"):
        with st.spinner("正在同步数据到GitHub..."):
            # 同步所有未同步的反馈
            conn = sqlite3.connect('image_processing_platform.db')
            c = conn.cursor()
            c.execute("SELECT id, feedback_content, submit_time, ip_address, user_agent FROM feedback WHERE github_synced = 0")
            unsynced_feedback = c.fetchall()
            
            synced_count = 0
            for row in unsynced_feedback:
                feedback_data = {
                    "content": row[1],
                    "submit_time": format_beijing_time(row[2]),
                    "ip_address": row[3],
                    "user_agent": row[4],
                    "record_id": row[0]
                }
                success, message = sync_data_to_github('feedback', row[0], feedback_data)
                if success:
                    synced_count += 1
            
            if synced_count > 0:
                st.success(f"✅ 已同步 {synced_count} 条反馈数据到GitHub")
            else:
                st.info("没有需要同步的反馈数据")
            conn.close()
    
    # 标签页布局
    admin_tabs = st.tabs(["📝 作品审核", "💬 意见反馈", "📊 平台统计", "🔄 数据同步"])
    
    # 1. 作品审核标签页
    with admin_tabs[0]:
        st.markdown("<h2 style='color:#dc2626;'>📝 作品审核管理</h2>", unsafe_allow_html=True)
        
        # 获取所有提交的作品
        submitted_projects = get_submitted_projects()
        
        if submitted_projects:
            # 创建筛选选项
            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input("搜索作品名称或作者", placeholder="输入关键词...")
            with col2:
                status_filter = st.selectbox("筛选状态", ["全部", "待审核", "已通过", "已拒绝"])
            
            # 筛选作品
            filtered_projects = submitted_projects
            if search_term:
                filtered_projects = [
                    p for p in filtered_projects 
                    if search_term.lower() in p["project_name"].lower() 
                    or search_term.lower() in p["author_name"].lower()
                ]
            
            if status_filter != "全部":
                filtered_projects = [
                    p for p in filtered_projects 
                    if p["status"] == status_filter
                ]
            
            # 显示统计信息
            pending_count = len([p for p in submitted_projects if p["status"] == "待审核"])
            approved_count = len([p for p in submitted_projects if p["status"] == "已通过"])
            rejected_count = len([p for p in submitted_projects if p["status"] == "已拒绝"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("待审核作品", pending_count)
            with col2:
                st.metric("已通过作品", approved_count)
            with col3:
                st.metric("已拒绝作品", rejected_count)
            
            st.divider()
            
            # 显示作品列表
            for project in filtered_projects:
                with st.expander(f"📄 {project['project_name']} - {project['author_name']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**提交时间：** {project['submit_time']}")
                        st.markdown(f"**作品描述：**")
                        st.info(project['project_desc'])
                        
                        if project['files']:
                            st.markdown(f"**上传文件：**")
                            for i, file in enumerate(project['files']):
                                github_status = "✅" if (project.get('github_paths') and i < len(project['github_paths']) and project['github_paths'][i]) else "❌"
                                st.markdown(f"- 📎 {file} {github_status}")
                            
                            # 管理员下载按钮
                            zip_data = download_project_files(project)
                            if zip_data:
                                st.download_button(
                                    label="📥 下载作品文件",
                                    data=zip_data,
                                    file_name=f"{project['project_name']}_作品文件.zip",
                                    mime="application/zip",
                                    key=f"admin_download_{project['id']}"
                                )
                    
                    with col2:
                        # 显示状态标签
                        status_color = ""
                        if project['status'] == "待审核":
                            status_color = "orange"
                        elif project['status'] == "已通过":
                            status_color = "green"
                        else:
                            status_color = "red"
                        st.markdown(f"**审核状态：** :{status_color}[{project['status']}]")
                        
                        if project['review_notes']:
                            st.markdown(f"**审核意见：**")
                            st.warning(project['review_notes'])
                    
                    # 审核操作
                    if project['status'] == "待审核":
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            review_notes = st.text_area(f"审核意见（可选）", key=f"notes_{project['id']}")
                        
                        with col2:
                            if st.button("✅ 通过审核", key=f"approve_{project['id']}"):
                                if update_project_status(project['id'], "已通过", review_notes):
                                    st.success("作品已通过审核！")
                                    st.rerun()
                            
                            if st.button("❌ 拒绝作品", key=f"reject_{project['id']}"):
                                if update_project_status(project['id'], "已拒绝", review_notes):
                                    st.success("作品已拒绝！")
                                    st.rerun()
        else:
            st.info("📭 暂无学生提交的作品")
    
    # 2. 意见反馈标签页 - 修复导出编码问题
    with admin_tabs[1]:
        st.markdown("<h2 style='color:#dc2626;'>💬 意见反馈管理</h2>", unsafe_allow_html=True)
        feedback_data = get_feedback_data()

        if feedback_data:
            # 显示反馈数据表格
            feedback_df = pd.DataFrame(feedback_data)
            st.dataframe(
                feedback_df,
                width='stretch',
                hide_index=True,
                column_config={
                    "序号": st.column_config.NumberColumn("序号", width="small"),
                    "提交时间": st.column_config.DatetimeColumn("提交时间", width="medium", format="YYYY-MM-DD HH:mm:ss"),
                    "反馈内容": st.column_config.TextColumn("反馈内容", width="large"),
                    "IP地址": st.column_config.TextColumn("IP地址", width="medium"),
                    "用户代理": st.column_config.TextColumn("用户代理", width="large"),
                    "GitHub同步": st.column_config.TextColumn("GitHub同步", width="small")
                }
            )

            # 导出反馈数据 - 使用修复的编码函数
            csv_bytes = export_feedback_to_csv(feedback_data)
            if csv_bytes:
                st.download_button(
                    label="📥 导出反馈数据（CSV-GB18030编码）",
                    data=csv_bytes,
                    file_name=f"意见反馈_{get_beijing_time().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # 显示反馈统计
            st.divider()
            st.markdown("#### 📊 反馈统计")
            total_feedback = len(feedback_data)
            synced_feedback = len([f for f in feedback_data if f["GitHub同步"] == "✅"])
            if total_feedback > 0:
                avg_length = sum(len(f["反馈内容"]) for f in feedback_data) / total_feedback
                latest_feedback = feedback_data[0]["提交时间"] if feedback_data else "暂无"
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总反馈数量", total_feedback)
                with col2:
                    st.metric("已同步GitHub", synced_feedback)
                with col3:
                    st.metric("平均字数", f"{avg_length:.0f}字")
                with col4:
                    st.metric("最新反馈", latest_feedback[:10])
        else:
            st.info("📭 暂无用户提交的意见反馈")
    
    # 3. 平台统计标签页
    with admin_tabs[2]:
        st.markdown("<h2 style='color:#dc2626;'>📊 平台基础统计</h2>", unsafe_allow_html=True)
        
        try:
            conn = sqlite3.connect('image_processing_platform.db')
            c = conn.cursor()
            
            # 用户统计
            c.execute("SELECT COUNT(*) FROM users")
            total_users = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
            student_count = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM users WHERE role = 'teacher'")
            teacher_count = c.fetchone()[0]
            
            # 作品统计
            submitted_projects = get_submitted_projects()
            total_projects = len(submitted_projects)
            pending_projects = len([p for p in submitted_projects if p['status'] == '待审核'])
            approved_projects = len([p for p in submitted_projects if p['status'] == '已通过'])
            rejected_projects = len([p for p in submitted_projects if p['status'] == '已拒绝'])
            
            # 反馈统计
            feedback_data = get_feedback_data()
            total_feedback = len(feedback_data)
            
            conn.close()

            # 显示用户统计
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👥 总用户数", total_users)
            with col2:
                st.metric("🎓 学生用户数", student_count)
            with col3:
                st.metric("👨‍🏫 教师用户数", teacher_count)
            
            st.divider()
            
            # 显示作品统计
            st.markdown("#### 📦 作品提交统计")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总提交作品", total_projects)
            with col2:
                st.metric("⏳ 待审核", pending_projects)
            with col3:
                st.metric("✅ 已通过", approved_projects)
            with col4:
                rejection_rate = (rejected_projects / total_projects * 100) if total_projects > 0 else 0
                st.metric("❌ 拒绝率", f"{rejection_rate:.1f}%")
            
            # 作品提交时间线
            if submitted_projects:
                st.divider()
                st.markdown("#### 📈 作品提交时间分布")
                
                # 提取月份信息
                month_counts = {}
                for project in submitted_projects:
                    if project['submit_time']:
                        month = project['submit_time'][:7]  # 取YYYY-MM
                        month_counts[month] = month_counts.get(month, 0) + 1
                
                if month_counts:
                    months = list(month_counts.keys())
                    counts = list(month_counts.values())
                    
                    timeline_df = pd.DataFrame({
                        '月份': months,
                        '作品数量': counts
                    }).sort_values('月份')
                    
                    fig_timeline = px.line(
                        timeline_df,
                        x='月份',
                        y='作品数量',
                        title='作品提交趋势',
                        markers=True,
                        line_shape='spline'
                    )
                    fig_timeline.update_traces(line_color='#dc2626', line_width=3)
                    st.plotly_chart(fig_timeline, width='stretch')
            
            st.divider()
            
            # 显示反馈统计
            st.markdown("#### 💬 意见反馈统计")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("总反馈数量", total_feedback)
            with col2:
                if total_feedback > 0:
                    avg_feedback_len = sum(len(f['反馈内容']) for f in feedback_data) / total_feedback
                    st.metric("平均反馈长度", f"{avg_feedback_len:.0f}字")
                else:
                    st.metric("平均反馈长度", "0字")
            
            # 显示平台运行时间
            st.divider()
            st.markdown("#### 🕒 平台运行信息")
            current_time = get_beijing_time()
            st.markdown(f"**当前服务器时间：** {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**时区：** 北京时间 (UTC+8)")
                
        except Exception as e:
            st.error(f"统计数据加载失败：{str(e)}")
    
    # 4. 数据同步标签页
    with admin_tabs[3]:
        st.markdown("<h2 style='color:#dc2626;'>🔄 数据同步管理</h2>", unsafe_allow_html=True)
        
        # GitHub连接状态
        if github_storage.connect():
            st.success("✅ GitHub仓库连接成功")
            
            # 显示仓库信息
            try:
                repo_info = github_storage.repo
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("仓库名称", repo_info.name)
                with col2:
                    files = github_storage.list_files()
                    st.metric("文件数量", len(files) if files else 0)
                with col3:
                    st.metric("最后更新", repo_info.updated_at.strftime('%Y-%m-%d'))
                
                # 显示最近的同步记录
                conn = sqlite3.connect('image_processing_platform.db')
                c = conn.cursor()
                c.execute('''
                    SELECT table_name, COUNT(*) as count, MAX(synced_at) as last_sync
                    FROM github_sync 
                    GROUP BY table_name
                    ORDER BY last_sync DESC
                ''')
                sync_stats = c.fetchall()
                
                if sync_stats:
                    st.markdown("#### 📊 同步统计")
                    for table_name, count, last_sync in sync_stats:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(f"{table_name}记录数", count)
                        with col2:
                            st.metric("最后同步", format_beijing_time(last_sync))
                        with col3:
                            # 重新同步按钮
                            if st.button(f"🔄 重新同步{table_name}", key=f"resync_{table_name}"):
                                with st.spinner(f"正在同步{table_name}..."):
                                    if table_name == 'feedback':
                                        c.execute("SELECT id FROM feedback")
                                        feedback_ids = c.fetchall()
                                        for (fid,) in feedback_ids:
                                            c.execute("SELECT feedback_content, submit_time, ip_address, user_agent FROM feedback WHERE id = ?", (fid,))
                                            row = c.fetchone()
                                            if row:
                                                feedback_data = {
                                                    "content": row[0],
                                                    "submit_time": format_beijing_time(row[1]),
                                                    "ip_address": row[2],
                                                    "user_agent": row[3],
                                                    "record_id": fid
                                                }
                                                sync_data_to_github('feedback', fid, feedback_data)
                                    elif table_name == 'submitted_projects':
                                        c.execute("SELECT id FROM submitted_projects")
                                        project_ids = c.fetchall()
                                        for (pid,) in project_ids:
                                            c.execute("SELECT project_name, author_name, project_desc, submit_time, status FROM submitted_projects WHERE id = ?", (pid,))
                                            row = c.fetchone()
                                            if row:
                                                project_data = {
                                                    "project_name": row[0],
                                                    "author_name": row[1],
                                                    "project_desc": row[2],
                                                    "submit_time": format_beijing_time(row[3]),
                                                    "status": row[4],
                                                    "record_id": pid
                                                }
                                                sync_data_to_github('submitted_projects', pid, project_data)
                                    st.success(f"✅ {table_name}数据重新同步完成")
                                    st.rerun()
                conn.close()
                
            except Exception as e:
                st.error(f"获取仓库信息失败：{str(e)}")
        else:
            st.warning("⚠️ GitHub仓库未连接")
            st.info("""
            **本地运行模式：**
            - 数据仅保存到本地数据库
            - 部署到Streamlit Cloud时可配置GitHub同步
            
            **Streamlit Cloud配置说明：**
            1. 在Secrets中设置GITHUB_TOKEN
            2. 确保GitHub仓库存在且有写入权限
            3. 配置文件格式：
            ```
            # .streamlit/secrets.toml
            GITHUB_TOKEN = "your_github_personal_access_token"
            ```
            """)

def render_main_content():
    """渲染主要的成果展示内容"""
    # 页面标题
    st.markdown("""
    <div class='modern-header'>
        <h1 >🏆 思政成果展示</h1>
        <p style='font-size: 1.2rem; color: rgba(255,255,255,0.9);'>技术赋能 · 思想引领 · 创新驱动 · 服务国家</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用标签页组织内容
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 优秀作品", "📊 成果分析", "💡 作品征集", "💬 意见反馈"])
    
    # 1. 优秀作品标签页
    with tab1:
        st.markdown("<h2 class='section-title'>🎨 优秀作品展示</h2>", unsafe_allow_html=True)
        
        # 筛选器
        filter_col1, filter_col2 = st.columns([1, 2])
        with filter_col1:
            filter_ideology = st.multiselect(
                "按思政元素筛选",
                options=["工匠精神", "家国情怀", "文化自信", "创新意识", "责任担当", "科学态度", "团队合作"],
                default=[]
            )
        with filter_col2:
            search_term = st.text_input("搜索作品关键词", placeholder="输入作品名称、作者或技术关键词...")
        
        # 获取并展示作品
        projects = generate_projects_data()
        
        # 筛选作品
        filtered_projects = projects
        if filter_ideology:
            filtered_projects = [
                p for p in projects
                if any(ide in p["ideology"] for ide in filter_ideology)
            ]
        
        if search_term:
            filtered_projects = [
                p for p in filtered_projects
                if (search_term.lower() in p["title"].lower() or 
                    search_term.lower() in p["author"].lower() or
                    search_term.lower() in p["tech_highlight"].lower())
            ]
        
        # 展示作品
        if filtered_projects:
            cols = st.columns(2)
            for idx, project in enumerate(filtered_projects):
                with cols[idx % 2]:
                    ideology_badges = ""
                    for ideology in project["ideology"]:
                        badge_class = "ideology-badge"
                        if ideology == "工匠精神":
                            badge_class += " blue"
                        elif ideology == "家国情怀":
                            badge_class += " green"
                        elif ideology == "创新意识":
                            badge_class += " yellow"
                        elif ideology == "文化自信":
                            badge_class += " purple"
                        
                        ideology_badges += f'<span class="{badge_class}">{ideology}</span> '
                    
                    st.markdown(f"""
                    <div class='project-card'>
                        <h3>{project['title']}</h3>
                        <p><strong>👤 作者：</strong>{project['author']}</p>
                        <p><strong>💡 技术亮点：</strong>{project['tech_highlight']}</p>
                        <p><strong>🏷️ 思政元素：</strong>{ideology_badges}</p>
                        <p><strong>📜 项目描述：</strong>{project['description']}</p>
                        <p><strong>🏆 获奖情况：</strong>{project['achievement']}</p>
                        <p><strong>🌍 社会影响：</strong>{project['impact']}</p>
                        <p><strong>📅 完成时间：</strong>{project['date']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("🔍 没有找到符合条件的作品，请调整筛选条件")
    
    # 2. 成果分析标签页
    with tab2:
        st.markdown("<h2 class='section-title'>📊 成果数据分析</h2>", unsafe_allow_html=True)
        
        # 生成图表数据
        ideology_df, type_df = generate_stats_data()
        
        # 创建两列布局
        col_a, col_b = st.columns(2)
        
        with col_a:
            fig1 = px.pie(
                ideology_df,
                values="作品数量",
                names="思政元素",
                title="📈 思政元素分布",
                color_discrete_sequence=px.colors.sequential.Reds
            )
            st.plotly_chart(fig1, width='stretch')
        
        with col_b:
            fig2 = px.bar(
                type_df,
                x="项目类型",
                y="数量",
                title="📊 项目类型分布",
                color="数量",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig2, width='stretch')
        
        # 获奖赛事统计
        st.markdown("<h3 style='color:#dc2626; margin-top: 30px;'>🏅 代表性赛事获奖情况</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #fefaf0, #fdf6e3); padding: 20px; border-radius: 15px; border-left: 5px solid #dc2626;'>
                <h4 style='color:#dc2626; margin: 0 0 10px 0;'>全国大学生计算机设计大赛</h4>
                <p style='margin: 0;'>🏆 一等奖：12项</p>
                <p style='margin: 5px 0 0 0;'>🥈 二等奖：25项</p>
                <p style='margin: 5px 0 0 0;'>🥉 三等奖：18项</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #fefaf0, #fdf6e3); padding: 20px; border-radius: 15px; border-left: 5px solid #3b82f6;'>
                <h4 style='color:#3b82f6; margin: 0 0 10px 0;'>挑战杯全国竞赛</h4>
                <p style='margin: 0;'>🥈 二等奖：8项</p>
                <p style='margin: 5px 0 0 0;'>🥉 三等奖：15项</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #fefaf0, #fdf6e3); padding: 20px; border-radius: 15px; border-left: 5px solid #10b981;'>
                <h4 style='color:#10b981; margin: 0 0 10px 0;'>中国互联网+大赛</h4>
                <p style='margin: 0;'>🏅 金奖：5项</p>
                <p style='margin: 5px 0 0 0;'>🥈 银奖：10项</p>
                <p style='margin: 5px 0 0 0;'>🥉 铜奖：12项</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 3. 作品征集标签页
    with tab3:
        st.markdown("<h2 class='section-title'>💡 作品征集</h2>", unsafe_allow_html=True)
        
        st.info("""
        📢 **征集说明：**
        欢迎提交您的思政与技术融合作品，优秀作品将纳入展示平台。
        作品要求体现技术创新的同时，融入思政元素，展现新时代大学生的责任与担当。
        
        💾 **数据保存说明：**
        - 本地运行：数据保存到本地数据库
        - 云端部署：数据同时保存到本地和GitHub仓库
        - 所有提交的文件都会永久保存
        
        📋 **提交后您可以：**
        1. 在侧边栏点击【我的提交记录】查看审核状态
        2. 无论审核状态如何，您都可以下载自己提交的文件
        3. 查看老师的审核意见
        4. 数据永久保存，随时可访问
        """)
        
        with st.form("project_submit_form"):
            col1, col2 = st.columns(2)
            with col1:
                project_name = st.text_input("📝 作品名称（必填）", placeholder="请输入作品名称...")
            with col2:
                author_name = st.text_input("👤 作者姓名（必填）", placeholder="请输入作者姓名，多人请用逗号分隔...")
            
            project_desc = st.text_area("📄 作品描述（必填）", 
                                      placeholder="请详细描述您的作品，包括：技术原理、创新点、思政元素体现等...",
                                      height=150)
            
            uploaded_files = st.file_uploader(
                "📎 上传相关文件（代码/文档/PPT/图片/视频等）",
                accept_multiple_files=True,
                type=["zip", "rar", "pdf", "doc", "docx", "pptx", "jpg", "jpeg", "png", "gif", "mp4", "avi", "mov"],
                help="支持多种格式文件，建议单个文件不超过20MB。文件将保存到本地数据库。"
            )
            
            submitted = st.form_submit_button("🚀 提交作品", type="primary")
            
            if submitted:
                if project_name and author_name and project_desc:
                    with st.spinner("正在保存作品..."):
                        # 保存上传的文件
                        saved_files = []
                        file_paths = []
                        github_paths = []
                        if uploaded_files:
                            saved_files, file_paths, github_paths = save_uploaded_files(uploaded_files, project_name, author_name)
                        
                        # 构建作品数据
                        project_data = {
                            "project_name": project_name,
                            "author_name": author_name,
                            "project_desc": project_desc,
                            "files": saved_files,
                            "file_paths": file_paths,
                            "github_paths": github_paths
                        }
                        
                        # 保存到数据库和GitHub
                        success, message = save_submitted_project(project_data, uploaded_files)
                        
                        if success:
                            if saved_files:
                                st.success(f"✅ 作品提交成功！{message}")
                                st.markdown("**已上传文件：**")
                                for file in saved_files:
                                    st.markdown(f"- 📎 {file}")
                            else:
                                st.success(f"✅ 作品提交成功！{message}")
                            
                            st.info("💡 您可以在侧边栏点击【我的提交记录】查看审核状态和下载您提交的文件")
                            st.balloons()
                        else:
                            st.error(f"❌ 作品提交失败：{message}")
                else:
                    st.error("⚠️ 请填写作品名称、作者和描述等必填信息")
    
    # 4. 意见反馈标签页
    with tab4:
        st.markdown("<h2 class='section-title'>💬 意见反馈</h2>", unsafe_allow_html=True)
        
        st.info("""
        📝 **反馈说明：**
        请留下您对本平台的建议或想法，帮助我们不断改进。
        您的反馈对我们非常重要！（本功能不收集个人敏感信息）
        
        💾 **数据保存说明：**
        - 本地运行：数据保存到本地数据库
        - 云端部署：数据同时保存到本地和GitHub仓库
        - 所有反馈都会永久保存
        """)
        
        feedback_content = st.text_area(
            "💭 您的反馈内容",
            height=150,
            placeholder="例如：希望增加更多文化传承类作品展示、建议优化搜索功能、希望增加XX功能..."
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("📤 提交反馈", type="primary"):
                if feedback_content.strip():
                    with st.spinner("正在保存反馈..."):
                        success, message = save_feedback_to_db(feedback_content)
                        if success:
                            st.success(f"✅ 感谢您的反馈！{message}")
                            st.balloons()
                        else:
                            st.error(f"❌ 提交失败：{message}")
                else:
                    st.warning("⚠️ 请输入反馈内容后再提交哦~")
        with col2:
            if st.button("🔄 清空内容"):
                st.rerun()

def main():
    # 初始化数据库
    init_database()
    
    # 应用CSS样式
    apply_modern_css()
    
    # 初始化session状态
    if "show_admin" not in st.session_state:
        st.session_state.show_admin = False
    if "show_my_projects" not in st.session_state:
        st.session_state.show_my_projects = False
    
    # 渲染侧边栏
    render_sidebar()
    
    # 根据状态显示不同内容
    if st.session_state.show_admin:
        # 检查是否为教师
        if "logged_in" in st.session_state and st.session_state.logged_in:
            if verify_teacher_role(st.session_state.username):
                render_admin_dashboard()
            else:
                st.error("🚫 权限不足！仅教师账号可访问管理员后台")
                st.session_state.show_admin = False
                st.rerun()
        else:
            st.error("🔒 您尚未登录，请先登录！")
            st.session_state.show_admin = False
            st.rerun()
    elif st.session_state.show_my_projects:
        # 显示用户提交记录
        render_my_projects()
    else:
        # 显示正常的成果展示内容
        render_main_content()

if __name__ == "__main__":
    main()
