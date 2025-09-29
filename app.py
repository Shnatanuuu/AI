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
from reportlab.lib.enums import TA_CENTER, TA_LEFT

load_dotenv()

st.set_page_config(
    page_title="AI Shoe QC Inspector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    
    .hero-title {
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 800;
        margin-bottom: 1rem;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem 2rem;
        border-radius: 16px;
        margin: 2rem 0 1rem 0;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .angle-header {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid rgba(226, 232, 240, 0.8) !important;
        border-radius: 8px !important;
        padding: 0.8rem 1rem !important;
        color: #374151 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        color: white !important;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .status-indicator {
        display: inline-flex;
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        margin-top: 3rem;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
    
    @media (max-width: 768px) {
        .main .block-container { padding: 0.5rem; }
        .hero-section { padding: 2rem 1rem !important; }
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

st.markdown('<div class="hero-section"><div class="hero-title">AI Footwear Quality Control Inspector</div></div>', unsafe_allow_html=True)

def encode_image(image):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

def analyze_shoe_image(client, image, angle_name, style_number="", color="", po_number=""):
    base64_image = encode_image(image)
    
    prompt = f"""You are an expert footwear QC inspector. Analyze this {angle_name} image.
Product: {style_number}, Color: {color}, PO: {po_number}

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

def generate_clean_pdf_report(export_report, po_number, style_number):
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, 
                               topMargin=1.5*cm, bottomMargin=1.5*cm)
        elements = []
        styles = getSampleStyleSheet()
        
        brand_blue = colors.Color(0.4, 0.49, 0.91)
        success_green = colors.Color(0.31, 0.78, 0.47)
        warning_orange = colors.Color(1.0, 0.6, 0.0)
        danger_red = colors.Color(1.0, 0.42, 0.42)
        light_gray = colors.Color(0.98, 0.98, 0.98)
        dark_gray = colors.Color(0.33, 0.33, 0.33)
        
        title_style = ParagraphStyle('Title', parent=styles['Normal'], fontSize=24, alignment=TA_CENTER,
                                     textColor=brand_blue, fontName='Helvetica-Bold', spaceAfter=20)
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, spaceAfter=12,
                                      spaceBefore=20, textColor=brand_blue, fontName='Helvetica-Bold')
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=6,
                                    fontName='Helvetica', textColor=dark_gray)
        
        inspection_data = export_report['inspection_summary']
        defect_data = export_report['defect_summary']
        defects = export_report['defect_details']
        
        elements.append(Paragraph("GRAND STEP (H.K.) LTD", title_style))
        elements.append(Paragraph("QUALITY CONTROL INSPECTION REPORT", title_style))
        elements.append(Spacer(1, 20))
        
        result_style = ParagraphStyle('Result', parent=styles['Normal'], fontSize=20, alignment=TA_CENTER,
                                     fontName='Helvetica-Bold', spaceAfter=15,
                                     textColor=success_green if inspection_data['final_result']=='ACCEPT' 
                                     else danger_red if inspection_data['final_result']=='REJECT' else warning_orange)
        elements.append(Paragraph(f"FINAL RESULT: {inspection_data['final_result']}", result_style))
        elements.append(Paragraph(f"Rationale: {export_report['decision_rationale']}", body_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("ORDER INFORMATION", section_style))
        order_data = [
            ['PO Number', inspection_data['po_number']], ['Style', inspection_data['style_number']],
            ['Color', inspection_data['color']], ['Customer', inspection_data['customer']],
            ['Inspector', inspection_data['inspector']], ['Date', inspection_data['inspection_date']],
            ['Standard', inspection_data['inspection_standard']]
        ]
        order_table = Table(order_data, colWidths=[4*cm, 7*cm])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), brand_blue), ('TEXTCOLOR', (0,0), (0,-1), colors.white),
            ('BACKGROUND', (1,0), (1,-1), light_gray), ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('TOPPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.Color(0.9, 0.9, 0.9))
        ]))
        elements.append(order_table)
        elements.append(Spacer(1, 20))
        
        # AI Findings
        elements.append(Paragraph("AI INSPECTION FINDINGS", section_style))
        ai_data = [
            ['Defect Type', 'AI Count', 'AQL Limit', 'Status'],
            ['Critical', str(defect_data['ai_critical_count']), '0',
             'FAIL' if defect_data['ai_critical_count']>0 else 'PASS'],
            ['Major', str(defect_data['ai_major_count']), '10',
             'FAIL' if defect_data['ai_major_count']>10 else 'PASS'],
            ['Minor', str(defect_data['ai_minor_count']), '14',
             'FAIL' if defect_data['ai_minor_count']>14 else 'PASS']
        ]
        ai_table = Table(ai_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        ai_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.Color(0.6, 0.7, 0.9)),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('GRID', (0,0), (-1,-1), 1, colors.Color(0.9, 0.9, 0.9)),
            ('TOPPADDING', (0,0), (-1,-1), 8)
        ]))
        elements.append(ai_table)
        elements.append(Spacer(1, 15))
        
        def add_defects(title, defect_list, color):
            if defect_list:
                elements.append(Paragraph(f"{title}", section_style))
                for i, d in enumerate(defect_list, 1):
                    s = ParagraphStyle(f'{title}{i}', parent=body_style, leftIndent=10, textColor=color)
                    elements.append(Paragraph(f"{i}. {d}", s))
                elements.append(Spacer(1, 10))
        
        add_defects("CRITICAL DEFECTS (AI)", defects['ai_critical_defects'], danger_red)
        add_defects("MAJOR DEFECTS (AI)", defects['ai_major_defects'], warning_orange)
        add_defects("MINOR DEFECTS (AI)", defects['ai_minor_defects'], brand_blue)
        
        if not any([defects['ai_critical_defects'], defects['ai_major_defects'], defects['ai_minor_defects']]):
            elements.append(Paragraph("✓ No AI defects detected", body_style))
        
        elements.append(Spacer(1, 20))
        
        # QC Manager Review
        elements.append(Paragraph("QC MANAGER REVIEW & AMENDMENTS", section_style))
        
        # Calculate changes
        crit_change = defect_data['critical_count'] - defect_data['ai_critical_count']
        maj_change = defect_data['major_count'] - defect_data['ai_major_count']
        min_change = defect_data['minor_count'] - defect_data['ai_minor_count']
        
        qc_data = [
            ['Defect Type', 'AI Count', 'QC Final', 'Change', 'AQL Limit', 'Status'],
            ['Critical', str(defect_data['ai_critical_count']), str(defect_data['critical_count']),
             f"{crit_change:+d}" if crit_change != 0 else "0", '0',
             'FAIL' if defect_data['critical_count']>0 else 'PASS'],
            ['Major', str(defect_data['ai_major_count']), str(defect_data['major_count']),
             f"{maj_change:+d}" if maj_change != 0 else "0", '10',
             'FAIL' if defect_data['major_count']>10 else 'PASS'],
            ['Minor', str(defect_data['ai_minor_count']), str(defect_data['minor_count']),
             f"{min_change:+d}" if min_change != 0 else "0", '14',
             'FAIL' if defect_data['minor_count']>14 else 'PASS']
        ]
        qc_table = Table(qc_data, colWidths=[2.5*cm, 2*cm, 2*cm, 1.8*cm, 2*cm, 2*cm])
        qc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.Color(0.85, 0.6, 0.1)),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('GRID', (0,0), (-1,-1), 1, colors.Color(0.9, 0.9, 0.9)),
            ('TOPPADDING', (0,0), (-1,-1), 8), ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold')
        ]))
        elements.append(qc_table)
        elements.append(Spacer(1, 15))
        
        add_defects("CRITICAL DEFECTS (FINAL)", defects['critical_defects'], danger_red)
        add_defects("MAJOR DEFECTS (FINAL)", defects['major_defects'], warning_orange)
        add_defects("MINOR DEFECTS (FINAL)", defects['minor_defects'], brand_blue)
        
        if export_report.get('qc_notes'):
            elements.append(Paragraph("QC MANAGER NOTES", section_style))
            elements.append(Paragraph(export_report['qc_notes'], body_style))
        
    
        
        doc.build(elements)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")
        return None

# Order Information
st.markdown('<div class="section-header">📋 Order Information</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    po_number = st.text_input("PO Number", value="0144540")
    customer = st.text_input("Customer", value="MIA")
with col2:
    style_number = st.text_input("Style Number", value="GS1412401B")
    color = st.text_input("Color", value="PPB")
with col3:
    inspector = st.text_input("Inspector Name", value="AI Inspector")
    inspection_date = st.date_input("Inspection Date", value=datetime.now().date())

# Image Upload
st.markdown('<div class="section-header">📸 Sequential Image Upload</div>', unsafe_allow_html=True)
st.markdown("""<div style="background: rgba(102, 126, 234, 0.1); border: 1px solid rgba(102, 126, 234, 0.2);
border-radius: 16px; padding: 1.5rem; text-align: center; margin-bottom: 1.5rem;">
<div style="font-size: 1.2rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">Upload Images in Sequence</div>
<div style="color: #6b7280; font-size: 0.95rem;">Please upload 4 images: Front → Right → Left → Back</div>
</div>""", unsafe_allow_html=True)

angle_sequence = ["Front View", "Right Side", "Left Side", "Back View"]
angle_icons = {"Front View": "📐", "Right Side": "➡️", "Left Side": "⬅️", "Back View": "🔄"}

uploaded_files = st.file_uploader("Upload Images", type=['png','jpg','jpeg'], accept_multiple_files=True,
                                  help="Upload exactly 4 images in sequence")

uploaded_images = {}

if uploaded_files:
    if len(uploaded_files) == 4:
        st.markdown('<div class="status-indicator" style="background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; width: 100%;">✅ All 4 images uploaded</div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for idx, (angle, file) in enumerate(zip(angle_sequence, uploaded_files)):
            uploaded_images[angle] = file
            with cols[idx]:
                st.markdown(f'<div class="angle-header">{angle_icons[angle]} {angle}</div>', unsafe_allow_html=True)
                st.image(Image.open(file), use_container_width=True)
    else:
        st.warning(f"⚠️ Please upload exactly 4 images (Current: {len(uploaded_files)})")
        cols = st.columns(4)
        for idx, file in enumerate(uploaded_files[:4]):
            if idx < len(angle_sequence):
                with cols[idx]:
                    st.markdown(f'<div class="angle-header">{angle_icons[angle_sequence[idx]]} {angle_sequence[idx]}</div>', unsafe_allow_html=True)
                    st.image(Image.open(file), use_container_width=True)
else:
    st.info("📤 Please upload 4 images in sequence: Front, Right, Left, Back")

# Analysis
if len(uploaded_images) == 4:
    if st.button("🚀 Start AI Quality Inspection", type="primary", use_container_width=True):
        st.markdown("""<div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 2rem;
        border-radius: 16px; text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 1.3rem; font-weight: 600;">🤖 AI Analysis in Progress</div></div>""", unsafe_allow_html=True)
        
        progress = st.progress(0)
        status = st.empty()
        analyses = []
        
        for idx, (angle, file) in enumerate(uploaded_images.items()):
            status.info(f"🔍 Analyzing {angle}... ({idx+1}/4)")
            image = Image.open(file)
            analysis = analyze_shoe_image(client, image, angle, style_number, color, po_number)
            analyses.append(analysis)
            progress.progress((idx + 1) / 4)
        
        status.success("✅ Analysis complete!")
        
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
        
        # Store AI results
        st.session_state.ai_report = final_report
        st.session_state.order_info = order_info
        st.session_state.analyses_done = True

# Display Results if analysis is complete
if 'analyses_done' in st.session_state and st.session_state.analyses_done:
    final_report = st.session_state.ai_report
    order_info = st.session_state.order_info
    
    # Display AI Results
    st.markdown("## 📊 AI Inspection Results")
    
    result_colors = {
        "ACCEPT": ("#10b981", "#dcfce7"), "REWORK": ("#f59e0b", "#fef3c7"), "REJECT": ("#ef4444", "#fecaca")
    }
    bg, light_bg = result_colors[final_report['result']]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""<div class="metric-card" style="background: {light_bg}; border: 2px solid {bg};">
        <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">AI RESULT</div>
        <div style="font-size: 2rem; font-weight: 800; color: {bg};">{final_report['result']}</div></div>""", 
        unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
        <div style="font-size: 1rem; font-weight: 600; margin-bottom: 0.8rem;">AI Decision Rationale</div>
        <div style="font-size: 0.9rem;">{final_report['reason']}</div></div>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    metrics = [
        ("Critical", final_report['critical_count'], "#ef4444"),
        ("Major", final_report['major_count'], "#f59e0b"),
        ("Minor", final_report['minor_count'], "#3b82f6")
    ]
    for col, (label, count, color) in zip([col1,col2,col3], metrics):
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left: 4px solid {color};">
            <div style="font-size: 2rem; font-weight: 800; color: {color};">{count}</div>
            <div style="font-size: 1rem; font-weight: 600;">AI {label}</div></div>""", unsafe_allow_html=True)
    
    # QC Manager Review Section
    st.markdown("""<div style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 2rem;
    border-radius: 16px; margin: 3rem 0 2rem; text-align: center;">
    <div style="font-size: 1.5rem; font-weight: 700;">👤 QC Manager Review & Amendments</div>
    <div style="font-size: 0.95rem; margin-top: 0.5rem;">Review AI findings and make adjustments as needed</div></div>""", 
    unsafe_allow_html=True)
    
    st.info("💡 **Instructions:** Review each defect category below. Click ❌ to remove defects or add new ones that AI missed.")
    
    # Critical Defects Review
    st.markdown("### 🚨 Critical Defects Review")
    
    if st.session_state.qc_amendments['critical_defects']:
        for idx, defect in enumerate(st.session_state.qc_amendments['critical_defects']):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"🔴 {defect}")
            with col2:
                if st.button("❌", key=f"remove_crit_{idx}", help="Remove this defect"):
                    st.session_state.qc_amendments['critical_defects'].pop(idx)
                    st.rerun()
    else:
        st.success("✅ No critical defects")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_crit = st.text_input("➕ Add new critical defect:", key="new_crit_input", placeholder="Enter defect description...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add Critical", key="add_crit_btn", use_container_width=True) and new_crit.strip():
            st.session_state.qc_amendments['critical_defects'].append(new_crit.strip())
            st.rerun()
    
    st.markdown("---")
    
    # Major Defects Review
    st.markdown("### ⚠️ Major Defects Review")
    
    if st.session_state.qc_amendments['major_defects']:
        for idx, defect in enumerate(st.session_state.qc_amendments['major_defects']):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"🟡 {defect}")
            with col2:
                if st.button("❌", key=f"remove_maj_{idx}", help="Remove this defect"):
                    st.session_state.qc_amendments['major_defects'].pop(idx)
                    st.rerun()
    else:
        st.success("✅ No major defects")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_maj = st.text_input("➕ Add new major defect:", key="new_maj_input", placeholder="Enter defect description...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add Major", key="add_maj_btn", use_container_width=True) and new_maj.strip():
            st.session_state.qc_amendments['major_defects'].append(new_maj.strip())
            st.rerun()
    
    st.markdown("---")
    
    # Minor Defects Review
    st.markdown("### ℹ️ Minor Defects Review")
    
    if st.session_state.qc_amendments['minor_defects']:
        for idx, defect in enumerate(st.session_state.qc_amendments['minor_defects']):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"🔵 {defect}")
            with col2:
                if st.button("❌", key=f"remove_min_{idx}", help="Remove this defect"):
                    st.session_state.qc_amendments['minor_defects'].pop(idx)
                    st.rerun()
    else:
        st.success("✅ No minor defects")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_min = st.text_input("➕ Add new minor defect:", key="new_min_input", placeholder="Enter defect description...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add Minor", key="add_min_btn", use_container_width=True) and new_min.strip():
            st.session_state.qc_amendments['minor_defects'].append(new_min.strip())
            st.rerun()
    
    st.markdown("---")
    
    # QC Notes
    st.markdown("### 📝 QC Manager Notes")
    qc_notes = st.text_area("Additional observations and comments:", 
                            value=st.session_state.qc_amendments['qc_notes'],
                            height=120, key="qc_notes_input",
                            placeholder="Add any additional notes or observations about the inspection...")
    
    # Save Notes button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💾 Save QC Notes", use_container_width=True, type="primary"):
            st.session_state.qc_amendments['qc_notes'] = qc_notes
            st.success("✅ QC Notes saved successfully!")
            st.rerun()
    
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
    
    # Final Decision after QC Review
    if amended_report['critical_count'] > 0:
        amended_result = "REJECT"
        amended_reason = f"Critical defects ({amended_report['critical_count']}) - Zero tolerance"
    elif amended_report['major_count'] > 10:
        amended_result = "REJECT"
        amended_reason = f"Major defects ({amended_report['major_count']}) exceed AQL limit (10)"
    elif amended_report['minor_count'] > 14:
        amended_result = "REWORK"
        amended_reason = f"Minor defects ({amended_report['minor_count']}) exceed AQL limit (14)"
    else:
        amended_result = "ACCEPT"
        amended_reason = "All defects within acceptable AQL 2.5 limits"
    
    # Display Amended Summary
    st.markdown("## 📊 Final Inspection Summary (After QC Review)")
    
    col1, col2, col3 = st.columns(3)
    
    changes = [
        (amended_report['critical_count'] - final_report['critical_count'], "#ef4444"),
        (amended_report['major_count'] - final_report['major_count'], "#f59e0b"),
        (amended_report['minor_count'] - final_report['minor_count'], "#3b82f6")
    ]
    
    labels = ["Critical", "Major", "Minor"]
    counts = [amended_report['critical_count'], amended_report['major_count'], amended_report['minor_count']]
    
    for col, label, count, (change, color) in zip([col1,col2,col3], labels, counts, changes):
        icon = "🔺" if change > 0 else "🔻" if change < 0 else "➖"
        change_color = "#ef4444" if change > 0 else "#10b981" if change < 0 else "#6b7280"
        with col:
            st.markdown(f"""<div class="metric-card" style="border-left: 4px solid {color};">
            <div style="font-size: 1.8rem; font-weight: 800; color: {color};">{count}</div>
            <div style="font-size: 0.9rem; font-weight: 600;">{label} Defects</div>
            <div style="font-size: 0.85rem; color: {change_color}; margin-top: 0.5rem; font-weight: 600;">
            {icon} {abs(change)} from AI</div></div>""", unsafe_allow_html=True)
    
    # Final Result Display
    result_colors_final = {
        "ACCEPT": ("#10b981", "#dcfce7"), "REWORK": ("#f59e0b", "#fef3c7"), "REJECT": ("#ef4444", "#fecaca")
    }
    final_bg, final_light = result_colors_final[amended_result]
    
    st.markdown(f"""<div style="background: {final_light}; border: 3px solid {final_bg}; border-radius: 16px;
    padding: 2rem; margin: 2rem 0; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.15);">
    <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; color: #374151;">FINAL QC DECISION</div>
    <div style="font-size: 2.5rem; font-weight: 800; color: {final_bg}; margin: 0.5rem 0;">{amended_result}</div>
    <div style="font-size: 1rem; color: #4b5563;">{amended_reason}</div></div>""", unsafe_allow_html=True)
    
    # Detailed Defect Lists
    with st.expander("📋 View Detailed Defect Lists", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🤖 AI Detected Defects")
            if final_report['critical_defects']:
                st.markdown("**Critical:**")
                for d in final_report['critical_defects']:
                    st.error(f"• {d}")
            if final_report['major_defects']:
                st.markdown("**Major:**")
                for d in final_report['major_defects']:
                    st.warning(f"• {d}")
            if final_report['minor_defects']:
                st.markdown("**Minor:**")
                for d in final_report['minor_defects']:
                    st.info(f"• {d}")
            if not any([final_report['critical_defects'], final_report['major_defects'], final_report['minor_defects']]):
                st.success("✅ No defects detected by AI")
        
        with col2:
            st.markdown("#### 👤 QC Manager Final List")
            if amended_report['critical_defects']:
                st.markdown("**Critical:**")
                for d in amended_report['critical_defects']:
                    st.error(f"• {d}")
            if amended_report['major_defects']:
                st.markdown("**Major:**")
                for d in amended_report['major_defects']:
                    st.warning(f"• {d}")
            if amended_report['minor_defects']:
                st.markdown("**Minor:**")
                for d in amended_report['minor_defects']:
                    st.info(f"• {d}")
            if not any([amended_report['critical_defects'], amended_report['major_defects'], amended_report['minor_defects']]):
                st.success("✅ No defects in final review")
    
    # PDF Export Section
    st.markdown("## 📄 Generate Final PDF Report")
    st.info("📊 The PDF report includes both AI analysis and QC Manager review with detailed comparison")
    
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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📄 Generate & Download PDF Report", type="primary", use_container_width=True):
            with st.spinner("🔄 Generating professional PDF report..."):
                pdf_bytes = generate_clean_pdf_report(export_data, po_number, style_number)
            
            if pdf_bytes:
                filename = f"QC_Report_{po_number}_{style_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                st.success("✅ PDF report generated successfully!")
            else:
                st.error("❌ Failed to generate PDF report")

