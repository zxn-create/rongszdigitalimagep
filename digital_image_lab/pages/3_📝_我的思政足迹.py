import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sqlite3
import pytz  # 新增：用于时区处理

st.set_page_config(
    page_title="我的思政足迹", 
    page_icon="📝", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 获取北京时间
def get_beijing_time():
    """获取北京时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(beijing_tz)

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
    
    /* 足迹卡片样式 */
    .footprint-card {
        background: linear-gradient(135deg, #fff, var(--beige-light));
        padding: 30px;
        border-radius: 20px;
        border-left: 5px solid var(--primary-red);
        margin: 20px 0;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
        border: 1px solid #e5e7eb;
    }
    
    .footprint-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--hover-shadow);
    }
    
    .record-item {
        background: linear-gradient(135deg, #fff, var(--beige-light));
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .record-item:hover {
        transform: translateX(5px);
        box-shadow: var(--hover-shadow);
    }
    
    .section-title {
        color: var(--primary-red);
        font-size: 2rem;
        margin: 30px 0 20px 0;
        border-bottom: 3px solid #e5e7eb;
        padding-bottom: 10px;
        font-weight: 700;
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
    
    /* 侧边栏样式 - 米色渐变 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #fdf6e3 0%, #faf0d9 50%, #f5e6c8 100%) !important;
    }
    
    .css-1d391kg {
        background: linear-gradient(135deg, #fdf6e3 0%, #faf0d9 50%, #f5e6c8 100%) !important;
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
    
    /* 成就徽章 */
    .achievement-badge {
        background: linear-gradient(135deg, var(--gold), #b8860b);
        color: white;
        padding: 8px 16px;
        border-radius: 25px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
        text-align: center;
        margin: 5px;
    }
    
    /* 状态标签样式 */
    .status-pending {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-reviewed {
        background: linear-gradient(135deg, #10b981, #047857);
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-returned {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* 字数统计样式 */
    .word-count {
        font-size: 0.9rem;
        color: #6b7280;
        text-align: right;
        margin-top: 5px;
    }
    
    .word-count.valid {
        color: #10b981;
    }
    
    .word-count.invalid {
        color: #ef4444;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .subtitle {
            font-size: 1.1rem;
        }
        .footprint-card {
            padding: 20px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 数据库操作函数
def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect('image_processing_platform.db')

def init_database():
    """初始化数据库表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建思政感悟表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ideology_reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_username TEXT NOT NULL,
            reflection_content TEXT NOT NULL,
            submission_time TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            teacher_feedback TEXT DEFAULT '',
            score INTEGER DEFAULT 0,
            word_count INTEGER DEFAULT 0,
            allow_view_score BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (student_username) REFERENCES users (username)
        )
    """)
    
    conn.commit()
    conn.close()

def get_ideology_reflections(student_username=None):
    """获取思政感悟记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if student_username:
        # 获取特定学生的记录
        cursor.execute("""
            SELECT * FROM ideology_reflections 
            WHERE student_username = ? 
            ORDER BY submission_time DESC
        """, (student_username,))
    else:
        # 获取所有学生的记录（教师端）
        cursor.execute("""
            SELECT * FROM ideology_reflections 
            ORDER BY submission_time DESC
        """)
    
    records = cursor.fetchall()
    conn.close()
    
    # 转换为字典列表
    columns = ['id', 'student_username', 'reflection_content', 'submission_time', 
               'status', 'teacher_feedback', 'score', 'word_count', 'allow_view_score']
    result = []
    for record in records:
        result.append(dict(zip(columns, record)))
    
    return result

def get_all_students():
    """获取所有学生列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT username FROM users WHERE role = 'student'")
    students = cursor.fetchall()
    conn.close()
    
    return [student[0] for student in students]

def add_ideology_reflection(student_username, reflection_content):
    """添加思政感悟记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 使用北京时间
    submission_time = get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')
    word_count = len(reflection_content.strip())
    
    cursor.execute("""
        INSERT INTO ideology_reflections 
        (student_username, reflection_content, submission_time, word_count)
        VALUES (?, ?, ?, ?)
    """, (student_username, reflection_content, submission_time, word_count))
    
    conn.commit()
    conn.close()

def update_reflection_status(reflection_id, status, teacher_feedback="", score=0, allow_view_score=True):
    """更新思政感悟状态（教师评分/退回）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE ideology_reflections 
        SET status = ?, teacher_feedback = ?, score = ?, allow_view_score = ?
        WHERE id = ?
    """, (status, teacher_feedback, score, allow_view_score, reflection_id))
    
    conn.commit()
    conn.close()

def delete_reflection(reflection_id):
    """删除思政感悟记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM ideology_reflections WHERE id = ?", (reflection_id,))
    
    conn.commit()
    conn.close()

def get_student_stats(student_username):
    """获取学生统计数据 - 修复版"""
    reflections = get_ideology_reflections(student_username)
    
    total_reflections = len(reflections)
    pending_count = len([r for r in reflections if r['status'] == 'pending'])
    reviewed_count = len([r for r in reflections if r['status'] == 'reviewed'])
    returned_count = len([r for r in reflections if r['status'] == 'returned'])
    
    # 计算平均分，只计算已评分且分数大于0的记录
    scored_reflections = [r for r in reflections if r['score'] > 0]
    avg_score = np.mean([r['score'] for r in scored_reflections]) if scored_reflections else 0
    
    return {
        'total_reflections': total_reflections,
        'pending_count': pending_count,
        'reviewed_count': reviewed_count,
        'returned_count': returned_count,
        'avg_score': round(avg_score, 1)
    }

def get_class_stats():
    """获取班级统计数据 - 修复版"""
    all_reflections = get_ideology_reflections()
    all_students = get_all_students()
    
    total_reflections = len(all_reflections)
    total_students = len(all_students)
    pending_count = len([r for r in all_reflections if r['status'] == 'pending'])
    reviewed_count = len([r for r in all_reflections if r['status'] == 'reviewed'])
    returned_count = len([r for r in all_reflections if r['status'] == 'returned'])
    
    # 计算平均分，只计算已评分且分数大于0的记录
    scored_reflections = [r for r in all_reflections if r['score'] > 0]
    avg_score = np.mean([r['score'] for r in scored_reflections]) if scored_reflections else 0
    
    # 计算提交率
    students_with_submissions = len(set([r['student_username'] for r in all_reflections]))
    submission_rate = round((students_with_submissions / total_students) * 100, 1) if total_students > 0 else 0
    
    return {
        'total_reflections': total_reflections,
        'total_students': total_students,
        'pending_count': pending_count,
        'reviewed_count': reviewed_count,
        'returned_count': returned_count,
        'avg_score': round(avg_score, 1),
        'submission_rate': submission_rate
    }

# 初始化session state
if 'learning_records' not in st.session_state:
    st.session_state.learning_records = []

if 'view_record_id' not in st.session_state:
    st.session_state.view_record_id = None

if 'edit_record_id' not in st.session_state:
    st.session_state.edit_record_id = None

# 生成模拟学习数据
def generate_sample_data():
    topics = [
        "图像边缘检测技术", "数字图像增强方法", "计算机视觉基础", 
        "OpenCV实战应用", "图像分割算法", "特征提取技术",
        "机器学习在图像处理中的应用", "深度学习与计算机视觉"
    ]
    
    ideologies = ["工匠精神", "科学态度", "创新意识", "家国情怀", "团队合作", "责任担当", "追求卓越", "技术报国"]
    
    reflections = [
        "通过本次学习，我深刻体会到技术研发需要精益求精的工匠精神。每一个参数的调整，每一行代码的优化，都体现了对完美的追求。在图像处理实验中，我反复调试算法参数，最终实现了更好的处理效果，这让我明白了坚持和耐心的重要性。",
        "科学态度的培养让我明白，图像处理不仅是技术活，更是科学探索。需要严谨的实验设计和数据分析。通过系统的学习和实践，我掌握了科学的研究方法，这对我的专业成长具有重要意义。",
        "创新意识的激发让我在传统算法基础上进行了改进，这种突破常规的思维方式让我受益匪浅。在项目实践中，我结合多种技术手段，创造性地解决了实际问题，体会到了技术创新的魅力。",
        "学习过程中，我深深感受到科技工作者的家国情怀。我们要用所学技术为国家发展贡献力量。作为新时代的青年，我们应该将个人理想与国家需求相结合，在技术领域做出自己的贡献。",
        "团队合作让我认识到，优秀的技术成果往往来自于集体的智慧和协作。在与同学的合作中，我们互相学习、共同进步，完成了复杂的图像处理项目，这让我体会到了团队力量的重要性。",
        "作为新时代的技术人才，我们要勇于承担技术发展的责任，用技术解决实际问题。通过本课程的学习，我不仅掌握了专业技能，更培养了社会责任感和使命感。"
    ]
    
    data = []
    for i in range(30):
        date = get_beijing_time() - timedelta(days=29-i)
        topic = np.random.choice(topics)
        ideology = np.random.choice(ideologies)
        duration = round(np.random.uniform(0.5, 4.0), 1)
        reflection = np.random.choice(reflections)
        
        data.append({
            'date': date,
            'topic': topic,
            'ideology': ideology,
            'duration': duration,
            'reflection': reflection,
            'rating': np.random.randint(3, 6)
        })
    
    return data

# 查看记录详情
def view_record_detail(record):
    """查看记录详情"""
    st.markdown(f"""
    <div class='footprint-card'>
        <h2>📋 学习记录详情</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**👤 提交学生:** {record['student_username']}")
        st.markdown(f"**📅 提交时间:** {record['submission_time']}")
        st.markdown(f"**📊 字数统计:** {record['word_count']} 字")
    
    with col2:
        status_display = {
            'pending': '⏳ 待审核',
            'reviewed': '✅ 已审核', 
            'returned': '↩️ 已退回'
        }
        st.markdown(f"**📝 审核状态:** {status_display.get(record['status'], record['status'])}")
        
        if record['score'] > 0:
            st.markdown(f"**⭐ 评分:** {record['score']} 分")
        
        if record['teacher_feedback']:
            st.markdown(f"**💬 教师反馈:** {record['teacher_feedback']}")
    
    st.markdown("---")
    st.markdown(f"**💭 心得体会:**")
    st.info(record['reflection_content'])
    
    # 操作按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("↩️ 返回记录列表", width='stretch'):
            st.session_state.view_record_id = None
            st.rerun()

# 教师评分界面
def teacher_review_interface(record):
    """教师评分界面"""
    st.markdown('<div class="section-title">👨‍🏫 审核学生感悟</div>', unsafe_allow_html=True)
    
    # 学生信息概览
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**👤 学生:** {record['student_username']}")
    with col2:
        st.markdown(f"**📅 提交时间:** {record['submission_time']}")
    with col3:
        st.markdown(f"**📊 字数:** {record['word_count']} 字")
    
    st.markdown("### 💭 学生感悟内容")
    st.text_area("感悟内容", record['reflection_content'], height=200, disabled=True, key="review_content")
    
    # 字数统计显示
    word_count = len(record['reflection_content'].strip())
    word_status = "✅ 符合要求" if word_count >= 60 else "❌ 字数不足"
    st.markdown(f"**📊 字数统计:** {word_count} 字 ({word_status})")
    
    st.markdown("### 📝 审核评价")
    
    with st.form(f"review_form_{record['id']}"):
        score = st.slider("评分", 0, 100, record['score'] if record['score'] else 60, key=f"score_{record['id']}")
        feedback = st.text_area("教师反馈", record['teacher_feedback'] if record['teacher_feedback'] else "", 
                               placeholder="请输入对学生的反馈和建议...", key=f"feedback_{record['id']}")
        allow_view_score = st.checkbox("允许学生查看分数", value=record['allow_view_score'] if record['allow_view_score'] else True, 
                                      key=f"allow_view_{record['id']}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            submit_review = st.form_submit_button("✅ 通过审核", width='stretch')
        with col2:
            submit_return = st.form_submit_button("↩️ 退回修改", width='stretch')
        with col3:
            cancel_review = st.form_submit_button("❌ 取消", width='stretch')
        with col4:
            # 添加返回按钮
            return_button = st.form_submit_button("🔙 返回列表", width='stretch')
        
        if submit_review:
            update_reflection_status(record['id'], 'reviewed', feedback, score, allow_view_score)
            st.success("✅ 已成功审核通过！")
            st.rerun()
        
        if submit_return:
            update_reflection_status(record['id'], 'returned', feedback, 0, False)
            st.success("↩️ 已退回给学生修改！")
            st.rerun()
        
        if cancel_review:
            st.rerun()
            
        if return_button:
            st.session_state.edit_record_id = None
            st.rerun()
    
    # 在表单外也添加一个独立的返回按钮，方便用户操作
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("↩️ 返回审核列表", width='stretch', key="return_to_list"):
            st.session_state.edit_record_id = None
            st.rerun()

# 渲染侧边栏
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; 
            padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px;
            box-shadow: 0 6px 12px rgba(220, 38, 38, 0.3);'>
            <h3>📝 思政足迹</h3>
            <p style='margin: 10px 0 0 0; font-size: 1rem;'>记录成长 · 内化价值 · 见证进步</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 快速导航
        st.markdown("### 🧭 快速导航")
        
        # 修复导航按钮 - 使用正确的页面路径
        if st.button("🏠 返回首页", width='stretch'):
            st.switch_page("main.py")
        if st.button("🔬 图像处理实验室", width='stretch'):
            st.switch_page("pages/1_🔬_图像处理实验室.py")
        if st.button("📝 智能与传统图片处理", use_container_width=True):
            # 使用JavaScript在新标签页打开链接
            js = """<script>window.open("https://29phcdb33h.coze.site", "_blank");</script>"""
            st.components.v1.html(js, height=0)
        if st.button("🏫加入班级与在线签到", width='stretch'):
            st.switch_page("pages/分班和在线签到.py")
        if st.button("📤 实验作业提交", width='stretch'):
            st.switch_page("pages/实验作业提交.py")
        if st.button("📚 学习资源中心", width='stretch'):
            st.switch_page("pages/2_📚_学习资源中心.py")
        if st.button("📝 我的思政足迹", width='stretch'):
            st.switch_page("pages/3_📝_我的思政足迹.py")
        if st.button("🏆 成果展示", width='stretch'):
            st.switch_page("pages/4_🏆_成果展示.py")
        
        # 个人成就统计（学生端显示）
        if st.session_state.get('logged_in') and st.session_state.get('role') == 'student':
            st.markdown("### 🏆 个人成就")
            
            stats = get_student_stats(st.session_state.username)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("总提交", stats['total_reflections'])
            with col2:
                st.metric("平均分", stats['avg_score'])
            
            st.markdown(f"**待审核:** {stats['pending_count']}")
            st.markdown(f"**已审核:** {stats['reviewed_count']}")
            if stats['returned_count'] > 0:
                st.markdown(f"**已退回:** {stats['returned_count']}")
        
        # 教师端统计
        elif st.session_state.get('logged_in') and st.session_state.get('role') == 'teacher':
            st.markdown("### 📊 班级统计")
            
            class_stats = get_class_stats()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("总学生数", class_stats['total_students'])
                st.metric("待审核", class_stats['pending_count'])
            with col2:
                st.metric("提交率", f"{class_stats['submission_rate']}%")
                st.metric("已审核", class_stats['reviewed_count'])
        
        st.markdown("---")
        
        # 学习提醒
        st.markdown("### ⏰ 学习提醒")
        st.info("""
        📅 **今日建议：**
        - 完成图像分割实验
        - 阅读科学家故事
        - 撰写技术感悟
        - 注意感悟内容不少于60字
        """)
        
        # 记录指南
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fee2e2, #fecaca); padding: 20px; 
                    border-radius: 12px; border-left: 4px solid #dc2626; margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);'>
            <h4 style='color: #dc2626;'>📝 记录指南</h4>
            <ol style='padding-left: 20px; color: #7f1d1d;'>
                <li style='color: #dc2626;'>记录学习主题</li>
                <li style='color: #dc2626;'>关联思政元素</li>
                <li style='color: #dc2626;'>撰写心得体会（不少于60字）</li>
                <li style='color: #dc2626;'>总结技术收获</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # 系统信息
        st.markdown("---")
        st.markdown("**📊 系统信息**")
        current_time = get_beijing_time().strftime('%Y-%m-%d %H:%M')
        st.text(f"时间: {current_time}")
        st.text("状态: 🟢 正常运行")
        st.text("版本: v2.1.0")

# 学习分析功能（学生和教师共用）
def render_learning_analysis():
    """渲染学习分析页面"""
    st.markdown('<div class="section-title">📊 学习数据分析</div>', unsafe_allow_html=True)
    
    # 生成样本数据用于展示
    sample_data = generate_sample_data()
    df = pd.DataFrame(sample_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 学习时长趋势图
        weekly_data = df.groupby(pd.Grouper(key='date', freq='W'))['duration'].sum().reset_index()
        fig1 = px.line(
            weekly_data, 
            x='date', 
            y='duration',
            title='📈 每周学习时长趋势',
            labels={'date': '日期', 'duration': '学习时长(小时)'}
        )
        fig1.update_traces(line_color='#dc2626', line_width=3)
        st.plotly_chart(fig1, width='stretch')
    
    with col2:
        # 思政关联分布
        ideology_counts = df['ideology'].value_counts()
        fig2 = px.pie(
            values=ideology_counts.values,
            names=ideology_counts.index,
            title='🇨🇳 思政关联分布',
            color_discrete_sequence=px.colors.sequential.Reds
        )
        st.plotly_chart(fig2, width='stretch')
    
    # 学习主题词云（模拟）
    st.markdown("### 🔥 热门学习主题")
    topics = ["图像处理", "边缘检测", "OpenCV", "机器学习", "深度学习", "计算机视觉", "算法优化", "技术创新"]
    cols = st.columns(4)
    for i, topic in enumerate(topics):
        with cols[i % 4]:
            st.markdown(f"""
            <div style='text-align: center; padding: 10px; background: linear-gradient(135deg, #fef2f2, #fff); 
                        border-radius: 10px; margin: 5px; border: 1px solid #fecaca;'>
                <h4>{topic}</h4>
                <p>学习次数: {np.random.randint(5, 20)}</p>
            </div>
            """, unsafe_allow_html=True)


# 历史记录功能（学生和教师共用）
def render_history_records():
    """渲染历史记录页面"""
    st.markdown('<div class="section-title">📚 学习历史记录</div>', unsafe_allow_html=True)
    
    # 根据角色获取记录
    if st.session_state.get('role') == 'student':
        records = get_ideology_reflections(st.session_state.username)
        title = f"您的学习记录 ({len(records)}条)"
    else:  # 教师
        records = get_ideology_reflections()
        title = f"全班学习记录 ({len(records)}条)"
    
    if records or (st.session_state.get('role') == 'student' and st.session_state.learning_records):
        st.markdown(f"### {title}")
        
        # 显示数据库记录
        for record in records:
            with st.container():
                # 使用Streamlit原生组件代替HTML
                with st.container():
                    st.markdown(f"### 👤 {record['student_username']} 的感悟")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**📅 提交时间：** {record['submission_time']}")
                        st.markdown(f"**📊 字数：** {record['word_count']}字")
                    with col2:
                        # 显示状态徽章
                        if record['status'] == 'pending':
                            st.markdown('<span class="status-pending">⏳ 待审核</span>', unsafe_allow_html=True)
                        elif record['status'] == 'reviewed':
                            st.markdown('<span class="status-reviewed">✅ 已审核</span>', unsafe_allow_html=True)
                        elif record['status'] == 'returned':
                            st.markdown('<span class="status-returned">↩️ 已退回</span>', unsafe_allow_html=True)
                    
                    # 显示分数（如果已评分）
                    if record['score'] > 0:
                        if st.session_state.get('role') == 'student' and record['allow_view_score']:
                            st.markdown(f"**⭐ 分数：** {record['score']}分")
                        elif st.session_state.get('role') == 'teacher':
                            st.markdown(f"**⭐ 分数：** {record['score']}分")
                        elif st.session_state.get('role') == 'student' and not record['allow_view_score']:
                            st.markdown("**⭐ 分数：** 教师设置不可见")
                    
                    st.markdown(f"**💭 感悟内容：** {record['reflection_content'][:150]}...")
                    st.markdown("---")

                    
                    # 操作按钮
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("👁️ 查看详情", key=f"view_db_{record['id']}", width='stretch'):
                            st.session_state.view_record_id = record
                            st.rerun()
                    with col2:
                        if st.session_state.get('role') == 'teacher':
                            if st.button("📝 审核评分", key=f"review_db_{record['id']}", width='stretch'):
                                st.session_state.edit_record_id = record
                                st.rerun()
                        elif st.session_state.get('role') == 'student' and record['status'] == 'pending':
                            if st.button("🗑️ 撤回", key=f"delete_db_{record['id']}", width='stretch'):
                                delete_reflection(record['id'])
                                st.success("✅ 记录已成功撤回！")
                                st.rerun()
                    with col3:
                        if record['status'] == 'returned' and record['teacher_feedback']:
                            st.info(f"教师反馈: {record['teacher_feedback']}")
                    
                    st.markdown("---")
        
        # 显示本地记录（仅学生端，兼容旧版本）
        if st.session_state.get('role') == 'student' and st.session_state.learning_records:
            st.markdown("### 本地学习记录")
            sorted_records = sorted(st.session_state.learning_records, 
                                  key=lambda x: x['timestamp'], reverse=True)
            
            for i, record in enumerate(sorted_records):
                with st.container():
                    word_count = len(record['reflection'].strip())
                    word_status = "✅" if word_count >= 60 else "⚠️"
                    
                    st.markdown(f"""
                    <div class='record-item'>
                        <div style='display: flex; justify-content: space-between; align-items: start;'>
                            <div style='flex: 1;'>
                                <h4>🎯 {record['topic']}</h4>
                                <p><strong>📅 日期：</strong>{record['date']} | 
                                   <strong>⏰ 时长：</strong>{record['duration']}小时 | 
                                   <strong>⭐ 评分：</strong>{'★' * record['satisfaction']}</p>
                                <p><strong>🇨🇳 思政关联：</strong>{', '.join([f'<span class="badge">{item}</span>' for item in record['ideology']])}</p>
                                <p><strong>📊 字数：</strong>{word_status} {word_count}字</p>
                            </div>
                            <div style='text-align: right;'>
                                <span class='achievement-badge'>本地记录</span>
                            </div>
                        </div>
                        <div style='margin-top: 15px;'>
                            <p><strong>💭 学习感悟：</strong>{record['reflection'][:100]}...</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 查看和删除按钮
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("👁️ 查看详情", key=f"view_local_{i}", width='stretch'):
                            st.session_state.view_record_id = {
                                'student_username': st.session_state.username,
                                'submission_time': record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                                'reflection_content': record['reflection'],
                                'status': 'local',
                                'score': 0,
                                'word_count': word_count,
                                'teacher_feedback': ''
                            }
                            st.rerun()
                    with col3:
                        if st.button("🗑️ 删除", key=f"delete_local_{i}", width='stretch'):
                            del st.session_state.learning_records[i]
                            st.success("✅ 记录已成功删除！")
                            st.rerun()
                    
                    st.markdown("---")
    else:
        st.info("📝 暂无学习记录")

# 成长成就功能（学生和教师共用）
def render_achievements():
    """渲染成长成就页面"""
    st.markdown('<div class="section-title">🏆 成长成就展示</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.get('role') == 'student':
            stats = get_student_stats(st.session_state.username)
            st.markdown(f"""
            <div class='footprint-card'>
                <h3>🎯 学习里程碑</h3>
                <div style='margin: 20px 0;'>
                    <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
                        <span>🔮 累计提交目标</span>
                        <span style='color: var(--primary-red); font-weight: bold;'>{stats['total_reflections']}/10篇</span>
                    </div>
                    <div style='background: #f1f5f9; border-radius: 10px; height: 10px;'>
                        <div style='background: linear-gradient(135deg, var(--primary-red), var(--accent-red)); 
                                    height: 100%; width: {min(stats['total_reflections'] * 10, 100)}%; border-radius: 10px;'></div>
                    </div>
                </div>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px;'>
                    <div style='text-align: center;'>
                        <h4 style='color: var(--primary-red); margin: 0;'>{stats['total_reflections']}</h4>
                        <p style='margin: 0; font-size: 0.8rem;'>总提交</p>
                    </div>
                    <div style='text-align: center;'>
                        <h4 style='color: var(--primary-red); margin: 0;'>{stats['avg_score']}</h4>
                        <p style='margin: 0; font-size: 0.8rem;'>平均分</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:  # 教师端
            class_stats = get_class_stats()
            st.markdown(f"""
            <div class='footprint-card'>
                <h3>🎯 班级里程碑</h3>
                <div style='margin: 20px 0;'>
                    <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
                        <span>🔮 提交率目标</span>
                        <span style='color: var(--primary-red); font-weight: bold;'>{class_stats['submission_rate']}/100%</span>
                    </div>
                    <div style='background: #f1f5f9; border-radius: 10px; height: 10px;'>
                        <div style='background: linear-gradient(135deg, var(--primary-red), var(--accent-red)); 
                                    height: 100%; width: {class_stats['submission_rate']}%; border-radius: 10px;'></div>
                    </div>
                </div>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px;'>
                    <div style='text-align: center;'>
                        <h4 style='color: var(--primary-red); margin: 0;'>{class_stats['total_reflections']}</h4>
                        <p style='margin: 0; font-size: 0.8rem;'>总提交</p>
                    </div>
                    <div style='text-align: center;'>
                        <h4 style='color: var(--primary-red); margin: 0;'>{class_stats['avg_score']}</h4>
                        <p style='margin: 0; font-size: 0.8rem;'>平均分</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px;'>
                <div class='achievement-badge'>🌟 技术达人</div>
                <div class='achievement-badge'>🎓 学习先锋</div>
                <div class='achievement-badge'>💡 创新之星</div>
                <div class='achievement-badge'>🇨🇳 思政标兵</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='footprint-card'>
            <h3>📈 能力雷达图</h3>
            <div style='text-align: center; margin: 20px 0;'>
                <p>技术能力: ⭐⭐⭐⭐⭐</p>
                <p>创新思维: ⭐⭐⭐⭐</p>
                <p>科学素养: ⭐⭐⭐⭐⭐</p>
                <p>团队协作: ⭐⭐⭐⭐</p>
                <p>责任担当: ⭐⭐⭐⭐⭐</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 优秀学习案例展示
    st.markdown("### 🌟 优秀学习案例")
    
    excellent_cases = [
        {
            "title": "图像处理中的工匠精神实践",
            "student": "张明",
            "description": "通过精细调整图像处理参数，实现了95%的准确率提升",
            "achievement": "校级技术竞赛一等奖"
        },
        {
            "title": "基于深度学习的创新应用",
            "student": "李华", 
            "description": "将传统算法与深度学习结合，提出创新解决方案",
            "achievement": "国家发明专利"
        },
        {
            "title": "技术报国项目实践",
            "student": "王伟",
            "description": "参与国家重点研发计划，用图像处理技术解决实际问题",
            "achievement": "优秀项目贡献奖"
        }
    ]
    
    for case in excellent_cases:
        with st.container():
            st.markdown(f"""
            <div class='record-item'>
                <h4>🏅 {case['title']}</h4>
                <p><strong>👤 学生：</strong>{case['student']}</p>
                <p><strong>📝 成果描述：</strong>{case['description']}</p>
                <p><strong>🎖️ 获得荣誉：</strong><span style='color: var(--gold); font-weight: bold;'>{case['achievement']}</span></p>
            </div>
            """, unsafe_allow_html=True)

# 学生端界面
def render_student_interface():
    """渲染学生端界面"""
    # 学习统计 - 使用修复后的统计数据
    stats = get_student_stats(st.session_state.username)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 总提交数", stats['total_reflections'])
    with col2:
        st.metric("⏳ 待审核", stats['pending_count'])
    with col3:
        st.metric("✅ 已审核", stats['reviewed_count'])
    with col4:
        st.metric("⭐ 平均分", stats['avg_score'])
    
    # 使用标签页组织内容
    tab1, tab2, tab3, tab4 = st.tabs(["✍️ 记录感悟", "📊 学习分析", "📚 历史记录", "🏆 成长成就"])
    
    with tab1:
        st.markdown('<div class="section-title">✍️ 记录学习感悟</div>', unsafe_allow_html=True)
        
        with st.form("learning_record", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("📅 学习日期", get_beijing_time().date())
                topic = st.text_input("🎯 学习主题", placeholder="例如：图像边缘检测技术与工匠精神")
                learning_type = st.selectbox(
                    "📖 学习类型",
                    ["技术实验", "理论学习", "项目实践", "思政学习", "技术研讨", "创新探索"]
                )
            
            with col2:
                ideology_connection = st.multiselect(
                    "🇨🇳 思政关联",
                    ["工匠精神", "科学态度", "创新意识", "家国情怀", "团队合作", "责任担当", "追求卓越", "技术报国"],
                    default=["工匠精神"]
                )
                learning_time = st.slider("⏰ 学习时长(小时)", 0.5, 8.0, 2.0, 0.5)
                satisfaction = st.slider("⭐ 学习满意度", 1, 5, 4)
            
            reflection = st.text_area(
                "💭 心得体会", 
                placeholder="""
请详细记录您的学习收获、技术体会和思政感悟...
（注意：内容不少于60字）

例如：
1. 技术层面：掌握了什么新技术？解决了什么技术难题？
2. 思想层面：对工匠精神/科学态度等有什么新的理解？
3. 实践层面：如何将思政元素融入技术实践？
4. 成长层面：这次学习对个人成长有什么帮助？
                """,
                height=200,
                key="reflection_input"
            )
            
            # 实时字数统计
            if reflection:
                word_count = len(reflection.strip())
                word_class = "valid" if word_count >= 60 else "invalid"
                status_icon = "✅" if word_count >= 60 else "❌"
                st.markdown(f'<div class="word-count {word_class}">{status_icon} 当前字数: {word_count} / 60</div>', unsafe_allow_html=True)
            
            # 技术收获
            tech_gains = st.text_area(
                "💻 技术收获",
                placeholder="记录具体的技术知识点、算法理解、代码实现等...",
                height=100
            )
            
            submitted = st.form_submit_button("💾 提交学习记录", width='stretch')
            if submitted:
                if reflection.strip():
                    word_count = len(reflection.strip())
                    if word_count < 60:
                        st.error(f"❌ 思政感悟内容不少于60字，当前字数：{word_count}字，请补充完善后再提交。")
                    else:
                        # 保存到数据库
                        add_ideology_reflection(st.session_state.username, reflection)
                        
                        # 同时保存到session state（用于本地展示）
                        new_record = {
                            'date': date,
                            'topic': topic,
                            'type': learning_type,
                            'ideology': ideology_connection,
                            'duration': learning_time,
                            'satisfaction': satisfaction,
                            'reflection': reflection,
                            'tech_gains': tech_gains,
                            'timestamp': get_beijing_time()
                        }
                        st.session_state.learning_records.append(new_record)
                        
                        st.success("🎉 学习记录已成功提交！您的成长足迹又增添了一笔宝贵经历。")
                        st.balloons()
                else:
                    st.error("❌ 请填写心得体会内容")
    
    with tab2:
        render_learning_analysis()
    
    with tab3:
        render_history_records()
    
    with tab4:
        render_achievements()

# 教师端界面
def render_teacher_interface():
    """渲染教师端界面"""
    # 班级统计概览 - 使用修复后的统计数据
    class_stats = get_class_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 总学生数", class_stats['total_students'])
    with col2:
        st.metric("📝 总提交数", class_stats['total_reflections'])
    with col3:
        st.metric("📊 提交率", f"{class_stats['submission_rate']}%")
    with col4:
        st.metric("⭐ 班级平均分", class_stats['avg_score'])
    
    # 使用标签页组织内容 - 教师端包含所有功能
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👨‍🏫 审核管理", "📊 学习分析", "📚 历史记录", "🏆 成长成就", "🎯 班级统计"])
    
    with tab1:
        st.markdown('<div class="section-title">👨‍🏫 学生思政感悟审核</div>', unsafe_allow_html=True)
        
        # 获取所有学生记录
        records = get_ideology_reflections()
        
        # 筛选选项
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_status = st.selectbox("筛选状态", ["全部", "待审核", "已审核", "已退回"])

        with col2:
            filter_student = st.text_input("筛选学生", placeholder="输入学生用户名", key="teacher_student_filter")
            
            # 添加筛选逻辑 - 使用真实数据
            if filter_student:
                st.info(f"🔍 正在筛选学生: {filter_student}")
                
                # 获取所有学生
                all_students = get_all_students()
                
                # 筛选匹配的学生
                matched_students = [student for student in all_students if filter_student.lower() in student.lower()]
                
                if matched_students:
                    st.success(f"找到 {len(matched_students)} 名学生")
                    
                    # 显示匹配的学生信息
                    for student in matched_students:
                        # 获取该学生的统计信息
                        student_stats = get_student_stats(student)
                        
                        with st.container():
                            col_a, col_b, col_c = st.columns([3, 2, 2])
                            with col_a:
                                st.write(f"👤 **{student}**")
                            with col_b:
                                st.write(f"提交: {student_stats['total_reflections']}篇")
                            with col_c:
                                st.write(f"平均分: {student_stats['avg_score']}")
                else:
                    st.warning(f"未找到学生: {filter_student}")
        with col3:
            sort_option = st.selectbox("排序方式", ["最新提交", "最早提交", "按分数排序"])
        
        # 应用筛选
        filtered_records = records
        if filter_status != "全部":
            status_map = {"待审核": "pending", "已审核": "reviewed", "已退回": "returned"}
            filtered_records = [r for r in filtered_records if r['status'] == status_map[filter_status]]
        
        if filter_student:
            filtered_records = [r for r in filtered_records if filter_student.lower() in r['student_username'].lower()]
        
        # 应用排序
        if sort_option == "最新提交":
            filtered_records.sort(key=lambda x: x['submission_time'], reverse=True)
        elif sort_option == "最早提交":
            filtered_records.sort(key=lambda x: x['submission_time'])
        elif sort_option == "按分数排序":
            filtered_records.sort(key=lambda x: x['score'], reverse=True)
        
        # 显示记录
        if filtered_records:
            st.markdown(f"### 找到 {len(filtered_records)} 条记录")
            
            for record in filtered_records:
                with st.container():
                    # 使用Streamlit原生组件代替HTML
                    with st.container():
                        st.markdown(f"### 👤 {record['student_username']} 的感悟")
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**📅 提交时间：** {record['submission_time']}")
                            st.markdown(f"**📊 字数：** {record['word_count']}字")
                        with col2:
                            # 显示状态徽章
                            if record['status'] == 'pending':
                                st.markdown('<span class="status-pending">⏳ 待审核</span>', unsafe_allow_html=True)
                            elif record['status'] == 'reviewed':
                                st.markdown('<span class="status-reviewed">✅ 已审核</span>', unsafe_allow_html=True)
                            elif record['status'] == 'returned':
                                st.markdown('<span class="status-returned">↩️ 已退回</span>', unsafe_allow_html=True)
                        
                        # 显示分数（如果已评分）
                        if record['score'] > 0:
                            st.markdown(f"**⭐ 分数：** {record['score']}分")
                        
                        st.markdown(f"**💭 感悟内容：** {record['reflection_content'][:150]}...")
                        st.markdown("---")
                    
                    # 操作按钮
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("👁️ 查看详情", key=f"view_{record['id']}", width='stretch'):
                            st.session_state.view_record_id = record
                            st.rerun()
                    with col2:
                        if st.button("📝 审核评分", key=f"review_{record['id']}", width='stretch'):
                            st.session_state.edit_record_id = record
                            st.rerun()
                    with col3:
                        if record['teacher_feedback']:
                            st.info(f"反馈: {record['teacher_feedback']}")
                    
                    st.markdown("---")
        else:
            st.info("📝 没有找到符合条件的记录。")
    
    with tab2:
        render_learning_analysis()
    
    with tab3:
        render_history_records()
    
    with tab4:
        render_achievements()
    
    with tab5:
        st.markdown('<div class="section-title">🎯 班级统计概览</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏳ 待审核", class_stats['pending_count'])
        with col2:
            st.metric("✅ 已审核", class_stats['reviewed_count'])
        with col3:
            st.metric("↩️ 已退回", class_stats['returned_count'])
        
        # 学生提交情况统计
        st.markdown("### 📊 学生提交情况")
        all_students = get_all_students()
        all_records = get_ideology_reflections()
        
        submission_data = []
        for student in all_students:
            student_records = [r for r in all_records if r['student_username'] == student]
            submission_data.append({
                '学生': student,
                '提交数量': len(student_records),
                '状态': '已提交' if len(student_records) > 0 else '未提交'
            })
        
        df_submission = pd.DataFrame(submission_data)
        
        # 提交状态分布
        submitted_count = len([s for s in submission_data if s['状态'] == '已提交'])
        not_submitted_count = len([s for s in submission_data if s['状态'] == '未提交'])
        
        fig_submission = px.pie(
            values=[submitted_count, not_submitted_count],
            names=['已提交', '未提交'],
            title='学生提交状态分布',
            color_discrete_sequence=['#10b981', '#ef4444']
        )
        st.plotly_chart(fig_submission, width='stretch')
# 主页面内容
def main():
    # 检查登录状态
    if not st.session_state.get('logged_in', False):
        st.warning("请先登录系统")
        if st.button("前往登录"):
            st.switch_page("main.py")
        return
    init_database()
    # 应用CSS样式
    apply_modern_css()
    
    # 页面标题
    st.markdown("""
    <div class='modern-header'>
        <h1>📝 我的思政足迹</h1>
        <p class='subtitle'>记录技术成长之路 · 内化思政价值感悟 · 见证全面发展历程</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 渲染侧边栏
    render_sidebar()
    
    # 如果正在查看详情，显示详情页面
    if st.session_state.view_record_id is not None:
        view_record_detail(st.session_state.view_record_id)
        return
    
    # 如果正在编辑/审核，显示审核界面
    if st.session_state.edit_record_id is not None and st.session_state.get('role') == 'teacher':
        teacher_review_interface(st.session_state.edit_record_id)
        return
    
    # 根据角色显示不同界面
    if st.session_state.get('role') == 'student':
        render_student_interface()
    elif st.session_state.get('role') == 'teacher':
        render_teacher_interface()
    else:
        st.error("未知用户角色")

if __name__ == "__main__":
    main()
