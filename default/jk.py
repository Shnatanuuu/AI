import streamlit as st
import openai
import base64
from PIL import Image, ImageDraw
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import re
import hashlib

load_dotenv()

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
        "annotate_image": "🔍 Annotate Image",
        "circle_position": "Circle Position",
        "x_position": "X Position",
        "y_position": "Y Position",
        "radius": "Radius",
        "generate_pdf_button": "Generate and Download PDF",
        "download_annotated_pdf": "Download Annotated PDF",
        "how_to_use": "How to use",
        "canvas_width": 600,
        "canvas_height": 400
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
        "annotate_image": "🔍 标注图像",
        "circle_position": "圆圈位置",
        "x_position": "X 位置",
        "y_position": "Y 位置",
        "radius": "半径",
        "generate_pdf_button": "生成并下载PDF",
        "download_annotated_pdf": "下载标注PDF",
        "how_to_use": "使用说明",
        "canvas_width": 600,
        "canvas_height": 400
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

# Photos of Faults storage
if 'qc_defect_containers' not in st.session_state:
    st.session_state.qc_defect_containers = []  # List of dictionaries for each defect container

# Annotation state for each defect container image
if 'annotation_data' not in st.session_state:
    st.session_state.annotation_data = {}  # Store annotation data for each image

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
    
    /* Annotation canvas styling */
    .annotation-canvas {
        border: 3px solid #888;
        border-radius: 10px;
        background-color: #f5f5f5;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

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
    qc_critical_count = len(st.session_state.defect_store['qc_critical'])
    qc_major_count = len(st.session_state.defect_store['qc_major'])
    qc_minor_count = len(st.session_state.defect_store['qc_minor'])
    
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
                [f"Result: {order_qty}", 
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
    """Create Photos of Faults table for PDF with actual QC Manager images - FIXED LANGUAGE CONSISTENCY"""
    # Get QC defect containers
    qc_containers = st.session_state.get('qc_defect_containers', [])
    
    if not qc_containers:
        return None  # Don't show the section if no containers
    
    # Group containers by severity
    containers_by_severity = {
        'minor': [c for c in qc_containers if c.get('severity') == 'minor'],
        'major': [c for c in qc_containers if c.get('severity') == 'major'],
        'critical': [c for c in qc_containers if c.get('severity') == 'critical']
    }
    
    # Remove empty severity groups
    containers_by_severity = {k: v for k, v in containers_by_severity.items() if v}
    
    if not containers_by_severity:
        return None
    
    elements = []
    
    # Define page width for table calculations (A4 portrait width minus margins)
    page_width = A4[0] - 4*cm  # This was missing!
    
    # Use appropriate title based on language
    if language == "Mandarin":
        title = "缺陷照片"
    else:
        title = "PHOTOS OF FAULTS"
    
    # Title section with appropriate language ONLY
    title_style = ParagraphStyle('PhotosTitle', fontName='Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold'),
                                fontSize=14, alignment=TA_CENTER, textColor=colors.black, spaceAfter=15)
    elements.append(Paragraph(title, title_style))
    
    # Define severity labels based on language
    severity_labels = {
        'minor': ("MINOR DEFECTS" if language == "English" else "次要问题"),
        'major': ("MAJOR DEFECTS" if language == "English" else "主要问题"),
        'critical': ("CRITICAL DEFECTS" if language == "English" else "严重问题")
    }
    
    # Define severity colors
    severity_colors = {
        'minor': colors.Color(0.9, 0.9, 0.9),  # Light gray
        'major': colors.Color(1, 0.7, 0.5),    # Orange
        'critical': colors.Color(0.9, 0.2, 0.2) # Red
    }
    
    container_counter = 1
    
    # Process each severity group
    for severity in ['minor', 'major', 'critical']:
        if severity not in containers_by_severity:
            continue
            
        severity_containers = containers_by_severity[severity]
        
        # Add severity header
        header_style = ParagraphStyle('SeverityHeader', 
                                     fontName='Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold'),
                                     fontSize=12, textColor=colors.black if severity != 'critical' else colors.white,
                                     alignment=TA_LEFT, leftIndent=10)
        
        # Create header row
        header_data = [[severity_labels[severity], '']]
        header_table = Table(header_data, colWidths=[page_width * 0.5, page_width * 0.5])
        header_style_table = TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), severity_colors[severity]),
            ('SPAN', (0, 0), (1, 0)),
            ('FONTSIZE', (0, 0), (1, 0), 11),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold' if language == "English" else (chinese_font if chinese_font else 'Helvetica-Bold')),
            ('ALIGN', (0, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
            ('GRID', (0, 0), (1, 0), 1.5, colors.black),
            ('LEFTPADDING', (0, 0), (1, 0), 10),
            ('TOPPADDING', (0, 0), (1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (1, 0), 8),
        ])
        header_table.setStyle(header_style_table)
        elements.append(header_table)
        elements.append(Spacer(1, 10))
        
        # Process each container in this severity group
        for container in severity_containers:
            images = container.get('images', [])
            
            if not images:
                continue
                
            # Create defect name row
            defect_name = f"{container_counter}. {container['name']}"
            container_counter += 1
            
            # Split images into pairs (2 per row)
            for i in range(0, len(images), 2):
                image_pair = images[i:i+2]
                row_data = []
                
                for j, image_bytes in enumerate(image_pair):
                    try:
                        # Create ReportLab Image from bytes
                        img_buffer = io.BytesIO(image_bytes)
                        reportlab_img = ReportLabImage(img_buffer)
                        
                        # Set image size (1 inch = 72 points)
                        img_width = 72  # 1 inch
                        img_height = 72  # 1 inch
                        reportlab_img.drawWidth = img_width
                        reportlab_img.drawHeight = img_height
                        
                        # Create a table cell with the image
                        cell_content = [[reportlab_img]]
                        image_table = Table(cell_content, colWidths=img_width, rowHeights=img_height)
                        image_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                            ('GRID', (0, 0), (0, 0), 0.5, colors.grey),
                        ]))
                        
                        if j == 0 and i == 0:
                            # First image in first row - include defect name
                            row_data.append([Paragraph(defect_name, ParagraphStyle(
                                'DefectName', 
                                fontName='Helvetica' if language == "English" else (chinese_font if chinese_font else 'Helvetica'),
                                fontSize=10,
                                alignment=TA_LEFT
                            )), image_table])
                        else:
                            row_data.append(['', image_table])
                            
                    except Exception as e:
                        st.warning(f"Error processing image: {str(e)}")
                        if j == 0 and i == 0:
                            row_data.append([Paragraph(defect_name, ParagraphStyle(
                                'DefectName', 
                                fontName='Helvetica' if language == "English" else (chinese_font if chinese_font else 'Helvetica'),
                                fontSize=10,
                                alignment=TA_LEFT
                            )), 'Image Error'])
                        else:
                            row_data.append(['', 'Image Error'])
                
                # Ensure we always have 2 columns
                while len(row_data) < 2:
                    row_data.append(['', ''])
                
                # Create the row table
                row_table = Table(row_data, colWidths=[page_width * 0.25, page_width * 0.25], 
                                 rowHeights=[20, 90])  # 20 for defect name, 90 for image
                
                row_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('SPAN', (0, 0), (0, 0)),  # Span defect name across both columns if needed
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                
                elements.append(row_table)
                elements.append(Spacer(1, 5))
        
        # Add spacing between severity sections
        elements.append(Spacer(1, 15))
    
    return KeepTogether(elements) if elements else None

def generate_multilingual_pdf(order_info, language):
    """Generate PDF with proper Mandarin font handling - UPDATED TO REMOVE SIGNATURES"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                               topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        styles = getSampleStyleSheet()
        
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
        
        brand_blue = colors.Color(0.4, 0.49, 0.91)
        success_green = colors.Color(0.31, 0.78, 0.47)
        warning_orange = colors.Color(1.0, 0.6, 0.0)
        danger_red = colors.Color(1.0, 0.42, 0.42)
        light_gray = colors.Color(0.97, 0.97, 0.97)
        
        # Styles
        title_style = ParagraphStyle('Title', parent=styles['Normal'], fontSize=22, alignment=TA_CENTER,
                                     textColor=brand_blue, fontName=bold_font, spaceAfter=12)
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER,
                                        textColor=colors.Color(0.3, 0.3, 0.3), fontName=base_font, spaceAfter=8)
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, spaceAfter=10,
                                      spaceBefore=15, textColor=brand_blue, fontName=bold_font, alignment=TA_CENTER)
        
        # Header
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
        
        # PHOTOS OF FAULTS - Start new page
        elements.append(PageBreak())
        
        # Create Photos of Faults table with actual images
        photos_table = create_photos_of_faults_table(language, chinese_font)
        if photos_table:
            elements.append(photos_table)
            elements.append(Spacer(1, 20))
        
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
        
        # SIGNATURES SECTION REMOVED AS REQUESTED
        
        doc.build(elements)
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

def resize_image_for_pdf(image_bytes, max_width=1*inch, max_height=1*inch):
    """Resize image to fit within 1 inch dimensions for PDF"""
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Calculate new dimensions maintaining aspect ratio
        width, height = img.size
        aspect_ratio = width / height
        
        if width > height:
            # Landscape image
            new_width = min(max_width, width)
            new_height = new_width / aspect_ratio
            if new_height > max_height:
                new_height = max_height
                new_width = new_height * aspect_ratio
        else:
            # Portrait or square image
            new_height = min(max_height, height)
            new_width = new_height * aspect_ratio
            if new_width > max_width:
                new_width = max_width
                new_height = new_width / aspect_ratio
        
        # Resize image
        img_resized = img.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
        
        # Save to bytes
        buffer = io.BytesIO()
        img_resized.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Error resizing image: {str(e)}")
        return image_bytes  # Return original if resize fails

def img_to_base64(img):
    """Convert PIL image to base64 string."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def draw_circle(img, canvas_x, canvas_y, canvas_r, canvas_width, canvas_height):
    """Draw a circle on the image using PIL, scaling coordinates from canvas to image."""
    copy = img.copy()
    draw = ImageDraw.Draw(copy)
    
    img_width, img_height = img.size
    
    # Calculate how the image was scaled to fit the canvas
    canvas_ratio = canvas_width / canvas_height
    img_ratio = img_width / img_height
    
    if img_ratio > canvas_ratio:
        # Image is wider - fits to canvas width
        scale = img_width / canvas_width
        scaled_height = img_height / scale
        offset_y = (canvas_height - scaled_height) / 2
        offset_x = 0
    else:
        # Image is taller - fits to canvas height
        scale = img_height / canvas_height
        scaled_width = img_width / scale
        offset_x = (canvas_width - scaled_width) / 2
        offset_y = 0
    
    # Convert canvas coordinates to image coordinates
    actual_x = int((canvas_x - offset_x) * scale)
    actual_y = int((canvas_y - offset_y) * scale)
    actual_r = int(canvas_r * scale)
    
    # Draw the circle
    draw.ellipse([actual_x - actual_r, actual_y - actual_r, 
                  actual_x + actual_r, actual_y + actual_r], 
                 outline="red", width=max(5, int(5 * scale)))
    draw.ellipse([actual_x - 5, actual_y - 5, actual_x + 5, actual_y + 5], 
                 fill="red")
    return copy

def render_image_annotation_interface(container_idx, img_idx, image_bytes, container_name):
    """Render the interactive annotation interface for an image"""
    img = Image.open(io.BytesIO(image_bytes))
    img_width, img_height = img.size
    img64 = img_to_base64(img)
    
    # Initialize annotation data for this image if not exists
    annotation_key = f"container_{container_idx}_img_{img_idx}"
    if annotation_key not in st.session_state.annotation_data:
        st.session_state.annotation_data[annotation_key] = {
            'circle_x': t('canvas_width') // 2,
            'circle_y': t('canvas_height') // 2,
            'circle_r': 60
        }
    
    # Get annotation data
    circle_x = st.session_state.annotation_data[annotation_key]['circle_x']
    circle_y = st.session_state.annotation_data[annotation_key]['circle_y']
    circle_r = st.session_state.annotation_data[annotation_key]['circle_r']
    
    # Sidebar with sliders for this image
    with st.sidebar:
        st.subheader(f"🎯 {t('circle_position')} - {container_name}")
        
        # Create sliders that update session state on change
        new_x = st.slider(
            t("x_position"), 
            min_value=0, 
            max_value=t('canvas_width'), 
            value=circle_x,
            key=f"slider_x_{annotation_key}",
            help="Horizontal position of circle center"
        )
        
        new_y = st.slider(
            t("y_position"), 
            min_value=0, 
            max_value=t('canvas_height'), 
            value=circle_y,
            key=f"slider_y_{annotation_key}",
            help="Vertical position of circle center"
        )
        
        new_r = st.slider(
            t("radius"), 
            min_value=10, 
            max_value=200, 
            value=circle_r,
            key=f"slider_r_{annotation_key}",
            help="Circle radius"
        )
        
        # Update session state when sliders change
        if (new_x != circle_x or new_y != circle_y or new_r != circle_r):
            st.session_state.annotation_data[annotation_key]['circle_x'] = new_x
            st.session_state.annotation_data[annotation_key]['circle_y'] = new_y
            st.session_state.annotation_data[annotation_key]['circle_r'] = new_r
            st.rerun()
        
        # Show current position
        st.divider()
        st.write("**Current Position:**")
        st.write(f"X: {circle_x}")
        st.write(f"Y: {circle_y}")
        st.write(f"Radius: {circle_r}")
        
        # Generate annotated image button
        if st.button(f"📸 {t('annotate_image')}", key=f"annotate_{annotation_key}", use_container_width=True):
            # Apply the circle to the image
            annotated_img = draw_circle(
                img,
                circle_x,
                circle_y,
                circle_r,
                t('canvas_width'),
                t('canvas_height')
            )
            
            # Convert to bytes
            buf = io.BytesIO()
            annotated_img.save(buf, format='PNG')
            annotated_bytes = buf.getvalue()
            
            # Update the container image with annotated version
            st.session_state.qc_defect_containers[container_idx]['images'][img_idx] = annotated_bytes
            st.success("Image annotated successfully!")
            st.rerun()
    
    # Main area - Display interactive canvas
    st.markdown("**Interactive Canvas:**")
    
    # JavaScript to make circle follow sliders
    html_code = f'''
    <!DOCTYPE html>
    <html>
    <body>
    <div style="text-align:center;">
        <canvas id="canvas_{annotation_key}" width="{t('canvas_width')}" height="{t('canvas_height')}"
            style="border:3px solid #888; border-radius:10px; background-color:#f5f5f5;" class="annotation-canvas"></canvas>
    </div>
    
    <script>
    const canvas = document.getElementById("canvas_{annotation_key}");
    const ctx = canvas.getContext("2d");
    const img = new Image();
    img.src = "data:image/png;base64,{img64}";
    
    // Initial circle position
    let circle = {{
        x: {circle_x},
        y: {circle_y},
        r: {circle_r}
    }};
    
    // Function to draw everything
    function draw() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Calculate image scaling
        const canvasRatio = canvas.width / canvas.height;
        const imgRatio = {img_width} / {img_height};
        
        let drawWidth, drawHeight, offsetX, offsetY;
        
        if(imgRatio > canvasRatio) {{
            drawWidth = canvas.width;
            drawHeight = canvas.width / imgRatio;
            offsetX = 0;
            offsetY = (canvas.height - drawHeight) / 2;
        }} else {{
            drawHeight = canvas.height;
            drawWidth = canvas.height * imgRatio;
            offsetX = (canvas.width - drawWidth) / 2;
            offsetY = 0;
        }}
        
        // Draw image
        ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
        
        // Draw circle
        ctx.beginPath();
        ctx.arc(circle.x, circle.y, circle.r, 0, Math.PI * 2);
        ctx.strokeStyle = "red";
        ctx.lineWidth = 4;
        ctx.stroke();
        
        // Center dot
        ctx.beginPath();
        ctx.arc(circle.x, circle.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = "red";
        ctx.fill();
        
        // Resize handle
        ctx.beginPath();
        ctx.arc(circle.x + circle.r, circle.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = "blue";
        ctx.fill();
        ctx.strokeStyle = "white";
        ctx.lineWidth = 2;
        ctx.stroke();
    }}
    
    // Update circle position from Streamlit
    function updateCirclePosition(x, y, r) {{
        circle.x = x;
        circle.y = y;
        circle.r = r;
        draw();
    }}
    
    // Mouse events for direct interaction
    function getMousePos(e) {{
        const rect = canvas.getBoundingClientRect();
        return {{
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        }};
    }}
    
    function distance(x1, y1, x2, y2) {{
        return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    }}
    
    let drag = false;
    let resize = false;
    
    canvas.onmousedown = function(e) {{
        const pos = getMousePos(e);
        
        // Check if clicking on resize handle
        if(distance(pos.x, pos.y, circle.x + circle.r, circle.y) < 12) {{
            resize = true;
            canvas.style.cursor = "nwse-resize";
        }}
        // Check if clicking inside circle
        else if(distance(pos.x, pos.y, circle.x, circle.y) < circle.r) {{
            drag = true;
            canvas.style.cursor = "move";
        }}
    }};
    
    canvas.onmousemove = function(e) {{
        const pos = getMousePos(e);
        
        if(drag) {{
            circle.x = pos.x;
            circle.y = pos.y;
            draw();
            // Update Streamlit sliders
            window.parent.postMessage({{
                type: 'updatePosition_{annotation_key}',
                x: circle.x,
                y: circle.y
            }}, '*');
        }}
        else if(resize) {{
            circle.r = distance(circle.x, circle.y, pos.x, pos.y);
            if(circle.r < 10) circle.r = 10;
            draw();
            // Update Streamlit slider
            window.parent.postMessage({{
                type: 'updateRadius_{annotation_key}',
                r: circle.r
            }}, '*');
        }}
        else {{
            // Change cursor based on hover
            if(distance(pos.x, pos.y, circle.x + circle.r, circle.y) < 12) {{
                canvas.style.cursor = "nwse-resize";
            }}
            else if(distance(pos.x, pos.y, circle.x, circle.y) < circle.r) {{
                canvas.style.cursor = "move";
            }}
            else {{
                canvas.style.cursor = "default";
            }}
        }}
    }};
    
    canvas.onmouseup = function() {{
        drag = false;
        resize = false;
    }};
    
    // Listen for updates from Streamlit sliders
    const eventSource = new EventSource('streamlit');
    window.addEventListener('message', function(event) {{
        if (event.data.type === 'sliderUpdate_{annotation_key}') {{
            circle.x = event.data.x;
            circle.y = event.data.y;
            circle.r = event.data.r;
            draw();
        }}
    }});
    
    // Initial draw
    img.onload = function() {{
        draw();
    }};
    
    // Send updates from canvas to Streamlit
    setInterval(function() {{
        window.parent.postMessage({{
            type: 'currentPosition_{annotation_key}',
            x: circle.x,
            y: circle.y,
            r: circle.r
        }}, '*');
    }}, 100);
    </script>
    </body>
    </html>
    '''
    
    # Display the interactive canvas
    st.components.v1.html(html_code, height=450)
    
    # JavaScript to update sliders when circle is dragged
    st.markdown(f'''
    <script>
    // Update Streamlit when circle is dragged
    window.addEventListener('message', function(event) {{
        if (event.data.type === 'updatePosition_{annotation_key}') {{
            // Update URL to trigger Streamlit update
            var url = new URL(window.location);
            url.searchParams.set('update_x_{annotation_key}', event.data.x);
            url.searchParams.set('update_y_{annotation_key}', event.data.y);
            window.history.pushState({{}}, '', url);
            window.location.reload();
        }}
        
        if (event.data.type === 'updateRadius_{annotation_key}') {{
            var url = new URL(window.location);
            url.searchParams.set('update_r_{annotation_key}', event.data.r);
            window.history.pushState({{}}, '', url);
            window.location.reload();
        }}
    }}, false);
    </script>
    ''', unsafe_allow_html=True)
    
    # Check for updates from JavaScript
    params = st.query_params
    
    update_x_key = f'update_x_{annotation_key}'
    update_y_key = f'update_y_{annotation_key}'
    update_r_key = f'update_r_{annotation_key}'
    
    if update_x_key in params and update_y_key in params:
        try:
            st.session_state.annotation_data[annotation_key]['circle_x'] = int(params[update_x_key])
            st.session_state.annotation_data[annotation_key]['circle_y'] = int(params[update_y_key])
            st.query_params.clear()
            st.rerun()
        except:
            pass
    
    if update_r_key in params:
        try:
            st.session_state.annotation_data[annotation_key]['circle_r'] = int(params[update_r_key])
            st.query_params.clear()
            st.rerun()
        except:
            pass

def render_photos_of_faults_ui():
    """Render Photos of Faults UI for QC Manager to add defect containers with images and annotation"""
    st.markdown(f"### {t('photos_of_faults')}")
    
    # Create new defect container
    with st.expander(t("create_new_defect_container"), expanded=False):
        col1, col2 = st.columns([3, 2])
        with col1:
            new_container_name = st.text_input(t("container_name"), key="new_container_name")
        with col2:
            new_container_severity = st.selectbox(
                t("defect_severity"),
                ['minor', 'major', 'critical'],
                format_func=lambda x: t(x.upper()),
                key="new_container_severity"
            )
        
        # Upload multiple images for this container
        uploaded_files = st.file_uploader(
            t("upload_defect_image"),
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="new_container_upload"
        )
        
        if st.button(t("add_defect_container"), key="add_container"):
            if new_container_name.strip() and uploaded_files:
                # Create container with resized images
                container_images = []
                for uploaded_file in uploaded_files:
                    image_bytes = uploaded_file.getvalue()
                    # Resize image for PDF (1 inch max dimensions)
                    resized_image = resize_image_for_pdf(image_bytes)
                    container_images.append(resized_image)
                
                # Add container to session state
                container = {
                    'name': new_container_name.strip(),
                    'severity': new_container_severity,
                    'images': container_images
                }
                st.session_state.qc_defect_containers.append(container)
                st.success(f"Container created: {new_container_name.strip()} with {len(container_images)} images")
                st.rerun()
            elif new_container_name.strip():
                st.warning("Please upload at least one image for the defect")
            else:
                st.warning("Please enter a container name")
    
    # Display existing containers
    if st.session_state.qc_defect_containers:
        for idx, container in enumerate(st.session_state.qc_defect_containers):
            severity_class = container['severity']
            
            st.markdown(f'<div class="defect-container {severity_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{container['name']}** - {t(container['severity'].upper())}")
            with col2:
                if st.button(f"❌ Remove", key=f"remove_container_{idx}"):
                    st.session_state.qc_defect_containers.pop(idx)
                    st.rerun()
            
            # Display images in this container with annotation option
            st.markdown(f"**{t('defect_images')}:**")
            if container['images']:
                # Create tabs for each image in this container
                image_tabs = st.tabs([f"Image {i+1}" for i in range(len(container['images']))])
                
                for img_idx, img_bytes in enumerate(container['images']):
                    with image_tabs[img_idx]:
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            # Display the image
                            img = Image.open(io.BytesIO(img_bytes))
                            st.image(img, use_container_width=True, caption=f"Image {img_idx+1}")
                        
                        with col2:
                            # Add annotation button
                            if st.button(f"🎯 {t('annotate_image')}", key=f"annotate_btn_{idx}_{img_idx}"):
                                # Store current container and image index for annotation
                                st.session_state.current_annotation = {
                                    'container_idx': idx,
                                    'img_idx': img_idx,
                                    'container_name': container['name']
                                }
                                st.rerun()
                            
                            # Add more images to this container
                            more_files = st.file_uploader(
                                f"Add more images to {container['name']}",
                                type=['png', 'jpg', 'jpeg'],
                                accept_multiple_files=True,
                                key=f"add_more_{idx}_{img_idx}"
                            )
                            
                            if more_files:
                                for uploaded_file in more_files:
                                    new_image_bytes = uploaded_file.getvalue()
                                    # Resize new image
                                    resized_image = resize_image_for_pdf(new_image_bytes)
                                    container['images'].append(resized_image)
                                    st.success(f"Image added to {container['name']}")
                                    st.rerun()
                            
                            # Remove image button
                            if st.button(f"❌ {t('remove_image')}", key=f"remove_img_{idx}_{img_idx}"):
                                container['images'].pop(img_idx)
                                st.rerun()
            else:
                st.info(t("no_images_uploaded"))
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No defect containers created yet. Create one above to add defect images.")
    
    # Render annotation interface if an image is selected for annotation
    if 'current_annotation' in st.session_state:
        annotation_data = st.session_state.current_annotation
        container_idx = annotation_data['container_idx']
        img_idx = annotation_data['img_idx']
        container_name = annotation_data['container_name']
        
        container = st.session_state.qc_defect_containers[container_idx]
        image_bytes = container['images'][img_idx]
        
        st.markdown("---")
        st.markdown(f"### 🎯 {t('annotate_image')}: {container_name} - Image {img_idx+1}")
        
        # Annotation interface
        render_image_annotation_interface(container_idx, img_idx, image_bytes, container_name)
        
        # Close annotation button
        if st.button("Close Annotation", key="close_annotation"):
            del st.session_state.current_annotation
            st.rerun()

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
    
    # Render QC problem table UI (editable)
    render_problem_table_ui("qc")
    
    # Photos of Faults - QC Manager ONLY with annotation
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
            ""', unsafe_allow_html=True)
    
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