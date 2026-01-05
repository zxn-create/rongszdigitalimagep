import streamlit as st
import cv2
import numpy as np
from plt import Image
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
    page_title="智能图像处理模块",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 目标链接（统一配置）
TARGET_URL = "https://29phcdb33h.coze.site/"

# 检查登录状态
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
