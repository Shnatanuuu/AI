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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

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

# Translation dictionary - UPDATED with new fields
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
        "image_upload": "Sequential Image Upload",
        "upload_images": "Upload 4 images",
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
        "ai_defects_given": "DEFECTS GIVEN OUT BY AI"
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
        "image_upload": "顺序图像上传",
        "upload_images": "上传4张图片",
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
        "ai_defects_given": "AI给出的缺陷"
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
        "image_upload": "順序圖像上傳",
        "upload_images": "上傳4張圖片",
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
        "ai_defects_given": "AI給出的缺陷"
    }
}

# Initialize session state
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "English"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "English"

# Core defect storage - always in English with unique IDs
if 'defect_store' not in st.session_state:
    st.session_state.defect_store = {
        'ai_critical': [],
        'ai_major': [],
        'ai_minor': [],
        'qc_critical': [],
        'qc_major': [],
        'qc_minor': []
    }

# NEW: Production status storage
if 'production_status' not in st.session_state:
    st.session_state.production_status = {
        'cutting_finished': '',
        'stitching_finished': '',
        'lasting_finished': '',
        'packing_finished': ''
    }

# NEW: Items used during inspection storage
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

def t(key):
    """Translation helper for UI elements"""
    return TRANSLATIONS[st.session_state.ui_language].get(key, key)

# CSS Styling - UPDATED with new styles
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
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .defect-item {
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid;
        background: white;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        color: #1f2937 !important;
        font-weight: 500;
    }
    
    .critical-defect { 
        border-left-color: #ef4444; 
        background: #fef2f2; 
        color: #991b1b !important;
    }
    .major-defect { 
        border-left-color: #f59e0b; 
        background: #fffbeb; 
        color: #92400e !important;
    }
    .minor-defect { 
        border-left-color: #3b82f6; 
        background: #eff6ff; 
        color: #1e40af !important;
    }
    
    .production-item {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.25rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .inspection-item {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.25rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    @media (max-width: 768px) {
        .main .block-container { padding: 0.5rem; }
        .hero-section { padding: 1.5rem 0.5rem; }
        .section-header { padding: 0.75rem; font-size: 1rem; }
        .metric-card { padding: 0.75rem; }
        .metric-number { font-size: 1.5rem !important; }
        .defect-item { padding: 0.5rem; font-size: 0.9rem; }
    }
    
    .metric-number { font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem; }
    .metric-label { font-size: 1rem; font-weight: 600; color: #374151; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OpenAI API key not found.")
        st.stop()
    return openai.OpenAI(api_key=api_key)

client = get_openai_client()

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

def encode_image(image):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

def analyze_shoe_image(client, image, angle_name, style_number="", color="", contract_number=""):
    """Analyze image - always returns defects in English with no duplicates across categories"""
    base64_image = encode_image(image)
    
    prompt = f"""You are an expert footwear QC inspector analyzing {angle_name} view.
Product: {style_number}, Color: {color}, Contract: {contract_number}

INSPECTION PROTOCOL:
1. First scan the overall construction and proportion
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
- Major Adhesive residue or excess glue visible
- Color variation outside acceptable tolerance
Dont repeat the defects which are already mentioned in minor defects and also make sure the defects in major defects are unique

MINOR DEFECT CATEGORIES (Count but typically acceptable):
- Minor sole defects, uneven texturing
Dont repeat the defects which are already mentioned in major defects and also make sure the defects in minor defects are unique

CRITICAL RULES FOR DEFECT CATEGORIZATION:
1. Each defect must appear in ONLY ONE category - never duplicate across critical, major, and minor
2. Use consistent terminology for similar defects (e.g., always use "strap edge - fraying" not variations)
3. Group similar observations together rather than listing duplicates
4. Be specific about location and defect type with precise measurements
5. If you see the same defect type in multiple areas, list them as separate entries only if they are actually different instances
6. Use standardized defect descriptions: "[location] - [defect type] [measurement if applicable]"
7. NEVER list the same defect type in multiple categories (e.g., if "upper material - scuff marks" is in major, it cannot appear in minor)

Return ONLY valid JSON in English:
{{
    "angle": "{angle_name}",
    "critical_defects": ["exact location + defect type + measurement"],
    "major_defects": ["exact location + defect type + measurement"], 
    "minor_defects": ["exact location + defect type + measurement"],
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
            max_tokens=1000,
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        
        if start != -1 and end > start:
            return json.loads(result_text[start:end])
        
        return {
            "angle": angle_name, "critical_defects": [], "major_defects": [], "minor_defects": [], 
            "overall_condition": "Fair", "confidence": "Low", "inspection_notes": "Parse failed"
        }
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return None

def normalize_defect_description(defect):
    """Normalize defect descriptions to remove variations and enable better duplicate detection"""
    if not defect:
        return defect
    
    # Convert to lowercase for comparison
    normalized = defect.lower().strip()
    
    # Remove extra spaces and standardize formatting
    normalized = ' '.join(normalized.split())
    
    # Standardize common terms
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
    """Generate initial AI report from analyses - ensure no duplicate defects across categories"""
    all_critical, all_major, all_minor = [], [], []
    
    for analysis in analyses:
        if analysis:
            # Remove duplicates within each analysis first
            critical_defects = list(dict.fromkeys(analysis.get('critical_defects', [])))
            major_defects = list(dict.fromkeys(analysis.get('major_defects', [])))
            minor_defects = list(dict.fromkeys(analysis.get('minor_defects', [])))
            
            all_critical.extend(critical_defects)
            all_major.extend(major_defects)
            all_minor.extend(minor_defects)
    
    # Remove duplicates across all analyses
    all_critical = list(dict.fromkeys(all_critical))
    all_major = list(dict.fromkeys(all_major))
    all_minor = list(dict.fromkeys(all_minor))
    
    # Create normalized versions for cross-category duplicate detection
    normalized_critical = [normalize_defect_description(d) for d in all_critical]
    normalized_major = [normalize_defect_description(d) for d in all_major]
    normalized_minor = [normalize_defect_description(d) for d in all_minor]
    
    # Remove duplicates across categories - priority: Critical > Major > Minor
    final_major = []
    final_minor = []
    
    # Remove from major if similar defect exists in critical
    for i, major_defect in enumerate(all_major):
        norm_major = normalized_major[i]
        if not any(norm_critical in norm_major or norm_major in norm_critical 
                  for norm_critical in normalized_critical):
            final_major.append(major_defect)
    
    # Remove from minor if similar defect exists in critical or major
    for i, minor_defect in enumerate(all_minor):
        norm_minor = normalized_minor[i]
        critical_match = any(norm_critical in norm_minor or norm_minor in norm_critical 
                           for norm_critical in normalized_critical)
        major_match = any(norm_major in norm_minor or norm_minor in norm_major 
                        for norm_major in [normalized_major[j] for j, d in enumerate(all_major) if d in final_major])
        
        if not critical_match and not major_match:
            final_minor.append(minor_defect)
    
    # Final cleanup - ensure no duplicates remain
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

def generate_multilingual_pdf(order_info, language):
    """Generate PDF with proper multilingual support and AI defects section"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                               topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        styles = getSampleStyleSheet()
        
        base_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'
        
        if language in ["Mandarin", "Cantonese"]:
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                base_font = 'STSong-Light'
                bold_font = 'STSong-Light'
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
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=6,
                                    fontName=base_font, textColor=colors.black)
        
        elements.append(Paragraph("GRAND STEP (H.K.) LTD", title_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Professional Footwear Manufacturing & Quality Control", subtitle_style))
        elements.append(Paragraph("AI-Powered Quality Inspection System", subtitle_style))
        elements.append(Spacer(1, 20))
        
        title_text = translate_text_with_openai("QUALITY CONTROL INSPECTION REPORT", language)
        report_title = ParagraphStyle('ReportTitle', parent=title_style, fontSize=16, textColor=colors.black)
        elements.append(Paragraph(title_text, report_title))
        elements.append(Spacer(1, 20))
        
        final_result, final_reason = calculate_final_decision()
        result_text = translate_text_with_openai(final_result, language)
        result_color = success_green if final_result=='ACCEPT' else (danger_red if final_result=='REJECT' else warning_orange)
        
        result_style = ParagraphStyle('Result', parent=styles['Normal'], fontSize=18, alignment=TA_CENTER,
                                     fontName=bold_font, spaceAfter=10, textColor=result_color)
        
        final_label = translate_text_with_openai("FINAL QC DECISION", language)
        elements.append(Paragraph(f"{final_label}: {result_text}", result_style))
        
        rationale_text = translate_text_with_openai(final_reason, language)
        elements.append(Paragraph(rationale_text, body_style))
        elements.append(Spacer(1, 20))
        
        order_label = translate_text_with_openai("ORDER INFORMATION", language)
        elements.append(Paragraph(order_label, section_style))
        elements.append(Spacer(1, 10))
        
        # UPDATED Order Information with new fields
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
            ('FONTNAME', (0,0), (-1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(order_table)
        elements.append(Spacer(1, 25))
        
        # NEW: Production Status Section
        production_label = translate_text_with_openai("PRODUCTION STATUS", language)
        elements.append(Paragraph(production_label, production_style))
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
            ('FONTNAME', (0,0), (-1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(production_table)
        elements.append(Spacer(1, 25))
        
        # NEW: Items Used During Inspection Section - MOVED BELOW PRODUCTION STATUS
        inspection_label = translate_text_with_openai("ITEMS USED DURING INSPECTION", language)
        elements.append(Paragraph(inspection_label, inspection_style))
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
            ('FONTNAME', (0,0), (-1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(inspection_table)
        elements.append(Spacer(1, 25))
        
        ai_label = translate_text_with_openai("AI INSPECTION FINDINGS", language)
        elements.append(Paragraph(ai_label, section_style))
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
            ('FONTNAME', (0,0), (-1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(ai_table)
        elements.append(Spacer(1, 20))
        
        # DEFECTS GIVEN OUT BY AI section
        ai_defects_label = translate_text_with_openai("DEFECTS GIVEN OUT BY AI", language)
        elements.append(Paragraph(ai_defects_label, section_style))
        elements.append(Spacer(1, 10))
        
        def add_ai_defects(title_key, defect_category, color_obj):
            defects_list = st.session_state.defect_store[defect_category]
            if defects_list:
                title = translate_text_with_openai(title_key, language)
                elements.append(Paragraph(title, ParagraphStyle('DefectCategory', parent=section_style, fontSize=12, alignment=TA_CENTER)))
                elements.append(Spacer(1, 6))
                for i, (defect_id, english_text) in enumerate(defects_list, 1):
                    translated_defect = translate_text_with_openai(english_text, language)
                    defect_style = ParagraphStyle(f'ai_defect{defect_id}', parent=body_style, 
                                                  leftIndent=15, textColor=color_obj, fontSize=9)
                    elements.append(Paragraph(f"{i}. {translated_defect}", defect_style))
                    elements.append(Spacer(1, 3))
                elements.append(Spacer(1, 8))
        
        add_ai_defects("CRITICAL DEFECTS (AI)", 'ai_critical', danger_red)
        add_ai_defects("MAJOR DEFECTS (AI)", 'ai_major', warning_orange)
        add_ai_defects("MINOR DEFECTS (AI)", 'ai_minor', brand_blue)
        
        elements.append(Spacer(1, 15))
        
        # QC MANAGER REVIEW & AMENDMENTS section
        qc_label = translate_text_with_openai("QC MANAGER REVIEW & AMENDMENTS", language)
        elements.append(Paragraph(qc_label, section_style))
        elements.append(Spacer(1, 10))
        
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
            ('FONTNAME', (0,0), (-1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0),(-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(qc_table)
        elements.append(Spacer(1, 20))
        
        def add_final_defects(title_key, defect_category, color_obj):
            defects_list = st.session_state.defect_store[defect_category]
            if defects_list:
                title = translate_text_with_openai(title_key, language)
                elements.append(Paragraph(title, section_style))
                elements.append(Spacer(1, 8))
                for i, (defect_id, english_text) in enumerate(defects_list, 1):
                    translated_defect = translate_text_with_openai(english_text, language)
                    defect_style = ParagraphStyle(f'defect{defect_id}', parent=body_style, 
                                                  leftIndent=15, textColor=color_obj, fontSize=10)
                    elements.append(Paragraph(f"{i}. {translated_defect}", defect_style))
                    elements.append(Spacer(1, 4))
                elements.append(Spacer(1, 10))
        
        add_final_defects("CRITICAL DEFECTS (FINAL)", 'qc_critical', danger_red)
        add_final_defects("MAJOR DEFECTS (FINAL)", 'qc_major', warning_orange)
        add_final_defects("MINOR DEFECTS (FINAL)", 'qc_minor', brand_blue)
        
        if st.session_state.qc_notes_english and st.session_state.qc_notes_english.strip():
            notes_label = translate_text_with_openai("QC MANAGER NOTES", language)
            elements.append(Paragraph(notes_label, section_style))
            notes_text = translate_text_with_openai(st.session_state.qc_notes_english, language)
            elements.append(Paragraph(notes_text, body_style))
        
        # NEW: Signatures Section
        signature_label = translate_text_with_openai("SIGNATURES", language)
        elements.append(Paragraph(signature_label, signature_style))
        elements.append(Spacer(1, 15))
        
        signature_data = [
            [translate_text_with_openai('Manufacturer Signature', language), "_________________________"],
            [translate_text_with_openai('Inspector Signature', language), "_________________________"]
        ]
        
        signature_table = Table(signature_data, colWidths=[5*cm, 9*cm])
        signature_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), signature_pink),
            ('TEXTCOLOR', (0,0), (0,-1), colors.white),
            ('BACKGROUND', (1,0), (1,-1), colors.Color(1.0, 0.95, 0.98)),
            ('FONTNAME', (0,0), (-1,-1), base_font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        elements.append(signature_table)
        
        doc.build(elements)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

def render_defect_input_section(defect_type, category_key):
    """Render text input section for adding defects"""
    st.markdown(f"**{t('add_defect')} ({t(defect_type)})**")
    
    text_input = st.text_input(
        t("type_defect"), 
        key=f"new_{category_key}_text", 
        placeholder=t("enter_defect"),
        label_visibility="collapsed"
    )
    
    if st.button(f"{t('add_text')} ({t(defect_type)})", key=f"add_{category_key}_btn", use_container_width=True):
        if text_input and text_input.strip():
            # Clean the input text
            cleaned_input = text_input.strip()
            
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
            
            # Add the defect to store
            add_defect_to_store(f'qc_{category_key}', english_text)
            st.success(f"{t(defect_type)} {t('defect_added')}")
            st.rerun()

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
st.markdown(f'<div class="hero-section"><h1 style="margin:0; font-size: 1.8rem;">{t("app_title")}</h1><p style="margin-top:0.5rem; font-size: 0.9rem;">GRAND STEP (H.K.) LTD<br>Professional Footwear Manufacturing & Quality Control<br>AI-Powered Quality Inspection System</p></div>', unsafe_allow_html=True)

st.markdown(f'<div class="section-header">{t("order_info")}</div>', unsafe_allow_html=True)

# UPDATED Order Information with new fields
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

# NEW: Production Status Section
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

# NEW: Items Used During Inspection Section
st.markdown(f'<div class="inspection-section">{t("items_used_inspection")}</div>', unsafe_allow_html=True)

insp_col1, insp_col2 = st.columns(2)
with insp_col1:
    st.session_state.inspection_items['staples_nail_used'] = st.text_input(t("staples_nail_used"), value="NO", key="staples_input")
with insp_col2:
    st.session_state.inspection_items['quantity_checked'] = st.text_input(t("quantity_checked"), value="ON LINE", key="quantity_checked_input")

st.markdown(f'<div class="section-header">{t("image_upload")}</div>', unsafe_allow_html=True)

angle_sequence = ["Front View", "Right Side", "Left Side", "Back View"]
uploaded_files = st.file_uploader(t("upload_images"), type=['png','jpg','jpeg'], accept_multiple_files=True)

uploaded_images = {}

if uploaded_files and len(uploaded_files) == 4:
    cols = st.columns(4)
    for idx, (angle, file) in enumerate(zip(angle_sequence, uploaded_files)):
        uploaded_images[angle] = file
        with cols[idx]:
            st.image(Image.open(file), caption=angle, use_container_width=True)

if len(uploaded_images) == 4:
    if st.button(f"{t('start_inspection')}", type="primary", use_container_width=True):
        progress = st.progress(0)
        analyses = []
        
        with st.spinner(t("analyzing")):
            for idx, (angle, file) in enumerate(uploaded_images.items()):
                image = Image.open(file)
                analysis = analyze_shoe_image(client, image, angle, style_number, color, contract_number)
                analyses.append(analysis)
                progress.progress((idx + 1) / 4)
        
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
        (t("critical"), len(ai_critical_ids), "#ef4444"),
        (t("major"), len(ai_major_ids), "#f59e0b"),
        (t("minor"), len(ai_minor_ids), "#3b82f6")
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
    
    qc_critical_ids, qc_critical_translated = get_translated_defects('qc_critical', st.session_state.ui_language)
    qc_major_ids, qc_major_translated = get_translated_defects('qc_major', st.session_state.ui_language)
    qc_minor_ids, qc_minor_translated = get_translated_defects('qc_minor', st.session_state.ui_language)
    
    st.markdown(f"### {t('critical_review')}")
    
    if qc_critical_translated:
        for idx, (defect_id, defect_text) in enumerate(zip(qc_critical_ids, qc_critical_translated)):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f'<div class="defect-item critical-defect">{defect_text}</div>', unsafe_allow_html=True)
            with col2:
                if st.button("❌", key=f"remove_crit_{defect_id}"):
                    remove_defect_from_store('qc_critical', defect_id)
                    st.rerun()
    else:
        st.success(f"{t('no_defects')}")
    
    render_defect_input_section("critical", "critical")
    
    st.markdown("---")
    
    st.markdown(f"### {t('major_review')}")
    
    if qc_major_translated:
        for idx, (defect_id, defect_text) in enumerate(zip(qc_major_ids, qc_major_translated)):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f'<div class="defect-item major-defect">{defect_text}</div>', unsafe_allow_html=True)
            with col2:
                if st.button("❌", key=f"remove_maj_{defect_id}"):
                    remove_defect_from_store('qc_major', defect_id)
                    st.rerun()
    else:
        st.success(f"{t('no_defects')}")
    
    render_defect_input_section("major", "major")
    
    st.markdown("---")
    
    st.markdown(f"### {t('minor_review')}")
    
    if qc_minor_translated:
        for idx, (defect_id, defect_text) in enumerate(zip(qc_minor_ids, qc_minor_translated)):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f'<div class="defect-item minor-defect">{defect_text}</div>', unsafe_allow_html=True)
            with col2:
                if st.button("❌", key=f"remove_min_{defect_id}"):
                    remove_defect_from_store('qc_minor', defect_id)
                    st.rerun()
    else:
        st.success(f"{t('no_defects')}")
    
    render_defect_input_section("minor", "minor")
    
    st.markdown("---")
    
    st.markdown(f"### {t('qc_notes')}")
    
    if 'qc_notes_english' not in st.session_state:
        st.session_state.qc_notes_english = ''
    
    displayed_notes = translate_text_with_openai(st.session_state.qc_notes_english, st.session_state.ui_language) if st.session_state.qc_notes_english else ''
    
    qc_notes_input = st.text_area(t("additional_notes"), value=displayed_notes, height=120, key="qc_notes_textarea")
    
    if st.button(f"{t('save_notes')}", type="primary", use_container_width=True):
        if qc_notes_input and qc_notes_input.strip():
            if st.session_state.ui_language != "English":
                try:
                    reverse_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "user",
                            "content": f"Translate this to English. Return ONLY the English translation:\n\n{qc_notes_input}"
                        }],
                        max_tokens=500,
                        temperature=0.1
                    )
                    st.session_state.qc_notes_english = reverse_response.choices[0].message.content.strip()
                except:
                    st.session_state.qc_notes_english = qc_notes_input
            else:
                st.session_state.qc_notes_english = qc_notes_input
            
            st.success(f"{t('notes_saved')}")
            st.rerun()
    
    st.markdown("---")
    
    final_result, final_reason = calculate_final_decision()
    
    st.markdown(f"## {t('final_summary')}")
    
    qc_critical_count = len(qc_critical_ids)
    qc_major_count = len(qc_major_ids)
    qc_minor_count = len(qc_minor_ids)
    
    col1, col2, col3 = st.columns(3)
    changes = [
        (qc_critical_count - len(ai_critical_ids), "#ef4444"),
        (qc_major_count - len(ai_major_ids), "#f59e0b"),
        (qc_minor_count - len(ai_minor_ids), "#3b82f6")
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
                <div style="font-size: 0.85rem; margin-top: 0.5rem;">{icon} {abs(change)} {t('from_ai')}</div>
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
