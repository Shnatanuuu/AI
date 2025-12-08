import streamlit as st
import openai
import base64
from PIL import Image
import io
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import hashlib

load_dotenv()

st.set_page_config(
    page_title="AI Shoe QC Inspector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Language configurations
LANGUAGES = {
    "English": {"code": "en", "flag": "🇺🇸", "label": "English"},
    "Mandarin": {"code": "zh", "flag": "🇨🇳", "label": "普通话 (Mandarin)"},
    "Cantonese": {"code": "yue", "flag": "🇭🇰", "label": "廣東話 (Cantonese)"}
}

# Translation dictionary
TRANSLATIONS = {
    "English": {
        "app_title": "AI Footwear Quality Control Inspector",
        "order_info": "Order Information",
        "factory": "Factory",
        "quantity": "Quantity",
        "contract_number": "Contract Number",
        "customer": "Customer",
        "style_number": "Style Number",
        "color": "Color",
        "inspector": "Inspector Name",
        "inspection_date": "Inspection Date",
        "production_status": "Production Status",
        "cutting_finished": "Cutting Finished",
        "stitching_finished": "Stitching Finished",
        "lasting_finished": "Lasting Finished",
        "packing_finished": "Packing Finished",
        "items_used_inspection": "ITEMS USED DURING INSPECTION",
        "staples_nail_used": "Staples/Nail Used in Production",
        "quantity_checked": "Quantity Checked",
        "signatures": "Signatures",
        "manufacturer_signature": "Manufacturer Signature",
        "inspector_signature": "Inspector Signature",
        "start_inspection": "Start AI Quality Inspection",
        "ai_results": "AI Inspection Results",
        "qc_review": "QC Manager Review & Amendments",
        "critical_review": "Critical Defects Review",
        "major_review": "Major Defects Review",
        "minor_review": "Minor Defects Review",
        "add_defect": "Add Defect",
        "qc_notes": "QC Manager Notes",
        "save_notes": "Save QC Notes",
        "final_summary": "Final Inspection Summary",
        "generate_pdf": "Generate PDF Report",
        "language_preference": "Language Preference",
        "no_defects": "No defects",
        "critical": "Critical",
        "major": "Major",
        "minor": "Minor",
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
        "ai_defects_given": "DEFECTS GIVEN OUT BY AI",
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
        "visual_evidence": "Visual Evidence"
    },
    "Mandarin": {
        "app_title": "AI鞋类质量控制检查员",
        "order_info": "订单信息",
        "factory": "工厂",
        "quantity": "数量",
        "contract_number": "合同编号",
        "customer": "客户",
        "style_number": "款式编号",
        "color": "颜色",
        "inspector": "检查员姓名",
        "inspection_date": "检查日期",
        "production_status": "生产状态",
        "cutting_finished": "裁断完成",
        "stitching_finished": "缝制完成",
        "lasting_finished": "定型完成",
        "packing_finished": "包装完成",
        "items_used_inspection": "检查期间使用的物品",
        "staples_nail_used": "生产中使用的钉/钉",
        "quantity_checked": "检查数量",
        "signatures": "签名",
        "manufacturer_signature": "制造商签名",
        "inspector_signature": "检查员签名",
        "start_inspection": "开始AI质量检查",
        "ai_results": "AI检查结果",
        "qc_review": "质检经理审查和修改",
        "critical_review": "严重缺陷审查",
        "major_review": "主要缺陷审查",
        "minor_review": "次要缺陷审查",
        "add_defect": "添加缺陷",
        "qc_notes": "质检经理备注",
        "save_notes": "保存质检备注",
        "final_summary": "最终检查摘要",
        "generate_pdf": "生成PDF报告",
        "language_preference": "语言偏好",
        "no_defects": "无缺陷",
        "critical": "严重",
        "major": "主要",
        "minor": "次要",
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
        "ai_defects_given": "AI给出的缺陷",
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
        "visual_evidence": "视觉证据"
    },
    "Cantonese": {
        "app_title": "AI鞋類質量控制檢查員",
        "order_info": "訂單信息",
        "factory": "工廠",
        "quantity": "數量",
        "contract_number": "合同編號",
        "customer": "客戶",
        "style_number": "款式編號",
        "color": "顏色",
        "inspector": "檢查員姓名",
        "inspection_date": "檢查日期",
        "production_status": "生產狀態",
        "cutting_finished": "裁斷完成",
        "stitching_finished": "縫製完成",
        "lasting_finished": "定型完成",
        "packing_finished": "包裝完成",
        "items_used_inspection": "檢查期間使用的物品",
        "staples_nail_used": "生產中使用的釘/釘",
        "quantity_checked": "檢查數量",
        "signatures": "簽名",
        "manufacturer_signature": "製造商簽名",
        "inspector_signature": "檢查員簽名",
        "start_inspection": "開始AI質量檢查",
        "ai_results": "AI檢查結果",
        "qc_review": "質檢經理審查和修改",
        "critical_review": "嚴重缺陷審查",
        "major_review": "主要缺陷審查",
        "minor_review": "次要缺陷審查",
        "add_defect": "添加缺陷",
        "qc_notes": "質檢經理備註",
        "save_notes": "保存質檢備註",
        "final_summary": "最終檢查摘要",
        "generate_pdf": "生成PDF報告",
        "language_preference": "語言偏好",
        "no_defects": "無缺陷",
        "critical": "嚴重",
        "major": "主要",
        "minor": "次要",
        "image_upload": "上傳檢查圖像",
        "upload_images": "上傳4張圖片(任意順序)",
        "view_ai_defects": "查看AI檢測到的缺陷",
        "type_defect": "輸入缺陷描述:",
        "enter_defect": "輸入缺陷...",
        "add_text": "添加",
        "defect_added": "缺陷已添加!",
        "additional_notes": "附加備註:",
        "notes_saved": "備註已保存!",
        "from_ai": "來自AI",
        "final_qc_decision": "最終質檢決定",
        "pdf_language_info": "PDF將生成為:",
        "download_pdf": "下載PDF",
        "pdf_ready": "PDF已準備好!",
        "pdf_failed": "PDF生成失敗",
        "generating_pdf": "正在生成多語言PDF...",
        "analyzing": "正在分析圖像...",
        "defects_found": "發現的缺陷",
        "overall_assessment": "整體評估",
        "ai_confidence": "AI置信度",
        "ai_defects_given": "AI給出的缺陷",
        "record_audio": "🎤 錄製音頻",
        "type_text": "📝 輸入文本",
        "start_recording": "🎤 開始錄製",
        "stop_recording": "⏹️ 停止錄製",
        "new_recording_captured": "新錄製已捕獲",
        "transcribing": "正在轉錄您的語音...",
        "transcription_complete": "轉錄完成！",
        "speak_clearly": "清晰說話3-10秒",
        "audio_too_short": "音頻似乎太短。請至少錄製2-3秒。",
        "no_text_transcribed": "沒有轉錄到文本。請大聲清晰地說話。",
        "use_voice_input": "使用語音輸入",
        "use_text_input": "使用文本輸入",
        "transcribed_text": "轉錄文本:",
        "click_to_record": "點擊下方按鈕錄製音頻",
        "edit_defect": "✏️ 編輯",
        "save_edit": "💾 保存",
        "cancel_edit": "❌ 取消",
        "edit_defect_prompt": "編輯缺陷描述:",
        "defect_image": "缺陷圖像",
        "visual_evidence": "視覺證據"
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

# Editing state
if 'editing_defect' not in st.session_state:
    st.session_state.editing_defect = None  # (category, defect_id)
if 'edit_text' not in st.session_state:
    st.session_state.edit_text = ""

# Production status storage
if 'production_status' not in st.session_state:
    st.session_state.production_status = {
        'cutting_finished': '',
        'stitching_finished': '',
        'lasting_finished': '',
        'packing_finished': ''
    }

# Items used during inspection storage
if 'inspection_items' not in st.session_state:
    st.session_state.inspection_items = {
        'staples_nail_used': '',
        'quantity_checked': ''
    }

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

def t(key):
    """Translation helper for UI elements"""
    return TRANSLATIONS[st.session_state.ui_language].get(key, key)

# Enhanced CSS for mobile responsiveness and better visibility
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .main .block-container {
        font-family: 'Inter', sans-serif;
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
    }
    
    .production-section {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
    }
    
    .inspection-section {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
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
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid rgba(226, 232, 240, 0.8);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 1rem;
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
        .section-header, .production-section, .inspection-section, .signature-section { 
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
    }
    
    .metric-number { 
        font-size: 2.5rem; 
        font-weight: 800; 
        margin-bottom: 0.25rem; 
    }
    .metric-label { 
        font-size: 1.1rem; 
        font-weight: 600; 
        color: #374151; 
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
                        "cmn": "Mandarin",
                        "yue": "Cantonese"
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
        "Cantonese": "Traditional Chinese (Cantonese style)"
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
    
    aql_limits = {"critical": 0, "major": 10, "minor": 14}
    
    if len(final_critical) > aql_limits["critical"]:
        result, reason = "REJECT", f"Critical defects ({len(final_critical)}) - Zero tolerance"
    elif len(final_major) > aql_limits["major"]:
        result, reason = "REJECT", f"Major defects ({len(final_major)}) exceed limit"
    elif len(final_minor) > aql_limits["minor"]:
        result, reason = "REWORK", f"Minor defects ({len(final_minor)}) exceed limit"
    else:
        result, reason = "ACCEPT", "All defects within AQL 2.5 limits"
    
    return {
        "result": result,
        "reason": reason,
        "critical_count": len(final_critical),
        "major_count": len(final_major),
        "minor_count": len(final_minor),
        "aql_limits": aql_limits
    }

def calculate_final_decision():
    """Calculate final decision based on QC defects"""
    qc_critical_count = len(st.session_state.defect_store['qc_critical'])
    qc_major_count = len(st.session_state.defect_store['qc_major'])
    qc_minor_count = len(st.session_state.defect_store['qc_minor'])
    
    if qc_critical_count > 0:
        return "REJECT", f"Critical defects ({qc_critical_count}) - Zero tolerance"
    elif qc_major_count > 10:
        return "REJECT", f"Major defects ({qc_major_count}) exceed AQL limit (10)"
    elif qc_minor_count > 14:
        return "REWORK", f"Minor defects ({qc_minor_count}) exceed AQL limit (14)"
    else:
        return "ACCEPT", "All defects within AQL 2.5 limits"

# Define font helper functions at module level
def get_font_for_text(text, chinese_font=None):
    """Return appropriate font based on text content"""
    base_font = 'Helvetica'
    if chinese_font and any('\u4e00' <= char <= '\u9fff' for char in text):
        return chinese_font
    return base_font

def get_bold_font_for_text(text, chinese_font=None):
    """Return appropriate bold font based on text content"""
    bold_font = 'Helvetica-Bold'
    if chinese_font and any('\u4e00' <= char <= '\u9fff' for char in text):
        return chinese_font
    return bold_font

def add_defects_with_images(elements, title_key, defect_category, color_obj, language, styles, chinese_font=None):
    """Add defects to PDF with their corresponding images"""
    defects_list = st.session_state.defect_store[defect_category]
    
    if defects_list:
        title = translate_text_with_openai(title_key, language)
        title_font = get_bold_font_for_text(title, chinese_font)
        cat_style = ParagraphStyle('DefectCategory', parent=styles['Heading2'], fontSize=12, 
                                  alignment=TA_CENTER, fontName=title_font, spaceAfter=12)
        elements.append(Paragraph(title, cat_style))
        
        for i, (defect_id, english_text) in enumerate(defects_list, 1):
            # Create a table for each defect with image
            translated_defect = translate_text_with_openai(english_text, language)
            defect_font = get_font_for_text(translated_defect, chinese_font)
            
            # Look for matching defect image
            defect_image_buffer = None
            image_found = False
            
            for stored_id, img_data in st.session_state.defect_images.items():
                if (img_data['description'].lower() == english_text.lower() and 
                    img_data['category'] in defect_category):
                    defect_image_buffer = img_data['image_buffer']
                    image_found = True
                    break
            
            if defect_image_buffer and image_found:
                # Create table with defect text and image side by side
                try:
                    defect_image_buffer.seek(0)  # Reset buffer position
                    
                    # Create a 2-column table for defect + image
                    defect_table_data = []
                    
                    # Text column
                    defect_style = ParagraphStyle(f'defect{defect_id}', parent=styles['Normal'], 
                                                textColor=color_obj, fontSize=9, fontName=defect_font)
                    text_para = Paragraph(f"{i}. {translated_defect}", defect_style)
                    
                    # Image column with caption
                    img = ReportLabImage(defect_image_buffer, width=1.2*inch, height=1.0*inch)
                    img.hAlign = 'CENTER'
                    
                    # Create caption for image
                    caption_style = ParagraphStyle('Caption', parent=styles['Normal'], 
                                                 fontSize=7, alignment=TA_CENTER, textColor=colors.gray)
                    caption = Paragraph(t("defect_image"), caption_style)
                    
                    # Stack image and caption vertically
                    image_elements = [img, Spacer(1, 2), caption]
                    
                    defect_table_data = [[text_para, image_elements]]
                    
                    defect_table = Table(defect_table_data, colWidths=[4.0*inch, 1.5*inch])
                    defect_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 5),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ]))
                    
                    elements.append(defect_table)
                    
                except Exception as e:
                    # Fallback: just text if image fails
                    st.warning(f"Image processing failed for defect {i}: {str(e)}")
                    defect_style = ParagraphStyle(f'defect{defect_id}', parent=styles['Normal'], 
                                                textColor=color_obj, fontSize=9, fontName=defect_font,
                                                leftIndent=15)
                    elements.append(Paragraph(f"{i}. {translated_defect}", defect_style))
            else:
                # No image available, just text
                defect_style = ParagraphStyle(f'defect{defect_id}', parent=styles['Normal'], 
                                            textColor=color_obj, fontSize=9, fontName=defect_font,
                                            leftIndent=15)
                elements.append(Paragraph(f"{i}. {translated_defect}", defect_style))
            
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 10))

def generate_multilingual_pdf(order_info, language):
    """Generate PDF with defect images and proper multilingual support"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                               topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        styles = getSampleStyleSheet()
        
        # Use standard fonts for English text in all languages
        base_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'
        chinese_font = None
        
        # Only use Chinese fonts for actual Chinese characters
        if language in ["Mandarin", "Cantonese"]:
            try:
                from reportlab.pdfbase.cidfonts import UnicodeCIDFont
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                chinese_font = 'STSong-Light'
            except:
                pass
        
        brand_blue = colors.Color(0.4, 0.49, 0.91)
        success_green = colors.Color(0.31, 0.78, 0.47)
        warning_orange = colors.Color(1.0, 0.6, 0.0)
        danger_red = colors.Color(1.0, 0.42, 0.42)
        light_gray = colors.Color(0.97, 0.97, 0.97)
        production_blue = colors.Color(0.31, 0.66, 0.95)
        inspection_green = colors.Color(0.26, 0.75, 0.59)
        signature_pink = colors.Color(0.98, 0.44, 0.62)
        
        # Styles
        title_style = ParagraphStyle('Title', parent=styles['Normal'], fontSize=22, alignment=TA_CENTER,
                                     textColor=brand_blue, fontName=bold_font, spaceAfter=12)
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER,
                                        textColor=colors.Color(0.3, 0.3, 0.3), fontName=base_font, spaceAfter=8)
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, spaceAfter=10,
                                      spaceBefore=15, textColor=brand_blue, fontName=bold_font, alignment=TA_CENTER)
        production_style = ParagraphStyle('Production', parent=styles['Heading2'], fontSize=14, spaceAfter=10,
                                         spaceBefore=15, textColor=production_blue, fontName=bold_font, alignment=TA_CENTER)
        inspection_style = ParagraphStyle('Inspection', parent=styles['Heading2'], fontSize=14, spaceAfter=10,
                                         spaceBefore=15, textColor=inspection_green, fontName=bold_font, alignment=TA_CENTER)
        signature_style = ParagraphStyle('Signature', parent=styles['Heading2'], fontSize=14, spaceAfter=10,
                                        spaceBefore=15, textColor=signature_pink, fontName=bold_font, alignment=TA_CENTER)
        
        # Header
        elements.append(Paragraph("GRAND STEP (H.K.) LTD", title_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Professional Footwear Manufacturing &amp; Quality Control", subtitle_style))
        elements.append(Paragraph("AI-Powered Quality Inspection System", subtitle_style))
        elements.append(Spacer(1, 20))
        
        # Title
        title_text = translate_text_with_openai("QUALITY CONTROL INSPECTION REPORT", language)
        # Use appropriate font for title
        report_title = ParagraphStyle('ReportTitle', parent=title_style, fontSize=16, 
                                      textColor=colors.black, fontName=get_bold_font_for_text(title_text, chinese_font))
        elements.append(Paragraph(title_text, report_title))
        elements.append(Spacer(1, 20))
        
        # Final Decision
        final_result, final_reason = calculate_final_decision()
        result_text = translate_text_with_openai(final_result, language)
        result_color = success_green if final_result=='ACCEPT' else (danger_red if final_result=='REJECT' else warning_orange)
        
        result_style = ParagraphStyle('Result', parent=styles['Normal'], fontSize=18, alignment=TA_CENTER,
                                     fontName=get_bold_font_for_text(result_text, chinese_font), spaceAfter=10, textColor=result_color)
        
        final_label = translate_text_with_openai("FINAL QC DECISION", language)
        elements.append(Paragraph(f"{final_label}: {result_text}", result_style))
        
        rationale_text = translate_text_with_openai(final_reason, language)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=6,
                                    fontName=get_font_for_text(rationale_text, chinese_font), textColor=colors.black)
        elements.append(Paragraph(rationale_text, body_style))
        elements.append(Spacer(1, 20))
        
        # Order Information
        order_label = translate_text_with_openai("ORDER INFORMATION", language)
        order_section_style = ParagraphStyle('OrderSection', parent=section_style, 
                                            fontName=get_bold_font_for_text(order_label, chinese_font))
        elements.append(Paragraph(order_label, order_section_style))
        elements.append(Spacer(1, 10))
        
        order_data = [
            [translate_text_with_openai('Contract Number', language), order_info['contract_number']],
            [translate_text_with_openai('Factory', language), order_info['factory']],
            [translate_text_with_openai('Quantity', language), order_info['quantity']],
            [translate_text_with_openai('Style', language), order_info['style_number']],
            [translate_text_with_openai('Color', language), order_info['color']],
            [translate_text_with_openai('Customer', language), order_info['customer']],
            [translate_text_with_openai('Inspector', language), order_info['inspector']],
            [translate_text_with_openai('Date', language), order_info['inspection_date']],
            [translate_text_with_openai('Standard', language), "AQL 2.5"]
        ]
        
        order_table = Table(order_data, colWidths=[5*cm, 9*cm])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), brand_blue),
            ('TEXTCOLOR', (0,0), (0,-1), colors.white),
            ('BACKGROUND', (1,0), (1,-1), light_gray),
            ('FONTNAME', (0,0), (0,-1), base_font if not chinese_font else chinese_font),
            ('FONTNAME', (1,0), (1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(order_table)
        elements.append(Spacer(1, 25))
        
        # Production Status
        production_label = translate_text_with_openai("PRODUCTION STATUS", language)
        prod_section_style = ParagraphStyle('ProdSection', parent=production_style,
                                           fontName=get_bold_font_for_text(production_label, chinese_font))
        elements.append(Paragraph(production_label, prod_section_style))
        elements.append(Spacer(1, 10))
        
        production_data = [
            [translate_text_with_openai('Cutting Finished', language), st.session_state.production_status['cutting_finished']],
            [translate_text_with_openai('Stitching Finished', language), st.session_state.production_status['stitching_finished']],
            [translate_text_with_openai('Lasting Finished', language), st.session_state.production_status['lasting_finished']],
            [translate_text_with_openai('Packing Finished', language), st.session_state.production_status['packing_finished']]
        ]
        
        production_table = Table(production_data, colWidths=[5*cm, 9*cm])
        production_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), production_blue),
            ('TEXTCOLOR', (0,0), (0,-1), colors.white),
            ('BACKGROUND', (1,0), (1,-1), colors.Color(0.9, 0.95, 1.0)),
            ('FONTNAME', (0,0), (0,-1), base_font if not chinese_font else chinese_font),
            ('FONTNAME', (1,0), (1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(production_table)
        elements.append(Spacer(1, 25))
        
        # Items Used During Inspection
        inspection_label = translate_text_with_openai("ITEMS USED DURING INSPECTION", language)
        insp_section_style = ParagraphStyle('InspSection', parent=inspection_style,
                                           fontName=get_bold_font_for_text(inspection_label, chinese_font))
        elements.append(Paragraph(inspection_label, insp_section_style))
        elements.append(Spacer(1, 10))
        
        inspection_data = [
            [translate_text_with_openai('Staples/Nail Used in Production', language), st.session_state.inspection_items['staples_nail_used']],
            [translate_text_with_openai('Quantity Checked', language), st.session_state.inspection_items['quantity_checked']]
        ]
        
        inspection_table = Table(inspection_data, colWidths=[5*cm, 9*cm])
        inspection_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), inspection_green),
            ('TEXTCOLOR', (0,0), (0,-1), colors.white),
            ('BACKGROUND', (1,0), (1,-1), colors.Color(0.9, 1.0, 0.95)),
            ('FONTNAME', (0,0), (0,-1), base_font if not chinese_font else chinese_font),
            ('FONTNAME', (1,0), (1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(inspection_table)
        elements.append(Spacer(1, 25))
        
        # AI Inspection Findings
        ai_label = translate_text_with_openai("AI INSPECTION FINDINGS", language)
        ai_section_style = ParagraphStyle('AISection', parent=section_style,
                                         fontName=get_bold_font_for_text(ai_label, chinese_font))
        elements.append(Paragraph(ai_label, ai_section_style))
        elements.append(Spacer(1, 10))
        
        ai_critical_count = len(st.session_state.defect_store['ai_critical'])
        ai_major_count = len(st.session_state.defect_store['ai_major'])
        ai_minor_count = len(st.session_state.defect_store['ai_minor'])
        
        ai_data = [
            [translate_text_with_openai('Defect Type', language), 
             translate_text_with_openai('AI Count', language), 
             translate_text_with_openai('AQL Limit', language), 
             translate_text_with_openai('Status', language)],
            [translate_text_with_openai('Critical', language), 
             str(ai_critical_count), '0',
             translate_text_with_openai('FAIL' if ai_critical_count>0 else 'PASS', language)],
            [translate_text_with_openai('Major', language), 
             str(ai_major_count), '10',
             translate_text_with_openai('FAIL' if ai_major_count>10 else 'PASS', language)],
            [translate_text_with_openai('Minor', language), 
             str(ai_minor_count), '14',
             translate_text_with_openai('FAIL' if ai_minor_count>14 else 'PASS', language)]
        ]
        
        ai_table = Table(ai_data, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        ai_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.Color(0.6, 0.7, 0.9)),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), base_font if not chinese_font else chinese_font),
            ('FONTNAME', (0,1), (-1,-1), base_font if not chinese_font else chinese_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(ai_table)
        elements.append(Spacer(1, 20))
        
        # DEFECTS GIVEN OUT BY AI - WITH IMAGES
        ai_defects_label = translate_text_with_openai("DEFECTS GIVEN OUT BY AI", language)
        ai_def_section_style = ParagraphStyle('AIDefSection', parent=section_style,
                                             fontName=get_bold_font_for_text(ai_defects_label, chinese_font))
        elements.append(Paragraph(ai_defects_label, ai_def_section_style))
        elements.append(Spacer(1, 10))
        
        # Add AI defects with images
        add_defects_with_images(elements, "CRITICAL DEFECTS (AI)", 'ai_critical', danger_red, language, styles, chinese_font)
        add_defects_with_images(elements, "MAJOR DEFECTS (AI)", 'ai_major', warning_orange, language, styles, chinese_font)
        add_defects_with_images(elements, "MINOR DEFECTS (AI)", 'ai_minor', brand_blue, language, styles, chinese_font)
        
        elements.append(Spacer(1, 15))
        
        # QC MANAGER REVIEW & AMENDMENTS
        qc_label = translate_text_with_openai("QC MANAGER REVIEW & AMENDMENTS", language)
        qc_section_style = ParagraphStyle('QCSection', parent=section_style,
                                         fontName=get_bold_font_for_text(qc_label, chinese_font))
        
        qc_critical_count = len(st.session_state.defect_store['qc_critical'])
        qc_major_count = len(st.session_state.defect_store['qc_major'])
        qc_minor_count = len(st.session_state.defect_store['qc_minor'])
        
        crit_change = qc_critical_count - ai_critical_count
        maj_change = qc_major_count - ai_major_count
        min_change = qc_minor_count - ai_minor_count
        
        qc_data = [
            [translate_text_with_openai('Defect Type', language),
             translate_text_with_openai('AI Count', language),
             translate_text_with_openai('QC Final', language),
             translate_text_with_openai('Change', language),
             translate_text_with_openai('Status', language)],
            [translate_text_with_openai('Critical', language),
             str(ai_critical_count),
             str(qc_critical_count),
             f"{crit_change:+d}" if crit_change != 0 else "0",
             translate_text_with_openai('FAIL' if qc_critical_count>0 else 'PASS', language)],
            [translate_text_with_openai('Major', language),
             str(ai_major_count),
             str(qc_major_count),
             f"{maj_change:+d}" if maj_change != 0 else "0",
             translate_text_with_openai('FAIL' if qc_major_count>10 else 'PASS', language)],
            [translate_text_with_openai('Minor', language),
             str(ai_minor_count),
             str(qc_minor_count),
             f"{min_change:+d}" if min_change != 0 else "0",
             translate_text_with_openai('FAIL' if qc_minor_count>14 else 'PASS', language)]
        ]
        
        qc_table = Table(qc_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3*cm])
        qc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), warning_orange),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), base_font if not chinese_font else chinese_font),
            ('FONTNAME', (0,1), (-1,-1), base_font if not chinese_font else chinese_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0),(-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        
        elements.append(Paragraph(qc_label, qc_section_style))
        elements.append(Spacer(1, 10))
        elements.append(qc_table)
        elements.append(Spacer(1, 20))
        
        # FINAL DEFECTS - WITH IMAGES
        add_defects_with_images(elements, "CRITICAL DEFECTS (FINAL)", 'qc_critical', danger_red, language, styles, chinese_font)
        add_defects_with_images(elements, "MAJOR DEFECTS (FINAL)", 'qc_major', warning_orange, language, styles, chinese_font)
        add_defects_with_images(elements, "MINOR DEFECTS (FINAL)", 'qc_minor', brand_blue, language, styles, chinese_font)
        
        if st.session_state.qc_notes_english and st.session_state.qc_notes_english.strip():
            notes_label = translate_text_with_openai("QC MANAGER NOTES", language)
            notes_font = get_bold_font_for_text(notes_label, chinese_font)
            notes_section_style = ParagraphStyle('NotesSection', parent=section_style, fontName=notes_font)
            elements.append(Paragraph(notes_label, notes_section_style))
            notes_text = translate_text_with_openai(st.session_state.qc_notes_english, language)
            notes_font_text = get_font_for_text(notes_text, chinese_font)
            notes_body_style = ParagraphStyle('NotesBody', parent=styles['Normal'], fontSize=10,
                                             fontName=notes_font_text)
            elements.append(Paragraph(notes_text, notes_body_style))
        
        # SIGNATURES SECTION
        signature_label = translate_text_with_openai("SIGNATURES", language)
        sig_section_style = ParagraphStyle('SigSection', parent=signature_style,
                                          fontName=get_bold_font_for_text(signature_label, chinese_font))
        
        signature_data = [
            [translate_text_with_openai('Manufacturer Signature', language), "_________________________"],
            [translate_text_with_openai('Inspector Signature', language), "_________________________"]
        ]
        
        signature_table = Table(signature_data, colWidths=[5*cm, 9*cm])
        signature_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), signature_pink),
            ('TEXTCOLOR', (0,0), (0,-1), colors.white),
            ('BACKGROUND', (1,0), (1,-1), colors.Color(1.0, 0.95, 0.98)),
            ('FONTNAME', (0,0), (0,-1), base_font if not chinese_font else chinese_font),
            ('FONTNAME', (1,0), (1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        
        elements.append(Paragraph(signature_label, sig_section_style))
        elements.append(Spacer(1, 15))
        elements.append(signature_table)
        
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

# Language Selector in Sidebar
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
    quantity = st.text_input(t("quantity"), value="1000")
    color = st.text_input(t("color"), value="PPB")
with col3:
    inspector = st.text_input(t("inspector"), value="XI")
    inspection_date = st.date_input(t("inspection_date"), value=datetime.now().date())

# Production Status Section
st.markdown(f'<div class="production-section">{t("production_status")}</div>', unsafe_allow_html=True)

prod_col1, prod_col2, prod_col3, prod_col4 = st.columns(4)
with prod_col1:
    st.session_state.production_status['cutting_finished'] = st.text_input(t("cutting_finished"), value="100", key="cutting_input")
with prod_col2:
    st.session_state.production_status['stitching_finished'] = st.text_input(t("stitching_finished"), value="100", key="stitching_input")
with prod_col3:
    st.session_state.production_status['lasting_finished'] = st.text_input(t("lasting_finished"), value="200", key="lasting_input")
with prod_col4:
    st.session_state.production_status['packing_finished'] = st.text_input(t("packing_finished"), value="100", key="packing_input")

# Items Used During Inspection Section
st.markdown(f'<div class="inspection-section">{t("items_used_inspection")}</div>', unsafe_allow_html=True)

insp_col1, insp_col2 = st.columns(2)
with insp_col1:
    st.session_state.inspection_items['staples_nail_used'] = st.text_input(t("staples_nail_used"), value="NO", key="staples_input")
with insp_col2:
    st.session_state.inspection_items['quantity_checked'] = st.text_input(t("quantity_checked"), value="ON LINE", key="quantity_checked_input")

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
            "quantity": quantity,
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