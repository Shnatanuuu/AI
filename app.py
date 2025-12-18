import streamlit as st
import geocoder  # For geolocation
from reportlab.lib.utils import simpleSplit
import openai
import base64
from PIL import Image
import pytz
import io
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage, PageBreak, KeepTogether, Indenter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import re
import hashlib
import streamlit.components.v1 as components
from PIL import Image, ImageDraw
# Simple handler for component messages

# Simple annotation handler at TOP LEVEL (not inside any function)
# Enhanced message handler for component communication - MUST BE AT TOP
# Enhanced message handler for component communication - MUST BE AT TOP

load_dotenv()
# Add this at the VERY END of your script, before the last line
# Add this message handler at the TOP LEVEL (not inside any function)
# Add this to handle messages from the arrow annotation component



# Add handler for receiving annotated image
if 'component_value' not in st.session_state:
    st.session_state.component_value = None

# Check for messages from the component
if st.session_state.component_value:
    # Store the annotated image data
    st.session_state.annotated_image_data = st.session_state.component_value
    st.session_state.component_value = None
    st.rerun()

st.set_page_config(
    page_title="AI Shoe QC Inspector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Language configurations - REMOVED CANTONESE
LANGUAGES = {
    "English": {"code": "en", "flag": "🇺🇸", "label": "English"},
    "Mandarin": {"code": "zh", "flag": "🇨🇳", "label": "普通话 (Mandarin)"}
}
# Timezone mapping for Chinese cities
CITY_TIMEZONES = {
    "Guangzhou": "Asia/Shanghai",
    "Shenzhen": "Asia/Shanghai",
    "Dongguan": "Asia/Shanghai",
    "Foshan": "Asia/Shanghai",
    "Zhongshan": "Asia/Shanghai",
    "Huizhou": "Asia/Shanghai",
    "Zhuhai": "Asia/Shanghai",
    "Jiangmen": "Asia/Shanghai",
    "Zhaoqing": "Asia/Shanghai",
    "Shanghai": "Asia/Shanghai",
    "Beijing": "Asia/Shanghai",
    "Suzhou": "Asia/Shanghai",
    "Hangzhou": "Asia/Shanghai",
    "Ningbo": "Asia/Shanghai",
    "Wenzhou": "Asia/Shanghai",
    "Wuhan": "Asia/Shanghai",
    "Chengdu": "Asia/Shanghai",
    "Chongqing": "Asia/Shanghai",
    "Tianjin": "Asia/Shanghai",
    "Nanjing": "Asia/Shanghai",
    "Xi'an": "Asia/Shanghai",
    "Qingdao": "Asia/Shanghai",
    "Dalian": "Asia/Shanghai",
    "Shenyang": "Asia/Shanghai",
    "Changsha": "Asia/Shanghai",
    "Zhengzhou": "Asia/Shanghai",
    "Jinan": "Asia/Shanghai",
    "Harbin": "Asia/Shanghai",
    "Changchun": "Asia/Shanghai",
    "Taiyuan": "Asia/Shanghai",
    "Shijiazhuang": "Asia/Shanghai",
    "Lanzhou": "Asia/Shanghai",
    "Xiamen": "Asia/Shanghai",
    "Fuzhou": "Asia/Shanghai",
    "Nanning": "Asia/Shanghai",
    "Kunming": "Asia/Shanghai",
    "Guiyang": "Asia/Shanghai",
    "Haikou": "Asia/Shanghai",
    "Ürümqi": "Asia/Urumqi",  # Different timezone for Ürümqi
    "Lhasa": "Asia/Urumqi"
}
# Translation dictionary - REMOVED CANTONESE
TRANSLATIONS = {
    "English": {
        "app_title": "AI Footwear Quality Control Inspector",
        "order_info": "Order Information",
        "factory": "Factory",
        "order_qty": "Order Qty",
        "contract_number": "Contract Number",
        "customer": "Customer",
        "style_number": "Style Number",
        "color": "Color",
        "inspector": "Inspector Name",
        "inspection_date": "Inspection Date",
        "sampling_inspection": "Sampling Inspection",
        "batch_size": "Batch Size",
        "to_inspect": "To Inspect",
        "critical_aql": "Critical AQL",
        "major_aql": "Major AQL",
        "minor_aql": "Minor AQL",
        "total_sampling": "Total Sampling",
        "ctn_no": "CTN No",
        "lot_size": "Lot Size",
        "problem_identified_ai": "PROBLEM IDENTIFIED BY THE AI",
        "problem_identified_qc": "PROBLEM IDENTIFIED BY THE QC MANAGER",
        "problem": "Problem",
        "critical": "CR",
        "major": "MAJOR",
        "minor": "MINOR",
        "signatures": "Signatures",
        "manufacturer_signature": "Manufacturer Signature",
        "inspector_signature": "Inspector Signature",
        "start_inspection": "Start AI Quality Inspection",
        "ai_results": "AI Inspection Results",
        "qc_review": "QC Inspector Review & Amendments",
        "critical_review": "Critical Defects Review",
        "major_review": "Major Defects Review",
        "minor_review": "Minor Defects Review",
        "add_defect": "Add Defect",
        "defect_name": "Defect Name",
        "defect_count": "Defect Count",
        "qc_notes": "QC Manager Notes",
        "save_notes": "Save QC Notes",
        "final_summary": "Final Inspection Summary",
        "generate_pdf": "Generate PDF Report",
        "language_preference": "Language Preference",
        "no_defects": "No defects",
        "image_upload": "Upload Inspection Images",
        "upload_images": "Upload 4 images (any order)",
        "view_ai_defects": "View AI Detected Defects",
        "type_defect": "Type defect description:",
        "enter_defect": "Enter defect...",
        "add_text": "Add",
        "defect_added": "defect added!",
        "additional_notes": "Additional notes:",
        "notes_saved": "Notes saved!",
        "from_ai": "from AI",
        "final_qc_decision": "FINAL QC DECISION",
        "pdf_language_info": "PDF will be generated in:",
        "download_pdf": "Download PDF",
        "pdf_ready": "PDF ready!",
        "pdf_failed": "PDF generation failed",
        "generating_pdf": "Generating multilingual PDF...",
        "analyzing": "Analyzing images...",
        "defects_found": "Defects Found",
        "overall_assessment": "Overall Assessment",
        "ai_confidence": "AI Confidence",
        "ai_defects_given": "PROBLEM IDENTIFIED BY THE AI",
        "record_audio": "🎤 Record Audio",
        "type_text": "📝 Type Text", 
        "start_recording": "🎤 Start Recording",
        "stop_recording": "⏹️ Stop Recording",
        "new_recording_captured": "New recording captured",
        "transcribing": "Transcribing your speech...",
        "transcription_complete": "Transcription Complete!",
        "speak_clearly": "Speak clearly for 3-10 seconds",
        "audio_too_short": "Audio seems very short. Please record for at least 2-3 seconds.",
        "no_text_transcribed": "No text was transcribed. Please speak louder and more clearly.",
        "use_voice_input": "Use voice input",
        "use_text_input": "Use text input",
        "transcribed_text": "Transcribed text:",
        "click_to_record": "Click the button below to record audio",
        "edit_defect": "✏️ Edit",
        "save_edit": "💾 Save",
        "cancel_edit": "❌ Cancel",
        "edit_defect_prompt": "Edit defect description:",
        "defect_image": "Defect Image",
        "visual_evidence": "Visual Evidence",
        "add_defect_name": "Add Defect Name",
        "enter_defect_name": "Enter defect name...",
        "color_variation": "Color Variation",
        "clean": "Clean",
        "toe_lasting": "Toe Lasting",
        "heel_angle": "Heel Angle",
        "waist": "Waist",
        "edge_wrinkle": "Edge Wrinkle",
        "lace": "Lace",
        "outsole": "Outsole",
        "velcro": "Velcro",
        "adhesion": "Adhesion",
        "buckle": "Buckle",
        "Sock Cushion": "Sock Cushion",
        "tongue": "Tongue",
        "Shank Attachment": "Shank Attachment",
        "back_strap_length": "Back strap Length",
        "heel": "Heel",
        "back_strap_attachment": "Back strap attachment",
        "toplift": "Toplift",
        "damage_upper": "Damage upper",
        "bottom_gapping": "Bottom Gapping",
        "xray_wrinkle": "X-RAY",
        "stains": "Stains",
        "thread_ends": "Thread ends",
        "inspection_results": "Inspection Results",
        "photos_of_faults": "PHOTOS OF FAULTS",
        "add_defect_container": "Add Defect Container",
        "defect_severity": "Defect Severity",
        "upload_defect_image": "Upload Defect Image",
        "defect_images": "Defect Images",
        "no_images_uploaded": "No images uploaded for this defect",
        "remove_image": "Remove Image",
        "qc_photos_of_faults": "QC Manager - Photos of Faults",
        "create_new_defect_container": "Create New Defect Container",
        "container_name": "Container Name",
        "total_defects_count": "Total Defects Count",
        "minor_defects": "MINOR DEFECTS",
        "major_defects": "MAJOR DEFECTS",
        "critical_defects": "CRITICAL DEFECTS",
        "edit_problem_counts": "Edit Problem Counts",
        "select_problem": "Select Problem",
        "select_severity": "Select Severity",
        "new_value": "New Value",
        "update_problem": "Update Problem Count"
    },
    "Mandarin": {
        "app_title": "AI鞋类质量控制检查员",
        "order_info": "订单信息",
        "factory": "工厂",
        "order_qty": "订单数量",
        "contract_number": "合同编号",
        "customer": "客户",
        "style_number": "款式编号",
        "color": "颜色",
        "inspector": "检查员姓名",
        "inspection_date": "检查日期",
        "sampling_inspection": "抽样检查",
        "batch_size": "批次数量",
        "to_inspect": "检查数量",
        "critical_aql": "严重 AQL",
        "major_aql": "主要 AQL",
        "minor_aql": "次要 AQL",
        "total_sampling": "总抽样",
        "ctn_no": "箱号",
        "lot_size": "批次大小",
        "problem_identified_ai": "AI识别的问题",
        "problem_identified_qc": "质检经理识别的问题",
        "problem": "问题",
        "critical": "严重",
        "major": "主要",
        "minor": "次要",
        "signatures": "签名",
        "manufacturer_signature": "制造商签名",
        "inspector_signature": "检查员签名",
        "start_inspection": "开始AI质量检查",
        "ai_results": "AI检查结果",
        "qc_review": "质检员检查与修改",
        "critical_review": "严重缺陷审查",
        "major_review": "主要缺陷审查",
        "minor_review": "次要缺陷审查",
        "add_defect": "添加缺陷",
        "defect_name": "缺陷名称",
        "defect_count": "缺陷数量",
        "qc_notes": "质检经理备注",
        "save_notes": "保存质检备注",
        "final_summary": "最终检查摘要",
        "generate_pdf": "生成PDF报告",
        "language_preference": "语言偏好",
        "no_defects": "无缺陷",
        "image_upload": "上传检查图像",
        "upload_images": "上传4张图片(任意顺序)",
        "view_ai_defects": "查看AI检测到的缺陷",
        "type_defect": "输入缺陷描述:",
        "enter_defect": "输入缺陷...",
        "add_text": "添加",
        "defect_added": "缺陷已添加!",
        "additional_notes": "附加备注:",
        "notes_saved": "备注已保存!",
        "from_ai": "来自AI",
        "final_qc_decision": "最终质检决定",
        "pdf_language_info": "PDF将生成为:",
        "download_pdf": "下载PDF",
        "pdf_ready": "PDF已准备好!",
        "pdf_failed": "PDF生成失败",
        "generating_pdf": "正在生成多语言PDF...",
        "analyzing": "正在分析图像...",
        "defects_found": "发现的缺陷",
        "overall_assessment": "整体评估",
        "ai_confidence": "AI置信度",
        "ai_defects_given": "AI识别的问题",
        "record_audio": "🎤 录制音频",
        "type_text": "📝 输入文本",
        "start_recording": "🎤 开始录制",
        "stop_recording": "⏹️ 停止录制", 
        "new_recording_captured": "新录制已捕获",
        "transcribing": "正在转录您的语音...",
        "transcription_complete": "转录完成！",
        "speak_clearly": "清晰说话3-10秒",
        "audio_too_short": "音频似乎太短。请至少录制2-3秒。",
        "no_text_transcribed": "没有转录到文本。请大声清晰地说话。",
        "use_voice_input": "使用语音输入",
        "use_text_input": "使用文本输入",
        "transcribed_text": "转录文本:",
        "click_to_record": "点击下方按钮录制音频",
        "edit_defect": "✏️ 编辑",
        "save_edit": "💾 保存",
        "cancel_edit": "❌ 取消",
        "edit_defect_prompt": "编辑缺陷描述:",
        "defect_image": "缺陷图像",
        "visual_evidence": "视觉证据",
        "add_defect_name": "添加缺陷名称",
        "enter_defect_name": "输入缺陷名称...",
        "color_variation": "Color Variation 色差",
        "clean": "Clean 清洁度",
        "toe_lasting": "Toe Lasting 前帮",
        "heel_angle": "Heel Angle 包跟布起角",
        "waist": "Waist 腰帮",
        "edge_wrinkle": "Edge Wrinkle 包边条皱",
        "lace": "Lace 鞋带",
        "outsole": "Outsole 大底",
        "velcro": "Velcro 魔术贴",
        "adhesion": "Adhesion 胶着力",
        "buckle": "Buckle 鞋扣",
        "midsole_glue": "Midsole Glue 中底布欠胶开胶皱",
        "tongue": "Tongue 鞋舌",
        "grinding_high": "Grinding High 帮脚打磨高",
        "back_strap_length": "Back strap Length 后带长",
        "heel": "Heel 鞋跟",
        "back_strap_attachment": "Back strap attachment 后带固定",
        "toplift": "Toplift 大皮",
        "damage_upper": "Damage upper 鞋面受损",
        "bottom_gapping": "Bottom Gapping 底开胶",
        "xray_wrinkle": "X-RAY 鞋面打皱",
        "stains": "Stains 溢胶",
        "thread_ends": "Thread ends 线头",
        "inspection_results": "检查总数",
        "photos_of_faults": "缺陷照片",
        "add_defect_container": "添加缺陷容器",
        "defect_severity": "缺陷严重程度",
        "upload_defect_image": "上传缺陷图像",
        "defect_images": "缺陷图像",
        "no_images_uploaded": "此缺陷暂无图像",
        "remove_image": "移除图像",
        "qc_photos_of_faults": "质检经理 - 缺陷照片",
        "create_new_defect_container": "创建新缺陷容器",
        "container_name": "容器名称",
        "total_defects_count": "总缺陷数",
        "minor_defects": "次要问题",
        "major_defects": "主要问题",
        "critical_defects": "严重问题",
        "edit_problem_counts": "编辑问题数量",
        "select_problem": "选择问题",
        "select_severity": "选择严重程度",
        "new_value": "新值",
        "update_problem": "更新问题数量"
    }
}

# Initialize session state
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "English"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "English"

# Voice recording session state
if 'audio_input_mode' not in st.session_state:
    st.session_state.audio_input_mode = {}  # Store mode per defect category
if 'last_audio_hash' not in st.session_state:
    st.session_state.last_audio_hash = {}
if 'transcription_text' not in st.session_state:
    st.session_state.transcription_text = {}
if 'recording_count' not in st.session_state:
    st.session_state.recording_count = {}
# Photos of Faults storage
if 'qc_defect_containers' not in st.session_state:
    st.session_state.qc_defect_containers = []  # List of dictionaries for each defect container

# Container form state
if 'show_add_container_form' not in st.session_state:
    st.session_state.show_add_container_form = True
if 'editing_existing_container_idx' not in st.session_state:
    st.session_state.editing_existing_container_idx = None

# Core defect storage
if 'defect_store' not in st.session_state:
    st.session_state.defect_store = {
        'ai_critical': [],
        'ai_major': [],
        'ai_minor': [],
        'qc_critical': [],
        'qc_major': [],
        'qc_minor': []
    }

# Problem table defects storage - AI detected
if 'problem_defects_ai' not in st.session_state:
    st.session_state.problem_defects_ai = {
        'color_variation': {'cr': 0, 'major': 0, 'minor': 0},
        'clean': {'cr': 0, 'major': 0, 'minor': 0},
        'toe_lasting': {'cr': 0, 'major': 0, 'minor': 0},
        'heel_angle': {'cr': 0, 'major': 0, 'minor': 0},
        'waist': {'cr': 0, 'major': 0, 'minor': 0},
        'edge_wrinkle': {'cr': 0, 'major': 0, 'minor': 0},
        'lace': {'cr': 0, 'major': 0, 'minor': 0},
        'outsole': {'cr': 0, 'major': 0, 'minor': 0},
        'velcro': {'cr': 0, 'major': 0, 'minor': 0},
        'adhesion': {'cr': 0, 'major': 0, 'minor': 0},
        'buckle': {'cr': 0, 'major': 0, 'minor': 0},
        'midsole_glue': {'cr': 0, 'major': 0, 'minor': 0},
        'tongue': {'cr': 0, 'major': 0, 'minor': 0},
        'grinding_high': {'cr': 0, 'major': 0, 'minor': 0},
        'back_strap_length': {'cr': 0, 'major': 0, 'minor': 0},
        'heel': {'cr': 0, 'major': 0, 'minor': 0},
        'back_strap_attachment': {'cr': 0, 'major': 0, 'minor': 0},
        'toplift': {'cr': 0, 'major': 0, 'minor': 0},
        'damage_upper': {'cr': 0, 'major': 0, 'minor': 0},
        'bottom_gapping': {'cr': 0, 'major': 0, 'minor': 0},
        'xray_wrinkle': {'cr': 0, 'major': 0, 'minor': 0},
        'stains': {'cr': 0, 'major': 0, 'minor': 0},
        'thread_ends': {'cr': 0, 'major': 0, 'minor': 0}
    }

# Problem table defects storage - QC Manager final
if 'problem_defects_qc' not in st.session_state:
    st.session_state.problem_defects_qc = {
        'color_variation': {'cr': 0, 'major': 0, 'minor': 0},
        'clean': {'cr': 0, 'major': 0, 'minor': 0},
        'toe_lasting': {'cr': 0, 'major': 0, 'minor': 0},
        'heel_angle': {'cr': 0, 'major': 0, 'minor': 0},
        'waist': {'cr': 0, 'major': 0, 'minor': 0},
        'edge_wrinkle': {'cr': 0, 'major': 0, 'minor': 0},
        'lace': {'cr': 0, 'major': 0, 'minor': 0},
        'outsole': {'cr': 0, 'major': 0, 'minor': 0},
        'velcro': {'cr': 0, 'major': 0, 'minor': 0},
        'adhesion': {'cr': 0, 'major': 0, 'minor': 0},
        'buckle': {'cr': 0, 'major': 0, 'minor': 0},
        'midsole_glue': {'cr': 0, 'major': 0, 'minor': 0},
        'tongue': {'cr': 0, 'major': 0, 'minor': 0},
        'grinding_high': {'cr': 0, 'major': 0, 'minor': 0},
        'back_strap_length': {'cr': 0, 'major': 0, 'minor': 0},
        'heel': {'cr': 0, 'major': 0, 'minor': 0},
        'back_strap_attachment': {'cr': 0, 'major': 0, 'minor': 0},
        'toplift': {'cr': 0, 'major': 0, 'minor': 0},
        'damage_upper': {'cr': 0, 'major': 0, 'minor': 0},
        'bottom_gapping': {'cr': 0, 'major': 0, 'minor': 0},
        'xray_wrinkle': {'cr': 0, 'major': 0, 'minor': 0},
        'stains': {'cr': 0, 'major': 0, 'minor': 0},
        'thread_ends': {'cr': 0, 'major': 0, 'minor': 0}
    }

# Custom defects added by QC inspector
if 'custom_defects' not in st.session_state:
    st.session_state.custom_defects = {
        'cr': [],
        'major': [],
        'minor': []
    }

# Editing state for problem tables
if 'editing_problem_table' not in st.session_state:
    st.session_state.editing_problem_table = None  # ('qc' or 'ai', 'problem_key', 'severity')
if 'problem_edit_value' not in st.session_state:
    st.session_state.problem_edit_value = ""

# Editing state for defects
if 'editing_defect' not in st.session_state:
    st.session_state.editing_defect = None  # (category, defect_id)
if 'edit_text' not in st.session_state:
    st.session_state.edit_text = ""

# Translation cache
if 'translation_cache' not in st.session_state:
    st.session_state.translation_cache = {}

# Store QC notes in English
if 'qc_notes_english' not in st.session_state:
    st.session_state.qc_notes_english = ''

# Defect images storage
if 'defect_images' not in st.session_state:
    st.session_state.defect_images = {}  # Store defect_id -> image_buffer

if 'uploaded_images_data' not in st.session_state:
    st.session_state.uploaded_images_data = []  # Store original uploaded images

if 'defect_coordinates' not in st.session_state:
    st.session_state.defect_coordinates = {}

# New input fields storage
if 'total_sampling' not in st.session_state:
    st.session_state.total_sampling = ''
if 'ctn_no' not in st.session_state:
    st.session_state.ctn_no = ''
if 'lot_size' not in st.session_state:
    st.session_state.lot_size = ''

# Photos of Faults storage - REMOVED AI CONTAINERS
if 'qc_defect_containers' not in st.session_state:
    st.session_state.qc_defect_containers = []  # List of dictionaries for each defect container

# Circle annotation storage

if 'component_value' not in st.session_state:
    st.session_state.component_value = None

# Photos of Faults storage
if 'qc_defect_containers' not in st.session_state:
    st.session_state.qc_defect_containers = []  # List of dictionaries for each defect container

# Container form state
if 'show_add_container_form' not in st.session_state:
    st.session_state.show_add_container_form = False
if 'show_success_message' not in st.session_state:
    st.session_state.show_success_message = False
if 'success_container_name' not in st.session_state:
    st.session_state.success_container_name = None
if 'editing_existing_container_idx' not in st.session_state:
    st.session_state.editing_existing_container_idx = None

def t(key):
    """Translation helper for UI elements"""
    return TRANSLATIONS[st.session_state.ui_language].get(key, key)

# Enhanced CSS for mobile responsiveness and better visibility with Edge compatibility
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&display=swap');
    
    .main .block-container {
        font-family: 'Inter', 'Noto Sans SC', sans-serif;
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 1rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    /* Add to existing CSS */
.defect-name-wrapper {
    word-wrap: break-word;
    word-break: break-word;
    overflow-wrap: break-word;
    white-space: normal !important;
}

/* For PDF text wrapping */
.wrap-text {
    word-wrap: break-word;
    word-break: break-word;
}
    .sampling-section {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    .signature-section {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid rgba(226, 232, 240, 0.8);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 1rem;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Enhanced defect items with better contrast */
    .defect-item {
        padding: 1rem;
        margin: 0.75rem 0;
        border-radius: 10px;
        border-left: 5px solid;
        background: white;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
        font-weight: 600;
        font-size: 1rem;
        line-height: 1.5;
        cursor: pointer;
        transition: all 0.2s ease;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    .defect-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .critical-defect { 
        border-left-color: #dc2626; 
        background: #fee2e2 !important;
        color: #7f1d1d !important;
    }
    .major-defect { 
        border-left-color: #ea580c; 
        background: #ffedd5 !important;
        color: #7c2d12 !important;
    }
    .minor-defect { 
        border-left-color: #2563eb; 
        background: #dbeafe !important;
        color: #1e3a8a !important;
    }
    
    /* Voice input styling */
    .voice-input-section {
        background: rgba(255, 255, 255, 0.9);
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Improved table styling for Edge compatibility */
    .scrollable-table {
        overflow-x: auto;
        width: 100%;
        margin: 1rem 0;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        font-smooth: always;
    }
    
    .scrollable-table table {
        min-width: 800px;
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        font-smooth: always;
    }
    
    .scrollable-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        padding: 0.75rem;
        text-align: center;
        border: 1px solid #e5e7eb;
        position: relative;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        font-smooth: always;
    }
    
    .scrollable-table td {
        padding: 0.75rem;
        border: 1px solid #e5e7eb;
        text-align: center;
        font-weight: 600;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        font-smooth: always;
    }
    
    .scrollable-table .problem-name {
        text-align: left !important;
        padding-left: 1rem !important;
        background: #f8fafc;
    }
    
    .scrollable-table .cr-cell { 
        background: #fee2e2; 
    }
    
    .scrollable-table .major-cell { 
        background: #ffedd5; 
    }
    
    .scrollable-table .minor-cell { 
        background: #dbeafe; 
    }
    
    /* Edit mode styling for problem tables */
    .problem-cell-editing {
        border: 2px solid #667eea !important;
        background: #f0f4ff !important;
    }
    
    .problem-edit-input {
        width: 60px;
        text-align: center;
        font-weight: bold;
        font-size: 14px;
        padding: 4px;
        border: 2px solid #667eea;
        border-radius: 4px;
        background: white;
    }
    
    /* Edit mode styling */
    .edit-mode {
        border: 2px solid #667eea !important;
        background: #f0f4ff !important;
    }
    
    /* Defect image styling */
    .defect-image {
        border: 2px solid #667eea;
        border-radius: 8px;
        margin: 0.5rem 0;
        max-width: 200px;
    }
    
    /* Problem table styling */
    .problem-table-container {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        overflow-x: auto;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    .problem-cell {
        padding: 0.5rem;
        border: 1px solid #e5e7eb;
        text-align: center;
        font-weight: 600;
        white-space: nowrap;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    .problem-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    .problem-name {
        background: #f8fafc;
        text-align: left !important;
        padding-left: 1rem !important;
        font-weight: 600;
    }
    
    .cr-cell { background: #fee2e2; }
    .major-cell { background: #ffedd5; }
    .minor-cell { background: #dbeafe; }
    
    /* Defect Container Styling */
    .defect-container {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08)
    }
    
    .defect-container.critical {
        border-left: 6px solid #dc2626;
    }
    
    .defect-container.major {
        border-left: 6px solid #ea580c;
    }
    
    .defect-container.minor {
        border-left: 6px solid #2563eb;
    }
    
    .defect-images-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .defect-image-item {
        position: relative;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .defect-image-item img {
        width: 100%;
        height: 150px;
        object-fit: cover;
    }
    
    .remove-image-btn {
        position: absolute;
        top: 5px;
        right: 5px;
        background: rgba(239, 68, 68, 0.9);
        color: white;
        border: none;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container { 
            padding: 0.5rem; 
        }
        .hero-section { 
            padding: 1.5rem 0.75rem; 
        }
        .hero-section h1 {
            font-size: 1.3rem !important;
        }
        .hero-section p {
            font-size: 0.8rem !important;
        }
        .section-header, .sampling-section, .signature-section { 
            padding: 0.75rem; 
            font-size: 0.95rem; 
        }
        .metric-card { 
            padding: 0.9rem; 
        }
        .metric-number { 
            font-size: 1.8rem !important; 
        }
        .metric-label {
            font-size: 0.9rem !important;
        }
        .defect-item { 
            padding: 0.75rem; 
            font-size: 0.9rem;
            margin: 0.5rem 0;
        }
        .voice-input-section {
            padding: 1rem;
        }
        .defect-image {
            max-width: 150px;
        }
        .problem-table-container {
            padding: 0.5rem;
            font-size: 0.8rem;
        }
        .problem-cell {
            padding: 0.25rem;
            font-size: 0.7rem;
        }
        .defect-container {
            padding: 1rem;
        }
        .defect-images-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    .metric-number { 
        font-size: 2.5rem; 
        font-weight: 800; 
        margin-bottom: 0.25rem; 
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    .metric-label { 
        font-size: 1.1rem; 
        font-weight: 600; 
        color: #374151; 
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Status colors */
    .status-pass { color: #10b981 !important; }
    .status-fail { color: #ef4444 !important; }
    .status-warning { color: #f59e0b !important; }
    
    /* Scrollable table for mobile */
    .scrollable-table {
        overflow-x: auto;
        width: 100%;
    }
    
    .scrollable-table table {
        min-width: 800px;
    }
</style>
""", unsafe_allow_html=True)

# Add message handler for component communication
# Add this component at the beginning of the main app, after other components.html

# Initialize audio input mode for each category
def init_audio_mode(category):
    if category not in st.session_state.audio_input_mode:
        st.session_state.audio_input_mode[category] = "text"
    if category not in st.session_state.last_audio_hash:
        st.session_state.last_audio_hash[category] = None
    if category not in st.session_state.transcription_text:
        st.session_state.transcription_text[category] = ""
    if category not in st.session_state.recording_count:
        st.session_state.recording_count[category] = 0

@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OpenAI API key not found.")
        st.stop()
    return openai.OpenAI(api_key=api_key)

client = get_openai_client()

def calculate_total_sampling(order_qty):
    """Calculate total sampling based on order quantity"""
    try:
        qty = int(order_qty)
        if qty <= 300:
            return "100%"
        elif qty <= 1200:
            return "80"
        elif qty <= 3200:
            return "125"
        elif qty <= 10000:
            return "200"
        else:
            return "315"
    except:
        return ""
    
# Add this function to create the arrow annotation component
def create_arrow_annotation_component():
    """Create simplified arrow annotation component with Download PNG only"""
    html_code = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Arrow Annotation Tool</title>
        <style>
            body {
                margin: 0;
                padding: 15px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: white;
            }
            
            .container {
                max-width: 700px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                text-align: center;
            }
            
            .header h2 {
                margin: 0 0 5px 0;
                font-size: 1.3rem;
            }
            
            .header p {
                margin: 0;
                opacity: 0.9;
                font-size: 0.8rem;
            }
            
            .content {
                padding: 15px;
            }
            
            .upload-section {
                text-align: center;
                padding: 30px 15px;
                border: 2px dashed #667eea;
                border-radius: 6px;
                margin-bottom: 15px;
                background: #f8f9ff;
            }
            
            .upload-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 0.9rem;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                font-weight: 600;
                transition: background 0.3s;
            }
            
            .upload-btn:hover {
                background: #5a67d8;
            }
            
            .canvas-container {
                display: flex;
                justify-content: center;
                margin: 15px 0;
                padding: 8px;
                background: #f5f5f5;
                border-radius: 6px;
            }
            
            canvas {
                border: 2px solid #ddd;
                border-radius: 6px;
                background: white;
                cursor: crosshair;
                max-width: 100%;
                height: auto;
            }
            
            .download-btn {
                width: 100%;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                margin-top: 15px;
                transition: all 0.2s;
            }
            
            .download-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .download-btn:disabled {
                background: #9ca3af;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            
            .info-box {
                background: #dbeafe;
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 15px;
                border-left: 3px solid #3b82f6;
                font-size: 0.85rem;
            }
            
            .info-box p {
                margin: 3px 0;
                color: #374151;
            }
            
            input[type="file"] {
                display: none;
            }
            
            .instructions {
                background: #fffbeb;
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 15px;
                border-left: 3px solid #f59e0b;
                font-size: 0.85rem;
            }
            
            .instructions ol {
                margin: 8px 0 0 0;
                padding-left: 20px;
            }
            
            .instructions li {
                margin: 3px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🎯 Arrow Annotation Tool</h2>
                <p>Drag green/blue dots to position QC arrow</p>
            </div>
            
            <div class="content">
                <div class="instructions">
                    <strong>Instructions:</strong>
                    <ol>
                        <li>Upload your defect image</li>
                        <li>Drag the <strong>green dot</strong> (tail) and <strong>blue dot</strong> (head) to position arrow</li>
                        <li>Click <strong>Download PNG</strong> to save annotated image</li>
                    </ol>
                </div>
                
                <div id="uploadSection" class="upload-section">
                    <input type="file" id="imageInput" accept="image/*">
                    <button class="upload-btn" onclick="document.getElementById('imageInput').click()">
                        📤 Upload Image
                    </button>
                    <p style="margin-top: 8px; color: #6b7280; font-size: 0.8rem;">Support: PNG, JPG, JPEG</p>
                </div>
                
                <div id="annotationSection" style="display: none;">
                    <div class="info-box">
                        <p>🟢 <strong>Green dot:</strong> Arrow tail (drag to move)</p>
                        <p>🔵 <strong>Blue dot:</strong> Arrow head (drag to move)</p>
                        <p>📏 <strong>Arrow length:</strong> <span id="arrowLength">0</span>px</p>
                    </div>
                    
                    <div class="canvas-container">
                        <canvas id="annotationCanvas" width="600" height="400"></canvas>
                    </div>
                    
                    <button id="downloadBtn" class="download-btn" onclick="downloadPNG()" disabled>
                        ⬇️ Download PNG
                    </button>
                </div>
            </div>
        </div>

        <script>
            let image = null;
            let canvas = null;
            let ctx = null;
            let arrow = {
                startX: 0.2,
                startY: 0.2,
                endX: 0.5,
                endY: 0.5,
                headSize: 20
            };
            let dragging = null;
            let dragOffset = { x: 0, y: 0 };
            let originalWidth = 0;
            let originalHeight = 0;
            let displayWidth = 0;
            let displayHeight = 0;
            let scale = 1;

            // Initialize when page loads
            document.addEventListener('DOMContentLoaded', function() {
                canvas = document.getElementById('annotationCanvas');
                ctx = canvas.getContext('2d');
                
                // Setup file input listener
                document.getElementById('imageInput').addEventListener('change', handleImageUpload);
                
                // Setup canvas event listeners
                canvas.addEventListener('mousedown', handleMouseDown);
                canvas.addEventListener('mousemove', handleMouseMove);
                canvas.addEventListener('mouseup', handleMouseUp);
                canvas.addEventListener('mouseleave', handleMouseUp);
                
                // Notify Streamlit that component is ready
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: 'annotation-tool-ready'
                }, '*');
            });

            function handleImageUpload(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        image = new Image();
                        image.onload = function() {
                            originalWidth = image.width;
                            originalHeight = image.height;
                            
                            // Calculate display size
                            const maxWidth = 600;
                            const maxHeight = 400;
                            scale = Math.min(maxWidth / originalWidth, maxHeight / originalHeight);
                            displayWidth = originalWidth * scale;
                            displayHeight = originalHeight * scale;
                            
                            // Set canvas size
                            canvas.width = displayWidth;
                            canvas.height = displayHeight;
                            
                            // Reset arrow to center
                            arrow = {
                                startX: 0.2,
                                startY: 0.2,
                                endX: 0.5,
                                endY: 0.5,
                                headSize: 20 * scale
                            };
                            
                            // Show annotation section
                            document.getElementById('uploadSection').style.display = 'none';
                            document.getElementById('annotationSection').style.display = 'block';
                            
                            // Enable download button
                            document.getElementById('downloadBtn').disabled = false;
                            
                            // Draw initial image and arrow
                            drawCanvas();
                            updateArrowLength();
                        };
                        image.src = e.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            }

            function drawCanvas() {
                if (!image || !canvas) return;
                
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Draw image
                ctx.drawImage(image, 0, 0, displayWidth, displayHeight);
                
                // Calculate display positions
                const startX = arrow.startX * displayWidth;
                const startY = arrow.startY * displayHeight;
                const endX = arrow.endX * displayWidth;
                const endY = arrow.endY * displayHeight;
                
                // Draw arrow line
                ctx.beginPath();
                ctx.moveTo(startX, startY);
                ctx.lineTo(endX, endY);
                ctx.strokeStyle = '#ef4444';
                ctx.lineWidth = 4;
                ctx.lineCap = 'round';
                ctx.stroke();

                // Draw arrowhead
                const angle = Math.atan2(endY - startY, endX - startX);
                ctx.save();
                ctx.translate(endX, endY);
                ctx.rotate(angle);
                
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(-arrow.headSize, -arrow.headSize/2);
                ctx.lineTo(-arrow.headSize, arrow.headSize/2);
                ctx.closePath();
                
                ctx.fillStyle = '#ef4444';
                ctx.fill();
                ctx.restore();

                // Draw control points
                ctx.beginPath();
                ctx.arc(startX, startY, 10, 0, 2 * Math.PI);
                ctx.fillStyle = '#10b981';
                ctx.fill();
                ctx.strokeStyle = 'white';
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.beginPath();
                ctx.arc(endX, endY, 10, 0, 2 * Math.PI);
                ctx.fillStyle = '#3b82f6';
                ctx.fill();
                ctx.strokeStyle = 'white';
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            function getMousePos(event) {
                const rect = canvas.getBoundingClientRect();
                return {
                    x: (event.clientX - rect.left) * (canvas.width / rect.width),
                    y: (event.clientY - rect.top) * (canvas.height / rect.height)
                };
            }

            function distance(x1, y1, x2, y2) {
                return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
            }

            function handleMouseDown(event) {
                if (!image) return;
                
                const pos = getMousePos(event);
                const startX = arrow.startX * displayWidth;
                const startY = arrow.startY * displayHeight;
                const endX = arrow.endX * displayWidth;
                const endY = arrow.endY * displayHeight;

                if (distance(pos.x, pos.y, startX, startY) < 15) {
                    dragging = 'start';
                    dragOffset = { x: pos.x - startX, y: pos.y - startY };
                } else if (distance(pos.x, pos.y, endX, endY) < 15) {
                    dragging = 'end';
                    dragOffset = { x: pos.x - endX, y: pos.y - endY };
                }
            }

            function handleMouseMove(event) {
                if (!image || !dragging) return;
                
                const pos = getMousePos(event);
                
                if (dragging === 'start') {
                    arrow.startX = Math.max(0.02, Math.min(0.98, (pos.x - dragOffset.x) / displayWidth));
                    arrow.startY = Math.max(0.02, Math.min(0.98, (pos.y - dragOffset.y) / displayHeight));
                } else if (dragging === 'end') {
                    arrow.endX = Math.max(0.02, Math.min(0.98, (pos.x - dragOffset.x) / displayWidth));
                    arrow.endY = Math.max(0.02, Math.min(0.98, (pos.y - dragOffset.y) / displayHeight));
                }
                
                drawCanvas();
                updateArrowLength();
            }

            function handleMouseUp() {
                dragging = null;
            }

            function updateArrowLength() {
                if (!image) return;
                
                const startX = arrow.startX * originalWidth;
                const startY = arrow.startY * originalHeight;
                const endX = arrow.endX * originalWidth;
                const endY = arrow.endY * originalHeight;
                
                const length = Math.round(Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2)));
                document.getElementById('arrowLength').textContent = length;
            }

            function downloadPNG() {
                if (!image) {
                    alert('Please upload an image first');
                    return;
                }

                // Create a canvas at original image resolution
                const tempCanvas = document.createElement('canvas');
                tempCanvas.width = originalWidth;
                tempCanvas.height = originalHeight;
                const tempCtx = tempCanvas.getContext('2d');

                // Draw original image
                tempCtx.drawImage(image, 0, 0, originalWidth, originalHeight);

                // Draw arrow at original resolution
                const startX = arrow.startX * originalWidth;
                const startY = arrow.startY * originalHeight;
                const endX = arrow.endX * originalWidth;
                const endY = arrow.endY * originalHeight;
                const headSize = arrow.headSize / scale * 1.5;

                // Draw arrow line
                tempCtx.beginPath();
                tempCtx.moveTo(startX, startY);
                tempCtx.lineTo(endX, endY);
                tempCtx.strokeStyle = '#ef4444';
                tempCtx.lineWidth = 6;
                tempCtx.lineCap = 'round';
                tempCtx.stroke();

                // Draw arrowhead
                const angle = Math.atan2(endY - startY, endX - startX);
                tempCtx.save();
                tempCtx.translate(endX, endY);
                tempCtx.rotate(angle);
                
                tempCtx.beginPath();
                tempCtx.moveTo(0, 0);
                tempCtx.lineTo(-headSize, -headSize/2);
                tempCtx.lineTo(-headSize, headSize/2);
                tempCtx.closePath();
                
                tempCtx.fillStyle = '#ef4444';
                tempCtx.fill();
                tempCtx.restore();

                // Convert to PNG data URL
                const pngDataUrl = tempCanvas.toDataURL('image/png');
                
                // Create download link
                const downloadLink = document.createElement('a');
                downloadLink.href = pngDataUrl;
                downloadLink.download = 'annotated-defect.png';
                
                // Trigger download
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                
                // Also send to Streamlit for automatic container creation
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: pngDataUrl
                }, '*');
            }
        </script>
    </body>
    </html>
    '''
    
    return html_code
def get_sampling_limits(order_qty):
    """Get sampling limits based on order quantity"""
    try:
        qty = int(order_qty)
        if qty <= 300:
            return {"to_inspect": "100%", "major_limit": 1, "minor_limit": 5}
        elif qty <= 1200:
            return {"to_inspect": "80", "major_limit": 5, "minor_limit": 9}
        elif qty <= 3200:
            return {"to_inspect": "125", "major_limit": 7, "minor_limit": 10}
        elif qty <= 10000:
            return {"to_inspect": "200", "major_limit": 10, "minor_limit": 14}
        else:
            return {"to_inspect": "315", "major_limit": 14, "minor_limit": 21}
    except:
        return {"to_inspect": "", "major_limit": 0, "minor_limit": 0}

def map_defect_to_problem(defect_text, severity):
    """Map AI defect to problem categories"""
    defect_lower = defect_text.lower()
    
    # Mapping of keywords to problem categories
    problem_mapping = {
        'color variation': 'color_variation',
        'color variation': 'color_variation',
        'color defect': 'color_variation',
        '色差': 'color_variation',
        'clean': 'clean',
        'cleanliness': 'clean',
        '清洁度': 'clean',
        'dirty': 'clean',
        'stain': 'clean',
        'toe lasting': 'toe_lasting',
        '前帮': 'toe_lasting',
        'heel angle': 'heel_angle',
        '包跟布起角': 'heel_angle',
        'heel': 'heel_angle',
        'waist': 'waist',
        '腰帮': 'waist',
        'edge wrinkle': 'edge_wrinkle',
        '包边条皱': 'edge_wrinkle',
        'edge': 'edge_wrinkle',
        'wrinkle': 'edge_wrinkle',
        'lace': 'lace',
        '鞋带': 'lace',
        'outsole': 'outsole',
        '大底': 'outsole',
        'sole': 'outsole',
        'velcro': 'velcro',
        '魔术贴': 'velcro',
        'hook': 'velcro',
        'loop': 'velcro',
        'adhesion': 'adhesion',
        '胶着力': 'adhesion',
        'glue': 'adhesion',
        'buckle': 'buckle',
        '鞋扣': 'buckle',
        'midsole': 'midsole_glue',
        '中底': 'midsole_glue',
        'tongue': 'tongue',
        '鞋舌': 'tongue',
        'grinding': 'grinding_high',
        '打磨': 'grinding_high',
        'back strap': 'back_strap_length',
        '后带': 'back_strap_length',
        'back strap attachment': 'back_strap_attachment',
        '后带固定': 'back_strap_attachment',
        'heel': 'heel',
        '鞋跟': 'heel',
        'toplift': 'toplift',
        '大皮': 'toplift',
        'damage': 'damage_upper',
        '受损': 'damage_upper',
        'damage upper': 'damage_upper',
        'bottom gapping': 'bottom_gapping',
        '底开胶': 'bottom_gapping',
        'gapping': 'bottom_gapping',
        'separation': 'bottom_gapping',
        'x-ray': 'xray_wrinkle',
        '打皱': 'xray_wrinkle',
        'stain': 'stains',
        '溢胶': 'stains',
        'thread': 'thread_ends',
        '线头': 'thread_ends',
        'thread ends': 'thread_ends'
    }
    
    # Find matching problem category
    for keyword, problem in problem_mapping.items():
        if keyword in defect_lower:
            return problem
    
    # Default to damage_upper if no match found
    return 'damage_upper'

def update_ai_problem_table(defects, severity):
    """Update AI problem table based on AI detected defects"""
    for defect in defects:
        problem_category = map_defect_to_problem(defect, severity)
        if problem_category in st.session_state.problem_defects_ai:
            if severity == 'critical':
                st.session_state.problem_defects_ai[problem_category]['cr'] += 1
            elif severity == 'major':
                st.session_state.problem_defects_ai[problem_category]['major'] += 1
            elif severity == 'minor':
                st.session_state.problem_defects_ai[problem_category]['minor'] += 1

def transcribe_audio(audio_bytes, category):
    """Transcribe audio using OpenAI Whisper"""
    try:
        # Create a hash of the audio to detect if it's a new recording
        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        
        # Check if this is a new recording
        is_new_recording = (audio_hash != st.session_state.last_audio_hash.get(category))
        
        if is_new_recording:
            st.session_state.last_audio_hash[category] = audio_hash
            st.session_state.recording_count[category] = st.session_state.recording_count.get(category, 0) + 1
            
            # Check if audio is substantial
            if len(audio_bytes) < 1000:
                st.warning(t("audio_too_short"))
                return None
            
            # Process the audio
            with st.spinner(f"🎧 {t('transcribing')}"):
                try:
                    # Convert bytes to file-like object
                    audio_file = io.BytesIO(audio_bytes)
                    audio_file.name = "recording.wav"
                    
                    # Transcribe using OpenAI Whisper
                    transcription_response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        language=None  # Auto-detect
                    )
                    
                    transcribed_text = transcription_response.text
                    detected_language = transcription_response.language
                    
                    # Map language codes to names
                    lang_map = {
                        "en": "English", 
                        "zh": "Mandarin",
                        "cmn": "Mandarin"
                    }
                    
                    detected_lang_name = lang_map.get(detected_language, detected_language.upper())
                    
                    # If detected language doesn't match UI language, translate
                    if detected_lang_name != st.session_state.ui_language:
                        target_lang = st.session_state.ui_language
                        translation_response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "system", 
                                    "content": f"You are a professional translator. Translate the following text to {target_lang}. Only provide the translation, nothing else."
                                },
                                {
                                    "role": "user", 
                                    "content": transcribed_text
                                }
                            ],
                            temperature=0.3
                        )
                        final_text = translation_response.choices[0].message.content
                    else:
                        final_text = transcribed_text
                    
                    st.session_state.transcription_text[category] = final_text
                    st.success(f"✅ {t('transcription_complete')}")
                    
                    return final_text
                    
                except Exception as e:
                    st.error(f"❌ Error during transcription: {str(e)}")
                    return None
        else:
            # Same recording as before - return cached text
            return st.session_state.transcription_text.get(category, "")
            
    except Exception as e:
        st.error(f"❌ Transcription error: {str(e)}")
        return None

def translate_text_with_openai(text, target_language):
    """Translate text using OpenAI with caching"""
    if not text or text.strip() == "" or target_language == "English":
        return text
    
    cache_key = (text, target_language)
    if cache_key in st.session_state.translation_cache:
        return st.session_state.translation_cache[cache_key]
    
    lang_map = {
        "Mandarin": "Simplified Chinese (Mandarin)",
    }
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Translate to {lang_map[target_language]}. Return ONLY the translation:\n\n{text}"
            }],
            max_tokens=500,
            temperature=0.1
        )
        translated = response.choices[0].message.content.strip()
        st.session_state.translation_cache[cache_key] = translated
        return translated
    except Exception as e:
        st.warning(f"Translation error: {str(e)}")
        return text

def remove_measurements_from_defect(defect_text):
    """Remove numerical measurements from defect descriptions"""
    # Remove patterns like "10mm", "5 mm", "2.5cm", "3 cm", etc.
    defect_text = re.sub(r'\d+\.?\d*\s*(mm|cm|m|inch|inches|in)', '', defect_text, flags=re.IGNORECASE)
    # Remove standalone numbers that might be measurements
    defect_text = re.sub(r'\b\d+\.?\d*\s*x\s*\d+\.?\d*\b', '', defect_text)
    # Clean up extra spaces
    defect_text = re.sub(r'\s+', ' ', defect_text).strip()
    # Remove trailing dashes or hyphens
    defect_text = re.sub(r'\s*-\s*$', '', defect_text).strip()
    return defect_text

def get_translated_defects(defect_category, target_language):
    """Get defects from store translated to target language"""
    defects = st.session_state.defect_store.get(defect_category, [])
    if target_language == "English":
        return [defect_id for defect_id, defect_text in defects], [defect_text for defect_id, defect_text in defects]
    
    translated = []
    ids = []
    for defect_id, english_text in defects:
        ids.append(defect_id)
        translated.append(translate_text_with_openai(english_text, target_language))
    
    return ids, translated

def add_defect_to_store(category, english_text):
    """Add a new defect to the store"""
    defect_id = f"{category}_{len(st.session_state.defect_store[category])}_{datetime.now().timestamp()}"
    st.session_state.defect_store[category].append((defect_id, english_text))
    return defect_id

def remove_defect_from_store(category, defect_id):
    """Remove a defect by ID"""
    st.session_state.defect_store[category] = [
        (did, text) for did, text in st.session_state.defect_store[category] 
        if did != defect_id
    ]

def update_defect_in_store(category, defect_id, new_text):
    """Update a defect's text"""
    for i, (did, text) in enumerate(st.session_state.defect_store[category]):
        if did == defect_id:
            st.session_state.defect_store[category][i] = (defect_id, new_text)
            break

def add_defect_from_input(input_text, store_category):
    """Add defect from either text or audio input, handling translation if needed"""
    cleaned_input = input_text.strip()
    
    if st.session_state.ui_language != "English":
        try:
            reverse_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"Translate this quality control defect description to English. Be precise and accurate. Return ONLY the English translation:\n\n{cleaned_input}"
                }],
                max_tokens=200,
                temperature=0.1
            )
            english_text = reverse_response.choices[0].message.content.strip()
        except Exception as e:
            st.warning(f"Translation warning: Using original text. Error: {str(e)}")
            english_text = cleaned_input
    else:
        english_text = cleaned_input
    
    # Remove measurements from manually added defects too
    english_text = remove_measurements_from_defect(english_text)
    add_defect_to_store(store_category, english_text)
    
    defect_type = store_category.split('_')[1].capitalize()
    st.success(f"{t(defect_type.lower())} {t('defect_added')}")

def render_audio_input_section(category, defect_type):
    """Render audio recording interface for defect input"""
    init_audio_mode(category)
    
    st.markdown(f"**{t('add_defect')} ({t(defect_type)})**")
    
    # Input mode selector
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"🎤 {t('use_voice_input')}", key=f"voice_btn_{category}", use_container_width=True):
            st.session_state.audio_input_mode[category] = "audio"
            st.rerun()
    with col2:
        if st.button(f"📝 {t('use_text_input')}", key=f"text_btn_{category}", use_container_width=True):
            st.session_state.audio_input_mode[category] = "text"
            st.rerun()
    
    if st.session_state.audio_input_mode[category] == "audio":
        # Audio recording interface
        st.markdown('<div class="voice-input-section">', unsafe_allow_html=True)
        try:
            from streamlit_mic_recorder import mic_recorder
            
            st.info(f"💡 {t('speak_clearly')}")
            
            # Record audio
            audio = mic_recorder(
                start_prompt=f"🎤 {t('start_recording')}",
                stop_prompt=f"⏹️ {t('stop_recording')}",
                just_once=False,
                use_container_width=True,
                key=f'recorder_{category}'
            )
            
            if audio and audio.get('bytes'):
                audio_bytes = audio['bytes']
                st.audio(audio_bytes)
                
                # Transcribe audio
                transcribed_text = transcribe_audio(audio_bytes, category)
                
                if transcribed_text:
                    # Display transcribed text in an editable text area
                    edited_text = st.text_area(
                        t("transcribed_text"),
                        value=transcribed_text,
                        height=80,
                        key=f"transcribed_{category}"
                    )
                    
                    # Add defect button
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button(f"{t('add_text')}", key=f"add_audio_{category}", use_container_width=True):
                            if edited_text and edited_text.strip():
                                store_category = f'qc_{category.split("_")[1]}'
                                add_defect_from_input(edited_text.strip(), store_category)
                                st.session_state.transcription_text[category] = ""  # Clear after adding
                                st.rerun()
        
        except ImportError:
            st.error("❌ **Missing Required Package**")
            st.write("Please install the required package:")
            st.code("pip install streamlit-mic-recorder", language="bash")
            st.write("Then restart your Streamlit app.")
            # Fall back to text input
            st.session_state.audio_input_mode[category] = "text"
        except Exception as e:
            st.error(f"Audio recording error: {str(e)}")
            st.session_state.audio_input_mode[category] = "text"
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Text input interface
        text_input = st.text_input(
            t("type_defect"), 
            key=f"new_{category}_text", 
            placeholder=t("enter_defect"),
            label_visibility="collapsed"
        )
        
        if st.button(f"{t('add_text')} ({t(defect_type)})", key=f"add_{category}_btn", use_container_width=True):
            if text_input and text_input.strip():
                store_category = f'qc_{category.split("_")[1]}'
                add_defect_from_input(text_input.strip(), store_category)
                st.rerun()

def render_qc_notes_audio_section():
    """Render audio input for QC Notes"""
    init_audio_mode("qc_notes")
    
    st.markdown(f"### {t('qc_notes')}")
    
    # Input mode selector for QC Notes
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"🎤 {t('use_voice_input')}", key="voice_btn_qc_notes", use_container_width=True):
            st.session_state.audio_input_mode["qc_notes"] = "audio"
            st.rerun()
    with col2:
        if st.button(f"📝 {t('use_text_input')}", key="text_btn_qc_notes", use_container_width=True):
            st.session_state.audio_input_mode["qc_notes"] = "text"
            st.rerun()
    
    if st.session_state.audio_input_mode["qc_notes"] == "audio":
        # Audio recording interface for QC Notes
        st.markdown('<div class="voice-input-section">', unsafe_allow_html=True)
        try:
            from streamlit_mic_recorder import mic_recorder
            
            st.info(f"💡 {t('speak_clearly')}")
            
            # Record audio
            audio = mic_recorder(
                start_prompt=f"🎤 {t('start_recording')}",
                stop_prompt=f"⏹️ {t('stop_recording')}",
                just_once=False,
                use_container_width=True,
                key='recorder_qc_notes'
            )
            
            if audio and audio.get('bytes'):
                audio_bytes = audio['bytes']
                st.audio(audio_bytes)
                
                # Transcribe audio
                transcribed_text = transcribe_audio(audio_bytes, "qc_notes")
                
                if transcribed_text:
                    # Display transcribed text in an editable text area
                    displayed_notes = st.text_area(
                        t("additional_notes"),
                        value=transcribed_text,
                        height=120,
                        key="qc_notes_audio_textarea"
                    )
                    
                    # Save notes button
                    if st.button(f"{t('save_notes')}", type="primary", key="save_audio_notes", use_container_width=True):
                        if displayed_notes and displayed_notes.strip():
                            save_qc_notes(displayed_notes.strip())
                            st.session_state.transcription_text["qc_notes"] = ""  # Clear after saving
                            st.rerun()
        
        except ImportError:
            st.error("❌ **Missing Required Package**")
            st.write("Please install the required package:")
            st.code("pip install streamlit-mic-recorder", language="bash")
            st.write("Then restart your Streamlit app.")
            # Fall back to text input
            st.session_state.audio_input_mode["qc_notes"] = "text"
        except Exception as e:
            st.error(f"Audio recording error: {str(e)}")
            st.session_state.audio_input_mode["qc_notes"] = "text"
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Text input interface for QC Notes
        if 'qc_notes_english' not in st.session_state:
            st.session_state.qc_notes_english = ''
        
        displayed_notes = translate_text_with_openai(st.session_state.qc_notes_english, st.session_state.ui_language) if st.session_state.qc_notes_english else ''
        
        qc_notes_input = st.text_area(t("additional_notes"), value=displayed_notes, height=120, key="qc_notes_textarea")
        
        if st.button(f"{t('save_notes')}", type="primary", use_container_width=True):
            if qc_notes_input and qc_notes_input.strip():
                save_qc_notes(qc_notes_input.strip())
                st.rerun()

def save_qc_notes(notes_text):
    """Save QC notes with translation if needed"""
    if st.session_state.ui_language != "English":
        try:
            reverse_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"Translate this to English. Return ONLY the English translation:\n\n{notes_text}"
                }],
                max_tokens=500,
                temperature=0.1
            )
            st.session_state.qc_notes_english = reverse_response.choices[0].message.content.strip()
        except:
            st.session_state.qc_notes_english = notes_text
    else:
        st.session_state.qc_notes_english = notes_text
    
    st.success(f"{t('notes_saved')}")

def encode_image(image):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

def crop_defect_area(image, coordinates, margin=5):
    """
    Crop defect area from image based on coordinates
    coordinates: [x1, y1, x2, y2] in percentage (0-100)
    margin: additional margin around defect in percentage
    """
    try:
        img_width, img_height = image.size
        
        # Convert percentage coordinates to pixel coordinates
        x1 = max(0, int((coordinates[0] - margin) / 100 * img_width))
        y1 = max(0, int((coordinates[1] - margin) / 100 * img_height))
        x2 = min(img_width, int((coordinates[2] + margin) / 100 * img_width))
        y2 = min(img_height, int((coordinates[3] + margin) / 100 * img_height))
        
        # Ensure valid crop area
        if x2 > x1 and y2 > y1:
            cropped_img = image.crop((x1, y1, x2, y2))
            return cropped_img
        return None
    except Exception as e:
        st.error(f"Crop error: {str(e)}")
        return None

def save_image_to_buffer(image):
    """Convert PIL image to bytes buffer for PDF inclusion"""
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    return buffer

def get_defect_category(defect_desc, analysis):
    """Determine which category a defect belongs to"""
    if defect_desc in analysis.get('critical_defects', []):
        return 'critical'
    elif defect_desc in analysis.get('major_defects', []):
        return 'major'
    elif defect_desc in analysis.get('minor_defects', []):
        return 'minor'
    return 'unknown'

def analyze_shoe_image_with_locations(client, image, image_number, style_number="", color="", contract_number=""):
    """Analyze image and return defect locations for cropping"""
    base64_image = encode_image(image)
    
    prompt = f"""You are an expert footwear QC inspector analyzing Image {image_number}.
Product: {style_number}, Color: {color}, Contract: {contract_number}

CRITICAL INSTRUCTIONS:
1. DO NOT include ANY measurements (mm, cm, inches, numbers) in defect descriptions
2. Each defect must be unique - never list similar defects in different categories
3. Use clear, descriptive language without numerical data
4. Focus on defect type and location only
5. For EACH defect, provide approximate location coordinates (x1,y1,x2,y2) where:
   - Coordinates are relative to image size (0-100%)
   - Format: [location - defect type] [(x1,y1,x2,y2)]

INSPECTION PROTOCOL:
1. Scan overall construction and proportion
2. Examine all visible materials for defects
3. Check all stitching lines and seam quality
4. Inspect hardware, eyelets, and functional components
5. Look for sole attachment and construction issues
6. Verify color consistency and finish quality
7. Note any safety or structural concerns

CRITICAL DEFECT CATEGORIES (REJECT immediately):
- Holes, tears, or punctures in upper materials
- Broken/missing eyelets, hardware, or structural components
- Sole separation or delamination
- Asymmetrical lasting or construction
- Safety hazards (sharp edges, protruding nails)

MAJOR DEFECT CATEGORIES (Count towards rejection limits):
- Stitching defects: skipped stitches, loose threads, crooked seams
- Material defects: scratches, scuffs, stains, grain breaks
- Construction issues: uneven toe caps, misaligned panels
- Adhesive residue or excess glue visible
- Color variation outside acceptable tolerance

MINOR DEFECT CATEGORIES (Count but typically acceptable):
- Minor sole defects, uneven texturing
- Very light surface marks that don't affect structural integrity

CRITICAL RULES:
1. NO measurements or numbers in descriptions
2. Each defect appears in ONLY ONE category
3. Be specific about location and defect type WITHOUT measurements
4. Use format: "[location] - [defect type] [(x1,y1,x2,y2)]"
5. Similar defects should not appear across categories

Return ONLY valid JSON in English:
{{
    "image_number": {image_number},
    "critical_defects": ["left toe area - deep scratch (10,15,25,30)"],
    "major_defects": ["heel counter - adhesive stain (60,70,80,85)"], 
    "minor_defects": ["side panel - light scuff mark (40,50,55,65)"],
    "defect_coordinates": {{
        "left toe area - deep scratch": [10, 15, 25, 30],
        "heel counter - adhesive stain": [60, 70, 80, 85],
        "side panel - light scuff mark": [40, 50, 55, 65]
    }},
    "overall_condition": "Good/Fair/Poor",
    "confidence": "High/Medium/Low",
    "inspection_notes": "brief notes"
}}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            max_tokens=1500,
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        
        if start != -1 and end > start:
            result = json.loads(result_text[start:end])
            # Extract coordinates and clean defect descriptions
            defect_coordinates = result.get('defect_coordinates', {})
            
            # Clean defect descriptions (remove coordinates from text)
            clean_defects = {}
            for category in ['critical_defects', 'major_defects', 'minor_defects']:
                clean_defects[category] = []
                for defect in result.get(category, []):
                    # Remove coordinate part from defect description
                    clean_defect = re.sub(r'\s*\(\d+,\d+,\d+,\d+\)', '', defect).strip()
                    clean_defects[category].append(clean_defect)
            
            result.update(clean_defects)
            return result, defect_coordinates
        
        return None, {}
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return None, {}

def normalize_defect_description(defect):
    """Normalize defect descriptions to remove variations and enable better duplicate detection"""
    if not defect:
        return defect
    
    normalized = defect.lower().strip()
    normalized = ' '.join(normalized.split())
    
    replacements = {
        'scuff marks': 'scuff',
        'scratch marks': 'scratch', 
        'loose thread': 'loose threads',
        'frayed edge': 'fraying',
        'adhesive mark': 'adhesive residue',
        'glue mark': 'adhesive residue',
        'stitching irregularity': 'stitching irregularities',
        'uneven stitch': 'uneven stitching'
    }
    
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    return normalized

def generate_qc_report(analyses):
    """Generate initial AI report from analyses with strict duplicate prevention"""
    all_critical, all_major, all_minor = [], [], []
    
    for analysis in analyses:
        if analysis:
            critical_defects = list(dict.fromkeys(analysis.get('critical_defects', [])))
            major_defects = list(dict.fromkeys(analysis.get('major_defects', [])))
            minor_defects = list(dict.fromkeys(analysis.get('minor_defects', [])))
            
            all_critical.extend(critical_defects)
            all_major.extend(major_defects)
            all_minor.extend(minor_defects)
    
    # Remove exact duplicates
    all_critical = list(dict.fromkeys(all_critical))
    all_major = list(dict.fromkeys(all_major))
    all_minor = list(dict.fromkeys(all_minor))
    
    # Create normalized versions for cross-category duplicate detection
    normalized_critical = [normalize_defect_description(d) for d in all_critical]
    normalized_major = [normalize_defect_description(d) for d in all_major]
    normalized_minor = [normalize_defect_description(d) for d in all_minor]
    
    # Remove from major if similar defect exists in critical
    final_major = []
    for i, major_defect in enumerate(all_major):
        norm_major = normalized_major[i]
        # Check for any overlap with critical defects
        is_duplicate = False
        for norm_critical in normalized_critical:
            # Check if either contains the other or if they share significant keywords
            if (norm_critical in norm_major or norm_major in norm_critical or
                len(set(norm_critical.split()) & set(norm_major.split())) >= 2):
                is_duplicate = True
                break
        if not is_duplicate:
            final_major.append(major_defect)
    
    # Remove from minor if similar defect exists in critical or major
    final_minor = []
    final_major_normalized = [normalize_defect_description(d) for d in final_major]
    
    for i, minor_defect in enumerate(all_minor):
        norm_minor = normalized_minor[i]
        is_duplicate = False
        
        # Check against critical
        for norm_critical in normalized_critical:
            if (norm_critical in norm_minor or norm_minor in norm_critical or
                len(set(norm_critical.split()) & set(norm_minor.split())) >= 2):
                is_duplicate = True
                break
        
        # Check against major
        if not is_duplicate:
            for norm_major in final_major_normalized:
                if (norm_major in norm_minor or norm_minor in norm_major or
                    len(set(norm_major.split()) & set(norm_minor.split())) >= 2):
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            final_minor.append(minor_defect)
    
    # Final cleanup
    final_critical = list(dict.fromkeys(all_critical))
    final_major = list(dict.fromkeys(final_major))
    final_minor = list(dict.fromkeys(final_minor))
    
    st.session_state.defect_store['ai_critical'] = [(f"ai_c_{i}", d) for i, d in enumerate(final_critical)]
    st.session_state.defect_store['ai_major'] = [(f"ai_m_{i}", d) for i, d in enumerate(final_major)]
    st.session_state.defect_store['ai_minor'] = [(f"ai_n_{i}", d) for i, d in enumerate(final_minor)]
    
    st.session_state.defect_store['qc_critical'] = st.session_state.defect_store['ai_critical'].copy()
    st.session_state.defect_store['qc_major'] = st.session_state.defect_store['ai_major'].copy()
    st.session_state.defect_store['qc_minor'] = st.session_state.defect_store['ai_minor'].copy()
    
    # Update AI problem table
    update_ai_problem_table(final_critical, 'critical')
    update_ai_problem_table(final_major, 'major')
    update_ai_problem_table(final_minor, 'minor')
    
    # Get sampling limits based on order quantity
    sampling_limits = get_sampling_limits(st.session_state.get('order_qty_input', 1000))
    major_limit = sampling_limits["major_limit"]
    minor_limit = sampling_limits["minor_limit"]
    
    if len(final_critical) > 0:
        result, reason = "REJECT", f"Critical defects ({len(final_critical)}) - Zero tolerance"
    elif len(final_major) > major_limit:
        result, reason = "REJECT", f"Major defects ({len(final_major)}) exceed limit ({major_limit})"
    elif len(final_minor) > minor_limit:
        result, reason = "REWORK", f"Minor defects ({len(final_minor)}) exceed limit ({minor_limit})"
    else:
        result, reason = "ACCEPT", "All defects within AQL 2.5 limits"
    
    return {
        "result": result,
        "reason": reason,
        "critical_count": len(final_critical),
        "major_count": len(final_major),
        "minor_count": len(final_minor),
        "sampling_limits": sampling_limits
    }

def calculate_final_decision():
    """Calculate final decision based on QC defects and sampling limits"""
    # Calculate defect counts from QC Manager problem table
    qc_critical_count, qc_major_count, qc_minor_count = calculate_problem_table_totals(st.session_state.problem_defects_qc)
    
    # Get sampling limits based on order quantity
    order_qty = st.session_state.get('order_qty_input', 1000)
    sampling_limits = get_sampling_limits(order_qty)
    major_limit = sampling_limits["major_limit"]
    minor_limit = sampling_limits["minor_limit"]
    
    if qc_critical_count > 0:
        return "REJECT", f"Critical defects ({qc_critical_count}) - Zero tolerance"
    elif qc_major_count > major_limit:
        return "REJECT", f"Major defects ({qc_major_count}) exceed AQL limit ({major_limit})"
    elif qc_minor_count > minor_limit:
        return "REWORK", f"Minor defects ({qc_minor_count}) exceed AQL limit ({minor_limit})"
    else:
        return "ACCEPT", "All defects within AQL 2.5 limits"

def calculate_problem_table_totals(problem_data):
    """Calculate total defects from problem table (sum of all columns)"""
    total_cr = 0
    total_major = 0
    total_minor = 0
    
    for problem_key, counts in problem_data.items():
        total_cr += counts['cr']
        total_major += counts['major']
        total_minor += counts['minor']
    
    return total_cr, total_major, total_minor

def create_sampling_table(order_qty, language, chinese_font=None):
    """Create sampling inspection table for PDF - FIXED FOR MANDARIN"""
    try:
        # Get sampling limits based on order quantity
        sampling_limits = get_sampling_limits(order_qty)
        to_inspect = sampling_limits["to_inspect"]
        major_limit = sampling_limits["major_limit"]
        minor_limit = sampling_limits["minor_limit"]
        
        # Calculate defect counts from QC Manager problem table
        qc_critical_count, qc_major_count, qc_minor_count = calculate_problem_table_totals(st.session_state.problem_defects_qc)
        
        # Determine status colors
        critical_status = "FAIL" if qc_critical_count > 0 else "PASS"
        major_status = "FAIL" if qc_major_count > major_limit else "PASS"
        minor_status = "FAIL" if qc_minor_count > minor_limit else "PASS"
        
        # Create data for table - DIFFERENT FOR MANDARIN
        if language == "Mandarin":
            # Use proper Chinese font or default to Helvetica
            font_name = chinese_font if chinese_font else 'Helvetica'
            
            data = [
                # Title row
                ['抽样检查标准 2.5', '', '', '', ''],
                # Header row
                ['批次数量', '检查数量', '严重 AQL', '主要 AQL', '次要 AQL'],
                # Data rows
                ['0-300 双', '100%', '0', '1', '5'],
                ['301-1200 双', '80', '0', '5', '9'],
                ['1201-3200 双', '125', '0', '7', '10'],
                ['3201-10000 双', '200', '0', '10', '14'],
                ['10001-35000 双以上', '315', '0', '14', '21'],
                # Last row with actual results
                [f"检查总数: {order_qty}", 
                 f"已抽样: {st.session_state.total_sampling if st.session_state.total_sampling else to_inspect}", 
                 f"{qc_critical_count} / 0", 
                 f"{qc_major_count} / {major_limit}", 
                 f"{qc_minor_count} / {minor_limit}"]
            ]
        else:
            data = [
                # Title row
                ['Inspection Standard 2.5', '', '', '', ''],
                # Header row
                ['BATCH SIZE', 'TO INSPECT', 'CRITICAL AQL', 'MAJOR AQL', 'MINOR AQL'],
                # Data rows
                ['0-300PRS', '100%', '0', '1', '5'],
                ['301-1200PRS', '80', '0', '5', '9'],
                ['1201-3200PRS', '125', '0', '7', '10'],
                ['3201-10000PRS', '200', '0', '10', '14'],
                ['10001-35000 above', '315', '0', '14', '21'],
                # Last row with actual results
                [f"Order Qty: {order_qty}", 
                 f"Sampled: {st.session_state.total_sampling if st.session_state.total_sampling else to_inspect}", 
                 f"{qc_critical_count} / 0", 
                 f"{qc_major_count} / {major_limit}", 
                 f"{qc_minor_count} / {minor_limit}"]
            ]
        
        # Create table with proper width for portrait A4
        page_width = A4[0] - 4*cm  # Portrait width minus margins
        col_widths = [page_width * 0.20] * 5
        row_heights = [30, 25] + [22]*5 + [30]
        
        table = Table(data, colWidths=col_widths, rowHeights=row_heights)
        
        # Define table style
        style = TableStyle([
            # Title row - yellow background
            ('BACKGROUND', (0, 0), (4, 0), colors.yellow),
            ('SPAN', (0, 0), (4, 0)),  # Merge all columns for title
            ('ALIGN', (0, 0), (4, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (4, 0), 12),
            ('FONTNAME', (0, 0), (4, 0), 'Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold')),
            ('VALIGN', (0, 0), (4, 0), 'MIDDLE'),
            
            # Header row - light gray background
            ('BACKGROUND', (0, 1), (4, 1), colors.Color(0.85, 0.85, 0.85)),
            ('FONTSIZE', (0, 1), (4, 1), 9),
            ('FONTNAME', (0, 1), (4, 1), 'Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold')),
            ('ALIGN', (0, 1), (4, 1), 'CENTER'),
            ('VALIGN', (0, 1), (4, 1), 'MIDDLE'),
            
            # Data rows - white background
            ('BACKGROUND', (0, 2), (4, 6), colors.white),
            ('FONTSIZE', (0, 2), (4, 6), 9),
            ('FONTNAME', (0, 2), (4, 6), 'Helvetica' if language == "English" else (chinese_font if chinese_font else 'Helvetica')),
            ('ALIGN', (0, 2), (0, 6), 'LEFT'),
            ('ALIGN', (1, 2), (4, 6), 'CENTER'),
            ('VALIGN', (0, 2), (4, 6), 'MIDDLE'),
            
            # Last row - yellow background with colored status
            ('BACKGROUND', (0, 7), (4, 7), colors.yellow),
            ('FONTSIZE', (0, 7), (4, 7), 9),
            ('FONTNAME', (0, 7), (4, 7), 'Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold')),
            ('ALIGN', (0, 7), (4, 7), 'CENTER'),
            ('VALIGN', (0, 7), (4, 7), 'MIDDLE'),
            
            # Color code the results based on status
            ('TEXTCOLOR', (2, 7), (2, 7), colors.red if critical_status == "FAIL" else colors.green),
            ('TEXTCOLOR', (3, 7), (3, 7), colors.red if major_status == "FAIL" else colors.green),
            ('TEXTCOLOR', (4, 7), (4, 7), colors.red if minor_status == "FAIL" else colors.green),
            
            # Grid - black borders
            ('GRID', (0, 0), (4, 7), 1, colors.black),
            ('LINEABOVE', (0, 0), (4, 0), 1, colors.black),
            ('LINEBELOW', (0, 7), (4, 7), 1, colors.black),
            
            # Padding
            ('LEFTPADDING', (0, 0), (4, 7), 4),
            ('RIGHTPADDING', (0, 0), (4, 7), 4),
            ('TOPPADDING', (0, 0), (4, 7), 3),
            ('BOTTOMPADDING', (0, 0), (4, 7), 3),
        ])
        
        table.setStyle(style)
        return KeepTogether(table)  # Keep table together on same page
        
    except Exception as e:
        st.error(f"Error creating sampling table: {str(e)}")
        return None

def create_problem_table(problem_data, title, language, chinese_font=None):
    """Create problem identification table for PDF - UPDATED FOR MANDARIN"""
    # Calculate totals from the problem table
    total_cr = sum(problem_data[problem]['cr'] for problem in problem_data)
    total_major = sum(problem_data[problem]['major'] for problem in problem_data)
    total_minor = sum(problem_data[problem]['minor'] for problem in problem_data)
    
    # Define the data structure for the problem table - DIFFERENT FOR MANDARIN
    if language == "Mandarin":
        # Use proper Chinese font
        font_name = chinese_font if chinese_font else 'Helvetica'
        
        table_data = [
            # Header row - ALL 8 COLUMNS IN MANDARIN
            ['问题', '严重', '主要', '次要', '问题', '严重', '主要', '次要'],
            
            # Row 1
            ['色差', 
             str(problem_data['color_variation']['cr']), 
             str(problem_data['color_variation']['major']), 
             str(problem_data['color_variation']['minor']), 
             '清洁', 
             str(problem_data['clean']['cr']), 
             str(problem_data['clean']['major']), 
             str(problem_data['clean']['minor'])],
            
            # Row 2
            ['前帮', 
             str(problem_data['toe_lasting']['cr']), 
             str(problem_data['toe_lasting']['major']), 
             str(problem_data['toe_lasting']['minor']), 
             '包跟角', 
             str(problem_data['heel_angle']['cr']), 
             str(problem_data['heel_angle']['major']), 
             str(problem_data['heel_angle']['minor'])],
            
            # Row 3
            ['腰帮', 
             str(problem_data['waist']['cr']), 
             str(problem_data['waist']['major']), 
             str(problem_data['waist']['minor']), 
             '包边皱', 
             str(problem_data['edge_wrinkle']['cr']), 
             str(problem_data['edge_wrinkle']['major']), 
             str(problem_data['edge_wrinkle']['minor'])],
            
            # Row 4
            ['鞋带', 
             str(problem_data['lace']['cr']), 
             str(problem_data['lace']['major']), 
             str(problem_data['lace']['minor']), 
             '大底', 
             str(problem_data['outsole']['cr']), 
             str(problem_data['outsole']['major']), 
             str(problem_data['outsole']['minor'])],
            
            # Row 5
            ['魔术贴', 
             str(problem_data['velcro']['cr']), 
             str(problem_data['velcro']['major']), 
             str(problem_data['velcro']['minor']), 
             '胶着', 
             str(problem_data['adhesion']['cr']), 
             str(problem_data['adhesion']['major']), 
             str(problem_data['adhesion']['minor'])],
            
            # Row 6
            ['鞋扣', 
             str(problem_data['buckle']['cr']), 
             str(problem_data['buckle']['major']), 
             str(problem_data['buckle']['minor']), 
             '中底胶', 
             str(problem_data['midsole_glue']['cr']), 
             str(problem_data['midsole_glue']['major']), 
             str(problem_data['midsole_glue']['minor'])],
            
            # Row 7
            ['鞋舌', 
             str(problem_data['tongue']['cr']), 
             str(problem_data['tongue']['major']), 
             str(problem_data['tongue']['minor']), 
             '打磨高', 
             str(problem_data['grinding_high']['cr']), 
             str(problem_data['grinding_high']['major']), 
             str(problem_data['grinding_high']['minor'])],
            
            # Row 8
            ['后带长', 
             str(problem_data['back_strap_length']['cr']), 
             str(problem_data['back_strap_length']['major']), 
             str(problem_data['back_strap_length']['minor']), 
             '鞋跟', 
             str(problem_data['heel']['cr']), 
             str(problem_data['heel']['major']), 
             str(problem_data['heel']['minor'])],
            
            # Row 9
            ['后带固', 
             str(problem_data['back_strap_attachment']['cr']), 
             str(problem_data['back_strap_attachment']['major']), 
             str(problem_data['back_strap_attachment']['minor']), 
             '大皮', 
             str(problem_data['toplift']['cr']), 
             str(problem_data['toplift']['major']), 
             str(problem_data['toplift']['minor'])],
            
            # Row 10
            ['鞋面损', 
             str(problem_data['damage_upper']['cr']), 
             str(problem_data['damage_upper']['major']), 
             str(problem_data['damage_upper']['minor']), 
             '底开胶', 
             str(problem_data['bottom_gapping']['cr']), 
             str(problem_data['bottom_gapping']['major']), 
             str(problem_data['bottom_gapping']['minor'])],
            
            # Row 11
            ['鞋面皱', 
             str(problem_data['xray_wrinkle']['cr']), 
             str(problem_data['xray_wrinkle']['major']), 
             str(problem_data['xray_wrinkle']['minor']), 
             '溢胶', 
             str(problem_data['stains']['cr']), 
             str(problem_data['stains']['major']), 
             str(problem_data['stains']['minor'])],
            
            # Row 12 - Thread ends only on left side, right side empty
            ['线头', 
             str(problem_data['thread_ends']['cr']), 
             str(problem_data['thread_ends']['major']), 
             str(problem_data['thread_ends']['minor']), 
             '', '', '', ''],
            
            # Last row - Inspection results - USE CALCULATED TOTALS
            [f'总缺陷数:', 
             str(total_cr), 
             str(total_major), 
             str(total_minor), 
             '', '', '', '']
        ]
    else:
        table_data = [
            # Header row - ALL 8 COLUMNS
            ['Problem', 'CR', 'MAJOR', 'MINOR', 'Problem', 'CR', 'MAJOR', 'MINOR'],
            
            # Row 1
            ['Color Variation', 
             str(problem_data['color_variation']['cr']), 
             str(problem_data['color_variation']['major']), 
             str(problem_data['color_variation']['minor']), 
             'Clean', 
             str(problem_data['clean']['cr']), 
             str(problem_data['clean']['major']), 
             str(problem_data['clean']['minor'])],
            
            # Row 2
            ['Toe Lasting', 
             str(problem_data['toe_lasting']['cr']), 
             str(problem_data['toe_lasting']['major']), 
             str(problem_data['toe_lasting']['minor']), 
             'Heel Angle', 
             str(problem_data['heel_angle']['cr']), 
             str(problem_data['heel_angle']['major']), 
             str(problem_data['heel_angle']['minor'])],
            
            # Row 3
            ['Waist', 
             str(problem_data['waist']['cr']), 
             str(problem_data['waist']['major']), 
             str(problem_data['waist']['minor']), 
             'Edge Wrinkle', 
             str(problem_data['edge_wrinkle']['cr']), 
             str(problem_data['edge_wrinkle']['major']), 
             str(problem_data['edge_wrinkle']['minor'])],
            
            # Row 4
            ['Lace', 
             str(problem_data['lace']['cr']), 
             str(problem_data['lace']['major']), 
             str(problem_data['lace']['minor']), 
             'Outsole', 
             str(problem_data['outsole']['cr']), 
             str(problem_data['outsole']['major']), 
             str(problem_data['outsole']['minor'])],
            
            # Row 5
            ['Velcro', 
             str(problem_data['velcro']['cr']), 
             str(problem_data['velcro']['major']), 
             str(problem_data['velcro']['minor']), 
             'Adhesion', 
             str(problem_data['adhesion']['cr']), 
             str(problem_data['adhesion']['major']), 
             str(problem_data['adhesion']['minor'])],
            
            # Row 6
            ['Buckle', 
             str(problem_data['buckle']['cr']), 
             str(problem_data['buckle']['major']), 
             str(problem_data['buckle']['minor']), 
             'Midsole Glue', 
             str(problem_data['midsole_glue']['cr']), 
             str(problem_data['midsole_glue']['major']), 
             str(problem_data['midsole_glue']['minor'])],
            
            # Row 7
            ['Tongue', 
             str(problem_data['tongue']['cr']), 
             str(problem_data['tongue']['major']), 
             str(problem_data['tongue']['minor']), 
             'Grinding High', 
             str(problem_data['grinding_high']['cr']), 
             str(problem_data['grinding_high']['major']), 
             str(problem_data['grinding_high']['minor'])],
            
            # Row 8
            ['Back strap Length', 
             str(problem_data['back_strap_length']['cr']), 
             str(problem_data['back_strap_length']['major']), 
             str(problem_data['back_strap_length']['minor']), 
             'Heel', 
             str(problem_data['heel']['cr']), 
             str(problem_data['heel']['major']), 
             str(problem_data['heel']['minor'])],
            
            # Row 9
            ['Back strap attachment', 
             str(problem_data['back_strap_attachment']['cr']), 
             str(problem_data['back_strap_attachment']['major']), 
             str(problem_data['back_strap_attachment']['minor']), 
             'Toplift', 
             str(problem_data['toplift']['cr']), 
             str(problem_data['toplift']['major']), 
             str(problem_data['toplift']['minor'])],
            
            # Row 10
            ['Damage upper', 
             str(problem_data['damage_upper']['cr']), 
             str(problem_data['damage_upper']['major']), 
             str(problem_data['damage_upper']['minor']), 
             'Bottom Gapping', 
             str(problem_data['bottom_gapping']['cr']), 
             str(problem_data['bottom_gapping']['major']), 
             str(problem_data['bottom_gapping']['minor'])],
            
            # Row 11
            ['X-RAY', 
             str(problem_data['xray_wrinkle']['cr']), 
             str(problem_data['xray_wrinkle']['major']), 
             str(problem_data['xray_wrinkle']['minor']), 
             'Stains', 
             str(problem_data['stains']['cr']), 
             str(problem_data['stains']['major']), 
             str(problem_data['stains']['minor'])],
            
            # Row 12 - Thread ends only on left side, right side empty
            ['Thread ends', 
             str(problem_data['thread_ends']['cr']), 
             str(problem_data['thread_ends']['major']), 
             str(problem_data['thread_ends']['minor']), 
             '', '', '', ''],
            
            # Last row - Inspection results - USE CALCULATED TOTALS
            [f'{t("total_defects_count")}:', 
             str(total_cr), 
             str(total_major), 
             str(total_minor), 
             '', '', '', '']
        ]
    
    # Calculate column widths for portrait A4
    page_width = A4[0] - 4*cm  # Portrait width minus margins
    col_widths = [
        page_width * 0.22,  # Problem column (left side)
        page_width * 0.07,  # CR
        page_width * 0.07,  # MAJOR
        page_width * 0.07,  # MINOR
        page_width * 0.22,  # Problem column (right side)
        page_width * 0.07,  # CR
        page_width * 0.07,  # MAJOR
        page_width * 0.07   # MINOR
    ]
    
    # Create table - 13 rows total (0-12)
    table = Table(table_data, colWidths=col_widths, rowHeights=[22] + [18]*12 + [22])
    
    # Define table style
    style = TableStyle([
        # Header row styling - ALL WHITE BACKGROUND
        ('BACKGROUND', (0, 0), (7, 0), colors.white),
        
        # All body rows - white background
        ('BACKGROUND', (0, 1), (7, 13), colors.white),
        
        # Grid - thin black borders
        ('GRID', (0, 0), (7, 13), 0.5, colors.black),
        
        # Font - Use appropriate font for Chinese
        ('FONTNAME', (0, 0), (7, 13), 'Helvetica' if language == "English" else (chinese_font if chinese_font else 'Helvetica')),
        ('FONTSIZE', (0, 0), (7, 13), 7),
        
        # Header row - bold
        ('FONTNAME', (0, 0), (7, 0), 'Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold')),
        ('FONTSIZE', (0, 0), (7, 0), 8),
        
        # Last row - bold
        ('FONTNAME', (0, 13), (3, 13), 'Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold')),
        ('FONTNAME', (4, 13), (4, 13), 'Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold')),
        ('FONTNAME', (5, 13), (7, 13), 'Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold')),
        
        # Background colors for last row to match screenshot
        ('BACKGROUND', (0, 13), (0, 13), colors.Color(0.95, 0.95, 0.7)),  # Light yellow
        ('BACKGROUND', (1, 13), (3, 13), colors.Color(0.8, 0.85, 1.0)),   # Light blue
        ('BACKGROUND', (4, 13), (4, 13), colors.white),
        ('BACKGROUND', (5, 13), (7, 13), colors.Color(0.8, 1.0, 0.8)),    # Light green
        
        # Alignment
        ('ALIGN', (0, 0), (0, 13), 'LEFT'),      # Left problem column
        ('ALIGN', (1, 0), (3, 13), 'CENTER'),    # CR, MAJOR, MINOR (left)
        ('ALIGN', (4, 0), (4, 13), 'LEFT'),      # Right problem column
        ('ALIGN', (5, 0), (7, 13), 'CENTER'),    # CR, MAJOR, MINOR (right)
        
        ('VALIGN', (0, 0), (7, 13), 'MIDDLE'),
        
        # Padding
        ('LEFTPADDING', (0, 0), (7, 13), 4),
        ('RIGHTPADDING', (0, 0), (7, 13), 4),
        ('TOPPADDING', (0, 0), (7, 13), 3),
        ('BOTTOMPADDING', (0, 0), (7, 13), 3),
    ])
    
    table.setStyle(style)
    return KeepTogether(table)  # Keep table together on same page

def create_photos_of_faults_table(language, chinese_font=None):
    """
    Create Photos of Faults section for PDF with:
    1. Only Defect Type headers have color (Critical=red, Major=orange, Minor=blue)
    2. Container name has NO background color (white background)
    3. Title "PHOTOS OF FAULTS" has color (dark blue)
    4. Images aligned to left under container name
    5. Defects arranged in rows (max 2 per row)
    6. Defect names wrap text
    7. All severity types on same page if possible
    """
    from reportlab.platypus import Image as ReportLabImage, PageBreak, Spacer, Table, TableStyle, Paragraph, KeepTogether
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    import io
    
    # Get QC defect containers
    qc_containers = st.session_state.get('qc_defect_containers', [])
    
    if not qc_containers:
        return None  # Don't show section if no containers
    
    # Group containers by severity
    containers_by_severity = {
        'critical': [c for c in qc_containers if c.get('severity') == 'critical'],
        'major': [c for c in qc_containers if c.get('severity') == 'major'],
        'minor': [c for c in qc_containers if c.get('severity') == 'minor']
    }
    
    # Remove empty severity groups
    containers_by_severity = {k: v for k, v in containers_by_severity.items() if v}
    
    if not containers_by_severity:
        return None
    
    elements = []
    
    # ========== MAIN TITLE ==========
    title_text = "缺陷照片" if language == "Mandarin" else "PHOTOS OF FAULTS"
    
    title_style = ParagraphStyle(
        'PhotosMainTitle',
        fontName='Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold'),
        fontSize=16,
        alignment=TA_CENTER,
        textColor=colors.white,
        spaceAfter=0
    )
    
    # Create title table with dark blue background
    title_table = Table(
        [[Paragraph(title_text, title_style)]],
        colWidths=[A4[0] - 4*cm]
    )
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.2, 0.3, 0.5)),  # Dark blue
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 2, colors.Color(0.15, 0.2, 0.35)),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(title_table)
    elements.append(Spacer(1, 20))
    
    # ========== DEFECT SEVERITY COLORS ==========
    severity_colors = {
        'critical': colors.Color(0.85, 0.2, 0.2),    # Red
        'major': colors.Color(0.95, 0.6, 0.15),      # Orange
        'minor': colors.Color(0.25, 0.5, 0.85)       # Blue
    }
    
    # ========== PROCESS ALL SEVERITY GROUPS ==========
    # Try to keep all on one page if possible
    all_containers_processed = []
    
    # Process in order: Critical, Major, Minor
    for severity in ['critical', 'major', 'minor']:
        if severity not in containers_by_severity:
            continue
        
        severity_containers = containers_by_severity[severity]
        containers_with_images = [c for c in severity_containers if c.get('images')]
        
        if not containers_with_images:
            continue
        
        # Add severity header with color
        if language == "Mandarin":
            severity_labels = {
                'critical': "严重问题",
                'major': "主要问题", 
                'minor': "次要问题"
            }
        else:
            severity_labels = {
                'critical': "CRITICAL DEFECTS",
                'major': "MAJOR DEFECTS",
                'minor': "MINOR DEFECTS"
            }
        
        header_text = severity_labels[severity]
        header_style = ParagraphStyle(
            f'SeverityHeader_{severity}',
            fontName='Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold'),
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.white
        )
        
        header_table = Table(
            [[Paragraph(header_text, header_style)]],
            colWidths=[A4[0] - 4*cm],
            rowHeights=[25]
        )
        
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), severity_colors[severity]),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, severity_colors[severity]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 10))
        
        
        # Process containers in rows (max 2 per row)
        container_count = len(containers_with_images)
        
        for i in range(0, container_count, 2):
            # Get up to 2 containers for this row
            row_containers = containers_with_images[i:min(i+2, container_count)]
            
            # Create table for this row (max 2 columns)
            row_data = []
            col_widths = []
            
            for container in row_containers:
                images = container.get('images', [])
                defect_name = container['name']
                
                # Translate defect name if needed
                if language == "Mandarin":
                    defect_name = translate_text_with_openai(defect_name, "Mandarin")
                
                # Create content for this cell
                cell_content = []
                
                # 1. Container name (NO background color, white background)
                name_style = ParagraphStyle(
                    f'DefectName_{severity}_{i}',
                    fontName='Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold'),
                    fontSize=10,
                    alignment=TA_LEFT,
                    textColor=colors.black,  # Black text on white background
                    wordWrap='LTR',  # Allow text wrapping
                    leading=12
                )
                
                # Wrap text if too long
                wrapped_name = defect_name
                if len(defect_name) > 30:
                    # Simple wrapping - break into multiple lines
                    words = defect_name.split()
                    lines = []
                    current_line = ""
                    for word in words:
                        if len(current_line) + len(word) + 1 <= 30:
                            current_line += " " + word if current_line else word
                        else:
                            lines.append(current_line)
                            current_line = word
                    if current_line:
                        lines.append(current_line)
                    wrapped_name = "\n".join(lines)
                
                cell_content.append(Paragraph(wrapped_name, name_style))
                
                # 2. Image (1 inch x 1 inch)
                if images:
                    try:
                        img_bytes = images[0]
                        img_buffer = io.BytesIO(img_bytes)
                        
                        # Create ReportLab Image
                        reportlab_img = ReportLabImage(img_buffer)
                        reportlab_img.drawWidth = 1 * inch
                        reportlab_img.drawHeight = 1 * inch
                        
                        cell_content.append(reportlab_img)
                    except Exception as e:
                        error_text = f"[Image error]"
                        error_style = ParagraphStyle(
                            'ErrorText',
                            fontName='Helvetica',
                            fontSize=8,
                            textColor=colors.red
                        )
                        cell_content.append(Paragraph(error_text, error_style))
                
                row_data.append(cell_content)
                col_widths.append((A4[0] - 5*cm) / 2)  # Equal width for 2 columns
            
            # If only one container in this row, add empty cell
            if len(row_containers) == 1:
                row_data.append([Paragraph("", ParagraphStyle('Empty'))])
                col_widths.append((A4[0] - 5*cm) / 2)
            
            # Create table for this row
            if row_data:
                # Convert to proper table structure
                table_data = []
                max_elements = max(len(cell) for cell in row_data)
                
                for element_idx in range(max_elements):
                    row = []
                    for cell_idx in range(len(row_data)):
                        if element_idx < len(row_data[cell_idx]):
                            row.append(row_data[cell_idx][element_idx])
                        else:
                            row.append(Paragraph("", ParagraphStyle('Empty')))
                    table_data.append(row)
                
                # Create the table
                row_table = Table(table_data, colWidths=col_widths)
                
                # Style the table - NO background color for container names
                table_style = TableStyle([
                    # All cells - white background, black border
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ])
                
                row_table.setStyle(table_style)
                elements.append(row_table)
                elements.append(Spacer(1, 15))
        
        # Add spacing between severity groups
        if severity in ['critical', 'major'] and 'minor' in containers_by_severity:
            elements.append(Spacer(1, 20))
    
    return elements
def get_current_location():
    """Get current city based on IP address"""
    try:
        g = geocoder.ip('me')
        if g.city:
            return f"{g.city}, {g.country}"
        return "Location unavailable"
    except Exception as e:
        return "Location unavailable"
        # Define header/footer function with timestamp and location
                # Define header/footer function with timestamp and location
        def add_header_footer(canvas, doc):
            """Add header and footer to all pages with timestamp and location"""
            canvas.saveState()
            
            # Get current timestamp in China time (UTC+8)
            from datetime import timedelta
            
            selected_city = st.session_state.get('selected_city', 'Guangzhou')
            
            # Calculate China time (UTC+8 for most cities, UTC+6 for Ürümqi)
            utc_now = datetime.utcnow()
            
            if selected_city == "Ürümqi":
                # Ürümqi uses Xinjiang Time (UTC+6)
                china_time = utc_now + timedelta(hours=6)
            else:
                # Most Chinese cities use China Standard Time (UTC+8)
                china_time = utc_now + timedelta(hours=8)
            
            timestamp = china_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # USE SELECTED CITY FROM DROPDOWN
            chinese_city_name = CHINESE_CITIES.get(selected_city, "广东")
            
            if language == "Mandarin":
                location = chinese_city_name
            else:
                location = selected_city
            
            # Page dimensions
            page_width = A4[0]
            page_height = A4[1]
            
            # FOOTER: Centered at bottom with timestamp and location
            footer_text = f"Generated: {timestamp} | Location: {location}"
            footer_font_size = 8
            
            canvas.setFont(base_font, footer_font_size)
            canvas.setFillColor(colors.grey)
            
            # Draw footer text centered at bottom
            text_width = canvas.stringWidth(footer_text, base_font, footer_font_size)
            footer_x = (page_width - text_width) / 2
            footer_y = 1*cm  # 1cm from bottom
            
            canvas.drawString(footer_x, footer_y, footer_text)
            
            # HEADER: GRAND STEP (H.K.) LTD on all pages except first
            if doc.page > 1:
                header_font_size = 12
                canvas.setFont(bold_font, header_font_size)
                canvas.setFillColor(colors.black)
                
                # Draw header at top center (NO UNDERLINE)
                header_text = "GRAND STEP (H.K.) LTD"
                canvas.drawCentredString(page_width/2, page_height - 1*cm, header_text)
            
            # PAGE NUMBER: Top right corner
            page_text = f"Page {doc.page}"
            canvas.setFont(base_font, 10)
            canvas.drawRightString(page_width - 2*cm, page_height - 1*cm, page_text)
            
            canvas.restoreState()
def render_photos_of_faults_ui():
    """Render Photos of Faults UI with arrow annotation tool"""
    st.markdown(f"### 📷 {t('qc_photos_of_faults')}")
    
    # Initialize session state for arrow annotation
    if 'show_arrow_annotation' not in st.session_state:
        st.session_state.show_arrow_annotation = False
    if 'annotated_image_data' not in st.session_state:
        st.session_state.annotated_image_data = None
    
    # Display existing containers
    if 'qc_defect_containers' in st.session_state and st.session_state.qc_defect_containers:
        # Group by severity
        containers_by_severity = {
            'critical': [],
            'major': [],
            'minor': []
        }
        
        for container in st.session_state.qc_defect_containers:
            severity = container.get('severity', 'minor')
            containers_by_severity[severity].append(container)
        
        # Display in order: Critical, Major, Minor
        for severity in ['critical', 'major', 'minor']:
            severity_containers = containers_by_severity[severity]
            
            if not severity_containers:
                continue
            
            # Severity header
            severity_colors = {
                'critical': '#ef4444',
                'major': '#f59e0b',
                'minor': '#3b82f6'
            }
            
            st.markdown(f"""
            <div style="background: {severity_colors[severity]}; color: white; padding: 0.5rem 1rem; 
                       border-radius: 6px; margin: 1rem 0; font-weight: bold;">
                {t(severity.upper())} DEFECTS ({len(severity_containers)})
            </div>
            """, unsafe_allow_html=True)
            
            # Display containers in rows (max 2 per row)
            for i in range(0, len(severity_containers), 2):
                cols = st.columns(2)
                
                for col_idx in range(2):
                    container_idx = i + col_idx
                    if container_idx < len(severity_containers):
                        container = severity_containers[container_idx]
                        
                        with cols[col_idx]:
                            # Container card
                            st.markdown(f"""
                            <div style="border: 1px solid #e5e7eb; border-radius: 8px; 
                                      padding: 1rem; margin-bottom: 1rem; background: white;">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <div style="flex: 1;">
                                        <h4 style="margin: 0 0 0.5rem 0; font-weight: bold; word-wrap: break-word;">
                                            {container['name']}
                                        </h4>
                                    </div>
                                    <span style="background: {severity_colors[severity]}; color: white; 
                                               padding: 2px 8px; border-radius: 10px; font-size: 0.7rem;">
                                        {t(severity.upper())}
                                    </span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Image
                            if container.get('images'):
                                try:
                                    st.image(
                                        container['images'][0],
                                        caption=f"Defect: {container['name']}",
                                        width=200
                                    )
                                except Exception as e:
                                    st.error(f"Error displaying image: {str(e)}")
                            
                            # Action buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✏️ Edit", key=f"edit_{severity}_{container_idx}", use_container_width=True):
                                    st.session_state.editing_existing_container_idx = container_idx
                                    st.session_state.temp_container_name = container['name']
                                    st.session_state.temp_severity = container['severity']
                                    st.session_state.temp_image_bytes = container['images'][0] if container.get('images') else None
                                    st.session_state.show_add_container_form = True
                                    st.rerun()
                            
                            with col2:
                                if st.button("🗑️ Delete", key=f"delete_{severity}_{container_idx}", use_container_width=True):
                                    # Find and remove the container
                                    for idx, c in enumerate(st.session_state.qc_defect_containers):
                                        if c['name'] == container['name'] and c.get('severity') == severity:
                                            st.session_state.qc_defect_containers.pop(idx)
                                            st.success(f"✅ Deleted '{container['name']}'")
                                            st.rerun()
                                            break
    
    # Main action buttons
    st.markdown("---")
    
    # Two column layout for buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # Arrow Annotation Tool Button
        if st.button("🎯 **ANNOTATE WITH ARROW TOOL**", type="primary", use_container_width=True):
            st.session_state.show_arrow_annotation = True
            st.session_state.show_add_container_form = False
            st.session_state.annotated_image_data = None
            st.rerun()
    
    with col2:
        # Create Container Button (direct)
        if st.button("📁 **CREATE DIRECT CONTAINER**", type="secondary", use_container_width=True):
            st.session_state.show_add_container_form = True
            st.session_state.show_arrow_annotation = False
            # Clear temp data
            for key in ['temp_container_name', 'temp_severity', 
                       'temp_image_bytes', 'temp_image', 'editing_existing_container_idx']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Show arrow annotation tool
    if st.session_state.show_arrow_annotation:
        st.markdown("---")
        st.markdown("#### 🎯 Arrow Annotation Tool")
        st.info("""
        1. Upload your defect image
        2. Drag the **green dot** (tail) and **blue dot** (head) to position the arrow
        3. Click **Save Annotated Image** when done
        4. The image will be ready for container creation
        """)
        
        # Display the React component
        components.html(
            create_arrow_annotation_component(),
            height=900,
            scrolling=False
        )
        
        # Display annotated image if available
        if st.session_state.annotated_image_data:
            st.markdown("---")
            st.markdown("#### ✅ Annotated Image Ready")
            
            # Decode the base64 image data
            import base64
            annotated_bytes = base64.b64decode(st.session_state.annotated_image_data.split(',')[1])
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(annotated_bytes, caption="Annotated Image", width=300)
            
            with col2:
                st.success("🎉 Arrow annotation saved!")
                
                # Buttons to use this image
                if st.button("📁 Use this image for new container", type="primary", use_container_width=True):
                    # Store the annotated image for container creation
                    st.session_state.temp_image_bytes = annotated_bytes
                    st.session_state.temp_image = Image.open(io.BytesIO(annotated_bytes))
                    st.session_state.show_add_container_form = True
                    st.session_state.show_arrow_annotation = False
                    st.rerun()
                
                if st.button("🔄 Annotate another image", type="secondary", use_container_width=True):
                    st.session_state.annotated_image_data = None
                    st.rerun()
        
        # Cancel button
        if st.button("❌ Cancel Annotation", type="secondary", use_container_width=True, key="cancel_annotation"):
            st.session_state.show_arrow_annotation = False
            st.session_state.annotated_image_data = None
            st.rerun()
    
    # Show add/edit container form (SIMPLIFIED - No sliders)
    elif st.session_state.show_add_container_form:
        edit_idx = st.session_state.get('editing_existing_container_idx')
        is_editing = edit_idx is not None and isinstance(edit_idx, int)
        
        st.markdown("---")
        st.markdown(f"#### {'✏️ EDIT CONTAINER' if is_editing else '📁 CREATE CONTAINER'}")
        
        # Check if we have an annotated image ready
        has_annotated_image = 'temp_image_bytes' in st.session_state and st.session_state.temp_image_bytes is not None
        
        if has_annotated_image:
            st.success("✅ Using annotated image from arrow tool")
            col1, col2 = st.columns(2)
            with col1:
                st.image(st.session_state.temp_image_bytes, caption="Annotated image", width=200)
        else:
            # Regular image upload
            uploaded_file = st.file_uploader(
                "📷 Upload Defect Image",
                type=['png', 'jpg', 'jpeg'],
                key="new_container_uploader"
            )
            
            if uploaded_file is not None:
                image_bytes = uploaded_file.getvalue()
                image = Image.open(io.BytesIO(image_bytes))
                
                # Store in session state
                st.session_state.temp_image_bytes = image_bytes
                st.session_state.temp_image = image
        
        # Container name and severity
        col1, col2 = st.columns([3, 2])
        with col1:
            # Get existing name if editing
            default_name = ""
            if is_editing and edit_idx < len(st.session_state.qc_defect_containers):
                default_name = st.session_state.qc_defect_containers[edit_idx]['name']
            
            new_container_name = st.text_input(
                "Container Name",
                value=st.session_state.get('temp_container_name', default_name),
                key="new_container_name_input",
                placeholder="e.g., Stitching Defect, Sole Separation"
            )
        with col2:
            # Get existing severity if editing
            default_severity = "minor"
            if is_editing and edit_idx < len(st.session_state.qc_defect_containers):
                default_severity = st.session_state.qc_defect_containers[edit_idx]['severity']
            
            new_container_severity = st.selectbox(
                "Defect Severity",
                ['minor', 'major', 'critical'],
                index=['minor', 'major', 'critical'].index(
                    st.session_state.get('temp_severity', default_severity)
                ),
                format_func=lambda x: x.upper(),
                key="new_container_severity_select"
            )
        
        # Check if we have everything needed
        has_name = new_container_name and new_container_name.strip()
        has_image = 'temp_image_bytes' in st.session_state and st.session_state.temp_image_bytes is not None
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Container", type="primary", use_container_width=True, 
                        disabled=not (has_name and has_image)):
                if has_name and has_image:
                    # Create container
                    container = {
                        'name': new_container_name.strip(),
                        'severity': new_container_severity,
                        'images': [st.session_state.temp_image_bytes],
                        'timestamp': datetime.now().isoformat(),
                        'has_annotation': has_annotated_image  # Flag if from arrow tool
                    }
                    
                    # Check if editing or adding new
                    if is_editing:
                        idx = st.session_state.editing_existing_container_idx
                        if isinstance(idx, int) and 0 <= idx < len(st.session_state.qc_defect_containers):
                            st.session_state.qc_defect_containers[idx] = container
                            st.success(f"✅ Updated: {new_container_name.strip()}")
                        else:
                            st.session_state.qc_defect_containers.append(container)
                            st.success(f"✅ Saved: {new_container_name.strip()}")
                    else:
                        st.session_state.qc_defect_containers.append(container)
                        st.success(f"✅ Saved: {new_container_name.strip()}")
                    
                    # Clean up
                    keys_to_remove = [
                        'temp_container_name', 'temp_severity',
                        'temp_image_bytes', 'temp_image', 'editing_existing_container_idx',
                        'show_add_container_form', 'annotated_image_data'
                    ]
                    
                    for key in keys_to_remove:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    # Return to main view
                    st.rerun()
                else:
                    st.warning("Please provide both container name and image")
        
        with col2:
            if st.button("❌ Cancel", type="secondary", use_container_width=True):
                # Clean up
                keys_to_remove = [
                    'temp_container_name', 'temp_severity',
                    'temp_image_bytes', 'temp_image', 'editing_existing_container_idx',
                    'show_add_container_form', 'annotated_image_data'
                ]
                
                for key in keys_to_remove:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.rerun()
        
        if not has_image and not has_annotated_image:
            st.info("📁 Please upload an image to create container")


def generate_multilingual_pdf(order_info, language):
    """Generate PDF with proper Mandarin font handling - UPDATED WITH TIMESTAMP & LOCATION FOOTER"""
    try:
        buffer = io.BytesIO()
        
        # Register Chinese font if available
        chinese_font = None
        try:
            if language == "Mandarin":
                # Try to use built-in Chinese font from ReportLab
                try:
                    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                    chinese_font = 'STSong-Light'
                except:
                    try:
                        # Try other common Chinese fonts
                        pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
                        chinese_font = 'SimSun'
                    except:
                        try:
                            pdfmetrics.registerFont(TTFont('YaHei', 'msyh.ttc'))
                            chinese_font = 'YaHei'
                        except:
                            # Fall back to Helvetica
                            chinese_font = 'Helvetica'
        except Exception as e:
            st.warning(f"Could not register Chinese font: {str(e)}")
            chinese_font = 'Helvetica'
        
        # Use appropriate font
        if language == "Mandarin" and chinese_font:
            base_font = chinese_font
            bold_font = chinese_font
        else:
            base_font = 'Helvetica'
            bold_font = 'Helvetica-Bold'
        
        # Define header/footer function with timestamp and location
        def add_header_footer(canvas, doc):
            """Add header and footer to all pages with timestamp and location"""
            canvas.saveState()
            
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # USE SELECTED CITY FROM DROPDOWN
            selected_city = st.session_state.get('selected_city', 'Guangzhou')
            chinese_city_name = CHINESE_CITIES.get(selected_city, "广东")
            
            if language == "Mandarin":
                location = chinese_city_name
            else:
                location = selected_city
            
            # Page dimensions
            page_width = A4[0]
            page_height = A4[1]
            
            # FOOTER: Centered at bottom with timestamp and location
            footer_text = f"Generated: {timestamp} | Location: {location}"
            footer_font_size = 8
            
            canvas.setFont(base_font, footer_font_size)
            canvas.setFillColor(colors.grey)
            
            # Draw footer text centered at bottom
            text_width = canvas.stringWidth(footer_text, base_font, footer_font_size)
            footer_x = (page_width - text_width) / 2
            footer_y = 1*cm  # 1cm from bottom
            
            canvas.drawString(footer_x, footer_y, footer_text)
            
            # HEADER: GRAND STEP (H.K.) LTD on all pages except first
            if doc.page > 1:
                header_font_size = 12
                canvas.setFont(bold_font, header_font_size)
                canvas.setFillColor(colors.black)
                
                # Draw header at top center (NO UNDERLINE)
                header_text = "GRAND STEP (H.K.) LTD"
                canvas.drawCentredString(page_width/2, page_height - 1*cm, header_text)
            
            # PAGE NUMBER: Top right corner
            page_text = f"Page {doc.page}"
            canvas.setFont(base_font, 10)
            canvas.drawRightString(page_width - 2*cm, page_height - 1*cm, page_text)
            
            canvas.restoreState()
        
        # Create document with increased bottom margin for footer
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=2*cm, leftMargin=2*cm, 
                               topMargin=2*cm, bottomMargin=2.5*cm)  # Increased bottom margin for footer
        
        elements = []
        styles = getSampleStyleSheet()
        
        brand_blue = colors.Color(0.4, 0.49, 0.91)  # Original purple color
        success_green = colors.Color(0.31, 0.78, 0.47)
        warning_orange = colors.Color(1.0, 0.6, 0.0)
        danger_red = colors.Color(1.0, 0.42, 0.42)
        light_gray = colors.Color(0.97, 0.97, 0.97)
        
        # Restore original styles
        title_style = ParagraphStyle('Title', parent=styles['Normal'], fontSize=22, alignment=TA_CENTER,
                                     textColor=brand_blue, fontName=bold_font, spaceAfter=12)
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER,
                                        textColor=colors.Color(0.3, 0.3, 0.3), fontName=base_font, spaceAfter=8)
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, spaceAfter=10,
                                      spaceBefore=15, textColor=brand_blue, fontName=bold_font, alignment=TA_CENTER)
        
        # HEADER FOR PAGE 1 - Original purple GRAND STEP (H.K.) LTD
        if language == "Mandarin":
            elements.append(Paragraph("GRAND STEP (H.K.) LTD", title_style))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("专业鞋类制造与质量控制", subtitle_style))
            elements.append(Paragraph("AI驱动质量检查系统", subtitle_style))
            elements.append(Spacer(1, 20))
            
            # Title
            title_text = "质量控制检查报告"
        else:
            elements.append(Paragraph("GRAND STEP (H.K.) LTD", title_style))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Professional Footwear Manufacturing & Quality Control", subtitle_style))
            elements.append(Paragraph("AI-Powered Quality Inspection System", subtitle_style))
            elements.append(Spacer(1, 20))
            
            # Title
            title_text = "QUALITY CONTROL INSPECTION REPORT"
        
        report_title = ParagraphStyle('ReportTitle', parent=title_style, fontSize=16, 
                                      textColor=colors.black, fontName=bold_font)
        elements.append(Paragraph(title_text, report_title))
        elements.append(Spacer(1, 20))
        
        # Final Decision
        final_result, final_reason = calculate_final_decision()
        result_text = final_result
        
        # TRANSLATE DECISION TEXT FOR MANDARIN
        if language == "Mandarin":
            final_label = "最终质检决定"
            if final_result == "ACCEPT":
                result_text = "接受"
                final_reason = "所有缺陷在AQL 2.5限制内"
            elif final_result == "REJECT":
                result_text = "拒绝"
                if "Critical defects" in final_reason:
                    final_reason = "严重缺陷 - 零容忍"
                else:
                    final_reason = "主要缺陷超出AQL限制"
            elif final_result == "REWORK":
                result_text = "返工"
                final_reason = "次要缺陷超出AQL限制"
        else:
            final_label = "FINAL QC DECISION"
        
        result_color = success_green if final_result=='ACCEPT' else (danger_red if final_result=='REJECT' else warning_orange)
        
        result_style = ParagraphStyle('Result', parent=styles['Normal'], fontSize=18, alignment=TA_CENTER,
                                     fontName=bold_font, spaceAfter=10, textColor=result_color)
        
        elements.append(Paragraph(f"{final_label}: {result_text}", result_style))
        
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=6,
                                    fontName=base_font, textColor=colors.black)
        elements.append(Paragraph(final_reason, body_style))
        elements.append(Spacer(1, 20))
        
        # Order Information
        if language == "Mandarin":
            order_label = "订单信息"
            # Prepare order data in Mandarin
            order_data = [
                ['合同编号', order_info['contract_number']],
                ['工厂', order_info['factory']],
                ['订单数量', order_info['order_qty']],
                ['款式', order_info['style_number']],
                ['颜色', order_info['color']],
                ['客户', order_info['customer']],
                ['检查员', order_info['inspector']],
                ['日期', order_info['inspection_date']],
                ['总抽样', st.session_state.total_sampling if st.session_state.total_sampling else calculate_total_sampling(order_info['order_qty'])],
                ['箱号', st.session_state.ctn_no if st.session_state.ctn_no else ''],
                ['批次大小', st.session_state.lot_size if st.session_state.lot_size else ''],
                ['标准', "AQL 2.5"]
            ]
        else:
            order_label = "ORDER INFORMATION"
            order_data = [
                ['Contract Number', order_info['contract_number']],
                ['Factory', order_info['factory']],
                ['Order Qty', order_info['order_qty']],
                ['Style', order_info['style_number']],
                ['Color', order_info['color']],
                ['Customer', order_info['customer']],
                ['Inspector', order_info['inspector']],
                ['Date', order_info['inspection_date']],
                ['Total Sampling', st.session_state.total_sampling if st.session_state.total_sampling else calculate_total_sampling(order_info['order_qty'])],
                ['CTN No', st.session_state.ctn_no if st.session_state.ctn_no else ''],
                ['Lot Size', st.session_state.lot_size if st.session_state.lot_size else ''],
                ['Standard', "AQL 2.5"]
            ]
        
        order_section_style = ParagraphStyle('OrderSection', parent=section_style, 
                                            fontName=bold_font)
        elements.append(Paragraph(order_label, order_section_style))
        elements.append(Spacer(1, 10))
        
        order_table = Table(order_data, colWidths=[5*cm, 9*cm])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), brand_blue),
            ('TEXTCOLOR', (0,0), (0,-1), colors.white),
            ('BACKGROUND', (1,0), (1,-1), light_gray),
            ('FONTNAME', (0,0), (0,-1), base_font),
            ('FONTNAME', (1,0), (1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(KeepTogether(order_table))  # Keep order table together
        elements.append(Spacer(1, 20))
        
        # SAMPLING INSPECTION TABLE - Start new page
        elements.append(PageBreak())
        
        if language == "Mandarin":
            sampling_label = "抽样检查"
        else:
            sampling_label = "SAMPLING INSPECTION"
            
        sampling_section_style = ParagraphStyle('SamplingSection', parent=section_style,
                                               fontName=bold_font)
        elements.append(Paragraph(sampling_label, sampling_section_style))
        elements.append(Spacer(1, 8))
        
        # Create sampling table
        sampling_table = create_sampling_table(order_info['order_qty'], language, chinese_font)
        if sampling_table:
            elements.append(sampling_table)
        elements.append(Spacer(1, 20))
        
        # PROBLEM IDENTIFIED BY THE AI TABLE
        if language == "Mandarin":
            problem_ai_label = "AI识别的问题"
        else:
            problem_ai_label = "PROBLEM IDENTIFIED BY THE AI"
            
        problem_section_style = ParagraphStyle('ProblemSection', parent=section_style,
                                              fontName=bold_font)
        elements.append(Paragraph(problem_ai_label, problem_section_style))
        elements.append(Spacer(1, 8))
        
        # Create AI problem table
        ai_problem_table = create_problem_table(st.session_state.problem_defects_ai, "AI", language, chinese_font)
        if ai_problem_table:
            elements.append(ai_problem_table)
        elements.append(Spacer(1, 20))
        
        # PROBLEM IDENTIFIED BY THE QC MANAGER TABLE - Start new page if needed
        elements.append(PageBreak())
        
        if language == "Mandarin":
            problem_qc_label = "质检经理识别的问题"
        else:
            problem_qc_label = "PROBLEM IDENTIFIED BY THE QC MANAGER"
            
        elements.append(Paragraph(problem_qc_label, problem_section_style))
        elements.append(Spacer(1, 8))
        
        # Create QC problem table
        qc_problem_table = create_problem_table(st.session_state.problem_defects_qc, "QC", language, chinese_font)
        if qc_problem_table:
            elements.append(qc_problem_table)
        elements.append(Spacer(1, 20))
        
        # CRITICAL DEFECTS REVIEW - Start new page
        elements.append(PageBreak())
        
        if language == "Mandarin":
            critical_label = "严重缺陷审查"
        else:
            critical_label = "CRITICAL DEFECTS REVIEW"
            
        critical_style = ParagraphStyle('CriticalSection', parent=section_style,
                                       fontName=bold_font, textColor=danger_red)
        elements.append(Paragraph(critical_label, critical_style))
        elements.append(Spacer(1, 8))
        
        # Get critical defects
        qc_critical_ids, qc_critical_translated = get_translated_defects('qc_critical', language)
        if qc_critical_translated:
            for i, defect in enumerate(qc_critical_translated, 1):
                defect_style = ParagraphStyle(f'defect{i}', parent=styles['Normal'], 
                                            textColor=danger_red, fontSize=9, 
                                            fontName=base_font, leftIndent=15)
                elements.append(Paragraph(f"{i}. {defect}", defect_style))
                elements.append(Spacer(1, 4))
        else:
            no_defects_text = "无严重缺陷" if language == "Mandarin" else "No critical defects found"
            no_defects_style = ParagraphStyle('NoDefects', parent=styles['Normal'], 
                                            fontSize=9, fontName=base_font, 
                                            alignment=TA_CENTER)
            elements.append(Paragraph(no_defects_text, no_defects_style))
        
        elements.append(Spacer(1, 12))
        
        # MAJOR DEFECTS REVIEW
        if language == "Mandarin":
            major_label = "主要缺陷审查"
        else:
            major_label = "MAJOR DEFECTS REVIEW"
            
        major_style = ParagraphStyle('MajorSection', parent=section_style,
                                    fontName=bold_font, textColor=warning_orange)
        elements.append(Paragraph(major_label, major_style))
        elements.append(Spacer(1, 8))
        
        # Get major defects
        qc_major_ids, qc_major_translated = get_translated_defects('qc_major', language)
        if qc_major_translated:
            for i, defect in enumerate(qc_major_translated, 1):
                defect_style = ParagraphStyle(f'defect{i}', parent=styles['Normal'], 
                                            textColor=warning_orange, fontSize=9, 
                                            fontName=base_font, leftIndent=15)
                elements.append(Paragraph(f"{i}. {defect}", defect_style))
                elements.append(Spacer(1, 4))
        else:
            no_defects_text = "无主要缺陷" if language == "Mandarin" else "No major defects found"
            no_defects_style = ParagraphStyle('NoDefects', parent=styles['Normal'], 
                                            fontSize=9, fontName=base_font, 
                                            alignment=TA_CENTER)
            elements.append(Paragraph(no_defects_text, no_defects_style))
        
        elements.append(Spacer(1, 12))
        
        # MINOR DEFECTS REVIEW
        if language == "Mandarin":
            minor_label = "次要缺陷审查"
        else:
            minor_label = "MINOR DEFECTS REVIEW"
            
        minor_style = ParagraphStyle('MinorSection', parent=section_style,
                                    fontName=bold_font, textColor=brand_blue)
        elements.append(Paragraph(minor_label, minor_style))
        elements.append(Spacer(1, 8))
        
        # Get minor defects
        qc_minor_ids, qc_minor_translated = get_translated_defects('qc_minor', language)
        if qc_minor_translated:
            for i, defect in enumerate(qc_minor_translated, 1):
                defect_style = ParagraphStyle(f'defect{i}', parent=styles['Normal'], 
                                            textColor=brand_blue, fontSize=9, 
                                            fontName=base_font, leftIndent=15)
                elements.append(Paragraph(f"{i}. {defect}", defect_style))
                elements.append(Spacer(1, 4))
        else:
            no_defects_text = "无次要缺陷" if language == "Mandarin" else "No minor defects found"
            no_defects_style = ParagraphStyle('NoDefects', parent=styles['Normal'], 
                                            fontSize=9, fontName=base_font, 
                                            alignment=TA_CENTER)
            elements.append(Paragraph(no_defects_text, no_defects_style))
        
        elements.append(Spacer(1, 20))
        
        # QC INSPECTOR REVIEW & AMENDMENTS - Start new page if needed
        elements.append(PageBreak())
        
        if language == "Mandarin":
            qc_label = "质检员检查与修改"
        else:
            qc_label = "QC INSPECTOR REVIEW & AMENDMENTS"
            
        qc_section_style = ParagraphStyle('QCSection', parent=section_style,
                                         fontName=bold_font)
        
        # Get sampling limits for display
        sampling_limits = get_sampling_limits(order_info['order_qty'])
        major_limit = sampling_limits["major_limit"]
        minor_limit = sampling_limits["minor_limit"]
        
        ai_critical_count = len(st.session_state.defect_store['ai_critical'])
        ai_major_count = len(st.session_state.defect_store['ai_major'])
        ai_minor_count = len(st.session_state.defect_store['ai_minor'])
        
        qc_critical_count = len(st.session_state.defect_store['qc_critical'])
        qc_major_count = len(st.session_state.defect_store['qc_major'])
        qc_minor_count = len(st.session_state.defect_store['qc_minor'])
        
        crit_change = qc_critical_count - ai_critical_count
        maj_change = qc_major_count - ai_major_count
        min_change = qc_minor_count - ai_minor_count
        
        if language == "Mandarin":
            qc_data = [
                ['缺陷类型', 'AI数量', '质检最终', '变化', '状态'],
                ['严重', str(ai_critical_count), str(qc_critical_count),
                 f"{crit_change:+d}" if crit_change != 0 else "0",
                 '失败' if qc_critical_count>0 else '通过'],
                ['主要', str(ai_major_count), str(qc_major_count),
                 f"{maj_change:+d}" if maj_change != 0 else "0",
                 f'失败' if qc_major_count>major_limit else '通过'],
                ['次要', str(ai_minor_count), str(qc_minor_count),
                 f"{min_change:+d}" if min_change != 0 else "0",
                 f'失败' if qc_minor_count>minor_limit else '通过']
            ]
        else:
            qc_data = [
                ['Defect Type', 'AI Count', 'QC Final', 'Change', 'Status'],
                ['Critical', str(ai_critical_count), str(qc_critical_count),
                 f"{crit_change:+d}" if crit_change != 0 else "0",
                 'FAIL' if qc_critical_count>0 else 'PASS'],
                ['Major', str(ai_major_count), str(qc_major_count),
                 f"{maj_change:+d}" if maj_change != 0 else "0",
                 f'FAIL' if qc_major_count>major_limit else 'PASS'],
                ['Minor', str(ai_minor_count), str(qc_minor_count),
                 f"{min_change:+d}" if min_change != 0 else "0",
                 f'FAIL' if qc_minor_count>minor_limit else 'PASS']
            ]
        
        qc_table = Table(qc_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3*cm])
        qc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), warning_orange),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), bold_font),
            ('FONTNAME', (0,1), (-1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0),(-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        
        elements.append(Paragraph(qc_label, qc_section_style))
        elements.append(Spacer(1, 10))
        elements.append(KeepTogether(qc_table))  # Keep QC table together
        elements.append(Spacer(1, 20))
        photos_elements = create_photos_of_faults_table(language, chinese_font)
        if photos_elements:
            elements.append(PageBreak())
            elements.extend(photos_elements)
        
        # QC NOTES - Start new page if needed
        if st.session_state.qc_notes_english and st.session_state.qc_notes_english.strip():
            elements.append(PageBreak())
            
            if language == "Mandarin":
                notes_label = "质检经理备注"
            else:
                notes_label = "QC MANAGER NOTES"
                
            notes_section_style = ParagraphStyle('NotesSection', parent=section_style, fontName=bold_font)
            elements.append(Paragraph(notes_label, notes_section_style))
            
            # Translate notes if needed
            if language == "Mandarin":
                notes_text = translate_text_with_openai(st.session_state.qc_notes_english, "Mandarin")
            else:
                notes_text = st.session_state.qc_notes_english
                
            notes_body_style = ParagraphStyle('NotesBody', parent=styles['Normal'], fontSize=10,
                                             fontName=base_font)
            elements.append(Paragraph(notes_text, notes_body_style))
            elements.append(Spacer(1, 15))
        
        # Build the PDF with unified header/footer on all pages
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

def render_defect_section_with_audio(defect_type, category_key):
    """Render defect section with audio input option and editing capability"""
    st.markdown(f"### {t(f'{defect_type.lower()}_review')}")
    
    # Display existing defects with remove and edit buttons
    qc_ids, qc_translated = get_translated_defects(f'qc_{category_key}', st.session_state.ui_language)
    
    if qc_translated:
        for idx, (defect_id, defect_text) in enumerate(zip(qc_ids, qc_translated)):
            # Check if this defect is currently being edited
            is_editing = (st.session_state.editing_defect == (f'qc_{category_key}', defect_id))
            
            col1, col2, col3 = st.columns([5, 1, 1])
            
            with col1:
                if is_editing:
                    # Edit mode - show text input
                    edited_text = st.text_input(
                        t("edit_defect_prompt"),
                        value=st.session_state.edit_text,
                        key=f"edit_{defect_id}",
                        label_visibility="collapsed"
                    )
                    st.session_state.edit_text = edited_text
                else:
                    # Display mode - show defect with hover effect
                    css_class = f"defect-item {category_key}-defect"
                    if is_editing:
                        css_class += " edit-mode"
                    st.markdown(f'<div class="{css_class}" onclick="alert(\'Double click to edit\')">{defect_text}</div>', unsafe_allow_html=True)
            
            with col2:
                if is_editing:
                    # Save button
                    if st.button(f"💾", key=f"save_{defect_id}"):
                        if st.session_state.edit_text.strip():
                            # Translate back to English if needed
                            if st.session_state.ui_language != "English":
                                try:
                                    reverse_response = client.chat.completions.create(
                                        model="gpt-4o-mini",
                                        messages=[{
                                            "role": "user",
                                            "content": f"Translate this quality control defect description to English. Be precise and accurate. Return ONLY the English translation:\n\n{st.session_state.edit_text.strip()}"
                                        }],
                                        max_tokens=200,
                                        temperature=0.1
                                    )
                                    english_text = reverse_response.choices[0].message.content.strip()
                                except Exception as e:
                                    st.warning(f"Translation warning: Using original text. Error: {str(e)}")
                                    english_text = st.session_state.edit_text.strip()
                            else:
                                english_text = st.session_state.edit_text.strip()
                            
                            # Remove measurements
                            english_text = remove_measurements_from_defect(english_text)
                            
                            # Update the defect
                            update_defect_in_store(f'qc_{category_key}', defect_id, english_text)
                            st.session_state.editing_defect = None
                            st.session_state.edit_text = ""
                            st.rerun()
                else:
                    # Edit button
                    if st.button(f"✏️", key=f"edit_{defect_id}"):
                        st.session_state.editing_defect = (f'qc_{category_key}', defect_id)
                        # Get the English text for editing
                        for did, text in st.session_state.defect_store[f'qc_{category_key}']:
                            if did == defect_id:
                                st.session_state.edit_text = text
                                break
                        st.rerun()
            
            with col3:
                if is_editing:
                    # Cancel button
                    if st.button(f"❌", key=f"cancel_{defect_id}"):
                        st.session_state.editing_defect = None
                        st.session_state.edit_text = ""
                        st.rerun()
                else:
                    # Remove button
                    if st.button("❌", key=f"remove_{category_key}_{defect_id}"):
                        remove_defect_from_store(f'qc_{category_key}', defect_id)
                        st.rerun()
    else:
        st.success(f"{t('no_defects')}")
    
    # Use the new audio-enabled input section
    render_audio_input_section(f"input_{category_key}", defect_type.lower())



def render_problem_table_ui(which_table="ai"):
    """Render the problem table UI with edit functionality for QC table"""
    if which_table == "ai":
        st.markdown(f"### {t('problem_identified_ai')}")
        problem_data = st.session_state.problem_defects_ai
        is_editable = False
    else:
        st.markdown(f"### {t('problem_identified_qc')}")
        problem_data = st.session_state.problem_defects_qc
        is_editable = True
    
    # Calculate totals for inspection results
    total_cr, total_major, total_minor = calculate_problem_table_totals(problem_data)
    
    # Define problem names based on UI language
    if st.session_state.ui_language == "Mandarin":
        problem_names = {
            'color_variation': '色差',
            'clean': '清洁',
            'toe_lasting': '前帮',
            'heel_angle': '包跟角',
            'waist': '腰帮',
            'edge_wrinkle': '包边皱',
            'lace': '鞋带',
            'outsole': '大底',
            'velcro': '魔术贴',
            'adhesion': '胶着',
            'buckle': '鞋扣',
            'midsole_glue': '中底胶',
            'tongue': '鞋舌',
            'grinding_high': '打磨高',
            'back_strap_length': '后带长',
            'heel': '鞋跟',
            'back_strap_attachment': '后带固',
            'toplift': '大皮',
            'damage_upper': '鞋面损',
            'bottom_gapping': '底开胶',
            'xray_wrinkle': '鞋面皱',
            'stains': '溢胶',
            'thread_ends': '线头'
        }
    else:
        problem_names = {
            'color_variation': 'Color Variation',
            'clean': 'Clean',
            'toe_lasting': 'Toe Lasting',
            'heel_angle': 'Heel Angle',
            'waist': 'Waist',
            'edge_wrinkle': 'Edge Wrinkle',
            'lace': 'Lace',
            'outsole': 'Outsole',
            'velcro': 'Velcro',
            'adhesion': 'Adhesion',
            'buckle': 'Buckle',
            'midsole_glue': 'Midsole Glue',
            'tongue': 'Tongue',
            'grinding_high': 'Grinding High',
            'back_strap_length': 'Back strap Length',
            'heel': 'Heel',
            'back_strap_attachment': 'Back strap attachment',
            'toplift': 'Toplift',
            'damage_upper': 'Damage upper',
            'bottom_gapping': 'Bottom Gapping',
            'xray_wrinkle': 'X-RAY',
            'stains': 'Stains',
            'thread_ends': 'Thread ends'
        }
    
    # Create a COMPLETE HTML table as a single string
    table_html = f'''<div class="scrollable-table">
    <table style="width: 100%; border-collapse: separate; border-spacing: 0; font-family: Arial, sans-serif; font-size: 14px; min-width: 800px; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;">
        <thead>
            <tr>
                <th style="width: 25%; padding: 8px; border: 1px solid #e5e7eb; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">{t('problem')}</th>
                <th style="width: 8%; padding: 8px; border: 1px solid #e5e7eb; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">{t('critical')}</th>
                <th style="width: 8%; padding: 8px; border: 1px solid #e5e7eb; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">{t('major')}</th>
                <th style="width: 8%; padding: 8px; border: 1px solid #e5e7eb; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">{t('minor')}</th>
                <th style="width: 25%; padding: 8px; border: 1px solid #e5e7eb; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">{t('problem')}</th>
                <th style="width: 8%; padding: 8px; border: 1px solid #e5e7eb; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">{t('critical')}</th>
                <th style="width: 8%; padding: 8px; border: 1px solid #e5e7eb; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">{t('major')}</th>
                <th style="width: 8%; padding: 8px; border: 1px solid #e5e7eb; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">{t('minor')}</th>
            </tr>
        </thead>
        <tbody>'''
    
    # Define problem pairs - each pair should be in ONE ROW
    problem_pairs = [
        ("color_variation", "clean"),
        ("toe_lasting", "heel_angle"),
        ("waist", "edge_wrinkle"),
        ("lace", "outsole"),
        ("velcro", "adhesion"),
        ("buckle", "midsole_glue"),
        ("tongue", "grinding_high"),
        ("back_strap_length", "heel"),
        ("back_strap_attachment", "toplift"),
        ("damage_upper", "bottom_gapping"),
        ("xray_wrinkle", "stains"),
        ("thread_ends", "")
    ]
    
    for left_key, right_key in problem_pairs:
        table_html += f'''
        <tr>
            <td style="text-align: left; padding: 8px; border: 1px solid #e5e7eb; background-color: #f8fafc; font-weight: 600;">{problem_names.get(left_key, '') if left_key else ''}</td>
            <td style="text-align: center; padding: 8px; border: 1px solid #e5e7eb; background-color: #fee2e2; font-weight: 600;">{problem_data[left_key]['cr'] if left_key else ''}</td>
            <td style="text-align: center; padding: 8px; border: 1px solid #e5e7eb; background-color: #ffedd5; font-weight: 600;">{problem_data[left_key]['major'] if left_key else ''}</td>
            <td style="text-align: center; padding: 8px; border: 1px solid #e5e7eb; background-color: #dbeafe; font-weight: 600;">{problem_data[left_key]['minor'] if left_key else ''}</td>'''
        
        if right_key:
            table_html += f'''
            <td style="text-align: left; padding: 8px; border: 1px solid #e5e7eb; background-color: #f8fafc; font-weight: 600;">{problem_names.get(right_key, '')}</td>
            <td style="text-align: center; padding: 8px; border: 1px solid #e5e7eb; background-color: #fee2e2; font-weight: 600;">{problem_data[right_key]['cr']}</td>
            <td style="text-align: center; padding: 8px; border: 1px solid #e5e7eb; background-color: #ffedd5; font-weight: 600;">{problem_data[right_key]['major']}</td>
            <td style="text-align: center; padding: 8px; border: 1px solid #e5e7eb; background-color: #dbeafe; font-weight: 600;">{problem_data[right_key]['minor']}</td>
            </tr>'''
        else:
            table_html += f'''
            <td style="padding: 8px; border: 1px solid #e5e7eb; background-color: white;"></td>
            <td style="padding: 8px; border: 1px solid #e5e7eb; background-color: white;"></td>
            <td style="padding: 8px; border: 1px solid #e5e7eb; background-color: white;"></td>
            <td style="padding: 8px; border: 1px solid #e5e7eb; background-color: white;"></td>
        </tr>'''
    
    # Last row - Inspection results - USE CALCULATED TOTALS
    table_html += f'''
        </tbody>
        <tfoot>
            <tr>
                <td style="text-align: left; padding: 8px; border: 1px solid #e5e7eb; background-color: #fffacd; font-weight: bold;">{t('total_defects_count')}:</td>
                <td style="text-align: center; padding: 8px; border: 1px solid #e5e7eb; background-color: #b0c4de; font-weight: bold;">{total_cr}</td>
                <td style="text-align: center; padding: 8px; border: 1px solid #e5e7eb; background-color: #b0c4de; font-weight: bold;">{total_major}</td>
                <td style="text-align: center; padding: 8px; border: 1px solid #e5e7eb; background-color: #b0c4de; font-weight: bold;">{total_minor}</td>
                <td style="padding: 8px; border: 1px solid #e5e7eb; background-color: white;"></td>
                <td style="padding: 8px; border: 1px solid #e5e7eb; background-color: #98fb98;"></td>
                <td style="padding: 8px; border: 1px solid #e5e7eb; background-color: #98fb98;"></td>
                <td style="padding: 8px; border: 1px solid #e5e7eb; background-color: #98fb98;"></td>
            </tr>
        </tfoot>
    </table>
    </div>'''
    
    # Render the entire table as a single HTML block
    st.markdown(table_html, unsafe_allow_html=True)
    
    # ADDED: Edit Problem Counts interface for QC Manager table
    if is_editable:
        st.markdown("---")
        st.markdown(f"### {t('edit_problem_counts')}")
        
        # Simple edit interface as fallback
        st.markdown("**Edit Problem Counts:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_problem = st.selectbox(
                t("select_problem"),
                list(problem_names.keys()),
                format_func=lambda x: problem_names[x],
                key=f"edit_problem_select_{which_table}"
            )
        with col2:
            selected_severity = st.selectbox(
                t("select_severity"),
                ['cr', 'major', 'minor'],
                format_func=lambda x: t(x.upper()),
                key=f"edit_severity_select_{which_table}"
            )
        with col3:
            new_value = st.number_input(
                t("new_value"),
                min_value=0,
                value=st.session_state.problem_defects_qc[selected_problem][selected_severity],
                key=f"edit_value_input_{which_table}"
            )
        
        if st.button(f"{t('update_problem')} - {problem_names[selected_problem]} - {t(selected_severity.upper())}", key=f"update_btn_{which_table}"):
            st.session_state.problem_defects_qc[selected_problem][selected_severity] = int(new_value)
            st.success(f"Updated {problem_names[selected_problem]} - {t(selected_severity.upper())} to {new_value}")
            st.rerun()

# JavaScript message handler for component communication
# Add this section AFTER the PDF language selection in the sidebar



with st.sidebar:
    st.markdown(f"### {t('language_preference')}")
    
    st.markdown("**Interface Language:**")
    ui_lang = st.selectbox(
        "UI Language",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.ui_language),
        format_func=lambda x: f"{LANGUAGES[x]['flag']} {LANGUAGES[x]['label']}",
        key="ui_lang_select",
        label_visibility="collapsed"
    )
    
    st.markdown("**PDF Report Language:**")
    pdf_lang = st.selectbox(
        "PDF Language",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.pdf_language),
        format_func=lambda x: f"{LANGUAGES[x]['flag']} {LANGUAGES[x]['label']}",
        key="pdf_lang_select",
        label_visibility="collapsed"
    )

if ui_lang != st.session_state.ui_language:
    st.session_state.ui_language = ui_lang
    st.rerun()

if pdf_lang != st.session_state.pdf_language:
    st.session_state.pdf_language = pdf_lang

# Main App Content
st.markdown(f'<div class="hero-section"><h1 style="margin:0; font-size: 1.8rem;">{t("app_title")}</h1><p style="margin-top:0.5rem; font-size: 0.9rem;">GRAND STEP (H.K.) LTD<br>Professional Footwear Manufacturing &amp; Quality Control<br>AI-Powered Quality Inspection System</p></div>', unsafe_allow_html=True)

st.markdown(f'<div class="section-header">{t("order_info")}</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    st.markdown("### 📍 Location Selection")
    
    # Major Chinese cities with Chinese and English names
    CHINESE_CITIES = {
        "Guangzhou": "广东",
        "Shenzhen": "深圳",
        "Dongguan": "东莞",
        "Foshan": "佛山",
        "Zhongshan": "中山",
        "Huizhou": "惠州",
        "Zhuhai": "珠海",
        "Jiangmen": "江门",
        "Zhaoqing": "肇庆",
        "Shanghai": "上海",
        "Beijing": "北京",
        "Suzhou": "苏州",
        "Hangzhou": "杭州",
        "Ningbo": "宁波",
        "Wenzhou": "温州",
        "Wuhan": "武汉",
        "Chengdu": "成都",
        "Chongqing": "重庆",
        "Tianjin": "天津",
        "Nanjing": "南京",
        "Xi'an": "西安",
        "Qingdao": "青岛",
        "Dalian": "大连",
        "Shenyang": "沈阳",
        "Changsha": "长沙",
        "Zhengzhou": "郑州",
        "Jinan": "济南",
        "Harbin": "哈尔滨",
        "Changchun": "长春",
        "Taiyuan": "太原",
        "Shijiazhuang": "石家庄",
        "Lanzhou": "兰州",
        "Xiamen": "厦门",
        "Fuzhou": "福州",
        "Nanning": "南宁",
        "Kunming": "昆明",
        "Guiyang": "贵阳",
        "Haikou": "海口",
        "Ürümqi": "乌鲁木齐",
        "Lhasa": "拉萨"
    }
    
    # Initialize session state for selected city
    if 'selected_city' not in st.session_state:
        st.session_state.selected_city = "Guangzhou"  # Default city
    
    # Create dropdown with both English and Chinese names
    city_options = [f"{city} ({chinese})" for city, chinese in CHINESE_CITIES.items()]
    
    selected_city_display = st.selectbox(
        "Select City for Report Footer",
        options=city_options,
        index=city_options.index(f"{st.session_state.selected_city} ({CHINESE_CITIES[st.session_state.selected_city]})"),
        help="Select a Chinese city for the report footer location"
    )
    
    # Extract the English city name from selection
    selected_city_english = selected_city_display.split(" (")[0]
    
    if selected_city_english != st.session_state.selected_city:
        st.session_state.selected_city = selected_city_english
        st.rerun()
# Order Information
col1, col2, col3 = st.columns(3)
with col1:
    contract_number = st.text_input(t("contract_number"), value="0144540")
    factory = st.text_input(t("factory"), value="RY Factory")
    customer = st.text_input(t("customer"), value="MIA")
with col2:
    style_number = st.text_input(t("style_number"), value="GS1412401B")
    order_qty = st.text_input(t("order_qty"), value="1000")
    color = st.text_input(t("color"), value="PPB")
with col3:
    inspector = st.text_input(t("inspector"), value="XI")
    inspection_date = st.date_input(t("inspection_date"), value=datetime.now().date())

# Store order quantity for later use
st.session_state.order_qty_input = order_qty

# New input fields
st.markdown(f'<div class="sampling-section">{t("sampling_inspection")}</div>', unsafe_allow_html=True)

new_col1, new_col2, new_col3 = st.columns(3)
with new_col1:
    # Calculate total sampling based on order quantity
    calculated_sampling = calculate_total_sampling(order_qty)
    st.session_state.total_sampling = st.text_input(
        t("total_sampling"), 
        value=calculated_sampling,
        key="total_sampling_input"
    )
with new_col2:
    st.session_state.ctn_no = st.text_input(t("ctn_no"), value="", key="ctn_no_input")
with new_col3:
    st.session_state.lot_size = st.text_input(t("lot_size"), value="", key="lot_size_input")

# Display sampling information based on order quantity
if order_qty:
    try:
        qty = int(order_qty)
        sampling_info = get_sampling_limits(order_qty)
        if sampling_info["to_inspect"]:
            st.info(f"**Based on Order Qty {qty}:** Total Sampling = {sampling_info['to_inspect']} | Major Limit = {sampling_info['major_limit']} | Minor Limit = {sampling_info['minor_limit']}")
    except:
        pass

st.markdown(f'<div class="section-header">{t("image_upload")}</div>', unsafe_allow_html=True)

# Upload images without specific order requirement
uploaded_files = st.file_uploader(t("upload_images"), type=['png','jpg','jpeg'], accept_multiple_files=True)

uploaded_images = []

if uploaded_files and len(uploaded_files) == 4:
    cols = st.columns(4)
    for idx, file in enumerate(uploaded_files):
        uploaded_images.append(file)
        with cols[idx]:
            st.image(Image.open(file), caption=f"Image {idx + 1}", use_container_width=True)

if len(uploaded_images) == 4:
    if st.button(f"{t('start_inspection')}", type="primary", use_container_width=True):
        progress = st.progress(0)
        analyses = []
        all_defect_coordinates = {}
        
        # Store uploaded images for later cropping
        st.session_state.uploaded_images_data = []
        for file in uploaded_images:
            image = Image.open(file)
            st.session_state.uploaded_images_data.append(image)
        
        # Reset AI problem table
        for key in st.session_state.problem_defects_ai:
            st.session_state.problem_defects_ai[key] = {'cr': 0, 'major': 0, 'minor': 0}
        
        with st.spinner(t("analyzing")):
            for idx, file in enumerate(uploaded_images):
                image = Image.open(file)
                analysis, defect_coordinates = analyze_shoe_image_with_locations(
                    client, image, idx + 1, style_number, color, contract_number
                )
                analyses.append(analysis)
                all_defect_coordinates.update(defect_coordinates)
                progress.progress((idx + 1) / 4)
        
        # Crop and store defect images
        st.session_state.defect_images = {}
        for defect_desc, coords in all_defect_coordinates.items():
            # Find which image contains this defect
            for img_idx, analysis in enumerate(analyses):
                if analysis:
                    all_defects = (analysis.get('critical_defects', []) + 
                                 analysis.get('major_defects', []) + 
                                 analysis.get('minor_defects', []))
                    
                    # Check if this defect exists in current image analysis
                    clean_defect = defect_desc
                    if clean_defect in all_defects:
                        original_image = st.session_state.uploaded_images_data[img_idx]
                        cropped_image = crop_defect_area(original_image, coords)
                        
                        if cropped_image:
                            # Create a unique ID for this defect
                            defect_id = f"defect_{hash(defect_desc)}_{img_idx}"
                            category = get_defect_category(clean_defect, analysis)
                            st.session_state.defect_images[defect_id] = {
                                'image_buffer': save_image_to_buffer(cropped_image),
                                'description': clean_defect,
                                'category': category
                            }
                        break
        
        order_info = {
            "contract_number": contract_number,
            "factory": factory,
            "order_qty": order_qty,
            "style_number": style_number,
            "color": color,
            "customer": customer,
            "inspector": inspector,
            "inspection_date": inspection_date.strftime("%Y-%m-%d")
        }
        
        ai_report = generate_qc_report(analyses)
        
        st.session_state.ai_report = ai_report
        st.session_state.order_info = order_info
        st.session_state.defect_coordinates = all_defect_coordinates
        st.session_state.qc_notes_english = ''
        st.session_state.analyses_done = True
        st.rerun()

if 'analyses_done' in st.session_state and st.session_state.analyses_done:
    ai_report = st.session_state.ai_report
    order_info = st.session_state.order_info
    
    st.markdown(f"## {t('ai_results')}")
    
    ai_critical_ids, ai_critical_translated = get_translated_defects('ai_critical', st.session_state.ui_language)
    ai_major_ids, ai_major_translated = get_translated_defects('ai_major', st.session_state.ui_language)
    ai_minor_ids, ai_minor_translated = get_translated_defects('ai_minor', st.session_state.ui_language)
    
    col1, col2, col3 = st.columns(3)
    metrics = [
        (t("critical"), len(ai_critical_ids), "#dc2626"),
        (t("major"), len(ai_major_ids), "#ea580c"),
        (t("minor"), len(ai_minor_ids), "#2563eb")
    ]
    
    for col, (label, count, color) in zip([col1, col2, col3], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {color};">
                <div class="metric-number" style="color: {color};">{count}</div>
                <div class="metric-label">AI {label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander(f"{t('view_ai_defects')}", expanded=True):
        if ai_critical_translated:
            st.markdown(f"**{t('critical')}:**")
            for d in ai_critical_translated:
                st.markdown(f'<div class="defect-item critical-defect">{d}</div>', unsafe_allow_html=True)
        
        if ai_major_translated:
            st.markdown(f"**{t('major')}:**")
            for d in ai_major_translated:
                st.markdown(f'<div class="defect-item major-defect">{d}</div>', unsafe_allow_html=True)
        
        if ai_minor_translated:
            st.markdown(f"**{t('minor')}:**")
            for d in ai_minor_translated:
                st.markdown(f'<div class="defect-item minor-defect">{d}</div>', unsafe_allow_html=True)
        
        if not (ai_critical_translated or ai_major_translated or ai_minor_translated):
            st.success(f"{t('no_defects')}")
    
    st.markdown("---")
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 1.5rem;
    border-radius: 12px; margin: 1.5rem 0; text-align: center;">
        <div style="font-size: 1.3rem; font-weight: 700;">{t('qc_review')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Render AI problem table UI (read-only)
    render_problem_table_ui("ai")
    
    st.markdown("---")
    
    # Render QC problem table UI (editable) - Now includes the edit interface
    render_problem_table_ui("qc")
    
    # Photos of Faults - QC Manager ONLY with Circle Annotation
    st.markdown("---")
    render_photos_of_faults_ui()
    
    st.markdown("---")
    
    # Critical defects section with audio and editing
    render_defect_section_with_audio("critical", "critical")
    
    st.markdown("---")
    
    # Major defects section with audio and editing  
    render_defect_section_with_audio("major", "major")
    
    st.markdown("---")
    
    # Minor defects section with audio and editing
    render_defect_section_with_audio("minor", "minor")
    
    st.markdown("---")
    
    # QC Notes with audio
    render_qc_notes_audio_section()
    
    st.markdown("---")
    
    final_result, final_reason = calculate_final_decision()
    
    st.markdown(f"## {t('final_summary')}")
    
    qc_critical_ids, qc_critical_translated = get_translated_defects('qc_critical', st.session_state.ui_language)
    qc_major_ids, qc_major_translated = get_translated_defects('qc_major', st.session_state.ui_language)
    qc_minor_ids, qc_minor_translated = get_translated_defects('qc_minor', st.session_state.ui_language)
    
    qc_critical_count = len(qc_critical_ids)
    qc_major_count = len(qc_major_ids)
    qc_minor_count = len(qc_minor_ids)
    
    # Get sampling limits for display
    sampling_limits = get_sampling_limits(order_qty)
    major_limit = sampling_limits["major_limit"]
    minor_limit = sampling_limits["minor_limit"]
    
    col1, col2, col3 = st.columns(3)
    changes = [
        (qc_critical_count - len(ai_critical_ids), "#dc2626"),
        (qc_major_count - len(ai_major_ids), "#ea580c"),
        (qc_minor_count - len(ai_minor_ids), "#2563eb")
    ]
    
    labels = [t("critical"), t("major"), t("minor")]
    counts = [qc_critical_count, qc_major_count, qc_minor_count]
    
    for col, label, count, (change, color) in zip([col1, col2, col3], labels, counts, changes):
        icon = "🔺" if change > 0 else "🔻" if change < 0 else "➖"
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {color};">
                <div class="metric-number" style="color: {color};">{count}</div>
                <div class="metric-label">{label}</div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem; color: #374151; font-weight: 600;">{icon} {abs(change)} {t('from_ai')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    result_colors_final = {
        "ACCEPT": ("#10b981", "#dcfce7"), 
        "REWORK": ("#f59e0b", "#fef3c7"), 
        "REJECT": ("#ef4444", "#fecaca")
    }
    final_bg, final_light = result_colors_final[final_result]
    
    translated_result = translate_text_with_openai(final_result, st.session_state.ui_language)
    translated_reason = translate_text_with_openai(final_reason, st.session_state.ui_language)
    
    st.markdown(f"""
    <div style="background: {final_light}; border: 3px solid {final_bg}; border-radius: 12px;
    padding: 1.5rem; margin: 1.5rem 0; text-align: center;">
        <div style="font-size: 1rem; font-weight: 600;">{t('final_qc_decision')}</div>
        <div style="font-size: 2rem; font-weight: 800; color: {final_bg};">{translated_result}</div>
        <div style="font-size: 0.9rem; margin-top: 0.5rem;">{translated_reason}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"## {t('generate_pdf')}")
    st.info(f"{t('pdf_language_info')} {LANGUAGES[st.session_state.pdf_language]['flag']} {LANGUAGES[st.session_state.pdf_language]['label']}")
    
    if st.button(f"{t('generate_pdf')}", type="primary", use_container_width=True):
        with st.spinner(t("generating_pdf")):
            pdf_bytes = generate_multilingual_pdf(
                order_info, 
                st.session_state.pdf_language
            )
        
        if pdf_bytes:
            lang_suffix = st.session_state.pdf_language[:2].upper()
            filename = f"QC_Report_{contract_number}_{style_number}_{lang_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            st.download_button(
                label=f"⬇️ {t('download_pdf')}",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            st.success(f"✅ {t('pdf_ready')}")
        else:
            st.error(f"❌ {t('pdf_failed')}")
# Add at the very end, before the last line


