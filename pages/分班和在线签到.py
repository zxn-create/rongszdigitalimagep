# pages/5_🏫_班级管理与在线签到.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import bcrypt
import time
import random
import hashlib
import uuid
import plotly.graph_objects as go
import plotly.express as px
import os
import io

# ==================== Supabase 相关导入 ====================
from supabase import create_client, Client
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="班级管理与在线签到 - 融思政",
    page_icon="🏫",
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

supabase = init_supabase()

# ==================== Supabase 表初始化 ====================
def init_classroom_db():
    """初始化班级管理和签到相关数据库表"""
    try:
        # 检查 classrooms 表是否存在
        try:
            supabase.table("classrooms").select("*").limit(1).execute()
        except:
            st.warning("请在 Supabase SQL 编辑器中执行以下 SQL 创建表：")
            st.code("""
-- 创建 classrooms 表
CREATE TABLE classrooms (
    id BIGSERIAL PRIMARY KEY,
    class_code VARCHAR(12) UNIQUE NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    teacher_username VARCHAR(50) NOT NULL,
    description TEXT,
    max_students INTEGER DEFAULT 50,
    created_at TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- 创建 classroom_members 表
CREATE TABLE classroom_members (
    id BIGSERIAL PRIMARY KEY,
    class_code VARCHAR(12) NOT NULL,
    student_username VARCHAR(50) NOT NULL,
    joined_at TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    role VARCHAR(20) DEFAULT 'student',
    UNIQUE(class_code, student_username)
);

-- 创建 attendance_sessions 表
CREATE TABLE attendance_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_code VARCHAR(10) UNIQUE NOT NULL,
    class_code VARCHAR(12) NOT NULL,
    session_name VARCHAR(100) NOT NULL,
    teacher_username VARCHAR(50) NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    duration_minutes INTEGER DEFAULT 10,
    location_name VARCHAR(100),
    attendance_type VARCHAR(20) DEFAULT 'standard',
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TEXT NOT NULL,
    total_students INTEGER DEFAULT 0,
    attended_students INTEGER DEFAULT 0
);

-- 创建 attendance_records 表
CREATE TABLE attendance_records (
    id BIGSERIAL PRIMARY KEY,
    session_code VARCHAR(10) NOT NULL,
    student_username VARCHAR(50) NOT NULL,
    class_code VARCHAR(12) NOT NULL,
    check_in_time TEXT NOT NULL,
    check_in_method VARCHAR(20) DEFAULT 'manual',
    device_info TEXT,
    ip_address VARCHAR(45),
    is_late BOOLEAN DEFAULT FALSE,
    points_earned INTEGER DEFAULT 10,
    status VARCHAR(20) DEFAULT 'present',
    UNIQUE(session_code, student_username)
);

-- 创建 class_notifications 表
CREATE TABLE class_notifications (
    id BIGSERIAL PRIMARY KEY,
    class_code VARCHAR(12) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    notification_type VARCHAR(20) DEFAULT 'announcement',
    created_by VARCHAR(50) NOT NULL,
    created_at TEXT NOT NULL,
    is_urgent BOOLEAN DEFAULT FALSE
);
            """)
            
    except Exception as e:
        st.error(f"Supabase 初始化检查失败: {e}")

# 执行初始化检查
init_classroom_db()

# ==================== 工具函数 ====================
def get_beijing_time():
    """获取当前北京时间"""
    utc_now = datetime.utcnow()
    beijing_time = utc_now + timedelta(hours=8)
    return beijing_time

def to_beijing_time_str(dt=None):
    """将datetime对象转换为北京时间的字符串格式"""
    if dt is None:
        dt = get_beijing_time()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def from_beijing_time_str(time_str):
    """从北京时间的字符串转换为datetime对象"""
    return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

def generate_unique_code(prefix="", length=8):
    """生成唯一的班级代码或签到代码"""
    timestamp = str(int(time.time()))[-4:]
    random_str = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:length-4]
    return f"{prefix}{timestamp}{random_str}".upper()

# ==================== 数据库操作函数 ====================
def create_classroom(teacher_username, class_name, description="", max_students=50):
    """创建新班级 - 无限制版本"""
    try:
        # 生成班级代码
        class_code = generate_unique_code("CLS", 8)
        
        # 创建班级
        created_at = to_beijing_time_str()
        supabase.table("classrooms").insert({
            "class_code": class_code,
            "class_name": class_name,
            "teacher_username": teacher_username,
            "description": description,
            "max_students": max_students,
            "created_at": created_at,
            "is_active": True
        }).execute()
        
        # 将教师自动加入班级
        supabase.table("classroom_members").insert({
            "class_code": class_code,
            "student_username": teacher_username,
            "joined_at": created_at,
            "role": "teacher"
        }).execute()
        
        return True, class_code
    except Exception as e:
        return False, f"创建班级失败: {str(e)}"

def join_classroom(student_username, class_code):
    """学生加入班级"""
    try:
        # 检查班级是否存在且活跃
        response = supabase.table("classrooms").select("class_name, max_students, is_active").eq("class_code", class_code).execute()
        
        if not response.data or len(response.data) == 0:
            return False, "班级不存在"
        
        class_info = response.data[0]
        
        if not class_info.get("is_active"):
            return False, "班级已关闭"
        
        # 检查班级是否已满
        members_response = supabase.table("classroom_members").select("id", count="exact").eq("class_code", class_code).eq("status", 'active').execute()
        current_students = members_response.count if hasattr(members_response, 'count') else len(members_response.data) if members_response.data else 0
        max_students = class_info.get("max_students", 50)
        
        if current_students >= max_students:
            return False, "班级人数已满"
        
        # 检查是否已经加入
        check_response = supabase.table("classroom_members").select("id").eq("class_code", class_code).eq("student_username", student_username).execute()
        
        if check_response.data and len(check_response.data) > 0:
            return False, "您已加入该班级"
        
        # 加入班级
        joined_at = to_beijing_time_str()
        supabase.table("classroom_members").insert({
            "class_code": class_code,
            "student_username": student_username,
            "joined_at": joined_at,
            "status": "active",
            "role": "student"
        }).execute()
        
        return True, "成功加入班级"
    except Exception as e:
        return False, f"加入班级失败: {str(e)}"

def create_attendance_session(class_code, teacher_username, session_name, 
                             start_time, end_time, duration_minutes=10,
                             location_name=None, attendance_type='standard'):
    """创建签到活动"""
    try:
        # 生成签到代码
        session_code = generate_unique_code("ATT", 6)
        
        # 获取班级总人数
        response = supabase.table("classroom_members").select("id", count="exact").eq("class_code", class_code).eq("status", 'active').eq("role", 'student').execute()
        total_students = response.count if hasattr(response, 'count') else len(response.data) if response.data else 0
        
        # 创建签到活动
        created_at = to_beijing_time_str()
        supabase.table("attendance_sessions").insert({
            "session_code": session_code,
            "class_code": class_code,
            "session_name": session_name,
            "teacher_username": teacher_username,
            "start_time": start_time,
            "end_time": end_time,
            "duration_minutes": duration_minutes,
            "location_name": location_name,
            "attendance_type": attendance_type,
            "status": "scheduled",
            "created_at": created_at,
            "total_students": total_students,
            "attended_students": 0
        }).execute()
        
        return True, session_code
    except Exception as e:
        return False, f"创建签到失败: {str(e)}"

def check_in_attendance(session_code, student_username, check_in_method='manual',
                       device_info=None, ip_address=None):
    """学生签到 - 修改：放宽签到条件"""
    try:
        # 检查签到活动是否存在
        response = supabase.table("attendance_sessions").select("class_code, start_time, end_time, status").eq("session_code", session_code).execute()
        
        if not response.data or len(response.data) == 0:
            return False, "签到活动不存在"
        
        session_info = response.data[0]
        
        class_code = session_info.get("class_code")
        start_time = from_beijing_time_str(session_info.get("start_time"))
        end_time = from_beijing_time_str(session_info.get("end_time"))
        current_time = get_beijing_time()
        
        # 检查时间是否在有效范围内
        if current_time < start_time:
            return False, "签到活动尚未开始"
        if current_time > end_time:
            # 允许超时15分钟内签到
            time_difference = (current_time - end_time).total_seconds() / 60
            if time_difference > 15:
                return False, "签到活动已结束"
        
        # 检查学生是否在班级中
        member_response = supabase.table("classroom_members").select("id").eq("class_code", class_code).eq("student_username", student_username).eq("status", 'active').execute()
        
        if not member_response.data or len(member_response.data) == 0:
            return False, "您不在该班级中"
        
        # 检查是否已经签到
        record_response = supabase.table("attendance_records").select("id").eq("session_code", session_code).eq("student_username", student_username).execute()
        
        if record_response.data and len(record_response.data) > 0:
            return False, "您已经签到过了"
        
        # 判断是否迟到
        is_late = current_time > start_time + timedelta(minutes=5)
        points_earned = 5 if is_late else 10
        
        # 记录签到
        check_in_time = to_beijing_time_str(current_time)
        supabase.table("attendance_records").insert({
            "session_code": session_code,
            "student_username": student_username,
            "class_code": class_code,
            "check_in_time": check_in_time,
            "check_in_method": check_in_method,
            "device_info": device_info,
            "ip_address": ip_address,
            "is_late": is_late,
            "points_earned": points_earned,
            "status": "present"
        }).execute()
        
        # 更新签到统计
        attended_response = supabase.table("attendance_records").select("id", count="exact").eq("session_code", session_code).execute()
        attended_count = attended_response.count if hasattr(attended_response, 'count') else len(attended_response.data) if attended_response.data else 0
        
        supabase.table("attendance_sessions").update({
            "attended_students": attended_count
        }).eq("session_code", session_code).execute()
        
        return True, "签到成功"
    except Exception as e:
        return False, f"签到失败: {str(e)}"

def get_teacher_classes(teacher_username):
    """获取教师创建的所有班级"""
    try:
        response = supabase.table("classrooms").select("*").eq("teacher_username", teacher_username).eq("is_active", True).order("created_at", desc=True).execute()
        
        classes = response.data if response.data else []
        
        # 获取每个班级的学生数和签到活动数
        for class_info in classes:
            class_code = class_info.get("class_code")
            
            # 获取学生数
            members_response = supabase.table("classroom_members").select("id", count="exact").eq("class_code", class_code).eq("role", 'student').execute()
            class_info["student_count"] = members_response.count if hasattr(members_response, 'count') else len(members_response.data) if members_response.data else 0
            
            # 获取签到活动数
            sessions_response = supabase.table("attendance_sessions").select("id", count="exact").eq("class_code", class_code).execute()
            class_info["session_count"] = sessions_response.count if hasattr(sessions_response, 'count') else len(sessions_response.data) if sessions_response.data else 0
        
        return classes
    except Exception as e:
        print(f"获取班级失败: {str(e)}")
        return []

def get_student_classes(student_username):
    """获取学生加入的所有班级"""
    try:
        response = supabase.table("classroom_members").select("class_code, joined_at, role").eq("student_username", student_username).eq("status", 'active').execute()
        
        classes = []
        
        if response.data:
            for member in response.data:
                class_code = member.get("class_code")
                joined_at = member.get("joined_at")
                
                # 获取班级信息
                class_response = supabase.table("classrooms").select("*").eq("class_code", class_code).execute()
                if class_response.data and len(class_response.data) > 0:
                    class_info = class_response.data[0]
                    class_info["joined_at"] = joined_at
                    
                    # 获取班级总学生数
                    members_response = supabase.table("classroom_members").select("id", count="exact").eq("class_code", class_code).eq("role", 'student').execute()
                    class_info["total_students"] = members_response.count if hasattr(members_response, 'count') else len(members_response.data) if members_response.data else 0
                    
                    # 获取签到活动数
                    sessions_response = supabase.table("attendance_sessions").select("id", count="exact").eq("class_code", class_code).execute()
                    class_info["total_sessions"] = sessions_response.count if hasattr(sessions_response, 'count') else len(sessions_response.data) if sessions_response.data else 0
                    
                    classes.append(class_info)
        
        return classes
    except Exception as e:
        print(f"获取学生班级失败: {str(e)}")
        return []

def get_class_attendance_sessions(class_code):
    """获取班级的所有签到活动"""
    try:
        response = supabase.table("attendance_sessions").select("session_code, session_name, start_time, end_time, duration_minutes, location_name, attendance_type, status, total_students, attended_students, created_at").eq("class_code", class_code).order("start_time", desc=True).execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"获取签到活动失败: {str(e)}")
        return []

def get_attendance_details(session_code):
    """获取签到活动的详细信息"""
    try:
        # 获取签到活动基本信息
        session_response = supabase.table("attendance_sessions").select("*").eq("session_code", session_code).execute()
        session_info = session_response.data[0] if session_response.data else None
        
        # 获取签到记录
        records_response = supabase.table("attendance_records").select("*").eq("session_code", session_code).order("check_in_time").execute()
        
        # 获取用户名
        records = []
        if records_response.data:
            for record in records_response.data:
                record["username"] = record.get("student_username")
                records.append(record)
        
        return session_info, records
    except Exception as e:
        print(f"获取签到详情失败: {str(e)}")
        return None, []

def delete_classroom_simple(class_code, teacher_username):
    """简单删除班级 - 软删除（标记为不活跃）"""
    try:
        # 简单验证：检查班级是否存在且教师匹配
        response = supabase.table("classrooms").select("teacher_username").eq("class_code", class_code).execute()
        
        if not response.data or len(response.data) == 0:
            return False, "班级不存在"
        
        if response.data[0].get("teacher_username") != teacher_username:
            return False, "只有创建教师可以删除班级"
        
        # 简单的软删除：将班级标记为不活跃
        supabase.table("classrooms").update({
            "is_active": False
        }).eq("class_code", class_code).execute()
        
        return True, "班级已成功删除"
    except Exception as e:
        return False, f"删除失败: {str(e)}"

def get_classroom_stats(class_code):
    """获取班级统计信息"""
    try:
        # 获取班级基本信息
        response = supabase.table("classrooms").select("class_name, teacher_username, created_at").eq("class_code", class_code).execute()
        
        if not response.data or len(response.data) == 0:
            return None
        
        class_info = response.data[0]
        
        # 获取成员数
        members_response = supabase.table("classroom_members").select("id", count="exact").eq("class_code", class_code).execute()
        total_members = members_response.count if hasattr(members_response, 'count') else len(members_response.data) if members_response.data else 0
        
        # 获取签到活动数
        sessions_response = supabase.table("attendance_sessions").select("id", count="exact").eq("class_code", class_code).execute()
        total_sessions = sessions_response.count if hasattr(sessions_response, 'count') else len(sessions_response.data) if sessions_response.data else 0
        
        # 获取签到记录数
        records_response = supabase.table("attendance_records").select("id", count="exact").eq("class_code", class_code).execute()
        total_attendance_records = records_response.count if hasattr(records_response, 'count') else len(records_response.data) if records_response.data else 0
        
        return {
            'class_name': class_info.get("class_name"),
            'teacher_username': class_info.get("teacher_username"),
            'created_at': class_info.get("created_at"),
            'total_members': total_members,
            'total_sessions': total_sessions,
            'total_attendance_records': total_attendance_records
        }
    except Exception as e:
        print(f"获取班级统计失败: {str(e)}")
        return None

def update_classroom_info(class_code, teacher_username, class_name=None, description=None, max_students=None):
    """
    更新班级信息
    
    Args:
        class_code: 班级代码
        teacher_username: 教师用户名（用于权限验证）
        class_name: 新的班级名称（可选）
        description: 新的班级描述（可选）
        max_students: 新的最大学生数（可选）
    
    Returns:
        (success, message): 成功标志和信息
    """
    try:
        # 验证教师权限
        response = supabase.table("classrooms").select("teacher_username, class_name").eq("class_code", class_code).eq("is_active", True).execute()
        
        if not response.data or len(response.data) == 0:
            return False, "班级不存在或已被删除"
        
        current_teacher = response.data[0].get("teacher_username")
        current_class_name = response.data[0].get("class_name")
        
        if current_teacher != teacher_username:
            return False, "只有创建教师可以修改班级信息"
        
        # 构建更新数据
        update_data = {}
        
        if class_name:
            update_data["class_name"] = class_name
        
        if description is not None:
            update_data["description"] = description
        
        if max_students:
            # 检查新的人数限制是否小于当前人数
            members_response = supabase.table("classroom_members").select("id", count="exact").eq("class_code", class_code).eq("status", 'active').execute()
            current_student_count = members_response.count if hasattr(members_response, 'count') else len(members_response.data) if members_response.data else 0
            
            if max_students < current_student_count:
                return False, f"当前已有 {current_student_count} 名学生，最大学生数不能小于当前人数"
            
            update_data["max_students"] = max_students
        
        if not update_data:
            return True, "没有需要更新的信息"
        
        # 执行更新
        supabase.table("classrooms").update(update_data).eq("class_code", class_code).execute()
        
        return True, "班级信息更新成功"
        
    except Exception as e:
        return False, f"更新班级信息失败: {str(e)}"

def delete_classroom_enhanced(class_code, teacher_username, delete_type="soft"):
    """
    删除班级（增强版）
    
    Args:
        class_code: 班级代码
        teacher_username: 教师用户名
        delete_type: 删除类型
            - 'soft': 软删除（只标记为不活跃）
            - 'hard': 硬删除（删除所有相关数据）
    """
    try:
        # 验证教师权限
        response = supabase.table("classrooms").select("teacher_username, class_name").eq("class_code", class_code).execute()
        
        if not response.data or len(response.data) == 0:
            return False, "班级不存在"
        
        if response.data[0].get("teacher_username") != teacher_username:
            return False, "只有创建教师可以删除班级"
        
        class_name = response.data[0].get("class_name")
        
        if delete_type == "soft":
            # 软删除：更新班级状态
            supabase.table("classrooms").update({
                "is_active": False
            }).eq("class_code", class_code).execute()
            
            message = f"班级 '{class_name}' 已标记为删除（不活跃状态）"
            
        elif delete_type == "hard":
            # 硬删除：删除所有相关数据
            # 注意：按照外键约束顺序删除
            
            # 1. 获取所有签到活动代码
            sessions_response = supabase.table("attendance_sessions").select("session_code").eq("class_code", class_code).execute()
            session_codes = [s["session_code"] for s in sessions_response.data] if sessions_response.data else []
            
            # 2. 删除签到记录
            if session_codes:
                for code in session_codes:
                    supabase.table("attendance_records").delete().eq("session_code", code).execute()
            
            # 3. 删除签到活动
            supabase.table("attendance_sessions").delete().eq("class_code", class_code).execute()
            
            # 4. 删除通知
            supabase.table("class_notifications").delete().eq("class_code", class_code).execute()
            
            # 5. 删除班级成员
            supabase.table("classroom_members").delete().eq("class_code", class_code).execute()
            
            # 6. 删除班级
            supabase.table("classrooms").delete().eq("class_code", class_code).execute()
            
            message = f"班级 '{class_name}' 及相关数据已永久删除"
        
        else:
            return False, "无效的删除类型"
        
        return True, message
        
    except Exception as e:
        return False, f"删除班级失败: {str(e)}"

def get_attendance_report(teacher_username, start_date=None, end_date=None, class_code=None):
    """获取签到报表数据"""
    try:
        # 构建查询
        query = supabase.table("attendance_sessions").select(
            "session_code, session_name, class_code, start_time, end_time, total_students, attended_students, created_at"
        ).eq("teacher_username", teacher_username)
        
        if class_code and class_code != "全部":
            query = query.eq("class_code", class_code)
        
        if start_date:
            query = query.gte("start_time", start_date)
        if end_date:
            query = query.lte("start_time", end_date)
        
        response = query.order("start_time", desc=True).execute()
        sessions = response.data if response.data else []
        
        # 获取班级名称
        for session in sessions:
            class_response = supabase.table("classrooms").select("class_name").eq("class_code", session.get("class_code")).execute()
            if class_response.data and len(class_response.data) > 0:
                session["class_name"] = class_response.data[0].get("class_name")
        
        return sessions
    except Exception as e:
        print(f"获取报表失败: {str(e)}")
        return []

def export_report_to_excel(sessions):
    """导出报表到Excel"""
    try:
        if not sessions:
            return None, "没有数据可导出"
        
        # 准备数据
        data = []
        for session in sessions:
            start_dt = from_beijing_time_str(session.get("start_time"))
            end_dt = from_beijing_time_str(session.get("end_time"))
            attendance_rate = (session.get("attended_students", 0) / session.get("total_students", 1) * 100) if session.get("total_students", 0) > 0 else 0
            
            data.append({
                "签到代码": session.get("session_code"),
                "签到名称": session.get("session_name"),
                "班级": session.get("class_name", session.get("class_code")),
                "开始时间": session.get("start_time"),
                "结束时间": session.get("end_time"),
                "时长(分钟)": session.get("duration_minutes", 0),
                "应到人数": session.get("total_students", 0),
                "实到人数": session.get("attended_students", 0),
                "签到率(%)": round(attendance_rate, 2),
                "创建时间": session.get("created_at")
            })
        
        df = pd.DataFrame(data)
        
        # 创建Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='签到报表', index=False)
            
            # 添加汇总
            summary_data = {
                "统计项": ["总签到次数", "平均签到率", "总应到人次", "总实到人次"],
                "数值": [
                    len(sessions),
                    round(df["签到率(%)"].mean(), 2),
                    df["应到人数"].sum(),
                    df["实到人数"].sum()
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='汇总', index=False)
        
        output.seek(0)
        return output, None
    except Exception as e:
        return None, f"导出失败: {str(e)}"

# ==================== CSS样式 ====================
def apply_modern_css():
    st.markdown("""
    <style>
    /* 现代化米色主题变量 */
    :root {
        --primary-red: #dc2626;
        --dark-red: #b91c1c;
        --accent-red: #ef4444;
        --light-red: #fee2e2;
        --beige-light: #fefaf0;
        --beige-medium: #fdf6e3;
        --beige-dark: #faf0d9;
        --gold: #d4af37;
        --light-gold: #fef3c7;
        --dark-text: #1f2937;
        --light-text: #6b7280;
        --card-shadow: 0 10px 25px -5px rgba(220, 38, 38, 0.1), 0 8px 10px -6px rgba(220, 38, 38, 0.1);
        --hover-shadow: 0 25px 50px -12px rgba(220, 38, 38, 0.25);
    }
    
    /* 整体页面背景 - 米色渐变 */
    .stApp {
        background: linear-gradient(135deg, #fefaf0 0%, #fdf6e3 50%, #faf0d9 100%);
    }
    
    /* 侧边栏样式 - 米色渐变 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #fdf6e3 0%, #faf0d9 50%, #f5e6c8 100%) !important;
    }
    
    /* 现代化头部 */
    .modern-header {
        background: linear-gradient(135deg, var(--primary-red) 0%, var(--dark-red) 100%);
        color: white;
        padding: 30px;
        text-align: center;
        border-radius: 20px;
        margin: 20px 0 30px 0;
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .class-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: var(--card-shadow);
        border-left: 4px solid var(--primary-red);
        transition: all 0.3s ease;
    }
    
    .class-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--hover-shadow);
    }
    
    .attendance-card {
        background: linear-gradient(135deg, #fff, #fef2f2);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border: 2px solid var(--primary-red);
        position: relative;
        overflow: hidden;
    }
    
    .attendance-card.active {
        border-color: #10b981;
        background: linear-gradient(135deg, #fff, #f0fdf4);
    }
    
    .attendance-card.expired {
        border-color: #9ca3af;
        background: linear-gradient(135deg, #fff, #f3f4f6);
        opacity: 0.8;
    }
    
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }
    
    .badge-danger {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
    }
    
    .badge-info {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
    }
    
    .qr-code-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        display: inline-block;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 2px solid var(--primary-red);
    }
    
    .timer-container {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: var(--primary-red);
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: var(--card-shadow);
        margin-bottom: 20px;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--primary-red);
        margin: 10px 0;
    }
    
    .stat-label {
        color: var(--light-text);
        font-size: 0.9rem;
    }
    
    /* 报表卡片 */
    .report-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .report-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--primary-red);
    }
    
    .report-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: var(--primary-red);
    }
    
    .report-meta {
        color: var(--light-text);
        font-size: 0.9rem;
    }
    
    .filter-panel {
        background: linear-gradient(135deg, #fff, #fefaf0);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border: 2px solid var(--gold);
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
    
    /* 整体页面内容区域 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: linear-gradient(135deg, #fefaf0 0%, #fdf6e3 50%, #faf0d9 100%);
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

# ==================== 侧边栏 ====================
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; 
            padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px;
            box-shadow: 0 6px 12px rgba(220, 38, 38, 0.3);'>
            <h3 style='margin: 0;'>🏫 班级管理</h3>
            <p style='margin: 10px 0 0 0; font-size: 1rem;'>智能签到 · 高效教学</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 快速导航
        st.markdown("### 🧭 快速导航")
        
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("main.py")
        
        if st.session_state.logged_in:
            role = st.session_state.role
            
            if role == "teacher":
                if st.button("📊 教师控制台", use_container_width=True):
                    st.session_state.current_page = "teacher_dashboard"
                    st.rerun()
                if st.button("➕ 创建班级", use_container_width=True):
                    st.session_state.current_page = "create_classroom"
                    st.rerun()
                if st.button("📝 创建签到", use_container_width=True):
                    st.session_state.current_page = "create_attendance"
                    st.rerun()
                if st.button("📈 签到报表", use_container_width=True):
                    st.session_state.current_page = "reports"
                    st.rerun()
            
            elif role == "student":
                if st.button("🎯 我的班级", use_container_width=True):
                    st.session_state.current_page = "student_classes"
                    st.rerun()
                if st.button("📱 在线签到", use_container_width=True):
                    st.session_state.current_page = "attendance_checkin"
                    st.rerun()
                if st.button("🔍 查找班级", use_container_width=True):
                    st.session_state.current_page = "find_classroom"
                    st.rerun()
        
        # 平台特色
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fee2e2, #fecaca); padding: 25px; 
                    border-radius: 15px; border-left: 5px solid #dc2626; margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);'>
            <h4 style='color: #dc2626;'>🎯 功能特色</h4>
            <ul style='padding-left: 20px; color: #7f1d1d;'>
                <li style='color: #dc2626;'>🏫 智能分班管理</li>
                <li style='color: #dc2626;'>📱 多种签到方式</li>
                <li style='color: #dc2626;'>📊 实时数据分析</li>
                <li style='color: #dc2626;'>📈 详细报表导出</li>
                <li style='color: #dc2626;'>🔒 安全可靠</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 签到状态
        if st.session_state.logged_in:
            try:
                username = st.session_state.username
                role = st.session_state.role
                
                if role == "student":
                    # 学生签到统计
                    records_response = supabase.table("attendance_records").select("session_code, points_earned").eq("student_username", username).execute()
                    records = records_response.data if records_response.data else []
                    
                    total_sessions = len(set([r.get("session_code") for r in records]))
                    attended_sessions = len(records)
                    
                    points = [r.get("points_earned", 0) for r in records if r.get("points_earned") is not None]
                    avg_points = sum(points) / len(points) if points else 0
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f0fdf4, #dcfce7); padding: 20px; 
                                border-radius: 12px; border: 2px solid #10b981; margin-bottom: 20px;'>
                        <h5 style='color: #10b981; text-align: center;'>📊 我的签到</h5>
                        <p style='color: #065f46; text-align: center; font-size: 0.9rem;'>
                        📅 总活动: {total_sessions}<br>
                        ✅ 已签到: {attended_sessions}<br>
                        ⭐ 平均分: {avg_points:.1f}分
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                pass
        
        # 今日提示
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fef3c7, #fde68a); padding: 20px; 
                    border-radius: 12px; border: 2px solid #d4af37; margin-bottom: 20px;'>
            <h5 style='color: #b45309; text-align: center;'>💡 使用提示</h5>
            <p style='font-size: 0.85rem; color: #78350f; text-align: center;'>
            教师可创建班级和签到活动<br>
            学生可加入班级并参与签到<br>
            签到可获得积分奖励<br>
            教师可在报表页面查看详细数据
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 系统信息
        st.markdown("---")
        st.markdown("**📊 系统信息**")
        st.text(f"北京时间: {get_beijing_time().strftime('%Y-%m-%d %H:%M')}")
        st.text("状态: 🟢 运行中")
        st.text("版本: v1.0.0 (Supabase)")

# ==================== 页面渲染函数 ====================

def render_teacher_dashboard():
    """教师控制台"""
    st.markdown("""
    <div class='modern-header'>
        <h2>👨‍🏫 教师控制台</h2>
        <p>管理班级、创建签到、查看统计</p>
    </div>
    """, unsafe_allow_html=True)
    
    username = st.session_state.username

    # 获取真实的统计数据
    try:
        # 1. 获取班级数量
        classes_response = supabase.table("classrooms").select("id", count="exact").eq("teacher_username", username).eq("is_active", True).execute()
        total_classes = classes_response.count if hasattr(classes_response, 'count') else len(classes_response.data) if classes_response.data else 0
        
        # 2. 获取总学生数
        teacher_classes_response = supabase.table("classrooms").select("class_code").eq("teacher_username", username).eq("is_active", True).execute()
        class_codes = [c["class_code"] for c in teacher_classes_response.data] if teacher_classes_response.data else []
        
        total_students = 0
        if class_codes:
            for code in class_codes:
                members_response = supabase.table("classroom_members").select("id", count="exact").eq("class_code", code).eq("role", 'student').eq("status", 'active').execute()
                count = members_response.count if hasattr(members_response, 'count') else len(members_response.data) if members_response.data else 0
                total_students += count
        
        # 3. 获取签到活动总数
        sessions_response = supabase.table("attendance_sessions").select("id", count="exact").eq("teacher_username", username).execute()
        total_sessions = sessions_response.count if hasattr(sessions_response, 'count') else len(sessions_response.data) if sessions_response.data else 0
        
    except Exception as e:
        print(f"获取统计数据失败: {str(e)}")
        total_classes = 0
        total_students = 0
        total_sessions = 0
    
    # 统计卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        html1 = f"""
        <div class='stat-card'>
            <div>🏫</div>
            <div class='stat-number'>{total_classes}</div>
            <div class='stat-label'>我的班级</div>
        </div>
        """
        st.markdown(html1, unsafe_allow_html=True)
    
    with col2:
        html2 = f"""
        <div class='stat-card'>
            <div>👥</div>
            <div class='stat-number'>{total_students}</div>
            <div class='stat-label'>总学生数</div>
        </div>
        """
        st.markdown(html2, unsafe_allow_html=True)
    
    with col3:
        html3 = f"""
        <div class='stat-card'>
            <div>📝</div>
            <div class='stat-number'>{total_sessions}</div>
            <div class='stat-label'>签到活动</div>
        </div>
        """
        st.markdown(html3, unsafe_allow_html=True)
    
    # 获取教师班级数据
    teacher_classes = get_teacher_classes(username)
    
    if teacher_classes:
        # 显示班级列表
        st.markdown("### 📚 我的班级")
        
        for class_info in teacher_classes:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='padding: 15px;'>
                        <h4 style='margin: 0; color: #dc2626;'>{class_info.get('class_name')}</h4>
                        <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                        班级代码: <strong>{class_info.get('class_code')}</strong>
                        </p>
                        <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                        {class_info.get('description') or '暂无描述'}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='padding: 15px;'>
                        <p style='margin: 5px 0;'>👥 学生: {class_info.get('student_count', 0)}/{class_info.get('max_students', 50)}</p>
                        <p style='margin: 5px 0;'>📝 签到: {class_info.get('session_count', 0)}次</p>
                        <p style='margin: 5px 0;'>📅 创建: {class_info.get('created_at', '')[:10]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if st.button("管理", key=f"manage_{class_info.get('class_code')}"):
                        st.session_state.selected_class = class_info.get('class_code')
                        st.session_state.current_page = "class_management"
                        st.rerun()
        
        # 快速操作
        st.markdown("---")
        st.markdown("### ⚡ 快速操作")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ 创建新班级", use_container_width=True):
                st.session_state.current_page = "create_classroom"
                st.rerun()
        
        with col2:
            if st.button("📝 创建签到", use_container_width=True):
                st.session_state.current_page = "create_attendance"
                st.rerun()
        
    else:
        # 没有班级的提示
        st.info("您还没有创建任何班级，点击下方按钮创建第一个班级吧！")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ 创建我的第一个班级", use_container_width=True, type="primary"):
                st.session_state.current_page = "create_classroom"
                st.rerun()

def render_create_classroom():
    """创建班级页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>➕ 创建新班级</h2>
        <p>创建您的第一个教学班级</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        class_name = st.text_input("📝 班级名称", 
                                  placeholder="例如：2025春季数字图像处理班",
                                  key="class_name_input")
    
    with col2:
        max_students = st.number_input("👥 最大学生数", 
                                     min_value=1, 
                                     max_value=500, 
                                     value=50,
                                     key="max_students_input")
    
    description = st.text_area("📋 班级描述",
                             placeholder="请输入班级介绍、课程目标等信息...",
                             height=100,
                             key="description_input")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        create_btn = st.button("🚀 创建班级", use_container_width=True, type="primary")
    
    with col_btn2:
        cancel_btn = st.button("❌ 取消", use_container_width=True)
    
    if cancel_btn:
        st.session_state.current_page = "teacher_dashboard"
        st.rerun()
    
    if create_btn:
        if class_name:
            with st.spinner("正在创建班级..."):
                success, result = create_classroom(
                    st.session_state.username,
                    class_name,
                    description,
                    max_students
                )
                
                if success:
                    st.success(f"🎉 班级创建成功！班级代码：**{result}**")
                    st.info("请将班级代码分享给学生，学生可以使用此代码加入班级")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🏫 前往班级管理", use_container_width=True, key="go_to_manage"):
                            st.session_state.selected_class = result
                            st.session_state.current_page = "class_management"
                            st.rerun()
                    
                    with col2:
                        if st.button("📝 立即创建签到", use_container_width=True, key="go_to_create_attendance"):
                            st.session_state.selected_class = result
                            st.session_state.current_page = "create_attendance"
                            st.rerun()
                else:
                    st.error(f"❌ {result}")
        else:
            st.warning("⚠️ 请输入班级名称")

def render_class_management():
    """班级管理页面 - 允许学生查看班级详情"""
    if 'selected_class' not in st.session_state:
        st.session_state.current_page = "teacher_dashboard"
        st.rerun()
    
    class_code = st.session_state.selected_class
    
    # 获取班级信息
    response = supabase.table("classrooms").select("class_name, description, teacher_username, created_at, max_students").eq("class_code", class_code).execute()
    
    if not response.data or len(response.data) == 0:
        st.error("班级不存在")
        return
    
    class_info = response.data[0]
    class_name = class_info.get("class_name")
    description = class_info.get("description")
    teacher_username = class_info.get("teacher_username")
    created_at = class_info.get("created_at")
    max_students = class_info.get("max_students", 50)
    
    # 检查当前用户是否有权限管理班级
    role = st.session_state.role
    username = st.session_state.username
    is_teacher = (role == "teacher" and username == teacher_username)
    
    # 获取班级成员
    members_response = supabase.table("classroom_members").select("student_username, joined_at, role").eq("class_code", class_code).eq("status", 'active').execute()
    members = members_response.data if members_response.data else []
    
    # 为每个成员获取签到次数
    for member in members:
        student_username = member.get("student_username")
        records_response = supabase.table("attendance_records").select("id", count="exact").eq("student_username", student_username).eq("class_code", class_code).execute()
        member["attendance_count"] = records_response.count if hasattr(records_response, 'count') else len(records_response.data) if records_response.data else 0
    
    members = sorted(members, key=lambda x: x.get("joined_at", ""))
    
    # 获取签到活动
    sessions = get_class_attendance_sessions(class_code)
    
    st.markdown(f"""
    <div class='modern-header'>
        <h2>🏫 {class_name}</h2>
        <p>班级代码: <strong>{class_code}</strong> | 创建时间: {created_at[:10]}</p>
        <p>授课教师: {teacher_username} | 您的角色: {'教师' if is_teacher else '学生'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 根据用户角色显示不同的选项卡
    if is_teacher:
        tab1, tab2, tab3, tab4 = st.tabs(["👥 班级成员", "📝 签到活动", "📊 数据分析", "⚙️ 班级设置"])
    else:
        tab1, tab2, tab3 = st.tabs(["👥 班级成员", "📝 签到活动", "📊 数据分析"])
    
    with tab1:
        st.markdown(f"### 👥 班级成员 ({len(members)}人/{max_students}人)")
        
        if members:
            members_data = []
            for member in members:
                members_data.append({
                    "用户名": member.get("student_username"),
                    "身份": "教师" if member.get("role") == "teacher" else "学生",
                    "加入时间": member.get("joined_at", "")[:10],
                    "参与签到": member.get("attendance_count", 0)
                })
            
            df_members = pd.DataFrame(members_data)
            st.dataframe(df_members, use_container_width=True, hide_index=True)
            
            if is_teacher:
                csv = df_members.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 导出成员名单",
                    data=csv,
                    file_name=f"{class_code}_members.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("暂无班级成员")
        
        if is_teacher:
            st.markdown("---")
            st.markdown("### ➕ 添加成员")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_member = st.text_input("输入用户名添加成员", placeholder="请输入学生用户名", key="new_member_input")
            
            with col2:
                if st.button("添加", use_container_width=True, key="add_member_btn"):
                    if new_member:
                        success, msg = join_classroom(new_member, class_code)
                        if success:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        st.warning("请输入用户名")
    
    with tab2:
        st.markdown("### 📝 签到活动")
        
        if sessions:
            for session in sessions:
                session_code = session.get("session_code")
                session_name = session.get("session_name")
                start_time = session.get("start_time")
                end_time = session.get("end_time")
                status = session.get("status")
                total = session.get("total_students", 0)
                attended = session.get("attended_students", 0)
                
                start_dt = from_beijing_time_str(start_time)
                end_dt = from_beijing_time_str(end_time)
                
                attendance_rate = (attended / total * 100) if total > 0 else 0
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='padding: 15px; border-radius: 10px; background: #f9fafb;'>
                        <h4 style='margin: 0;'>{session_name}</h4>
                        <p style='margin: 5px 0; font-size: 0.9rem; color: #6b7280;'>
                        📅 {start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')}
                        </p>
                        <p style='margin: 5px 0; font-size: 0.9rem;'>
                        签到代码: <code>{session_code}</code>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    badge_class = 'badge-success' if status == 'completed' else 'badge-warning' if status == 'active' else 'badge-info'
                    badge_text = '已完成' if status == 'completed' else '进行中' if status == 'active' else '已计划'
                    
                    st.markdown(f"""
                    <div style='padding: 15px;'>
                        <p style='margin: 5px 0;'>👥 {attended}/{total}</p>
                        <p style='margin: 5px 0;'>📊 {attendance_rate:.1f}%</p>
                        <p style='margin: 5px 0;'>
                        <span class='badge {badge_class}'>
                            {badge_text}
                        </span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if st.button("详情", key=f"detail_{session_code}"):
                        st.session_state.selected_session = session_code
                        st.session_state.current_page = "attendance_detail"
                        st.rerun()
        else:
            st.info("暂无签到活动")
        
        if is_teacher:
            st.markdown("---")
            if st.button("➕ 创建新签到活动", use_container_width=True):
                st.session_state.current_page = "create_attendance"
                st.rerun()
    
    with tab3:
        st.markdown("### 📊 数据分析")
        
        if sessions:
            session_names = []
            attendance_rates = []
            
            for session in sessions:
                session_name = session.get("session_name", "")
                total = session.get("total_students", 0)
                attended = session.get("attended_students", 0)
                rate = (attended / total * 100) if total > 0 else 0
                
                short_name = session_name[:15] + "..." if len(session_name) > 15 else session_name
                session_names.append(short_name)
                attendance_rates.append(rate)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=session_names,
                    y=attendance_rates,
                    marker_color=['#ef4444' if rate < 70 else '#f59e0b' if rate < 90 else '#10b981' for rate in attendance_rates]
                )
            ])
            
            fig.update_layout(
                title="各签到活动参与率",
                xaxis_title="签到活动",
                yaxis_title="参与率 (%)",
                yaxis=dict(range=[0, 100]),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无数据可分析")
    
    if is_teacher and 'tab4' in locals():
        with tab4:
            st.markdown("### ⚙️ 班级设置")
            
            new_class_name = st.text_input("班级名称", value=class_name, key="new_class_name")
            new_description = st.text_area("班级描述", value=description or "", height=100, key="new_description")
            new_max_students = st.number_input("最大学生数", min_value=1, max_value=500, value=max_students, key="new_max_students")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 保存设置", use_container_width=True, type="primary"):
                    success, msg = update_classroom_info(
                        class_code, 
                        username, 
                        new_class_name if new_class_name != class_name else None,
                        new_description if new_description != description else None,
                        new_max_students if new_max_students != max_students else None
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            with col2:
                if st.button("🗑️ 删除班级", use_container_width=True):
                    st.warning("此操作不可恢复，请确认")
                    if st.button("确认永久删除", key="confirm_delete"):
                        success, msg = delete_classroom_enhanced(class_code, username, "hard")
                        if success:
                            st.success(msg)
                            st.session_state.current_page = "teacher_dashboard"
                            st.rerun()
                        else:
                            st.error(msg)

def render_create_attendance():
    """创建签到活动页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>📝 创建签到活动</h2>
        <p>为您的班级创建在线签到</p>
    </div>
    """, unsafe_allow_html=True)
    
    username = st.session_state.username
    
    # 获取教师的班级列表
    teacher_classes = get_teacher_classes(username)
    
    if not teacher_classes:
        st.warning("您还没有创建任何班级，请先创建班级")
        if st.button("🏫 去创建班级"):
            st.session_state.current_page = "create_classroom"
            st.rerun()
        return
    
    # 选择班级
    class_options = {c['class_code']: f"{c['class_name']} ({c['class_code']})" for c in teacher_classes}
    selected_class = st.selectbox("选择班级", options=list(class_options.keys()), 
                                 format_func=lambda x: class_options[x],
                                 key="class_select")
    
    col1, col2 = st.columns(2)
    
    with col1:
        session_name = st.text_input("📝 签到活动名称", 
                                    placeholder="例如：第1次课程签到",
                                    key="session_name_input")
    
    with col2:
        attendance_type = st.selectbox("📱 签到方式", 
                                      options=['standard'],
                                      format_func=lambda x: {
                                          'standard': '标准签到'
                                      }[x],
                                      key="attendance_type_select")
    
    col3, col4 = st.columns(2)
    
    with col3:
        date_val = st.date_input("📅 签到日期", 
                               value=get_beijing_time().date(),
                               min_value=get_beijing_time().date(),
                               key="date_input")
        time_val = st.time_input("⏰ 开始时间", 
                               value=(get_beijing_time() + timedelta(minutes=5)).time(),
                               key="time_input")
        start_time = datetime.combine(date_val, time_val)
    
    with col4:
        duration_minutes = st.number_input("⏱️ 签到时长(分钟)", 
                                         min_value=1, 
                                         max_value=180, 
                                         value=15,
                                         key="duration_input")
    
    end_time = start_time + timedelta(minutes=duration_minutes)
    location_name = st.text_input("📍 签到地点(可选)", 
                                 placeholder="例如：信息楼301教室",
                                 key="location_input")    
    
    st.info(f"签到时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')} 至 {end_time.strftime('%H:%M:%S')} (北京时间)")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        create_btn = st.button("🚀 创建签到", use_container_width=True, type="primary", key="create_attendance_btn")
    
    with col_btn2:
        cancel_btn = st.button("❌ 取消", use_container_width=True, key="cancel_attendance_btn")
    
    if cancel_btn:
        st.session_state.current_page = "teacher_dashboard"
        st.rerun()
    
    if create_btn:
        if session_name:
            with st.spinner("正在创建签到活动..."):
                success, result = create_attendance_session(
                    selected_class,
                    username,
                    session_name,
                    start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    duration_minutes,
                    location_name,
                    attendance_type
                )
                
                if success:
                    st.success(f"🎉 签到活动创建成功！签到代码：**{result}**")
                    
                    st.markdown(f"""
                    <div class='attendance-card active'>
                        <h3 style='margin: 0; color: #10b981;'>签到信息</h3>
                        <p><strong>签到代码：</strong>{result}</p>
                        <p><strong>签到方式：</strong>标准签到</p>
                        <p><strong>有效时间：</strong>{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}</p>
                        <p><strong>签到地点：</strong>{location_name or "无限制"}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.code(result, language="text")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 复制签到代码", use_container_width=True, key="copy_code_btn"):
                            st.toast("签到代码已复制到剪贴板")
                    
                    with col2:
                        if st.button("📊 查看签到详情", use_container_width=True, key="view_detail_btn"):
                            st.session_state.selected_session = result
                            st.session_state.current_page = "attendance_detail"
                            st.rerun()
                else:
                    st.error(f"❌ {result}")
        else:
            st.warning("⚠️ 请输入签到活动名称")

def render_attendance_checkin():
    """学生签到页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>📱 在线签到</h2>
        <p>参与班级签到活动</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        st.warning("请先登录")
        return
    
    username = st.session_state.username
    
    try:
        # 获取学生加入的班级
        members_response = supabase.table("classroom_members").select("class_code").eq("student_username", username).eq("status", 'active').execute()
        class_codes = [row["class_code"] for row in members_response.data] if members_response.data else []
        
        if not class_codes:
            st.info("您还没有加入任何班级")
            if st.button("🔍 查找班级"):
                st.session_state.current_page = "find_classroom"
                st.rerun()
            return
        
        current_time = to_beijing_time_str()
        
        # 获取当前可签到的活动
        active_sessions = []
        upcoming_sessions = []
        
        for class_code in class_codes:
            # 获取班级名称
            class_response = supabase.table("classrooms").select("class_name").eq("class_code", class_code).execute()
            class_name = class_response.data[0]["class_name"] if class_response.data else "未知班级"
            
            # 获取签到活动
            sessions_response = supabase.table("attendance_sessions").select("*").eq("class_code", class_code).execute()
            
            if sessions_response.data:
                for session in sessions_response.data:
                    start_time = session.get("start_time")
                    end_time = session.get("end_time")
                    session_code = session.get("session_code")
                    
                    # 检查是否已签到
                    check_response = supabase.table("attendance_records").select("id").eq("session_code", session_code).eq("student_username", username).execute()
                    has_checked_in = len(check_response.data) > 0 if check_response.data else False
                    
                    session["class_name"] = class_name
                    session["has_checked_in"] = has_checked_in
                    
                    if current_time >= start_time and current_time <= end_time:
                        active_sessions.append(session)
                    elif current_time < start_time:
                        upcoming_sessions.append(session)
        
        # 显示当前可签到活动
        if active_sessions:
            st.markdown("### 🟢 当前可签到")
            
            for session in active_sessions:
                session_code = session.get("session_code")
                session_name = session.get("session_name")
                start_time = session.get("start_time")
                end_time = session.get("end_time")
                location_name = session.get("location_name")
                class_name = session.get("class_name")
                has_checked_in = session.get("has_checked_in", False)
                
                start_dt = from_beijing_time_str(start_time)
                end_dt = from_beijing_time_str(end_time)
                
                remaining_minutes = (end_dt - get_beijing_time()).total_seconds() / 60
                
                if has_checked_in:
                    st.markdown(f"""
                    <div class='attendance-card' style='border-color: #10b981;'>
                        <h4 style='margin: 0; color: #10b981;'>✅ {session_name}</h4>
                        <p style='margin: 5px 0;'><strong>班级：</strong>{class_name}</p>
                        <p style='margin: 5px 0;'><strong>时间：</strong>{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}</p>
                        <p style='margin: 5px 0;'><strong>地点：</strong>{location_name or '无限制'}</p>
                        <p style='margin: 5px 0; color: #10b981; font-weight: bold;'>✓ 您已完成签到</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div style='padding: 15px; border-radius: 10px; background: #f0fdf4;'>
                                <h4 style='margin: 0;'>{session_name}</h4>
                                <p style='margin: 5px 0;'><strong>班级：</strong>{class_name}</p>
                                <p style='margin: 5px 0;'><strong>时间：</strong>{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}</p>
                                <p style='margin: 5px 0;'><strong>地点：</strong>{location_name or '无限制'}</p>
                                <p style='margin: 5px 0; color: #ef4444;'>
                                ⏰ 剩余时间: {int(remaining_minutes)}分钟
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("签到", key=f"checkin_{session_code}", use_container_width=True):
                                with st.spinner("正在签到..."):
                                    success, msg = check_in_attendance(
                                        session_code, 
                                        username,
                                        check_in_method='web',
                                        device_info='Web Browser'
                                    )
                                    
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
        
        else:
            st.info("暂无当前可签到的活动")
        
        # 显示即将开始的签到活动
        if upcoming_sessions:
            st.markdown("### 📅 即将开始")
            
            for session in upcoming_sessions:
                session_name = session.get("session_name")
                class_name = session.get("class_name")
                start_time = session.get("start_time")
                location_name = session.get("location_name")
                
                start_dt = from_beijing_time_str(start_time)
                time_until = (start_dt - get_beijing_time()).total_seconds() / 3600
                
                if time_until < 24:
                    st.markdown(f"""
                    <div class='attendance-card'>
                        <h4 style='margin: 0;'>{session_name}</h4>
                        <p style='margin: 5px 0;'><strong>班级：</strong>{class_name}</p>
                        <p style='margin: 5px 0;'><strong>开始时间：</strong>{start_dt.strftime('%m月%d日 %H:%M')}</p>
                        <p style='margin: 5px 0;'><strong>地点：</strong>{location_name or '待定'}</p>
                        <p style='margin: 5px 0; color: #f59e0b;'>
                        ⏳ 将在{int(time_until)}小时后开始
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 手动输入签到代码
        st.markdown("---")
        st.markdown("### 🔢 手动签到")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            manual_code = st.text_input("输入签到代码", placeholder="请输入6位签到代码", key="manual_code_input")
        
        with col2:
            if st.button("提交", use_container_width=True, key="manual_submit_btn"):
                if manual_code:
                    with st.spinner("正在验证签到代码..."):
                        success, msg = check_in_attendance(
                            manual_code.upper(),
                            username,
                            check_in_method='manual',
                            device_info='Web Browser'
                        )
                        
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.warning("请输入签到代码")
    
    except Exception as e:
        st.error(f"获取签到信息失败: {str(e)}")

def render_find_classroom():
    """查找班级页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>🔍 查找班级</h2>
        <p>查找并加入感兴趣的班级</p>
    </div>
    """, unsafe_allow_html=True)
    
    search_type = st.radio("搜索方式", ["🔢 班级代码", "📝 班级名称"], horizontal=True, key="search_type_radio")
    
    if search_type == "🔢 班级代码":
        class_code = st.text_input("请输入班级代码", placeholder="例如：CLS123456", key="class_code_search")
        
        if class_code:
            try:
                response = supabase.table("classrooms").select("*").eq("class_code", class_code.upper()).eq("is_active", True).execute()
                
                if response.data and len(response.data) > 0:
                    class_info = response.data[0]
                    
                    # 获取当前学生数
                    members_response = supabase.table("classroom_members").select("id", count="exact").eq("class_code", class_code.upper()).eq("status", 'active').execute()
                    current_students = members_response.count if hasattr(members_response, 'count') else len(members_response.data) if members_response.data else 0
                    
                    # 检查是否已经加入
                    check_response = supabase.table("classroom_members").select("id").eq("class_code", class_code.upper()).eq("student_username", st.session_state.username).execute()
                    already_joined = len(check_response.data) > 0 if check_response.data else False
                    
                    st.markdown(f"""
                    <div class='class-card'>
                        <h3 style='color: #dc2626;'>{class_info.get('class_name')}</h3>
                        <p><strong>班级代码：</strong><code>{class_info.get('class_code')}</code></p>
                        <p><strong>授课教师：</strong>{class_info.get('teacher_username')}</p>
                        <p><strong>创建时间：</strong>{class_info.get('created_at')[:10]}</p>
                        <p><strong>班级规模：</strong>{current_students}/{class_info.get('max_students', 50)}人</p>
                        <p><strong>班级描述：</strong></p>
                        <p style='color: #6b7280;'>{class_info.get('description') or '暂无描述'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if not already_joined:
                        if current_students >= class_info.get('max_students', 50):
                            st.error("⚠️ 班级人数已满")
                        else:
                            if st.button("🎯 加入班级", type="primary", use_container_width=True, key="join_class_btn"):
                                success, msg = join_classroom(st.session_state.username, class_code.upper())
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                    else:
                        st.success("✅ 您已加入该班级")
                else:
                    st.warning("未找到该班级，请检查班级代码是否正确")
                    
            except Exception as e:
                st.error(f"查询失败: {str(e)}")
    
    else:
        class_name_keyword = st.text_input("请输入班级名称关键词", placeholder="例如：图像处理", key="class_name_search")
        
        if class_name_keyword:
            try:
                response = supabase.table("classrooms").select("*").ilike("class_name", f"%{class_name_keyword}%").eq("is_active", True).order("created_at", desc=True).limit(10).execute()
                
                if response.data and len(response.data) > 0:
                    st.markdown(f"### 找到 {len(response.data)} 个相关班级")
                    
                    for class_info in response.data:
                        class_code = class_info.get("class_code")
                        class_name = class_info.get("class_name")
                        description = class_info.get("description")
                        teacher_username = class_info.get("teacher_username")
                        created_at = class_info.get("created_at")
                        
                        # 获取当前学生数
                        members_response = supabase.table("classroom_members").select("id", count="exact").eq("class_code", class_code).eq("status", 'active').execute()
                        current_students = members_response.count if hasattr(members_response, 'count') else len(members_response.data) if members_response.data else 0
                        max_students = class_info.get("max_students", 50)
                        
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div style='padding: 15px; border-radius: 10px; background: #f9fafb; margin-bottom: 10px;'>
                                    <h4 style='margin: 0;'>{class_name}</h4>
                                    <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                                    教师: {teacher_username} | 创建: {created_at[:10]}
                                    </p>
                                    <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                                    人数: {current_students}/{max_students}
                                    </p>
                                    <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                                    {description[:100] if description else '暂无描述'}...
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                if st.button("查看详情", key=f"view_{class_code}"):
                                    st.info(f"班级代码: {class_code}")
                else:
                    st.info("未找到相关班级")
                    
            except Exception as e:
                st.error(f"搜索失败: {str(e)}")

def render_attendance_detail():
    """签到详情页面"""
    if 'selected_session' not in st.session_state:
        st.session_state.current_page = "teacher_dashboard"
        st.rerun()
    
    session_code = st.session_state.selected_session
    
    session_info, attendance_records = get_attendance_details(session_code)
    
    if not session_info:
        st.error("签到活动不存在")
        return
    
    st.markdown(f"""
    <div class='modern-header'>
        <h2>📊 签到详情</h2>
        <p>{session_info.get('session_name')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("签到代码", session_code)
    
    with col2:
        total = session_info.get('total_students', 0)
        attended = session_info.get('attended_students', 0)
        attendance_rate = (attended / total * 100) if total > 0 else 0
        st.metric("签到率", f"{attendance_rate:.1f}%")
    
    with col3:
        st.metric("参与人数", f"{attended}/{total}")
    
    st.markdown("### 📋 签到记录")
    
    if attendance_records:
        records_data = []
        for record in attendance_records:
            check_in_time = from_beijing_time_str(record.get('check_in_time'))
            start_time = from_beijing_time_str(session_info.get('start_time'))
            is_late = check_in_time > start_time + timedelta(minutes=5)
            
            records_data.append({
                "学生": record.get('username'),
                "签到时间": record.get('check_in_time'),
                "签到方式": record.get('check_in_method'),
                "是否迟到": "是" if is_late else "否",
                "获得积分": record.get('points_earned'),
                "状态": record.get('status')
            })
        
        df_records = pd.DataFrame(records_data)
        st.dataframe(df_records, use_container_width=True, hide_index=True)
        
        csv = df_records.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 导出签到记录",
            data=csv,
            file_name=f"attendance_{session_code}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("暂无签到记录")
    
    st.markdown("### 📈 签到统计")
    
    if attendance_records:
        late_count = sum(1 for record in attendance_records 
                        if from_beijing_time_str(record.get('check_in_time')) > 
                           from_beijing_time_str(session_info.get('start_time')) + timedelta(minutes=5))
        on_time_count = len(attendance_records) - late_count
        
        fig1 = go.Figure(data=[
            go.Pie(
                labels=['准时', '迟到'],
                values=[on_time_count, late_count],
                hole=.3,
                marker_colors=['#10b981', '#ef4444']
            )
        ])
        
        fig1.update_layout(
            title="准时情况分布",
            height=300
        )
        
        st.plotly_chart(fig1, use_container_width=True)

def render_student_classes():
    """学生班级页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>🎯 我的班级</h2>
        <p>我加入的所有班级</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        st.warning("请先登录")
        return
    
    username = st.session_state.username
    
    student_classes = get_student_classes(username)
    
    if student_classes:
        st.markdown(f"### 📚 共加入 {len(student_classes)} 个班级")
        
        for class_info in student_classes:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='padding: 15px;'>
                        <h4 style='margin: 0; color: #dc2626;'>{class_info.get('class_name')}</h4>
                        <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                        班级代码: <strong>{class_info.get('class_code')}</strong>
                        </p>
                        <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                        授课教师: {class_info.get('teacher_username')}
                        </p>
                        <p style='margin: 5px 0; color: #6b7280; font-size: 0.9rem;'>
                        {class_info.get('description') or '暂无描述'}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='padding: 15px;'>
                        <p style='margin: 5px 0;'>👥 学生: {class_info.get('total_students', 0)}人</p>
                        <p style='margin: 5px 0;'>📝 活动: {class_info.get('total_sessions', 0)}次</p>
                        <p style='margin: 5px 0;'>📅 加入: {class_info.get('joined_at', '')[:10]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if st.button("查看", key=f"view_{class_info.get('class_code')}"):
                        st.session_state.selected_class = class_info.get('class_code')
                        st.session_state.current_page = "class_management"
                        st.rerun()
    else:
        st.info("您还没有加入任何班级")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 查找班级", use_container_width=True, type="primary"):
                st.session_state.current_page = "find_classroom"
                st.rerun()

def render_reports():
    """报表页面"""
    st.markdown("""
    <div class='modern-header'>
        <h2>📈 签到报表</h2>
        <p>查看和分析班级签到数据</p>
    </div>
    """, unsafe_allow_html=True)
    
    username = st.session_state.username
    
    # 获取教师的班级列表
    teacher_classes = get_teacher_classes(username)
    
    if not teacher_classes:
        st.info("您还没有创建任何班级，无法查看报表")
        if st.button("➕ 创建班级", use_container_width=True):
            st.session_state.current_page = "create_classroom"
            st.rerun()
        return
    
    # 筛选面板
    with st.expander("🔍 筛选条件", expanded=True):
        st.markdown("<div class='filter-panel'>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            class_options = {c['class_code']: c['class_name'] for c in teacher_classes}
            class_options["全部"] = "全部班级"
            selected_class = st.selectbox(
                "选择班级",
                options=list(class_options.keys()),
                format_func=lambda x: class_options[x],
                index=0,
                key="report_class_select"
            )
        
        with col2:
            date_range = st.selectbox(
                "时间范围",
                options=["本周", "本月", "本季度", "本学期", "全部"],
                index=0,
                key="report_date_range"
            )
        
        with col3:
            export_btn = st.button("📥 导出报表", use_container_width=True, type="primary")
        
        # 计算日期范围
        end_date = to_beijing_time_str()[:10]
        
        if date_range == "本周":
            start_date = (get_beijing_time() - timedelta(days=get_beijing_time().weekday())).strftime('%Y-%m-%d')
        elif date_range == "本月":
            start_date = (get_beijing_time().replace(day=1)).strftime('%Y-%m-%d')
        elif date_range == "本季度":
            month = get_beijing_time().month
            quarter_start_month = ((month - 1) // 3) * 3 + 1
            start_date = (get_beijing_time().replace(month=quarter_start_month, day=1)).strftime('%Y-%m-%d')
        elif date_range == "本学期":
            year = get_beijing_time().year
            if get_beijing_time().month >= 2 and get_beijing_time().month <= 7:
                start_date = f"{year}-02-01"
            else:
                start_date = f"{year}-09-01"
        else:
            start_date = None
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 获取报表数据
    with st.spinner("正在加载报表数据..."):
        class_code_param = None if selected_class == "全部" else selected_class
        sessions = get_attendance_report(username, start_date, end_date, class_code_param)
    
    if sessions:
        # 显示统计卡片
        st.markdown("### 📊 统计概览")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_sessions = len(sessions)
        total_attended = sum(s.get("attended_students", 0) for s in sessions)
        total_expected = sum(s.get("total_students", 0) for s in sessions)
        avg_rate = (total_attended / total_expected * 100) if total_expected > 0 else 0
        
        with col1:
            st.metric("签到次数", total_sessions)
        with col2:
            st.metric("总应到人次", total_expected)
        with col3:
            st.metric("总实到人次", total_attended)
        with col4:
            st.metric("平均签到率", f"{avg_rate:.1f}%")
        
        # 趋势图
        st.markdown("### 📈 签到趋势")
        
        # 按日期分组
        df_sessions = pd.DataFrame(sessions)
        df_sessions['date'] = df_sessions['start_time'].apply(lambda x: x[:10])
        daily_stats = df_sessions.groupby('date').agg({
            'attended_students': 'sum',
            'total_students': 'sum',
            'session_code': 'count'
        }).reset_index()
        daily_stats['rate'] = daily_stats['attended_students'] / daily_stats['total_students'] * 100
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['rate'],
            mode='lines+markers',
            name='签到率',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="每日签到率趋势",
            xaxis_title="日期",
            yaxis_title="签到率 (%)",
            yaxis=dict(range=[0, 100]),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 详细列表
        st.markdown("### 📋 详细记录")
        
        # 准备表格数据
        table_data = []
        for session in sessions:
            start_dt = from_beijing_time_str(session.get("start_time"))
            rate = (session.get("attended_students", 0) / session.get("total_students", 1) * 100) if session.get("total_students", 0) > 0 else 0
            
            # 获取班级名称
            class_response = supabase.table("classrooms").select("class_name").eq("class_code", session.get("class_code")).execute()
            class_name = class_response.data[0].get("class_name") if class_response.data else session.get("class_code")
            
            table_data.append({
                "签到名称": session.get("session_name"),
                "班级": class_name,
                "日期": start_dt.strftime('%Y-%m-%d'),
                "时间": start_dt.strftime('%H:%M'),
                "应到": session.get("total_students", 0),
                "实到": session.get("attended_students", 0),
                "签到率": f"{rate:.1f}%",
                "状态": session.get("status", "unknown")
            })
        
        df_table = pd.DataFrame(table_data)
        st.dataframe(df_table, use_container_width=True, hide_index=True)
        
        # 导出功能
        if export_btn:
            with st.spinner("正在生成Excel报表..."):
                excel_data, error = export_report_to_excel(sessions)
                if excel_data:
                    filename = f"签到报表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    st.download_button(
                        label="📥 下载Excel报表",
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    st.success("✅ 报表生成成功！")
                else:
                    st.error(f"❌ {error}")
    else:
        st.info("暂无签到数据，请先创建签到活动")

# ==================== 主函数 ====================
def main():
    # 初始化session_state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'role' not in st.session_state:
        st.session_state.role = ""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "teacher_dashboard" if st.session_state.get('role') == 'teacher' else "student_classes"
    if 'selected_class' not in st.session_state:
        st.session_state.selected_class = ""
    if 'selected_session' not in st.session_state:
        st.session_state.selected_session = ""
    
    # 应用CSS样式
    apply_modern_css()
    
    # 检查登录状态
    if not st.session_state.logged_in:
        st.warning("请先登录系统")
        if st.button("返回首页登录"):
            st.switch_page("main.py")
        return
    
    # 渲染侧边栏
    render_sidebar()
    
    # 根据当前页面渲染内容
    current_page = st.session_state.current_page
    role = st.session_state.role
    
    # 教师端页面
    if role == "teacher":
        if current_page == "teacher_dashboard":
            render_teacher_dashboard()
        elif current_page == "create_classroom":
            render_create_classroom()
        elif current_page == "class_management":
            render_class_management()
        elif current_page == "create_attendance":
            render_create_attendance()
        elif current_page == "attendance_detail":
            render_attendance_detail()
        elif current_page == "reports":
            render_reports()
        else:
            render_teacher_dashboard()
    
    # 学生端页面
    elif role == "student":
        if current_page == "student_classes":
            render_student_classes()
        elif current_page == "attendance_checkin":
            render_attendance_checkin()
        elif current_page == "find_classroom":
            render_find_classroom()
        elif current_page == "class_management":
            render_class_management()
        else:
            render_student_classes()

if __name__ == "__main__":
    main()