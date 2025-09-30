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

# Use streamlit-audio-recorder (browser-compatible)
try:
    from audiorecorder import audiorecorder
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    st.warning("⚠️ Audio recording not available. Install with: pip install streamlit-audiorecorder")

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
        "po_number": "PO Number",
        "customer": "Customer",
        "style_number": "Style Number",
        "color": "Color",
        "inspector": "Inspector Name",
        "inspection_date": "Inspection Date",
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
        "add_text": "Add (Text)",
        "voice_input": "Voice Input for",
        "listening": "Processing audio...",
        "recognized": "Recognized:",
        "translated": "Translated:",
        "defect_added": "defect added!",
        "additional_notes": "Additional notes:",
        "notes_saved": "Notes saved!",
        "add_voice_notes": "Add Voice Notes",
        "voice_added": "Added:",
        "from_ai": "from AI",
        "final_qc_decision": "FINAL QC DECISION",
        "pdf_language_info": "PDF will be generated in:",
        "download_pdf": "Download PDF",
        "pdf_ready": "PDF ready!",
        "pdf_failed": "PDF generation failed",
        "generating_pdf": "Generating multilingual PDF...",
        "analyzing": "Analyzing images...",
        "record_audio": "🎤 Click to Record Audio",
        "start_recording": "Click to start recording",
        "stop_recording": "Click to stop recording"
    },
    "Mandarin": {
        "app_title": "AI鞋类质量控制检查员",
        "order_info": "订单信息",
        "po_number": "采购订单号",
        "customer": "客户",
        "style_number": "款式编号",
        "color": "颜色",
        "inspector": "检查员姓名",
        "inspection_date": "检查日期",
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
        "add_text": "添加（文本）",
        "voice_input": "语音输入",
        "listening": "正在处理音频...",
        "recognized": "识别:",
        "translated": "翻译:",
        "defect_added": "缺陷已添加!",
        "additional_notes": "附加备注:",
        "notes_saved": "备注已保存!",
        "add_voice_notes": "添加语音备注",
        "voice_added": "已添加:",
        "from_ai": "来自AI",
        "final_qc_decision": "最终质检决定",
        "pdf_language_info": "PDF将生成为:",
        "download_pdf": "下载PDF",
        "pdf_ready": "PDF已准备好!",
        "pdf_failed": "PDF生成失败",
        "generating_pdf": "正在生成多语言PDF...",
        "analyzing": "正在分析图像...",
        "record_audio": "🎤 点击录音",
        "start_recording": "点击开始录音",
        "stop_recording": "点击停止录音"
    },
    "Cantonese": {
        "app_title": "AI鞋類質量控制檢查員",
        "order_info": "訂單信息",
        "po_number": "採購訂單號",
        "customer": "客戶",
        "style_number": "款式編號",
        "color": "顏色",
        "inspector": "檢查員姓名",
        "inspection_date": "檢查日期",
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
        "add_text": "添加（文本）",
        "voice_input": "語音輸入",
        "listening": "正在處理音頻...",
        "recognized": "識別:",
        "translated": "翻譯:",
        "defect_added": "缺陷已添加!",
        "additional_notes": "附加備註:",
        "notes_saved": "備註已保存!",
        "add_voice_notes": "添加語音備註",
        "voice_added": "已添加:",
        "from_ai": "來自AI",
        "final_qc_decision": "最終質檢決定",
        "pdf_language_info": "PDF將生成為:",
        "download_pdf": "下載PDF",
        "pdf_ready": "PDF已準備好!",
        "pdf_failed": "PDF生成失敗",
        "generating_pdf": "正在生成多語言PDF...",
        "analyzing": "正在分析圖像...",
        "record_audio": "🎤 點擊錄音",
        "start_recording": "點擊開始錄音",
        "stop_recording": "點擊停止錄音"
    }
}

# Initialize session state
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "English"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "English"

def t(key):
    """Translation helper"""
    return TRANSLATIONS[st.session_state.ui_language].get(key, key)

# CSS Styling
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
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem 2rem;
        border-radius: 16px;
        margin: 2rem 0 1rem 0;
        font-weight: 700;
        font-size: 1.2rem;
        text-align: center;
    }
    
    .speech-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .audio-recorder {
        margin: 1rem 0;
    }
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

# Language Selector in Sidebar
with st.sidebar:
    st.markdown(f"### 🌐 {t('language_preference')}")
    
    st.markdown("**Interface Language:**")
    ui_lang = st.selectbox(
        "UI Language",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.ui_language),
        format_func=lambda x: f"{LANGUAGES[x]['flag']} {LANGUAGES[x]['label']}",
        key="ui_lang_select",
        label_visibility="collapsed"
    )
    if ui_lang != st.session_state.ui_language:
        st.session_state.ui_language = ui_lang
        st.rerun()
    
    st.markdown("**PDF Report Language:**")
    pdf_lang = st.selectbox(
        "PDF Language",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.pdf_language),
        format_func=lambda x: f"{LANGUAGES[x]['flag']} {LANGUAGES[x]['label']}",
        key="pdf_lang_select",
        label_visibility="collapsed"
    )
    if pdf_lang != st.session_state.pdf_language:
        st.session_state.pdf_language = pdf_lang

st.markdown(f'<div class="hero-section"><h1 style="margin:0;">{t("app_title")}</h1><p style="margin-top:0.5rem;">GRAND STEP (H.K.) LTD<br>Professional Footwear Manufacturing & Quality Control<br>AI-Powered Quality Inspection System</p></div>', unsafe_allow_html=True)

def translate_text(text, target_language):
    """Translate text using OpenAI"""
    if target_language == "English" or not text:
        return text
    
    lang_map = {
        "Mandarin": "Simplified Chinese",
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
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except:
        return text

def transcribe_and_translate_audio(audio_bytes, target_ui_language):
    """Transcribe audio using OpenAI Whisper API and translate if needed"""
    try:
        # Convert audiorecorder output to bytes
        if hasattr(audio_bytes, 'tobytes'):
            audio_data = audio_bytes.tobytes()
        else:
            audio_data = audio_bytes
            
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "recording.wav"
        
        # Transcribe without language constraint to detect any language
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        
        recognized_text = transcript.text
        
        # If UI language is not English, translate the recognized text
        if target_ui_language != "English":
            translated_text = translate_text(recognized_text, target_ui_language)
            return recognized_text, translated_text
        else:
            return recognized_text, recognized_text
            
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return None, None

def encode_image(image):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

def analyze_shoe_image(client, image, angle_name, style_number="", color="", po_number="", target_language="English"):
    base64_image = encode_image(image)
    
    # Request AI to respond in target language
    lang_instruction = ""
    if target_language == "Mandarin":
        lang_instruction = "\nIMPORTANT: Provide ALL defect descriptions in Simplified Chinese (简体中文)."
    elif target_language == "Cantonese":
        lang_instruction = "\nIMPORTANT: Provide ALL defect descriptions in Traditional Chinese (繁體中文)."
    
    prompt = f"""You are an expert footwear QC inspector. Analyze this {angle_name} image.
Product: {style_number}, Color: {color}, PO: {po_number}
{lang_instruction}

Return ONLY valid JSON:
{{
    "angle": "{angle_name}",
    "critical_defects": ["list defects"],
    "major_defects": ["list defects"],
    "minor_defects": ["list defects"],
    "overall_condition": "Good/Fair/Poor",
    "confidence": "High/Medium/Low",
    "inspection_notes": "notes"
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
            max_tokens=800,
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        
        if start != -1 and end > start:
            return json.loads(result_text[start:end])
        return {"angle": angle_name, "critical_defects": [], "major_defects": [], "minor_defects": [], 
                "overall_condition": "Fair", "confidence": "Low", "inspection_notes": "Parse failed"}
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def generate_qc_report(analyses, order_info):
    all_critical, all_major, all_minor = [], [], []
    
    for analysis in analyses:
        if analysis:
            all_critical.extend(analysis.get('critical_defects', []))
            all_major.extend(analysis.get('major_defects', []))
            all_minor.extend(analysis.get('minor_defects', []))
    
    all_critical = list(dict.fromkeys(all_critical))
    all_major = list(dict.fromkeys(all_major))
    all_minor = list(dict.fromkeys(all_minor))
    
    aql_limits = {"critical": 0, "major": 10, "minor": 14}
    
    if len(all_critical) > aql_limits["critical"]:
        result, reason = "REJECT", f"Critical defects ({len(all_critical)}) - Zero tolerance"
    elif len(all_major) > aql_limits["major"]:
        result, reason = "REJECT", f"Major defects ({len(all_major)}) exceed limit"
    elif len(all_minor) > aql_limits["minor"]:
        result, reason = "REWORK", f"Minor defects ({len(all_minor)}) exceed limit"
    else:
        result, reason = "ACCEPT", "All defects within AQL 2.5 limits"
    
    return {
        "result": result, "reason": reason,
        "critical_count": len(all_critical), "major_count": len(all_major), "minor_count": len(all_minor),
        "critical_defects": all_critical, "major_defects": all_major, "minor_defects": all_minor,
        "aql_limits": aql_limits
    }

def generate_multilingual_pdf(export_report, po_number, style_number, language):
    """Generate PDF with proper Chinese font support using CID fonts"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                               topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        styles = getSampleStyleSheet()
        
        # Register Unicode CID fonts for Chinese
        base_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'
        
        if language in ["Mandarin", "Cantonese"]:
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                base_font = 'STSong-Light'
                bold_font = 'STSong-Light'
            except Exception as e:
                st.warning(f"Chinese font registration failed, using ASCII fallback: {e}")
        
        # Colors
        brand_blue = colors.Color(0.4, 0.49, 0.91)
        success_green = colors.Color(0.31, 0.78, 0.47)
        warning_orange = colors.Color(1.0, 0.6, 0.0)
        danger_red = colors.Color(1.0, 0.42, 0.42)
        light_gray = colors.Color(0.97, 0.97, 0.97)
        
        # Styles
        title_style = ParagraphStyle('Title', parent=styles['Normal'], fontSize=22, alignment=TA_CENTER,
                                     textColor=brand_blue, fontName=bold_font, spaceAfter=12, spaceBefore=10)
        
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER,
                                        textColor=colors.Color(0.3, 0.3, 0.3), fontName=base_font, spaceAfter=8)
        
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, spaceAfter=10,
                                      spaceBefore=15, textColor=brand_blue, fontName=bold_font, alignment=TA_CENTER)
        
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=6,
                                    fontName=base_font, textColor=colors.black)
        
        inspection_data = export_report['inspection_summary']
        defect_data = export_report['defect_summary']
        defects = export_report['defect_details']
        
        # Header with proper spacing
        elements.append(Paragraph("GRAND STEP (H.K.) LTD", title_style))
        elements.append(Spacer(1, 12))  # Space after company name
        elements.append(Paragraph("Professional Footwear Manufacturing & Quality Control", subtitle_style))
        elements.append(Paragraph("AI-Powered Quality Inspection System", subtitle_style))
        elements.append(Spacer(1, 20))
        
        # Title
        title_text = translate_text("QUALITY CONTROL INSPECTION REPORT", language)
        report_title = ParagraphStyle('ReportTitle', parent=title_style, fontSize=16, textColor=colors.black, fontName=bold_font)
        elements.append(Paragraph(title_text, report_title))
        elements.append(Spacer(1, 20))
        
        # Final Result
        result_text = translate_text(inspection_data['final_result'], language)
        result_color = success_green if inspection_data['final_result']=='ACCEPT' else (danger_red if inspection_data['final_result']=='REJECT' else warning_orange)
        
        result_style = ParagraphStyle('Result', parent=styles['Normal'], fontSize=18, alignment=TA_CENTER,
                                     fontName=bold_font, spaceAfter=10, textColor=result_color)
        
        final_label = translate_text("FINAL QC DECISION", language)
        elements.append(Paragraph(f"{final_label}: {result_text}", result_style))
        
        rationale_text = translate_text(export_report['decision_rationale'], language)
        elements.append(Paragraph(rationale_text, body_style))
        elements.append(Spacer(1, 20))
        
        # Order Information
        order_label = translate_text("ORDER INFORMATION", language)
        elements.append(Paragraph(order_label, section_style))
        elements.append(Spacer(1, 10))
        
        order_data = [
            [translate_text('PO Number', language), inspection_data['po_number']],
            [translate_text('Style', language), inspection_data['style_number']],
            [translate_text('Color', language), inspection_data['color']],
            [translate_text('Customer', language), inspection_data['customer']],
            [translate_text('Inspector', language), inspection_data['inspector']],
            [translate_text('Date', language), inspection_data['inspection_date']],
            [translate_text('Standard', language), inspection_data['inspection_standard']]
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
        
        # AI Analysis Section
        ai_label = translate_text("AI INSPECTION FINDINGS", language)
        elements.append(Paragraph(ai_label, section_style))
        elements.append(Spacer(1, 10))
        
        ai_header = [
            [translate_text('Defect Type', language), 
             translate_text('AI Count', language), 
             translate_text('AQL Limit', language), 
             translate_text('Status', language)]
        ]
        
        ai_data = [
            [translate_text('Critical', language), 
             str(defect_data['ai_critical_count']), '0',
             translate_text('FAIL' if defect_data['ai_critical_count']>0 else 'PASS', language)],
            [translate_text('Major', language), 
             str(defect_data['ai_major_count']), '10',
             translate_text('FAIL' if defect_data['ai_major_count']>10 else 'PASS', language)],
            [translate_text('Minor', language), 
             str(defect_data['ai_minor_count']), '14',
             translate_text('FAIL' if defect_data['ai_minor_count']>14 else 'PASS', language)]
        ]
        
        ai_table = Table(ai_header + ai_data, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
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
        
        # QC Manager Review Section
        qc_label = translate_text("QC MANAGER REVIEW & AMENDMENTS", language)
        elements.append(Paragraph(qc_label, section_style))
        elements.append(Spacer(1, 10))
        
        # Changes calculation
        crit_change = defect_data['critical_count'] - defect_data['ai_critical_count']
        maj_change = defect_data['major_count'] - defect_data['ai_major_count']
        min_change = defect_data['minor_count'] - defect_data['ai_minor_count']
        
        qc_header = [
            [translate_text('Defect Type', language),
             translate_text('AI Count', language),
             translate_text('QC Final', language),
             translate_text('Change', language),
             translate_text('Status', language)]
        ]
        
        qc_data = [
            [translate_text('Critical', language),
             str(defect_data['ai_critical_count']),
             str(defect_data['critical_count']),
             f"{crit_change:+d}" if crit_change != 0 else "0",
             translate_text('FAIL' if defect_data['critical_count']>0 else 'PASS', language)],
            [translate_text('Major', language),
             str(defect_data['ai_major_count']),
             str(defect_data['major_count']),
             f"{maj_change:+d}" if maj_change != 0 else "0",
             translate_text('FAIL' if defect_data['major_count']>10 else 'PASS', language)],
            [translate_text('Minor', language),
             str(defect_data['ai_minor_count']),
             str(defect_data['minor_count']),
             f"{min_change:+d}" if min_change != 0 else "0",
             translate_text('FAIL' if defect_data['minor_count']>14 else 'PASS', language)]
        ]
        
        qc_table = Table(qc_header + qc_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3*cm])
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
        
        # Defect Details
        def add_defects(title_key, defect_list, color_obj):
            if defect_list:
                title = translate_text(title_key, language)
                elements.append(Paragraph(title, section_style))
                elements.append(Spacer(1, 8))
                for i, d in enumerate(defect_list, 1):
                    defect_style = ParagraphStyle(f'defect{i}_{id(d)}', parent=body_style, leftIndent=15, 
                                                  textColor=color_obj, fontSize=10)
                    elements.append(Paragraph(f"{i}. {d}", defect_style))
                    elements.append(Spacer(1, 4))
                elements.append(Spacer(1, 10))
        
        add_defects("CRITICAL DEFECTS (FINAL)", defects['critical_defects'], danger_red)
        add_defects("MAJOR DEFECTS (FINAL)", defects['major_defects'], warning_orange)
        add_defects("MINOR DEFECTS (FINAL)", defects['minor_defects'], brand_blue)
        
        # QC Notes
        if export_report.get('qc_notes'):
            notes_label = translate_text("QC MANAGER NOTES", language)
            elements.append(Paragraph(notes_label, section_style))
            notes_text = export_report['qc_notes']
            if language != st.session_state.ui_language:
                notes_text = translate_text(notes_text, language)
            elements.append(Paragraph(notes_text, body_style))
        
        doc.build(elements)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

# Order Information
st.markdown(f'<div class="section-header">{t("order_info")}</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    po_number = st.text_input(t("po_number"), value="0144540")
    customer = st.text_input(t("customer"), value="MIA")
with col2:
    style_number = st.text_input(t("style_number"), value="GS1412401B")
    color = st.text_input(t("color"), value="PPB")
with col3:
    inspector = st.text_input(t("inspector"), value="AI Inspector")
    inspection_date = st.date_input(t("inspection_date"), value=datetime.now().date())

# Image Upload
st.markdown(f'<div class="section-header">📸 {t("image_upload")}</div>', unsafe_allow_html=True)

angle_sequence = ["Front View", "Right Side", "Left Side", "Back View"]
uploaded_files = st.file_uploader(t("upload_images"), type=['png','jpg','jpeg'], accept_multiple_files=True)

uploaded_images = {}

if uploaded_files and len(uploaded_files) == 4:
    cols = st.columns(4)
    for idx, (angle, file) in enumerate(zip(angle_sequence, uploaded_files)):
        uploaded_images[angle] = file
        with cols[idx]:
            st.image(Image.open(file), caption=angle, use_container_width=True)

# Analysis
if len(uploaded_images) == 4:
    if st.button(f"🚀 {t('start_inspection')}", type="primary", use_container_width=True):
        progress = st.progress(0)
        analyses = []
        
        with st.spinner(t("analyzing")):
            for idx, (angle, file) in enumerate(uploaded_images.items()):
                image = Image.open(file)
                analysis = analyze_shoe_image(client, image, angle, style_number, color, po_number, st.session_state.ui_language)
                analyses.append(analysis)
                progress.progress((idx + 1) / 4)
        
        order_info = {
            "po_number": po_number, "style_number": style_number, "color": color,
            "customer": customer, "inspector": inspector,
            "inspection_date": inspection_date.strftime("%Y-%m-%d")
        }
        
        final_report = generate_qc_report(analyses, order_info)
        
        # Initialize session state
        if 'qc_amendments' not in st.session_state:
            st.session_state.qc_amendments = {
                'critical_defects': final_report['critical_defects'].copy(),
                'major_defects': final_report['major_defects'].copy(),
                'minor_defects': final_report['minor_defects'].copy(),
                'qc_notes': ''
            }
        
        st.session_state.ai_report = final_report
        st.session_state.order_info = order_info
        st.session_state.analyses_done = True

# Display Results
if 'analyses_done' in st.session_state and st.session_state.analyses_done:
    final_report = st.session_state.ai_report
    order_info = st.session_state.order_info
    
    # AI Results Display
    st.markdown(f"## {t('ai_results')}")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    metrics = [
        (t("critical"), final_report['critical_count'], "#ef4444"),
        (t("major"), final_report['major_count'], "#f59e0b"),
        (t("minor"), final_report['minor_count'], "#3b82f6")
    ]
    for col, (label, count, color) in zip([col1,col2,col3], metrics):
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left: 4px solid {color};">
            <div style="font-size: 2rem; font-weight: 800; color: {color};">{count}</div>
            <div style="font-size: 1rem; font-weight: 600;">AI {label}</div></div>""", unsafe_allow_html=True)
    
    # Display defects
    with st.expander(f"📋 {t('view_ai_defects')}", expanded=True):
        if final_report.get('critical_defects'):
            st.markdown(f"**{t('critical')}:**")
            for d in final_report['critical_defects']:
                st.error(f"• {d}")
        if final_report.get('major_defects'):
            st.markdown(f"**{t('major')}:**")
            for d in final_report['major_defects']:
                st.warning(f"• {d}")
        if final_report.get('minor_defects'):
            st.markdown(f"**{t('minor')}:**")
            for d in final_report['minor_defects']:
                st.info(f"• {d}")
    
    st.markdown("---")
    
    # QC Manager Review Section
    st.markdown(f"""<div style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 2rem;
    border-radius: 16px; margin: 2rem 0; text-align: center;">
    <div style="font-size: 1.5rem; font-weight: 700;">👤 {t('qc_review')}</div></div>""", unsafe_allow_html=True)
    
    # Critical Defects Review
    st.markdown(f"### 🚨 {t('critical_review')}")
    
    if st.session_state.qc_amendments['critical_defects']:
        for idx, defect in enumerate(st.session_state.qc_amendments['critical_defects']):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.error(f"🔴 {defect}")
            with col2:
                if st.button("❌", key=f"remove_crit_{idx}"):
                    st.session_state.qc_amendments['critical_defects'].pop(idx)
                    st.rerun()
    else:
        st.success(f"✅ {t('no_defects')}")
    
    st.markdown(f"**{t('add_defect')} ({t('critical')})**")
    
    # Text input for critical defects
    new_crit_text = st.text_input(t("type_defect"), key="new_crit_text", placeholder=t("enter_defect"))
    if st.button(f"➕ {t('add_text')} ({t('critical')})", key="add_crit_text_btn", use_container_width=True):
        if new_crit_text.strip():
            # Translate text if UI language is not English
            if st.session_state.ui_language != "English":
                translated = translate_text(new_crit_text.strip(), st.session_state.ui_language)
                st.session_state.qc_amendments['critical_defects'].append(translated)
            else:
                st.session_state.qc_amendments['critical_defects'].append(new_crit_text.strip())
            st.success(f"✅ {t('critical')} {t('defect_added')}")
            st.rerun()
    
    # Audio input for critical defects
    if AUDIO_AVAILABLE:
        st.markdown('<div class="speech-section">', unsafe_allow_html=True)
        st.markdown(f"**🎤 {t('voice_input')} {t('critical')}**")
        
        st.markdown(f"*{t('start_recording')}*")
        # Simple audiorecorder without any parameters
        audio_bytes_crit = audiorecorder("Click to record", "Recording...", key="audio_crit")
        
        if audio_bytes_crit and len(audio_bytes_crit) > 0:
            # Use a unique key based on audio content to detect new recordings
            audio_hash = hash(audio_bytes_crit.tobytes() if hasattr(audio_bytes_crit, 'tobytes') else str(audio_bytes_crit))
            if 'last_audio_crit_hash' not in st.session_state or st.session_state.last_audio_crit_hash != audio_hash:
                st.session_state.last_audio_crit_hash = audio_hash
                
                with st.spinner(t("listening")):
                    recognized, translated = transcribe_and_translate_audio(audio_bytes_crit, st.session_state.ui_language)
                    
                    if recognized and translated:
                        st.info(f"🎤 {t('recognized')} {recognized}")
                        if recognized != translated:
                            st.success(f"🌐 {t('translated')} {translated}")
                        
                        st.session_state.qc_amendments['critical_defects'].append(translated)
                        st.success(f"✅ {t('defect_added')}")
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Major Defects Review
    st.markdown(f"### ⚠️ {t('major_review')}")
    
    if st.session_state.qc_amendments['major_defects']:
        for idx, defect in enumerate(st.session_state.qc_amendments['major_defects']):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.warning(f"🟡 {defect}")
            with col2:
                if st.button("❌", key=f"remove_maj_{idx}"):
                    st.session_state.qc_amendments['major_defects'].pop(idx)
                    st.rerun()
    else:
        st.success(f"✅ {t('no_defects')}")
    
    st.markdown(f"**{t('add_defect')} ({t('major')})**")
    
    # Text input for major defects
    new_maj_text = st.text_input(t("type_defect"), key="new_maj_text", placeholder=t("enter_defect"))
    if st.button(f"➕ {t('add_text')} ({t('major')})", key="add_maj_text_btn", use_container_width=True):
        if new_maj_text.strip():
            if st.session_state.ui_language != "English":
                translated = translate_text(new_maj_text.strip(), st.session_state.ui_language)
                st.session_state.qc_amendments['major_defects'].append(translated)
            else:
                st.session_state.qc_amendments['major_defects'].append(new_maj_text.strip())
            st.success(f"✅ {t('major')} {t('defect_added')}")
            st.rerun()
    
    # Audio input for major defects
    if AUDIO_AVAILABLE:
        st.markdown('<div class="speech-section">', unsafe_allow_html=True)
        st.markdown(f"**🎤 {t('voice_input')} {t('major')}**")
        
        st.markdown(f"*{t('start_recording')}*")
        # Simple audiorecorder without any parameters
        audio_bytes_maj = audiorecorder("Click to record", "Recording...", key="audio_maj")
        
        if audio_bytes_maj and len(audio_bytes_maj) > 0:
            audio_hash = hash(audio_bytes_maj.tobytes() if hasattr(audio_bytes_maj, 'tobytes') else str(audio_bytes_maj))
            if 'last_audio_maj_hash' not in st.session_state or st.session_state.last_audio_maj_hash != audio_hash:
                st.session_state.last_audio_maj_hash = audio_hash
                
                with st.spinner(t("listening")):
                    recognized, translated = transcribe_and_translate_audio(audio_bytes_maj, st.session_state.ui_language)
                    
                    if recognized and translated:
                        st.info(f"🎤 {t('recognized')} {recognized}")
                        if recognized != translated:
                            st.success(f"🌐 {t('translated')} {translated}")
                        
                        st.session_state.qc_amendments['major_defects'].append(translated)
                        st.success(f"✅ {t('defect_added')}")
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Minor Defects Review
    st.markdown(f"### ℹ️ {t('minor_review')}")
    
    if st.session_state.qc_amendments['minor_defects']:
        for idx, defect in enumerate(st.session_state.qc_amendments['minor_defects']):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.info(f"🔵 {defect}")
            with col2:
                if st.button("❌", key=f"remove_min_{idx}"):
                    st.session_state.qc_amendments['minor_defects'].pop(idx)
                    st.rerun()
    else:
        st.success(f"✅ {t('no_defects')}")
    
    st.markdown(f"**{t('add_defect')} ({t('minor')})**")
    
    # Text input for minor defects
    new_min_text = st.text_input(t("type_defect"), key="new_min_text", placeholder=t("enter_defect"))
    if st.button(f"➕ {t('add_text')} ({t('minor')})", key="add_min_text_btn", use_container_width=True):
        if new_min_text.strip():
            if st.session_state.ui_language != "English":
                translated = translate_text(new_min_text.strip(), st.session_state.ui_language)
                st.session_state.qc_amendments['minor_defects'].append(translated)
            else:
                st.session_state.qc_amendments['minor_defects'].append(new_min_text.strip())
            st.success(f"✅ {t('minor')} {t('defect_added')}")
            st.rerun()
    
    # Audio input for minor defects
    if AUDIO_AVAILABLE:
        st.markdown('<div class="speech-section">', unsafe_allow_html=True)
        st.markdown(f"**🎤 {t('voice_input')} {t('minor')}**")
        
        st.markdown(f"*{t('start_recording')}*")
        # Simple audiorecorder without any parameters
        audio_bytes_min = audiorecorder("Click to record", "Recording...", key="audio_min")
        
        if audio_bytes_min and len(audio_bytes_min) > 0:
            audio_hash = hash(audio_bytes_min.tobytes() if hasattr(audio_bytes_min, 'tobytes') else str(audio_bytes_min))
            if 'last_audio_min_hash' not in st.session_state or st.session_state.last_audio_min_hash != audio_hash:
                st.session_state.last_audio_min_hash = audio_hash
                
                with st.spinner(t("listening")):
                    recognized, translated = transcribe_and_translate_audio(audio_bytes_min, st.session_state.ui_language)
                    
                    if recognized and translated:
                        st.info(f"🎤 {t('recognized')} {recognized}")
                        if recognized != translated:
                            st.success(f"🌐 {t('translated')} {translated}")
                        
                        st.session_state.qc_amendments['minor_defects'].append(translated)
                        st.success(f"✅ {t('defect_added')}")
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # QC Notes
    st.markdown(f"### 📝 {t('qc_notes')}")
    
    qc_notes = st.text_area(t("additional_notes"), value=st.session_state.qc_amendments['qc_notes'], height=120, key="qc_notes_textarea")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"💾 {t('save_notes')}", type="primary", use_container_width=True):
            st.session_state.qc_amendments['qc_notes'] = qc_notes
            st.success(f"✅ {t('notes_saved')}")
    
    with col2:
        if AUDIO_AVAILABLE:
            st.markdown(f"**{t('add_voice_notes')}**")
    
    # Audio input for QC notes
    if AUDIO_AVAILABLE:
        st.markdown('<div class="speech-section">', unsafe_allow_html=True)
        st.markdown(f"**🎤 {t('voice_input')} - {t('qc_notes')}**")
        
        st.markdown(f"*{t('start_recording')}*")
        # Simple audiorecorder without any parameters
        audio_bytes_notes = audiorecorder("Click to record", "Recording...", key="audio_notes")
        
        if audio_bytes_notes and len(audio_bytes_notes) > 0:
            audio_hash = hash(audio_bytes_notes.tobytes() if hasattr(audio_bytes_notes, 'tobytes') else str(audio_bytes_notes))
            if 'last_audio_notes_hash' not in st.session_state or st.session_state.last_audio_notes_hash != audio_hash:
                st.session_state.last_audio_notes_hash = audio_hash
                
                with st.spinner(t("listening")):
                    recognized, translated = transcribe_and_translate_audio(audio_bytes_notes, st.session_state.ui_language)
                    
                    if recognized and translated:
                        st.info(f"🎤 {t('recognized')} {recognized}")
                        if recognized != translated:
                            st.success(f"🌐 {t('translated')} {translated}")
                        
                        current = st.session_state.qc_amendments['qc_notes']
                        st.session_state.qc_amendments['qc_notes'] = (current + " " + translated) if current else translated
                        st.success(f"✅ {t('voice_added')}")
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Calculate Amended Report
    amended_report = {
        'critical_count': len(st.session_state.qc_amendments['critical_defects']),
        'major_count': len(st.session_state.qc_amendments['major_defects']),
        'minor_count': len(st.session_state.qc_amendments['minor_defects']),
        'critical_defects': st.session_state.qc_amendments['critical_defects'],
        'major_defects': st.session_state.qc_amendments['major_defects'],
        'minor_defects': st.session_state.qc_amendments['minor_defects'],
        'aql_limits': final_report['aql_limits']
    }
    
    if amended_report['critical_count'] > 0:
        amended_result = "REJECT"
        amended_reason = f"Critical defects ({amended_report['critical_count']}) - Zero tolerance"
    elif amended_report['major_count'] > 10:
        amended_result = "REJECT"
        amended_reason = f"Major defects ({amended_report['major_count']}) exceed AQL limit"
    elif amended_report['minor_count'] > 14:
        amended_result = "REWORK"
        amended_reason = f"Minor defects ({amended_report['minor_count']}) exceed AQL limit"
    else:
        amended_result = "ACCEPT"
        amended_reason = "All defects within AQL 2.5 limits"
    
    # Final Summary
    st.markdown(f"## {t('final_summary')}")
    
    col1, col2, col3 = st.columns(3)
    changes = [
        (amended_report['critical_count'] - final_report['critical_count'], "#ef4444"),
        (amended_report['major_count'] - final_report['major_count'], "#f59e0b"),
        (amended_report['minor_count'] - final_report['minor_count'], "#3b82f6")
    ]
    
    labels = [t("critical"), t("major"), t("minor")]
    counts = [amended_report['critical_count'], amended_report['major_count'], amended_report['minor_count']]
    
    for col, label, count, (change, color) in zip([col1,col2,col3], labels, counts, changes):
        icon = "🔺" if change > 0 else "🔻" if change < 0 else "➖"
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left: 4px solid {color};">
            <div style="font-size: 1.8rem; font-weight: 800; color: {color};">{count}</div>
            <div style="font-size: 0.9rem; font-weight: 600;">{label}</div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem;">{icon} {abs(change)} {t('from_ai')}</div></div>""", 
            unsafe_allow_html=True)
    
    # Final Result
    result_colors_final = {
        "ACCEPT": ("#10b981", "#dcfce7"), "REWORK": ("#f59e0b", "#fef3c7"), "REJECT": ("#ef4444", "#fecaca")
    }
    final_bg, final_light = result_colors_final[amended_result]
    
    translated_result = translate_text(amended_result, st.session_state.ui_language)
    translated_reason = translate_text(amended_reason, st.session_state.ui_language)
    
    st.markdown(f"""<div style="background: {final_light}; border: 3px solid {final_bg}; border-radius: 16px;
    padding: 2rem; margin: 2rem 0; text-align: center;">
    <div style="font-size: 1.1rem; font-weight: 600;">{t('final_qc_decision')}</div>
    <div style="font-size: 2.5rem; font-weight: 800; color: {final_bg};">{translated_result}</div>
    <div style="font-size: 1rem; margin-top: 0.5rem;">{translated_reason}</div></div>""", unsafe_allow_html=True)
    
    # PDF Export
    st.markdown(f"## 📄 {t('generate_pdf')}")
    st.info(f"📊 {t('pdf_language_info')} {LANGUAGES[st.session_state.pdf_language]['flag']} {LANGUAGES[st.session_state.pdf_language]['label']}")
    
    export_data = {
        "inspection_summary": {
            "inspection_date": order_info["inspection_date"],
            "inspector": order_info["inspector"],
            "customer": order_info["customer"],
            "po_number": order_info["po_number"],
            "style_number": order_info["style_number"],
            "color": order_info["color"],
            "final_result": amended_result,
            "inspection_standard": "AQL 2.5"
        },
        "defect_summary": {
            "ai_critical_count": final_report['critical_count'],
            "ai_major_count": final_report['major_count'],
            "ai_minor_count": final_report['minor_count'],
            "critical_count": amended_report['critical_count'],
            "major_count": amended_report['major_count'],
            "minor_count": amended_report['minor_count'],
            "aql_limits": final_report['aql_limits']
        },
        "defect_details": {
            "ai_critical_defects": final_report['critical_defects'],
            "ai_major_defects": final_report['major_defects'],
            "ai_minor_defects": final_report['minor_defects'],
            "critical_defects": amended_report['critical_defects'],
            "major_defects": amended_report['major_defects'],
            "minor_defects": amended_report['minor_defects']
        },
        "decision_rationale": amended_reason,
        "qc_notes": st.session_state.qc_amendments['qc_notes']
    }
    
    if st.button(f"📄 {t('generate_pdf')}", type="primary", use_container_width=True):
        with st.spinner(t("generating_pdf")):
            pdf_bytes = generate_multilingual_pdf(export_data, po_number, style_number, st.session_state.pdf_language)
        
        if pdf_bytes:
            lang_suffix = st.session_state.pdf_language[:2].upper()
            filename = f"QC_Report_{po_number}_{style_number}_{lang_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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
