import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import sqlite3
import json
import os

st.set_page_config(
    page_title="思政成果展示", 
    page_icon="🏆", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化数据库
def init_database():
    """初始化数据库表"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        # 创建作品提交表
        c.execute('''
            CREATE TABLE IF NOT EXISTS submitted_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                author_name TEXT NOT NULL,
                project_desc TEXT NOT NULL,
                submit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                files TEXT,
                status TEXT DEFAULT '待审核',
                review_notes TEXT,
                review_time TIMESTAMP,
                reviewer TEXT
            )
        ''')
        
        # 创建意见反馈表
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_content TEXT NOT NULL,
                submit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"数据库初始化失败：{str(e)}")

# 渲染侧边栏
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
        
        # 快速导航
        st.markdown("### 🧭 快速导航")
        
        # 修复导航按钮 - 使用正确的页面路径
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
        
        # 检查是否为教师，显示管理员入口
        if "logged_in" in st.session_state and st.session_state.logged_in:
            if verify_teacher_role(st.session_state.username):
                st.markdown("---")
                if st.button("🔧 进入教师后台", use_container_width=True, type="primary"):
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
            if st.button(f"📖 {topic}", key=f"theory_{topic}", use_container_width=True):
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

def get_feedback_data():
    """从数据库读取意见反馈数据"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        c.execute('''
            SELECT id, feedback_content, submit_time, ip_address, user_agent
            FROM feedback
            ORDER BY submit_time DESC
        ''')
        
        feedback_list = []
        for row in c.fetchall():
            feedback_list.append({
                "序号": row[0],
                "反馈内容": row[1],
                "提交时间": row[2],
                "IP地址": row[3] if row[3] else "未知",
                "用户代理": row[4] if row[4] else "未知"
            })
        
        conn.close()
        return feedback_list
    except Exception as e:
        st.error(f"读取反馈数据失败：{str(e)}")
        return []

def save_feedback_to_db(feedback_content):
    """保存反馈到数据库"""
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
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"保存反馈失败：{str(e)}")
        return False

def save_submitted_project(project_data):
    """保存提交的作品到数据库"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        files_str = json.dumps(project_data.get('files', []))
        c.execute('''
            INSERT INTO submitted_projects (project_name, author_name, project_desc, files)
            VALUES (?, ?, ?, ?)
        ''', (project_data['project_name'], project_data['author_name'], 
              project_data['project_desc'], files_str))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"保存作品失败：{str(e)}")
        return False

def get_submitted_projects():
    """获取所有提交的作品"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        c.execute('''
            SELECT id, project_name, author_name, project_desc, 
                   submit_time, files, status, review_notes, review_time, reviewer
            FROM submitted_projects
            ORDER BY submit_time DESC
        ''')
        
        projects = []
        for row in c.fetchall():
            files = json.loads(row[5]) if row[5] else []
            projects.append({
                "id": row[0],
                "project_name": row[1],
                "author_name": row[2],
                "project_desc": row[3],
                "submit_time": row[4],
                "files": files,
                "status": row[6],
                "review_notes": row[7],
                "review_time": row[8],
                "reviewer": row[9]
            })
        
        conn.close()
        return projects
    except Exception as e:
        st.error(f"获取作品失败：{str(e)}")
        return []

def update_project_status(project_id, status, review_notes=""):
    """更新作品审核状态"""
    try:
        conn = sqlite3.connect('image_processing_platform.db')
        c = conn.cursor()
        
        c.execute('''
            UPDATE submitted_projects 
            SET status = ?, review_notes = ?, review_time = CURRENT_TIMESTAMP, reviewer = ?
            WHERE id = ?
        ''', (status, review_notes, st.session_state.username, project_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"更新作品状态失败：{str(e)}")
        return False

def render_admin_dashboard():
    """渲染管理员后台内容"""
    # 页面标题与用户信息
    st.markdown("<h1 style='color:#dc2626; font-size:2rem;'>🔧 管理员后台</h1>", unsafe_allow_html=True)
    st.markdown(f"### 👤 当前登录教师：{st.session_state.username}")
    st.markdown("---")
    
    # 返回普通视图按钮
    if st.button("← 返回成果展示"):
        st.session_state.show_admin = False
        st.rerun()
    
    # 标签页布局
    admin_tabs = st.tabs(["📝 作品审核", "💬 意见反馈", "📊 平台统计"])
    
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
                            st.markdown(f"**上传文件：** {', '.join(project['files'])}")
                    
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
    
    # 2. 意见反馈标签页
    with admin_tabs[1]:
        st.markdown("<h2 style='color:#dc2626;'>💬 意见反馈管理</h2>", unsafe_allow_html=True)
        feedback_data = get_feedback_data()

        if feedback_data:
            feedback_df = pd.DataFrame(feedback_data)
            st.dataframe(
                feedback_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "序号": st.column_config.NumberColumn("序号", width="small"),
                    "提交时间": st.column_config.DatetimeColumn("提交时间", width="medium"),
                    "反馈内容": st.column_config.TextColumn("反馈内容", width="large"),
                    "IP地址": st.column_config.TextColumn("IP地址", width="medium"),
                    "用户代理": st.column_config.TextColumn("用户代理", width="large")
                }
            )

            # 导出反馈数据
            csv = feedback_df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 导出反馈数据（CSV）",
                data=csv,
                file_name=f"意见反馈_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
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
            c.execute("SELECT COUNT(*) FROM feedback")
            total_feedback = c.fetchone()[0]
            
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
            
            st.divider()
            
            # 显示反馈统计
            st.markdown("#### 💬 意见反馈统计")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("总反馈数量", total_feedback)
            with col2:
                avg_feedback_len = sum(len(f['反馈内容']) for f in get_feedback_data()) / max(total_feedback, 1)
                st.metric("平均反馈长度", f"{avg_feedback_len:.0f}字")
                
        except Exception as e:
            st.error(f"统计数据加载失败：{str(e)}")

def render_main_content():
    """渲染主要的成果展示内容"""
    # 页面标题
    st.markdown("""
    <div class='modern-header'>
        <h1 >🏆 思政成果展示</h1>
        <p style='font-size: 1.2rem; color: rgba(255,255,255,0.9);'>技术赋能 · 思想引领 · 创新驱动 · 服务国家</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 总体统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 优秀作品", "156个", "+28个")
    with col2:
        st.metric("🏅 获得奖项", "86项", "+15项")
    with col3:
        st.metric("💡 技术创新", "245项", "+42项")
    with col4:
        st.metric("🌟 思政融合", "100%", "深度融合")
    
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
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_b:
            fig2 = px.bar(
                type_df,
                x="项目类型",
                y="数量",
                title="📊 项目类型分布",
                color="数量",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
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
                "📎 上传相关文件（代码/文档/PPT等）",
                accept_multiple_files=True,
                type=["zip", "rar", "pdf", "doc", "docx", "pptx", "jpg", "png", "mp4"],
                help="支持多种格式文件，单个文件大小建议不超过20MB"
            )
            
            submitted = st.form_submit_button("🚀 提交作品", type="primary")
            
            if submitted:
                if project_name and author_name and project_desc:
                    # 保存上传的文件名
                    file_names = []
                    if uploaded_files:
                        for file in uploaded_files:
                            # 这里可以添加保存文件的逻辑
                            file_names.append(file.name)
                    
                    # 构建作品数据
                    project_data = {
                        "project_name": project_name,
                        "author_name": author_name,
                        "project_desc": project_desc,
                        "files": file_names
                    }
                    
                    # 保存到数据库
                    if save_submitted_project(project_data):
                        if file_names:
                            st.success(f"✅ 作品提交成功！已上传文件：{', '.join(file_names)}")
                        else:
                            st.success("✅ 作品提交成功！我们将尽快审核~")
                        st.balloons()
                    else:
                        st.error("❌ 作品提交失败，请稍后重试")
                else:
                    st.error("⚠️ 请填写作品名称、作者和描述等必填信息")
    
    # 4. 意见反馈标签页
    with tab4:
        st.markdown("<h2 class='section-title'>💬 意见反馈</h2>", unsafe_allow_html=True)
        
        st.info("""
        📝 **反馈说明：**
        请留下您对本平台的建议或想法，帮助我们不断改进。
        您的反馈对我们非常重要！（本功能不收集个人敏感信息）
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
                    if save_feedback_to_db(feedback_content):
                        st.success("✅ 感谢您的反馈！我们会认真参考~")
                        st.balloons()
                    else:
                        st.error("❌ 提交失败，请稍后重试")
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
    else:
        # 显示正常的成果展示内容
        render_main_content()

if __name__ == "__main__":
    main()
