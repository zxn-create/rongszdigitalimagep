import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import json
import os
import zipfile
import tempfile
import shutil
import csv
import io
from supabase import create_client, Client
import pytz

st.set_page_config(
    page_title="思政成果展示", 
    page_icon="🏆", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Supabase 初始化 ====================
@st.cache_resource
def init_supabase():
    """初始化 Supabase 客户端"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_supabase()

# ==================== 北京时间处理 ====================
def get_beijing_time():
    """获取北京时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.datetime.now(beijing_tz)

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

# 应用CSS样式（保持不变）
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

# ==================== Supabase 数据库操作函数 ====================

def verify_teacher_role(username):
    """校验用户是否为教师角色"""
    try:
        result = supabase.table("users").select("role").eq("username", username).execute()
        if result.data:
            return result.data[0].get("role") == "teacher"
        return False
    except Exception as e:
        st.error(f"验证教师角色失败：{str(e)}")
        return False

def get_user_id(username):
    """获取用户ID"""
    try:
        result = supabase.table("users").select("id").eq("username", username).execute()
        return result.data[0]["id"] if result.data else None
    except Exception as e:
        st.error(f"获取用户ID失败：{str(e)}")
        return None

def get_feedback_data():
    """从数据库读取意见反馈数据"""
    try:
        result = supabase.table("feedback").select("*").order("submit_time", desc=True).execute()
        
        feedback_list = []
        for idx, row in enumerate(result.data):
            feedback_list.append({
                "序号": idx + 1,
                "反馈内容": row.get("feedback_content", ""),
                "提交时间": format_beijing_time(row.get("submit_time")),
                "IP地址": row.get("ip_address", "未知"),
                "用户代理": row.get("user_agent", "未知")
            })
        
        return feedback_list
    except Exception as e:
        st.error(f"读取反馈数据失败：{str(e)}")
        return []

def save_feedback_to_db(feedback_content):
    """保存反馈到数据库"""
    try:
        # 获取IP地址（简化版）
        ip_address = "127.0.0.1"
        user_agent = "未知"
        
        data = {
            "feedback_content": feedback_content,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        supabase.table("feedback").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"保存反馈失败：{str(e)}")
        return False

def save_uploaded_files_to_storage(uploaded_files, project_name, author_name, user_id):
    """
    将上传的文件保存到 Supabase Storage，并返回文件名列表和存储路径列表
    """
    try:
        saved_files = []
        storage_paths = []
        
        if uploaded_files:
            # 为每个文件生成存储路径：user_id/project_name_timestamp/filename
            timestamp = get_beijing_time().strftime("%Y%m%d%H%M%S")
            folder_path = f"{user_id}/{project_name}_{timestamp}"
            
            for uploaded_file in uploaded_files:
                # 生成安全的文件名
                safe_filename = "".join(c for c in uploaded_file.name if c.isalnum() or c in "._- ").rstrip()
                # 完整存储路径
                storage_path = f"{folder_path}/{timestamp}_{safe_filename}"
                
                # 读取文件内容
                file_bytes = uploaded_file.getbuffer()
                
                # 上传到 Supabase Storage 的 project_files 桶
                response = supabase.storage.from_("project_files").upload(
                    path=storage_path,
                    file=file_bytes.tobytes(),
                    file_options={"content-type": uploaded_file.type}
                )
                
                saved_files.append(uploaded_file.name)
                storage_paths.append(storage_path)
            
            return saved_files, storage_paths
    except Exception as e:
        st.error(f"保存文件到云端失败：{str(e)}")
        return [], []

def save_submitted_project(project_data):
    """保存提交的作品到数据库"""
    try:
        # 获取用户ID
        user_id = None
        if "logged_in" in st.session_state and st.session_state.logged_in:
            user_id = get_user_id(st.session_state.username)
        
        data = {
            "project_name": project_data['project_name'],
            "author_name": project_data['author_name'],
            "project_desc": project_data['project_desc'],
            "files": json.dumps(project_data.get('files', [])),
            "storage_paths": json.dumps(project_data.get('storage_paths', [])),  # 改为 storage_paths
            "user_id": user_id,
            "status": "待审核"
        }
        
        result = supabase.table("submitted_projects").insert(data).execute()
        return True, result.data[0]["id"] if result.data else None
    except Exception as e:
        st.error(f"保存作品失败：{str(e)}")
        return False, None

def get_submitted_projects(user_id=None):
    """获取所有提交的作品"""
    try:
        query = supabase.table("submitted_projects").select("*")
        
        if user_id:
            query = query.eq("user_id", user_id)
        
        result = query.order("submit_time", desc=True).execute()
        
        projects = []
        for row in result.data:
            files = json.loads(row.get("files", "[]")) if row.get("files") else []
            storage_paths = json.loads(row.get("storage_paths", "[]")) if row.get("storage_paths") else []
            
            projects.append({
                "id": row["id"],
                "project_name": row["project_name"],
                "author_name": row["author_name"],
                "project_desc": row["project_desc"],
                "submit_time": format_beijing_time(row.get("submit_time")),
                "files": files,
                "storage_paths": storage_paths,  # 改为 storage_paths
                "status": row.get("status", "待审核"),
                "review_notes": row.get("review_notes", ""),
                "review_time": format_beijing_time(row.get("review_time")),
                "reviewer": row.get("reviewer", "")
            })
        
        return projects
    except Exception as e:
        st.error(f"获取作品失败：{str(e)}")
        return []

def update_project_status(project_id, status, review_notes=""):
    """更新作品审核状态"""
    try:
        data = {
            "status": status,
            "review_notes": review_notes,
            "review_time": get_beijing_time().isoformat(),
            "reviewer": st.session_state.username
        }
        
        supabase.table("submitted_projects").update(data).eq("id", project_id).execute()
        return True
    except Exception as e:
        st.error(f"更新作品状态失败：{str(e)}")
        return False

def download_project_files_from_storage(project):
    """
    从 Supabase Storage 下载项目文件并打包成 ZIP
    """
    try:
        if not project.get('storage_paths'):
            return None
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, f"{project['project_name']}_files.zip")
            
            # 创建ZIP文件
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, storage_path in enumerate(project['storage_paths']):
                    try:
                        # 从 Supabase Storage 下载文件
                        file_data = supabase.storage.from_("project_files").download(storage_path)
                        
                        # 使用原始文件名
                        original_filename = project['files'][i] if i < len(project['files']) else f"file_{i+1}"
                        
                        # 写入 zip
                        zipf.writestr(original_filename, file_data)
                    except Exception as e:
                        st.warning(f"文件 {original_filename} 下载失败：{str(e)}")
            
            # 读取ZIP文件内容
            with open(zip_path, 'rb') as f:
                zip_data = f.read()
            
            return zip_data
    except Exception as e:
        st.error(f"下载文件失败：{str(e)}")
        return None

def get_platform_stats():
    """获取平台统计信息"""
    try:
        # 用户统计
        users_result = supabase.table("users").select("*", count="exact").execute()
        total_users = users_result.count if hasattr(users_result, 'count') else len(users_result.data)
        
        students_result = supabase.table("users").select("*", count="exact").eq("role", "student").execute()
        student_count = students_result.count if hasattr(students_result, 'count') else len(students_result.data)
        
        teachers_result = supabase.table("users").select("*", count="exact").eq("role", "teacher").execute()
        teacher_count = teachers_result.count if hasattr(teachers_result, 'count') else len(teachers_result.data)
        
        # 作品统计
        projects = get_submitted_projects()
        total_projects = len(projects)
        pending_projects = len([p for p in projects if p['status'] == '待审核'])
        approved_projects = len([p for p in projects if p['status'] == '已通过'])
        rejected_projects = len([p for p in projects if p['status'] == '已拒绝'])
        
        # 反馈统计
        feedback = get_feedback_data()
        total_feedback = len(feedback)
        
        return {
            'total_users': total_users,
            'student_count': student_count,
            'teacher_count': teacher_count,
            'total_projects': total_projects,
            'pending_projects': pending_projects,
            'approved_projects': approved_projects,
            'rejected_projects': rejected_projects,
            'total_feedback': total_feedback
        }
    except Exception as e:
        st.error(f"获取统计信息失败：{str(e)}")
        return {
            'total_users': 0, 'student_count': 0, 'teacher_count': 0,
            'total_projects': 0, 'pending_projects': 0, 'approved_projects': 0,
            'rejected_projects': 0, 'total_feedback': 0
        }

# ==================== 生成示例数据（保持不变）====================
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

def generate_stats_data():
    """生成用于图表的数据"""
    ideology_data = {
        '思政元素': ['工匠精神', '家国情怀', '创新意识', '责任担当', '科学态度', '团队合作'],
        '作品数量': [35, 28, 22, 25, 20, 18]
    }
    
    project_type_data = {
        '项目类型': ['技术创新类', '社会服务类', '文化传承类', '国家战略类'],
        '数量': [45, 30, 15, 10]
    }
    
    return pd.DataFrame(ideology_data), pd.DataFrame(project_type_data)

def export_feedback_to_csv(feedback_data):
    """导出反馈数据到CSV"""
    try:
        if not feedback_data:
            return None
        
        output = io.StringIO()
        fieldnames = ["序号", "反馈内容", "提交时间", "IP地址", "用户代理"]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for feedback in feedback_data:
            writer.writerow(feedback)
        
        csv_str = output.getvalue()
        output.close()
        
        csv_bytes = csv_str.encode('gb18030', errors='ignore')
        
        return csv_bytes
    except Exception as e:
        st.error(f"导出CSV失败：{str(e)}")
        return None

# ==================== 渲染侧边栏（保持不变）====================
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
        
        st.markdown("### 🧭 快速导航")
        
        if st.button("🏠 返回首页", width='content'):
            st.switch_page("main.py")
        if st.button("🔬 图像处理实验室", width='content'):
            st.switch_page("pages/1_🔬_图像处理实验室.py")
        if st.button("📝 智能与传统图片处理", use_container_width=True):
            st.switch_page("pages/智能与传统图片处理.py")
        if st.button("🏫 加入班级与在线签到", width='content'):
            st.switch_page("pages/分班和在线签到.py")
        if st.button("📤 实验作业提交", width='content'):
            st.switch_page("pages/实验作业提交.py")            
        if st.button("📚 学习资源中心", width='content'):
            st.switch_page("pages/2_📚_学习资源中心.py")
        if st.button("📝 我的思政足迹", width='content'):
            st.switch_page("pages/3_📝_我的思政足迹.py")
        if st.button("🏆 成果展示", width='content'):
            st.switch_page("pages/4_🏆_成果展示.py")
        
        if "logged_in" in st.session_state and st.session_state.logged_in:
            st.markdown("---")
            if st.button("📋 我的提交记录", width='content'):
                st.session_state.show_my_projects = True
                st.rerun()
        
        if "logged_in" in st.session_state and st.session_state.logged_in:
            if verify_teacher_role(st.session_state.username):
                st.markdown("---")
                if st.button("🔧 进入教师后台", width='content', type="primary"):
                    st.session_state.show_admin = True
                    st.rerun()
        
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
        
        st.markdown("### 🎯 思政理论学习")
        theory_topics = [
            "新时代工匠精神的内涵与实践",
            "科技创新与国家发展战略",
            "社会主义核心价值观与技术伦理",
            "科学家精神与家国情怀",
            "数字时代的责任与担当"
        ]
        
        for topic in theory_topics:
            if st.button(f"📖 {topic}", key=f"theory_{topic}", width='content'):
                st.info(f"开始学习：{topic}")
        
        st.markdown("---")
        
        st.markdown("### 💫 思政学习提醒")
        st.success("""
        🎯 **本周思政重点：**
        - 学习科学家精神
        - 践行工匠精神
        - 培养家国情怀
        - 强化责任担当
        """)

# ==================== 渲染我的提交记录 ====================
def render_my_projects():
    """渲染用户提交记录"""
    st.markdown("<h1 style='color:#dc2626; font-size:2rem;'>📋 我的提交记录</h1>", unsafe_allow_html=True)
    
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.error("🔒 请先登录查看提交记录")
        return
    
    if st.button("← 返回成果展示", width='content'):
        st.session_state.show_my_projects = False
        st.rerun()
    
    user_id = get_user_id(st.session_state.username)
    if not user_id:
        st.error("无法获取用户信息")
        return
    
    my_projects = get_submitted_projects(user_id)
    
    if my_projects:
        st.markdown(f"### 📊 提交统计：共提交了 {len(my_projects)} 个作品")
        
        status_counts = {}
        for project in my_projects:
            status = project['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
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
        
        for project in my_projects:
            with st.expander(f"📄 {project['project_name']} - 提交时间：{project['submit_time']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**作者：** {project['author_name']}")
                    st.markdown(f"**作品描述：**")
                    st.info(project['project_desc'])
                    
                    if project['files']:
                        st.markdown(f"**上传文件：**")
                        for file in project['files']:
                            st.markdown(f"- 📎 {file}")
                
                with col2:
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
                    
                    if project['review_notes']:
                        st.markdown(f"**审核意见：**")
                        st.warning(project['review_notes'])
                    
                    if project['review_time']:
                        st.markdown(f"**审核时间：** {project['review_time']}")
                    
                    if project['reviewer']:
                        st.markdown(f"**审核老师：** {project['reviewer']}")
                
                if project['files'] and project.get('storage_paths'):
                    zip_data = download_project_files_from_storage(project)
                    if zip_data:
                        st.download_button(
                            label="📥 下载我的作品文件",
                            data=zip_data,
                            file_name=f"{project['project_name']}_作品文件.zip",
                            mime="application/zip",
                            key=f"download_{project['id']}",
                            width='content'
                        )
                        st.info("💡 您可以随时下载您提交的文件")
    else:
        st.info("📭 您还没有提交过作品，快去【作品征集】页面提交您的第一个作品吧！")

# ==================== 渲染管理员后台 ====================
def render_admin_dashboard():
    """渲染管理员后台内容"""
    st.markdown("<h1 style='color:#dc2626; font-size:2rem;'>🔧 管理员后台</h1>", unsafe_allow_html=True)
    st.markdown(f"### 👤 当前登录教师：{st.session_state.username}")
    st.markdown("---")
    
    if st.button("← 返回成果展示", width='content'):
        st.session_state.show_admin = False
        st.rerun()
    
    admin_tabs = st.tabs(["📝 作品审核", "💬 意见反馈", "📊 平台统计"])
    
    with admin_tabs[0]:
        st.markdown("<h2 style='color:#dc2626;'>📝 作品审核管理</h2>", unsafe_allow_html=True)
        
        submitted_projects = get_submitted_projects()
        
        if submitted_projects:
            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input("搜索作品名称或作者", placeholder="输入关键词...")
            with col2:
                status_filter = st.selectbox("筛选状态", ["全部", "待审核", "已通过", "已拒绝"])
            
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
            
            for project in filtered_projects:
                with st.expander(f"📄 {project['project_name']} - {project['author_name']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**提交时间：** {project['submit_time']}")
                        st.markdown(f"**作品描述：**")
                        st.info(project['project_desc'])
                        
                        if project['files']:
                            st.markdown(f"**上传文件：**")
                            for file in project['files']:
                                st.markdown(f"- 📎 {file}")
                            
                            if project.get('storage_paths'):
                                zip_data = download_project_files_from_storage(project)
                                if zip_data:
                                    st.download_button(
                                        label="📥 下载作品文件",
                                        data=zip_data,
                                        file_name=f"{project['project_name']}_作品文件.zip",
                                        mime="application/zip",
                                        key=f"admin_download_{project['id']}",
                                        width='content'
                                    )
                    
                    with col2:
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
                    
                    if project['status'] == "待审核":
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            review_notes = st.text_area(f"审核意见（可选）", key=f"notes_{project['id']}")
                        
                        with col2:
                            if st.button("✅ 通过审核", key=f"approve_{project['id']}", width='content'):
                                if update_project_status(project['id'], "已通过", review_notes):
                                    st.success("作品已通过审核！")
                                    st.rerun()
                            
                            if st.button("❌ 拒绝作品", key=f"reject_{project['id']}", width='content'):
                                if update_project_status(project['id'], "已拒绝", review_notes):
                                    st.success("作品已拒绝！")
                                    st.rerun()
        else:
            st.info("📭 暂无学生提交的作品")
    
    with admin_tabs[1]:
        st.markdown("<h2 style='color:#dc2626;'>💬 意见反馈管理</h2>", unsafe_allow_html=True)
        feedback_data = get_feedback_data()

        if feedback_data:
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
                    "用户代理": st.column_config.TextColumn("用户代理", width="large")
                }
            )

            csv_bytes = export_feedback_to_csv(feedback_data)
            if csv_bytes:
                st.download_button(
                    label="📥 导出反馈数据（CSV-GB18030编码）",
                    data=csv_bytes,
                    file_name=f"意见反馈_{get_beijing_time().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width='content'
                )
            
            st.divider()
            st.markdown("#### 📊 反馈统计")
            total_feedback = len(feedback_data)
            if total_feedback > 0:
                avg_length = sum(len(f["反馈内容"]) for f in feedback_data) / total_feedback
                latest_feedback = feedback_data[0]["提交时间"] if feedback_data else "暂无"
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总反馈数量", total_feedback)
                with col2:
                    st.metric("平均字数", f"{avg_length:.0f}字")
                with col3:
                    st.metric("最新反馈", latest_feedback[:10])
        else:
            st.info("📭 暂无用户提交的意见反馈")
    
    with admin_tabs[2]:
        st.markdown("<h2 style='color:#dc2626;'>📊 平台基础统计</h2>", unsafe_allow_html=True)
        
        stats = get_platform_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 总用户数", stats['total_users'])
        with col2:
            st.metric("🎓 学生用户数", stats['student_count'])
        with col3:
            st.metric("👨‍🏫 教师用户数", stats['teacher_count'])
        
        st.divider()
        
        st.markdown("#### 📦 作品提交统计")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总提交作品", stats['total_projects'])
        with col2:
            st.metric("⏳ 待审核", stats['pending_projects'])
        with col3:
            st.metric("✅ 已通过", stats['approved_projects'])
        with col4:
            rejection_rate = (stats['rejected_projects'] / stats['total_projects'] * 100) if stats['total_projects'] > 0 else 0
            st.metric("❌ 拒绝率", f"{rejection_rate:.1f}%")
        
        submitted_projects = get_submitted_projects()
        if submitted_projects:
            st.divider()
            st.markdown("#### 📈 作品提交时间分布")
            
            month_counts = {}
            for project in submitted_projects:
                if project['submit_time']:
                    month = project['submit_time'][:7]
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
        
        st.markdown("#### 💬 意见反馈统计")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("总反馈数量", stats['total_feedback'])
        with col2:
            if stats['total_feedback'] > 0:
                feedback_data = get_feedback_data()
                avg_feedback_len = sum(len(f['反馈内容']) for f in feedback_data) / stats['total_feedback']
                st.metric("平均反馈长度", f"{avg_feedback_len:.0f}字")
            else:
                st.metric("平均反馈长度", "0字")
        
        st.divider()
        st.markdown("#### 🕒 平台运行信息")
        current_time = get_beijing_time()
        st.markdown(f"**当前服务器时间：** {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(f"**时区：** 北京时间 (UTC+8)")

# ==================== 渲染主要内容 ====================
def render_main_content():
    """渲染主要的成果展示内容"""
    st.markdown("""
    <div class='modern-header'>
        <h1 class='main-title'>🏆 思政成果展示</h1>
        <p style='font-size: 1.2rem; color: rgba(255,255,255,0.9);'>技术赋能 · 思想引领 · 创新驱动 · 服务国家</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 优秀作品", "3个", "+1个")
    with col2:
        st.metric("🏅 获得奖项", "120项", "+1项")
    with col3:
        st.metric("💡 技术创新", "8项", "+42项")
    with col4:
        st.metric("🌟 思政融合", "98%", "深度融合")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 优秀作品", "📊 成果分析", "💡 作品征集", "💬 意见反馈"])
    
    with tab1:
        st.markdown("<h2 class='section-title'>🎨 优秀作品展示</h2>", unsafe_allow_html=True)
        
        filter_col1, filter_col2 = st.columns([1, 2])
        with filter_col1:
            filter_ideology = st.multiselect(
                "按思政元素筛选",
                options=["工匠精神", "家国情怀", "文化自信", "创新意识", "责任担当", "科学态度", "团队合作"],
                default=[]
            )
        with filter_col2:
            search_term = st.text_input("搜索作品关键词", placeholder="输入作品名称、作者或技术关键词...")
        
        projects = generate_projects_data()
        
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
    
    with tab2:
        st.markdown("<h2 class='section-title'>📊 成果数据分析</h2>", unsafe_allow_html=True)
        
        ideology_df, type_df = generate_stats_data()
        
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
    
    with tab3:
        st.markdown("<h2 class='section-title'>💡 作品征集</h2>", unsafe_allow_html=True)
        
        st.info("""
        📢 **征集说明：**
        欢迎提交您的思政与技术融合作品，优秀作品将纳入展示平台。
        作品要求体现技术创新的同时，融入思政元素，展现新时代大学生的责任与担当。
        
        📋 **提交后您可以：**
        1. 在侧边栏点击【我的提交记录】查看审核状态
        2. 无论审核状态如何，您都可以下载自己提交的文件
        3. 查看老师的审核意见
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
                help="支持多种格式文件，建议单个文件不超过20MB"
            )
            
            submitted = st.form_submit_button("🚀 提交作品", type="primary", width='content')
            
            if submitted:
                if project_name and author_name and project_desc:
                    if "logged_in" not in st.session_state or not st.session_state.logged_in:
                        st.error("❌ 请先登录后再提交作品")
                    else:
                        user_id = get_user_id(st.session_state.username)
                        
                        # 保存文件到 Supabase Storage
                        saved_files = []
                        storage_paths = []
                        if uploaded_files:
                            saved_files, storage_paths = save_uploaded_files_to_storage(
                                uploaded_files, project_name, author_name, user_id
                            )
                        
                        # 构建作品数据
                        project_data = {
                            "project_name": project_name,
                            "author_name": author_name,
                            "project_desc": project_desc,
                            "files": saved_files,
                            "storage_paths": storage_paths
                        }
                        
                        # 保存到数据库
                        success, project_id = save_submitted_project(project_data)
                        if success:
                            if saved_files:
                                st.success(f"✅ 作品提交成功！已上传 {len(saved_files)} 个文件到云端永久保存")
                                for file in saved_files:
                                    st.markdown(f"- 📎 {file}")
                            else:
                                st.success("✅ 作品提交成功！我们将尽快审核~")
                            
                            st.info("💡 您可以在侧边栏点击【我的提交记录】查看审核状态和下载您提交的文件")
                            st.balloons()
                        else:
                            st.error("❌ 作品提交失败，请稍后重试")
                else:
                    st.error("⚠️ 请填写作品名称、作者和描述等必填信息")
    
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
            if st.button("📤 提交反馈", type="primary", width='content'):
                if feedback_content.strip():
                    if save_feedback_to_db(feedback_content):
                        st.success("✅ 感谢您的反馈！我们会认真参考~")
                        st.balloons()
                    else:
                        st.error("❌ 提交失败，请稍后重试")
                else:
                    st.warning("⚠️ 请输入反馈内容后再提交哦~")
        with col2:
            if st.button("🔄 清空内容", width='content'):
                st.rerun()

# ==================== 主函数 ====================
def main():
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
        render_my_projects()
    else:
        render_main_content()

if __name__ == "__main__":
    main()