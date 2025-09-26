import streamlit as st
import openai
import base64
from PIL import Image
import io
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF

# Load environment variables
load_dotenv()

# Set up the page with mobile-friendly configuration
st.set_page_config(
    page_title="AI Shoe QC Inspector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean, professional CSS with mobile-first design
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');
    
    /* CSS Variables for consistent theming */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --danger-gradient: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        --glass-bg: rgba(255, 255, 255, 0.15);
        --glass-border: rgba(255, 255, 255, 0.25);
        --shadow-light: 0 8px 32px rgba(0, 0, 0, 0.1);
        --shadow-heavy: 0 20px 60px rgba(0, 0, 0, 0.2);
        --border-radius: 16px;
        --animation-smooth: cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Global reset and base styling */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }
    
    /* Main container with improved spacing */
    .main .block-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        .stColumns > div {
            margin-bottom: 1rem;
        }
        
        .hero-section {
            padding: 2rem 1rem !important;
        }
        
        .grid-4, .grid-3, .grid-2 {
            grid-template-columns: 1fr !important;
        }
    }
    
    /* Clean hero section */
    .hero-section {
        background: var(--primary-gradient);
        color: white;
        padding: 3rem 2rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: var(--shadow-heavy);
    }
    
    .hero-title {
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 800;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    
    /* Section headers */
    .section-header {
        background: var(--primary-gradient);
        color: white;
        padding: 1.2rem 2rem;
        border-radius: var(--border-radius);
        margin: 2rem 0 1rem 0;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: var(--shadow-light);
    }
    
    /* Upload containers */
    .upload-container {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(226, 232, 240, 0.8);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s var(--animation-smooth);
    }
    
    .upload-container:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-light);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    /* Angle headers */
    .angle-header {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        font-weight: 600;
        font-size: 1rem;
        color: #2d3748;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Form inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > div > div {
        border: 2px solid rgba(226, 232, 240, 0.8) !important;
        border-radius: 8px !important;
        padding: 0.8rem 1rem !important;
        font-size: 0.95rem !important;
        background: rgba(255, 255, 255, 0.95) !important;
        transition: all 0.3s var(--animation-smooth) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within,
    .stDateInput > div > div > div > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: var(--primary-gradient) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        color: white !important;
        box-shadow: var(--shadow-light) !important;
        transition: all 0.3s var(--animation-smooth) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-heavy) !important;
    }
    
    /* Metrics cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow-light);
        transition: all 0.3s var(--animation-smooth);
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-heavy);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: var(--shadow-light);
    }
    
    .status-success {
        background: var(--success-gradient);
        color: white;
    }
    
    .status-warning {
        background: var(--warning-gradient);
        color: white;
    }
    
    .status-danger {
        background: var(--danger-gradient);
        color: white;
    }
    
    /* Clean footer */
    .footer {
        margin-top: 3rem;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: var(--border-radius);
        text-align: center;
        box-shadow: var(--shadow-light);
    }
    
    /* Responsive grids */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }
    
    @media (max-width: 1024px) {
        .grid-4 { grid-template-columns: repeat(2, 1fr); }
        .grid-3 { grid-template-columns: 1fr 1fr; }
    }
    
    @media (max-width: 640px) {
        .grid-4, .grid-3, .grid-2 { grid-template-columns: 1fr; }
        .section-header { padding: 1rem 1.5rem; }
        .upload-container { padding: 1rem; }
    }
    
    /* Remove extra spacing */
    .element-container {
        margin-bottom: 0 !important;
    }
    
    /* Ensure proper mobile layout */
    @media (max-width: 768px) {
        .stColumn {
            padding: 0.5rem !important;
        }
        
        .hero-title {
            font-size: 2rem !important;
        }
        
        .section-header {
            font-size: 1.1rem !important;
            padding: 1rem 1.2rem !important;
        }
        
        .metric-card {
            padding: 1.2rem !important;
        }
        
        .status-indicator {
            font-size: 0.9rem !important;
            padding: 0.6rem 1.2rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client from environment variable
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found in environment variables. Please check your .env file.")
        st.stop()
    return openai.OpenAI(api_key=api_key)

client = get_openai_client()

# Clean, professional hero section
st.markdown("""
<div class="hero-section">
    <div class="hero-title">AI Footwear Quality Control Inspector</div>
</div>
""", unsafe_allow_html=True)

# Function to encode image
def encode_image(image):
    """Convert PIL image to base64 string for OpenAI API"""
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

# Professional QC Analysis function
def analyze_shoe_image(client, image, angle_name, style_number="", color="", po_number=""):
    """Analyze shoe image using OpenAI GPT-4 Vision API with professional QC expertise"""
    base64_image = encode_image(image)
    
    prompt = f"""
PROFESSIONAL FOOTWEAR QUALITY CONTROL INSPECTION - EXPERT ANALYSIS

INSPECTOR PROFILE:
You are a highly experienced footwear quality control inspector with 15+ years in athletic and fashion footwear manufacturing. You have worked with major brands and understand international quality standards. You are known for your meticulous attention to detail and strict adherence to AQL standards.

CURRENT INSPECTION ASSIGNMENT:
- Order: PO#{po_number}
- Product: {style_number} footwear 
- Color: {color}
- View Angle: {angle_name}
- Quality Standard: AQL 2.5 (Manufacturing Grade A)
- Inspection Type: Pre-shipment final inspection
- Client Requirement: Zero tolerance for critical defects

CRITICAL DEFECT CATEGORIES (REJECT immediately):
- Holes, tears, or punctures in upper materials
- Broken/missing eyelets, hardware, or structural components
- Sole separation or delamination >5mm
- Wrong color/material used
- Size/labeling errors
- Asymmetrical lasting or construction
- Safety hazards (sharp edges, protruding nails)

MAJOR DEFECT CATEGORIES (Count towards rejection limits):
- Stitching defects: skipped stitches, loose threads >5mm, crooked seams
- Material defects: scratches >10mm, scuffs, stains, grain breaks
- Construction issues: uneven toe caps, misaligned panels
- Adhesive residue or excess glue visible
- Minor sole defects, uneven texturing
- Color variation outside acceptable tolerance

MINOR DEFECT CATEGORIES (Count but typically acceptable):
- Light scuffs <5mm, minor scratches
- Loose threads <5mm that can be trimmed
- Slight color variations within tolerance
- Minor stitching irregularities that don't affect function
- Light glue marks that can be cleaned
- Minor material texture variations

INSPECTION PROTOCOL:
1. First scan the overall construction and proportion
2. Examine all visible materials for defects
3. Check all stitching lines and seam quality
4. Inspect hardware, eyelets, and functional components
5. Look for sole attachment and construction issues
6. Verify color consistency and finish quality
7. Note any safety or structural concerns

OUTPUT REQUIREMENTS:
Provide your professional assessment in this EXACT JSON format:

{{
    "angle": "{angle_name}",
    "critical_defects": ["Be specific: location + defect type + severity"],
    "major_defects": ["Include exact location and detailed description"], 
    "minor_defects": ["Precise location and nature of defect"],
    "overall_condition": "Good/Fair/Poor",
    "confidence": "High/Medium/Low",
    "inspection_notes": "Professional summary with any concerns about image quality or recommendations"
}}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=800,
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content
        
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = result_text[start_idx:end_idx]
            return json.loads(json_str)
        else:
            return {
                "angle": angle_name,
                "critical_defects": [],
                "major_defects": [],
                "minor_defects": [],
                "overall_condition": "Fair",
                "confidence": "Low",
                "inspection_notes": "API response parsing failed - raw response logged"
            }
            
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error for {angle_name}: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error analyzing {angle_name}: {str(e)}")
        return None

# Generate comprehensive QC Report
def generate_qc_report(analyses, order_info):
    """Generate final QC report based on all angle analyses and AQL 2.5 standards"""
    all_critical = []
    all_major = []
    all_minor = []
    
    for analysis in analyses:
        if analysis:
            all_critical.extend(analysis.get('critical_defects', []))
            all_major.extend(analysis.get('major_defects', []))
            all_minor.extend(analysis.get('minor_defects', []))
    
    all_critical = list(dict.fromkeys(all_critical))
    all_major = list(dict.fromkeys(all_major))
    all_minor = list(dict.fromkeys(all_minor))
    
    critical_count = len(all_critical)
    major_count = len(all_major)
    minor_count = len(all_minor)
    
    aql_limits = {
        "critical": 0,
        "major": 10,
        "minor": 14
    }
    
    if critical_count > aql_limits["critical"]:
        result = "REJECT"
        reason = f"Critical defects found ({critical_count}) - Zero tolerance policy"
    elif major_count > aql_limits["major"]:
        result = "REJECT" 
        reason = f"Major defects ({major_count}) exceed AQL limit ({aql_limits['major']})"
    elif minor_count > aql_limits["minor"]:
        result = "REWORK"
        reason = f"Minor defects ({minor_count}) exceed AQL limit ({aql_limits['minor']})"
    else:
        result = "ACCEPT"
        reason = "All defects within acceptable AQL 2.5 limits"
    
    return {
        "result": result,
        "reason": reason,
        "critical_count": critical_count,
        "major_count": major_count,
        "minor_count": minor_count,
        "critical_defects": all_critical,
        "major_defects": all_major,
        "minor_defects": all_minor,
        "aql_limits": aql_limits
    }

# Clean PDF generation with mobile-optimized layout
def generate_clean_pdf_report(export_report, po_number, style_number):
    """Generate clean, professional PDF report optimized for mobile viewing"""
    
    try:
        buffer = io.BytesIO()
        
        # Create document with mobile-friendly margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Define professional colors
        brand_blue = colors.Color(0.4, 0.49, 0.91)
        success_green = colors.Color(0.31, 0.78, 0.47)
        warning_orange = colors.Color(1.0, 0.6, 0.0)
        danger_red = colors.Color(1.0, 0.42, 0.42)
        light_gray = colors.Color(0.98, 0.98, 0.98)
        dark_gray = colors.Color(0.33, 0.33, 0.33)
        
        # Clean professional styles
        company_title_style = ParagraphStyle(
            'CompanyTitle',
            parent=styles['Normal'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=brand_blue,
            fontName='Helvetica-Bold'
        )
        
        report_title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=dark_gray,
            fontName='Helvetica-Bold'
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=brand_blue,
            fontName='Helvetica-Bold'
        )
        
        # Dynamic result styles
        result_style_accept = ParagraphStyle(
            'ResultAccept',
            parent=styles['Normal'],
            fontSize=20,
            alignment=TA_CENTER,
            textColor=success_green,
            fontName='Helvetica-Bold',
            spaceAfter=15
        )
        
        result_style_reject = ParagraphStyle(
            'ResultReject',
            parent=styles['Normal'],
            fontSize=20,
            alignment=TA_CENTER,
            textColor=danger_red,
            fontName='Helvetica-Bold',
            spaceAfter=15
        )
        
        result_style_rework = ParagraphStyle(
            'ResultRework',
            parent=styles['Normal'],
            fontSize=20,
            alignment=TA_CENTER,
            textColor=warning_orange,
            fontName='Helvetica-Bold',
            spaceAfter=15
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName='Helvetica',
            textColor=dark_gray
        )
        
        # Get report data
        inspection_data = export_report['inspection_summary']
        defect_data = export_report['defect_summary']
        defects = export_report['defect_details']
        
        # Clean header
        elements.append(Paragraph("GRAND STEP (H.K.) LTD", company_title_style))
        elements.append(Spacer(1, 10))
        
        # Report title
        elements.append(Paragraph("QUALITY CONTROL INSPECTION REPORT", report_title_style))
        elements.append(Spacer(1, 20))
        
        # Result banner
        result_text = f"FINAL RESULT: {inspection_data['final_result']}"
        if inspection_data['final_result'] == 'ACCEPT':
            elements.append(Paragraph(result_text, result_style_accept))
        elif inspection_data['final_result'] == 'REJECT':
            elements.append(Paragraph(result_text, result_style_reject))
        else:  # REWORK
            elements.append(Paragraph(result_text, result_style_rework))
        
        # Decision rationale
        elements.append(Paragraph(f"Decision Rationale: {export_report['decision_rationale']}", body_style))
        elements.append(Spacer(1, 20))
        
        # Order Information
        elements.append(Paragraph("ORDER INFORMATION", section_header_style))
        
        order_data = [
            ['PO Number', inspection_data['po_number']],
            ['Style Number', inspection_data['style_number']],
            ['Color', inspection_data['color']],
            ['Customer', inspection_data['customer']],
            ['Inspector', inspection_data['inspector']],
            ['Inspection Date', inspection_data['inspection_date']],
            ['Standard', inspection_data['inspection_standard']]
        ]
        
        # Mobile-optimized table
        order_table = Table(order_data, colWidths=[4*cm, 7*cm])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), brand_blue),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('BACKGROUND', (1, 0), (1, -1), light_gray),
            ('TEXTCOLOR', (1, 0), (1, -1), dark_gray),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.9, 0.9, 0.9))
        ]))
        elements.append(order_table)
        elements.append(Spacer(1, 20))
        
        # Defect Summary
        elements.append(Paragraph("DEFECT SUMMARY (AQL 2.5 STANDARD)", section_header_style))
        
        def get_status_color(count, limit):
            if count > limit:
                return danger_red, colors.Color(1.0, 0.95, 0.95)
            else:
                return success_green, colors.Color(0.95, 1.0, 0.95)
        
        critical_color, critical_bg = get_status_color(defect_data['critical_count'], defect_data['aql_limits']['critical'])
        major_color, major_bg = get_status_color(defect_data['major_count'], defect_data['aql_limits']['major'])
        minor_color, minor_bg = get_status_color(defect_data['minor_count'], defect_data['aql_limits']['minor'])
        
        summary_data = [
            ['Defect Type', 'Count', 'AQL Limit', 'Status'],
            ['Critical Defects', str(defect_data['critical_count']), str(defect_data['aql_limits']['critical']), 
             'FAIL' if defect_data['critical_count'] > defect_data['aql_limits']['critical'] else 'PASS'],
            ['Major Defects', str(defect_data['major_count']), str(defect_data['aql_limits']['major']), 
             'FAIL' if defect_data['major_count'] > defect_data['aql_limits']['major'] else 'PASS'],
            ['Minor Defects', str(defect_data['minor_count']), str(defect_data['aql_limits']['minor']), 
             'FAIL' if defect_data['minor_count'] > defect_data['aql_limits']['minor'] else 'PASS']
        ]
        
        # Mobile-friendly summary table
        summary_table = Table(summary_data, colWidths=[3.5*cm, 2*cm, 2*cm, 2*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), brand_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, 1), critical_bg),
            ('TEXTCOLOR', (3, 1), (3, 1), critical_color),
            ('BACKGROUND', (0, 2), (-1, 2), major_bg),
            ('TEXTCOLOR', (3, 2), (3, 2), major_color),
            ('BACKGROUND', (0, 3), (-1, 3), minor_bg),
            ('TEXTCOLOR', (3, 3), (3, 3), minor_color),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.9, 0.9, 0.9))
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Defect Details
        def add_defect_section(title, defect_list, color):
            if defect_list:
                elements.append(Paragraph(f"{title.upper()}", section_header_style))
                for i, defect in enumerate(defect_list, 1):
                    defect_text = f"{i}. {defect}"
                    defect_style = ParagraphStyle(
                        f'{title}Item',
                        parent=body_style,
                        leftIndent=10,
                        spaceAfter=4,
                        textColor=color
                    )
                    elements.append(Paragraph(defect_text, defect_style))
                elements.append(Spacer(1, 10))
        
        add_defect_section("Critical Defects", defects['critical_defects'], danger_red)
        add_defect_section("Major Defects", defects['major_defects'], warning_orange)  
        add_defect_section("Minor Defects", defects['minor_defects'], brand_blue)
        
        if not any([defects['critical_defects'], defects['major_defects'], defects['minor_defects']]):
            no_defects_style = ParagraphStyle(
                'NoDefects',
                parent=body_style,
                fontSize=12,
                textColor=success_green,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                spaceAfter=20
            )
            elements.append(Paragraph("✓ No defects detected in any view angle", no_defects_style))
        
        # Clean footer
        elements.append(Spacer(1, 30))
        
        # Footer with company information
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=brand_blue,
            fontName='Helvetica',
            leading=12
        )
        
        footer_text = f"""
        <para align="center">
        <b>GRAND STEP (H.K.) LTD</b><br/>
        AI Footwear Quality Control Inspector<br/>
        Report Generated: {inspection_data['inspection_date']}<br/>
        Technology: OpenAI GPT-4 Vision API | AQL 2.5 Compliance
        </para>
        """
        elements.append(Paragraph(footer_text, footer_style))
        
        # Build the PDF
        doc.build(elements)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

# Order Information Section
st.markdown('<div class="section-header">📋 Order Information</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    po_number = st.text_input("PO Number", value="0144540", help="Purchase Order Number")
    customer = st.text_input("Customer", value="MIA", help="Customer/Brand Name")
    
with col2:
    style_number = st.text_input("Style Number", value="GS1412401B", help="Product Style Code")
    color = st.text_input("Color", value="PPB", help="Product Color Code")
    
with col3:
    inspector = st.text_input("Inspector Name", value="AI Inspector", help="QC Inspector Name")
    inspection_date = st.date_input("Inspection Date", value=datetime.now().date())

# Image Upload Section
st.markdown('<div class="section-header">📸 Multi-Angle Image Analysis</div>', unsafe_allow_html=True)

# Upload instruction
st.markdown("""
<div style="
    background: rgba(102, 126, 234, 0.1);
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 1.5rem;
">
    <div style="font-size: 1.2rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
        Multi-Angle Quality Inspection
    </div>
    <div style="color: #6b7280; font-size: 0.95rem;">
        Upload high-resolution images from different angles for comprehensive analysis
    </div>
</div>
""", unsafe_allow_html=True)

# Image upload grid
col1, col2, col3, col4 = st.columns(4)

uploaded_images = {}

with col1:
    st.markdown('<div class="angle-header">📐 Front View</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    front_image = st.file_uploader(
        "Upload Front View",
        type=['png', 'jpg', 'jpeg'],
        key="front",
        help="Toe cap, laces, tongue view"
    )
    if front_image:
        uploaded_images["Front View"] = front_image
        st.image(Image.open(front_image), caption="Front View", use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="angle-header">🔄 Back View</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    back_image = st.file_uploader(
        "Upload Back View",
        type=['png', 'jpg', 'jpeg'],
        key="back",
        help="Heel, counter, back seam view"
    )
    if back_image:
        uploaded_images["Back View"] = back_image
        st.image(Image.open(back_image), caption="Back View", use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="angle-header">⬅️ Left Side</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    left_image = st.file_uploader(
        "Upload Left Side",
        type=['png', 'jpg', 'jpeg'],
        key="left",
        help="Left profile view"
    )
    if left_image:
        uploaded_images["Left Side"] = left_image
        st.image(Image.open(left_image), caption="Left Side", use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="angle-header">➡️ Right Side</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    right_image = st.file_uploader(
        "Upload Right Side",
        type=['png', 'jpg', 'jpeg'],
        key="right",
        help="Right profile view"
    )
    if right_image:
        uploaded_images["Right Side"] = right_image
        st.image(Image.open(right_image), caption="Right Side", use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Upload status
if uploaded_images:
    st.markdown(f"""
    <div class="status-indicator status-success" style="margin: 1.5rem 0; width: 100%;">
        ✅ {len(uploaded_images)} images uploaded successfully
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="
        text-align: center;
        padding: 2rem;
        background: rgba(249, 250, 251, 0.8);
        border: 2px dashed rgba(156, 163, 175, 0.4);
        border-radius: 16px;
        margin: 1.5rem 0;
    ">
        <div style="font-size: 2rem; margin-bottom: 0.8rem; opacity: 0.6;">📤</div>
        <div style="font-size: 1rem; color: #6b7280; font-weight: 500;">
            Please upload at least 2 images from different angles to begin inspection
        </div>
    </div>
    """, unsafe_allow_html=True)

# Analysis Section
if len(uploaded_images) >= 2:
    if st.button("🚀 Start AI Quality Inspection", type="primary", width='stretch'):
        
        # Loading header
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        ">
            <div style="font-size: 1.3rem; font-weight: 600;">🤖 AI Analysis in Progress</div>
            <div style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">
                Processing your quality inspection images
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress tracking
        total_images = len(uploaded_images)
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        analyses = []
        
        # Analyze each image
        for idx, (angle_name, uploaded_file) in enumerate(uploaded_images.items()):
            status_placeholder.markdown(f"""
            <div class="status-indicator status-warning" style="margin: 1rem 0; width: 100%;">
                🔍 Analyzing {angle_name}... ({idx+1}/{total_images})
            </div>
            """, unsafe_allow_html=True)
            
            image = Image.open(uploaded_file)
            analysis = analyze_shoe_image(
                client, 
                image, 
                angle_name, 
                style_number, 
                color, 
                po_number
            )
            analyses.append(analysis)
            
            progress_bar.progress((idx + 1) / total_images)
        
        # Completion status
        status_placeholder.markdown("""
        <div class="status-indicator status-success" style="margin: 1rem 0; width: 100%;">
            ✅ Analysis complete! Generating report...
        </div>
        """, unsafe_allow_html=True)
        
        # Generate final report
        order_info = {
            "po_number": po_number,
            "style_number": style_number,
            "color": color,
            "customer": customer,
            "inspector": inspector,
            "inspection_date": inspection_date.strftime("%Y-%m-%d")
        }
        
        final_report = generate_qc_report(analyses, order_info)
        
        # Results section
        st.markdown("""
        <div style="
            background: rgba(248, 250, 252, 0.9);
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(226, 232, 240, 0.8);
        ">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="
                    font-size: 1.8rem; 
                    font-weight: 700; 
                    color: #1e40af; 
                    margin-bottom: 0.5rem;
                ">
                    Quality Control Report
                </div>
                <div style="font-size: 0.95rem; color: #6b7280;">
                    AQL 2.5 compliance analysis completed
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Result display
        result_colors = {
            "ACCEPT": ("#10b981", "#dcfce7", "#065f46"),
            "REWORK": ("#f59e0b", "#fef3c7", "#92400e"), 
            "REJECT": ("#ef4444", "#fecaca", "#991b1b")
        }
        
        bg_color, light_bg, text_color = result_colors[final_report['result']]
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="
                background: {light_bg};
                border: 2px solid {bg_color};
                border-left: 6px solid {bg_color};
            ">
                <div style="font-size: 1rem; color: {text_color}; font-weight: 600; margin-bottom: 0.5rem;">
                    FINAL RESULT
                </div>
                <div style="font-size: 2rem; font-weight: 800; color: {bg_color};">
                    {final_report['result']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1rem; font-weight: 600; color: #374151; margin-bottom: 0.8rem;">
                    Decision Rationale
                </div>
                <div style="font-size: 0.9rem; color: #6b7280; line-height: 1.5;">
                    {final_report['reason']}
                </div>
                <div style="font-size: 0.8rem; color: #9ca3af; margin-top: 0.8rem; font-style: italic;">
                    Inspected on {inspection_date.strftime('%B %d, %Y')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Metrics dashboard
        st.markdown("""
        <div style="
            margin: 2rem 0 1.5rem 0;
            text-align: center;
            font-size: 1.3rem;
            font-weight: 700;
            color: #1f2937;
        ">
            Defect Analysis
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        metrics_data = [
            ("Critical", final_report['critical_count'], final_report['aql_limits']['critical'], "#ef4444"),
            ("Major", final_report['major_count'], final_report['aql_limits']['major'], "#f59e0b"),
            ("Minor", final_report['minor_count'], final_report['aql_limits']['minor'], "#3b82f6")
        ]
        
        for i, (col, (label, count, limit, color)) in enumerate(zip([col1, col2, col3], metrics_data)):
            with col:
                over_limit = count > limit
                status_color = "#ef4444" if over_limit else "#10b981"
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid {color};">
                    <div style="font-size: 2rem; font-weight: 800; color: {color}; margin-bottom: 0.5rem;">
                        {count}
                    </div>
                    <div style="font-size: 1rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
                        {label}
                    </div>
                    <div style="
                        font-size: 0.8rem; 
                        color: {status_color}; 
                        font-weight: 600;
                        background: rgba({'239,68,68' if over_limit else '16,185,129'}, 0.1);
                        padding: 0.3rem 0.6rem;
                        border-radius: 12px;
                        display: inline-block;
                    ">
                        Limit: {limit} | {'OVER' if over_limit else 'OK'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed defects
        if any([final_report['critical_defects'], final_report['major_defects'], final_report['minor_defects']]):
            st.markdown("""
            <div style="
                margin: 2rem 0 1.5rem 0;
                text-align: center;
                font-size: 1.3rem;
                font-weight: 700;
                color: #1f2937;
            ">
                Detailed Defect Analysis
            </div>
            """, unsafe_allow_html=True)
            
            # Critical defects
            if final_report['critical_defects']:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #fef2f2, #fecaca);
                    border: 2px solid #ef4444;
                    border-radius: 16px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                ">
                    <div style="
                        font-size: 1.1rem; 
                        font-weight: 700; 
                        color: #991b1b; 
                        margin-bottom: 1rem;
                    ">
                        🚨 Critical Defects
                    </div>
                """, unsafe_allow_html=True)
                
                for i, defect in enumerate(final_report['critical_defects'], 1):
                    st.markdown(f"""
                    <div style="
                        background: rgba(255, 255, 255, 0.7);
                        border-left: 4px solid #ef4444;
                        padding: 0.8rem 1rem;
                        margin: 0.6rem 0;
                        border-radius: 0 8px 8px 0;
                    ">
                        <strong style="color: #991b1b;">{i}.</strong> 
                        <span style="color: #374151;">{defect}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Major defects
            if final_report['major_defects']:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #fffbeb, #fef3c7);
                    border: 2px solid #f59e0b;
                    border-radius: 16px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                ">
                    <div style="
                        font-size: 1.1rem; 
                        font-weight: 700; 
                        color: #92400e; 
                        margin-bottom: 1rem;
                    ">
                        ⚠️ Major Defects
                    </div>
                """, unsafe_allow_html=True)
                
                for i, defect in enumerate(final_report['major_defects'], 1):
                    st.markdown(f"""
                    <div style="
                        background: rgba(255, 255, 255, 0.7);
                        border-left: 4px solid #f59e0b;
                        padding: 0.8rem 1rem;
                        margin: 0.6rem 0;
                        border-radius: 0 8px 8px 0;
                    ">
                        <strong style="color: #92400e;">{i}.</strong> 
                        <span style="color: #374151;">{defect}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Minor defects
            if final_report['minor_defects']:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #eff6ff, #dbeafe);
                    border: 2px solid #3b82f6;
                    border-radius: 16px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                ">
                    <div style="
                        font-size: 1.1rem; 
                        font-weight: 700; 
                        color: #1e40af; 
                        margin-bottom: 1rem;
                    ">
                        ℹ️ Minor Defects
                    </div>
                """, unsafe_allow_html=True)
                
                for i, defect in enumerate(final_report['minor_defects'], 1):
                    st.markdown(f"""
                    <div style="
                        background: rgba(255, 255, 255, 0.7);
                        border-left: 4px solid #3b82f6;
                        padding: 0.8rem 1rem;
                        margin: 0.6rem 0;
                        border-radius: 0 8px 8px 0;
                    ">
                        <strong style="color: #1e40af;">{i}.</strong> 
                        <span style="color: #374151;">{defect}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # No defects
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #ecfdf5, #d1fae5);
                border: 2px solid #10b981;
                border-radius: 16px;
                padding: 2rem;
                margin: 1.5rem 0;
                text-align: center;
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
                <div style="
                    font-size: 1.3rem; 
                    font-weight: 700; 
                    color: #065f46; 
                    margin-bottom: 0.5rem;
                ">
                    Perfect Quality
                </div>
                <div style="font-size: 0.95rem; color: #059669;">
                    No defects detected in any view angle
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Individual angle analysis
        st.markdown("""
        <div style="
            margin: 2rem 0 1.5rem 0;
            text-align: center;
            font-size: 1.3rem;
            font-weight: 700;
            color: #1f2937;
        ">
            Analysis by View Angle
        </div>
        """, unsafe_allow_html=True)
        
        for angle_name, analysis in zip(uploaded_images.keys(), analyses):
            if analysis:
                condition_colors = {
                    "Good": ("#10b981", "#dcfce7"), 
                    "Fair": ("#f59e0b", "#fef3c7"), 
                    "Poor": ("#ef4444", "#fecaca")
                }
                condition_icons = {"Good": "🟢", "Fair": "🟡", "Poor": "🔴"}
                
                condition = analysis['overall_condition']
                color, bg_color = condition_colors.get(condition, ("#6b7280", "#f9fafb"))
                icon = condition_icons.get(condition, "⚫")
                
                with st.expander(f"{icon} {angle_name} - {condition} (Confidence: {analysis['confidence']})", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        defect_sections = [
                            ("Critical", analysis['critical_defects'], "#ef4444"),
                            ("Major", analysis['major_defects'], "#f59e0b"),
                            ("Minor", analysis['minor_defects'], "#3b82f6")
                        ]
                        
                        has_defects = False
                        for section_name, defect_list, section_color in defect_sections:
                            if defect_list:
                                has_defects = True
                                st.markdown(f"""
                                <div style="
                                    border-left: 4px solid {section_color};
                                    padding: 0.6rem 1rem;
                                    margin: 0.6rem 0;
                                    background: rgba(248, 250, 252, 0.8);
                                    border-radius: 0 6px 6px 0;
                                ">
                                    <strong style="color: {section_color};">{section_name}:</strong>
                                    <span style="color: #374151;"> {' | '.join(defect_list)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if not has_defects:
                            st.markdown("""
                            <div style="
                                background: linear-gradient(135deg, #ecfdf5, #d1fae5);
                                border-left: 4px solid #10b981;
                                padding: 0.8rem 1rem;
                                border-radius: 0 8px 8px 0;
                                margin: 0.8rem 0;
                            ">
                                <strong style="color: #065f46;">✅ No defects detected</strong>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if analysis.get('inspection_notes'):
                            st.markdown(f"""
                            <div style="
                                background: rgba(59, 130, 246, 0.05);
                                border: 1px solid rgba(59, 130, 246, 0.2);
                                border-radius: 6px;
                                padding: 0.8rem;
                                margin-top: 0.8rem;
                            ">
                                <strong style="color: #1e40af;">Notes:</strong>
                                <span style="color: #374151;"> {analysis['inspection_notes']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        uploaded_file = uploaded_images[angle_name]
                        thumb_image = Image.open(uploaded_file)
                        st.markdown(f"""
                        <div style="
                            border: 3px solid {color};
                            border-radius: 8px;
                            padding: 0.3rem;
                            background: {bg_color};
                        ">
                        """, unsafe_allow_html=True)
                        st.image(thumb_image, caption=f"{angle_name}", use_column_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
        
        # PDF Export Section
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 16px;
            margin: 2rem 0;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        ">
            <div style="font-size: 1.5rem; margin-bottom: 0.8rem;">📄</div>
            <div style="font-size: 1.3rem; font-weight: 700; margin-bottom: 0.5rem;">
                Professional Report
            </div>
            <div style="font-size: 0.9rem; opacity: 0.9;">
                Generate PDF documentation for your records
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Prepare report data
        export_report = {
            "inspection_summary": {
                "inspection_date": order_info["inspection_date"],
                "inspector": order_info["inspector"],
                "customer": order_info["customer"],
                "po_number": order_info["po_number"],
                "style_number": order_info["style_number"],
                "color": order_info["color"],
                "final_result": final_report['result'],
                "inspection_standard": "AQL 2.5"
            },
            "defect_summary": {
                "critical_count": final_report['critical_count'],
                "major_count": final_report['major_count'],
                "minor_count": final_report['minor_count'],
                "aql_limits": final_report['aql_limits']
            },
            "defect_details": {
                "critical_defects": final_report['critical_defects'],
                "major_defects": final_report['major_defects'],
                "minor_defects": final_report['minor_defects']
            },
            "angle_analyses": analyses,
            "decision_rationale": final_report['reason']
        }
        
        # Generate PDF
        with st.spinner("🎨 Generating PDF report..."):
            pdf_bytes = generate_clean_pdf_report(export_report, po_number, style_number)
        
        if pdf_bytes:
            filename = f"QC_Report_{po_number}_{style_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    width='stretch',
                    type="primary"
                )
            
            st.markdown("""
            <div style="
                text-align: center;
                background: linear-gradient(135deg, #ecfdf5, #d1fae5);
                border: 2px solid #10b981;
                border-radius: 12px;
                padding: 1.2rem;
                margin: 1rem 0;
            ">
                <div style="color: #065f46; font-weight: 600;">
                    ✅ PDF report generated successfully!
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                text-align: center;
                background: linear-gradient(135deg, #fef2f2, #fecaca);
                border: 2px solid #ef4444;
                border-radius: 12px;
                padding: 1.2rem;
                margin: 1rem 0;
            ">
                <div style="color: #991b1b; font-weight: 600;">
                    ❌ Failed to generate PDF report
                </div>
            </div>
            """, unsafe_allow_html=True)

# Clean footer
st.markdown("""
<div class="footer">
    <div style="
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    ">
        GRAND STEP (H.K.) LTD
    </div>
    <div style="color: #6b7280; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0.8rem;">
        Professional Footwear Manufacturing & Quality Control
    </div>
    <div style="color: #9ca3af; font-size: 0.85rem; line-height: 1.5;">
        AI-Powered Quality Inspection System<br/>
        Transforming Manufacturing Excellence
    </div>
</div>
""", unsafe_allow_html=True)
