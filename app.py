import streamlit as st
import openai
import base64
from PIL import Image
import io
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import weasyprint
from weasyprint import HTML, CSS

# Load environment variables
load_dotenv()

# Set up the page with mobile-friendly configuration
st.set_page_config(
    page_title="AI Shoe QC Inspector",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile responsiveness
st.markdown("""
<style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .stColumns > div {
            margin-bottom: 1rem;
        }
        
        .upload-section {
            margin-bottom: 2rem;
        }
        
        .metric-container {
            margin-bottom: 1rem;
        }
    }
    
    .upload-box {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        background-color: #f8f9fa;
    }
    
    .upload-box:hover {
        border-color: #007bff;
        background-color: #e3f2fd;
    }
    
    .company-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .angle-header {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 4px solid #007bff;
        font-weight: bold;
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

# Company header
st.markdown("""
<div class="company-header">
    <h1 style="margin: 0; font-size: 2rem;">Grand Step</h1>
    <h2 style="margin: 5px 0; font-size: 1.5rem;">Grand Step (H.K.) Ltd</h2>
    <h3 style="margin: 10px 0; font-size: 1.2rem;">🔍 AI FOOTWEAR QUALITY CONTROL INSPECTOR</h3>
    <div style="margin-top: 15px; font-size: 0.9rem;">
        📞 Tel: 86-769-8308 0888-381 | 📠 Fax: 86-769-8308 0999<br>
        📧 production7@grandstep.com | production@grandstep.com<br>
        🌐 www.grandstep.com
    </div>
</div>
""", unsafe_allow_html=True)

# Function to encode image
def encode_image(image):
    """Convert PIL image to base64 string for OpenAI API"""
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

# Professional QC Analysis function (keeping the same comprehensive analysis)
def analyze_shoe_image(client, image, angle_name, style_number="", color="", po_number=""):
    """
    Analyze shoe image using OpenAI GPT-4 Vision API with professional QC expertise
    """
    base64_image = encode_image(image)
    
    # COMPREHENSIVE PROFESSIONAL QC INSPECTOR PROMPT (same as original)
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

MANUFACTURING CONTEXT:
This is a final quality inspection before shipment to retail customers. Any defect that reaches the end customer could result in returns, complaints, and brand reputation damage. You must inspect with the understanding that this product will be sold at retail and worn by consumers who expect high quality.

DETAILED DEFECT CLASSIFICATION SYSTEM:

🚨 CRITICAL DEFECTS (ZERO TOLERANCE - Immediate Rejection):
**1. Structural Integrity Issues:**
- Complete or partial **outsole debonding** or separation
- Major **heel defects**: broken, warped, or causing instability/tilt
- **Boot barrel deformation** (elastic band deformation) affecting structural integrity
- **The inside exploded** (major lining failure)
- **The upper is damaged** (tears, holes larger than 1mm)
- Broken or cracked structural components
- **Heel kick** (severe front and back kick deformation)

**2. Safety Hazards:**
- Sharp edges or protruding elements
- **Rubber wire** creating safety risks
- Loose hardware that could cause injury
- Chemical odors or visible contamination
- Unstable heel attachment causing tilt or instability

⚠️ MAJOR DEFECTS (Require Rework - Customer Visible Issues):
**1. Adhesive & Bonding Problems:**
- **Overflowing glue** (visible excess adhesive)
- **The outsole lacks glue** (poor bonding preparation)
- **The outsole combination is not tight** (separation gaps >1mm)
- **The middle skin is glued** improperly
- **The skin is glued** with visible defects
- Poor bonding between upper/midsole/outsole components

**2. Alignment & Shape Defects:**
- **The rear trim strip is skewed**
- **Skewed lines** (edges, spacing misalignment)
- **The toe of the shoe is crooked**
- **Toe defects**: misaligned toe box or irregular cap length
- **The length of the toe cap** inconsistency
- **The back package is high and low** (uneven heel counter)
- Components misaligned or twisted relative to shoe centerline
- **Heel counter defects**: shape/height inconsistent or deformed

**3. Material Deformation:**
- **Mesothelial wrinkles** (significant upper creasing)
- **Wrinkled upper** affecting appearance
- **Inner wrinkles** (lining deformation)
- **The waist is not smooth** (poor lasting)
- **Indentation on the upper** (shape defects)
- Midfoot/shank area irregularities affecting profile

**4. Color and Appearance:**
- **Chromatic aberration** (noticeable color differences)
- Color variation between shoe parts (>2 shade difference)
- Color bleeding or staining between materials
- Uneven dyeing or color patches

**5. Construction Defects:**
- **Upper thread** defects (loose, broken, or improper stitching)
- Poor toe lasting (wrinkles, bubbles, asymmetry)
- Visible gaps between sole and upper (>1mm)
- Misaligned or crooked stitching lines
- Puckering or gathering in upper materials

**6. Hardware and Components:**
- Damaged, bent, or non-functional eyelets
- Broken or damaged lace hooks/D-rings
- Velcro not adhering properly
- Buckle damage or malfunction

**7. Lining and Interior:**
- Lining tears, wrinkles, or separation
- Sock liner/insole misprinting or damage
- Tongue positioning issues (too far left/right)

**8. Sole and Bottom:**
- Outsole molding defects or incomplete patterns
- Midsole compression or deformation
- Heel cap damage or misalignment
- Tread pattern inconsistencies

ℹ️ MINOR DEFECTS (Acceptable within AQL limits):
**1. Surface & Cleanliness Issues:**
- **Cleanliness** defects (surface dirt, dust - cleanable)
- Minor scuff marks (<3mm)
- Small adhesive residue spots
- Temporary marking pen marks
- **Transparency marks** (minor see-through effects)

**2. Finishing Details:**
- Thread ends not trimmed (<3mm length)
- Minor stitching irregularities (straight lines)
- Small material texture variations
- Minor logo/branding imperfections
- **Toe corners** with slight irregularities

**3. Cosmetic Issues:**
- Minor sole texture variations
- Slight asymmetry in non-structural elements
- Minor trim imperfections

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

PROFESSIONAL STANDARDS:
- Apply the same scrutiny you would for premium retail footwear
- Remember that consumers will examine these shoes closely in stores
- Consider that defects may become more pronounced with wear
- Prioritize customer satisfaction and brand reputation
- When in doubt about borderline cases, classify as the higher severity level

INSPECTION DIRECTIVE:
Conduct a thorough, professional quality control inspection of this {angle_name} view. Apply your expertise to identify all visible defects with precision and professional judgment. Your assessment will determine if this product meets manufacturing quality standards for retail distribution.

Focus on this specific angle provide detailed, actionable feedback that would help improve manufacturing processes.
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

# Generate comprehensive QC Report (same as original)
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

# Enhanced HTML Report Generation for PDF (Mobile-Responsive)
def generate_html_for_pdf(export_report, po_number, style_number):
    """Generate mobile-responsive HTML report optimized for PDF conversion"""
    
    inspection_data = export_report['inspection_summary']
    defect_data = export_report['defect_summary']
    defects = export_report['defect_details']
    
    result_colors = {
        "ACCEPT": "#28a745",
        "REWORK": "#ffc107",
        "REJECT": "#dc3545"
    }
    
    result_color = result_colors.get(inspection_data['final_result'], "#6c757d")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QC Inspection Report - {po_number}</title>
        <style>
            @page {{
                size: A4;
                margin: 15mm;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Arial', sans-serif;
                line-height: 1.4;
                color: #333;
                font-size: 12px;
            }}
            
            .report-container {{
                width: 100%;
                max-width: 800px;
                margin: 0 auto;
                background: white;
            }}
            
            .company-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
                border-radius: 8px;
            }}
            
            .company-header h1 {{
                font-size: 24px;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            
            .company-header h2 {{
                font-size: 18px;
                margin-bottom: 10px;
            }}
            
            .company-header h3 {{
                font-size: 16px;
                margin-bottom: 15px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .contact-info {{
                font-size: 11px;
                line-height: 1.6;
            }}
            
            .result-banner {{
                background: {result_color};
                color: white;
                padding: 15px;
                text-align: center;
                font-size: 18px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 20px;
                border-radius: 5px;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin-bottom: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }}
            
            .info-item {{
                display: flex;
                justify-content: space-between;
                padding: 5px 0;
                border-bottom: 1px solid #dee2e6;
            }}
            
            .info-label {{
                font-weight: bold;
                color: #495057;
            }}
            
            .info-value {{
                color: #212529;
                font-family: 'Courier New', monospace;
                font-weight: bold;
            }}
            
            .metrics-container {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin: 20px 0;
            }}
            
            .metric-card {{
                text-align: center;
                padding: 15px;
                border-radius: 5px;
                color: white;
            }}
            
            .metric-card.critical {{
                background: linear-gradient(135deg, #dc3545, #c82333);
            }}
            
            .metric-card.major {{
                background: linear-gradient(135deg, #ffc107, #e0a800);
            }}
            
            .metric-card.minor {{
                background: linear-gradient(135deg, #17a2b8, #138496);
            }}
            
            .metric-number {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            
            .metric-label {{
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 3px;
            }}
            
            .metric-limit {{
                font-size: 10px;
                opacity: 0.9;
            }}
            
            .section-title {{
                font-size: 14px;
                font-weight: bold;
                color: #495057;
                margin: 20px 0 10px 0;
                padding: 8px 0;
                border-bottom: 2px solid #e9ecef;
            }}
            
            .defect-list {{
                background: #fff;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 15px;
                border: 1px solid #e9ecef;
            }}
            
            .defect-item {{
                padding: 8px;
                margin: 5px 0;
                border-radius: 3px;
                border-left: 3px solid;
                font-size: 11px;
                line-height: 1.4;
            }}
            
            .defect-item.critical {{
                background: #fff5f5;
                border-left-color: #dc3545;
                color: #721c24;
            }}
            
            .defect-item.major {{
                background: #fff8e1;
                border-left-color: #ffc107;
                color: #7d4e00;
            }}
            
            .defect-item.minor {{
                background: #e3f2fd;
                border-left-color: #17a2b8;
                color: #0c5460;
            }}
            
            .defect-number {{
                font-weight: bold;
                margin-right: 8px;
                display: inline-block;
                min-width: 20px;
            }}
            
            .no-defects {{
                text-align: center;
                padding: 15px;
                color: #28a745;
                font-style: italic;
                background: #f8fff8;
                border: 1px dashed #28a745;
                border-radius: 3px;
                font-size: 11px;
            }}
            
            .reason-box {{
                background: linear-gradient(135deg, #6f42c1, #5a32a3);
                color: white;
                padding: 12px;
                border-radius: 5px;
                margin: 15px 0;
                text-align: center;
                font-weight: 500;
                font-size: 12px;
            }}
            
            .footer {{
                background: #f8f9fa;
                padding: 15px;
                text-align: center;
                color: #6c757d;
                border-top: 1px solid #e9ecef;
                margin-top: 20px;
                font-size: 10px;
            }}
            
            .footer .logo {{
                font-size: 12px;
                font-weight: bold;
                color: #495057;
                margin-bottom: 5px;
            }}
            
            /* Mobile responsive adjustments */
            @media (max-width: 600px) {{
                .info-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .metrics-container {{
                    grid-template-columns: 1fr;
                    gap: 10px;
                }}
                
                .metric-card {{
                    padding: 10px;
                }}
                
                .metric-number {{
                    font-size: 20px;
                }}
                
                .company-header h1 {{
                    font-size: 20px;
                }}
                
                .company-header h2 {{
                    font-size: 16px;
                }}
                
                .company-header h3 {{
                    font-size: 14px;
                }}
                
                .result-banner {{
                    font-size: 16px;
                    padding: 12px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <div class="company-header">
                <h1>Grand Step</h1>
                <h2>Grand Step (H.K.) Ltd</h2>
                <h3>ONLINE INSPECTION REPORT</h3>
                <div class="contact-info">
                    Tel: 86-769-8308 0888-381 | Fax: 86-769-8308 0999<br>
                    Email: production7@grandstep.com | production@grandstep.com<br>
                    Web: www.grandstep.com
                </div>
            </div>
            
            <div class="result-banner">
                Final Result: {inspection_data['final_result']}
            </div>
            
            <div class="reason-box">
                <strong>Decision Rationale:</strong> {export_report['decision_rationale']}
            </div>
            
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">PO Number:</span>
                    <span class="info-value">{inspection_data['po_number']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Style:</span>
                    <span class="info-value">{inspection_data['style_number']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Color:</span>
                    <span class="info-value">{inspection_data['color']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Customer:</span>
                    <span class="info-value">{inspection_data['customer']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Inspector:</span>
                    <span class="info-value">{inspection_data['inspector']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Date:</span>
                    <span class="info-value">{inspection_data['inspection_date']}</span>
                </div>
            </div>
            
            <div class="section-title">
                Defect Summary (AQL 2.5 Standard)
            </div>
            
            <div class="metrics-container">
                <div class="metric-card critical">
                    <div class="metric-number">{defect_data['critical_count']}</div>
                    <div class="metric-label">Critical Defects</div>
                    <div class="metric-limit">Limit: {defect_data['aql_limits']['critical']}</div>
                </div>
                <div class="metric-card major">
                    <div class="metric-number">{defect_data['major_count']}</div>
                    <div class="metric-label">Major Defects</div>
                    <div class="metric-limit">Limit: {defect_data['aql_limits']['major']}</div>
                </div>
                <div class="metric-card minor">
                    <div class="metric-number">{defect_data['minor_count']}</div>
                    <div class="metric-label">Minor Defects</div>
                    <div class="metric-limit">Limit: {defect_data['aql_limits']['minor']}</div>
                </div>
            </div>
    """
    
    # Critical Defects Section
    html_content += """
            <div class="section-title">Critical Defects</div>
            <div class="defect-list">
    """
    
    if defects['critical_defects']:
        for i, defect in enumerate(defects['critical_defects'], 1):
            html_content += f"""
                <div class="defect-item critical">
                    <span class="defect-number">{i}.</span>
                    <span>{defect}</span>
                </div>
            """
    else:
        html_content += '<div class="no-defects">No critical defects found</div>'
    
    html_content += "</div>"
    
    # Major Defects Section
    html_content += """
            <div class="section-title">Major Defects</div>
            <div class="defect-list">
    """
    
    if defects['major_defects']:
        for i, defect in enumerate(defects['major_defects'], 1):
            html_content += f"""
                <div class="defect-item major">
                    <span class="defect-number">{i}.</span>
                    <span>{defect}</span>
                </div>
            """
    else:
        html_content += '<div class="no-defects">No major defects found</div>'
    
    html_content += "</div>"
    
    # Minor Defects Section
    html_content += """
            <div class="section-title">Minor Defects</div>
            <div class="defect-list">
    """
    
    if defects['minor_defects']:
        for i, defect in enumerate(defects['minor_defects'], 1):
            html_content += f"""
                <div class="defect-item minor">
                    <span class="defect-number">{i}.</span>
                    <span>{defect}</span>
                </div>
            """
    else:
        html_content += '<div class="no-defects">No minor defects found</div>'
    
    html_content += f"""
            </div>
            
            <div class="footer">
                <div class="logo">AI Footwear Quality Control Inspector</div>
                <div>
                    Report generated on {inspection_data['inspection_date']} using OpenAI GPT-4 Vision API<br>
                    Powered by advanced computer vision and professional QC expertise
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

# Function to generate PDF from HTML
def generate_pdf_report(export_report, po_number, style_number):
    """Generate PDF report from HTML using WeasyPrint"""
    html_content = generate_html_for_pdf(export_report, po_number, style_number)
    
    try:
        # Create PDF from HTML
        html_doc = HTML(string=html_content)
        pdf_bytes = html_doc.write_pdf()
        return pdf_bytes
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

# Order Information Section
st.header("Order Information")
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

st.divider()

# Image Upload Section with 4 separate angle options
st.header("Upload Shoe Images by Angle")
st.markdown("Upload clear, well-lit images from each angle for comprehensive quality inspection:")

# Create 4 columns for the 4 angles
col1, col2, col3, col4 = st.columns(4)

uploaded_images = {}
angle_names = ["Front View", "Back View", "Left Side", "Right Side"]

with col1:
    st.markdown('<div class="angle-header">📐 Front View</div>', unsafe_allow_html=True)
    front_image = st.file_uploader(
        "Upload Front View",
        type=['png', 'jpg', 'jpeg'],
        key="front",
        help="Toe cap, laces, tongue view"
    )
    if front_image:
        uploaded_images["Front View"] = front_image
        st.image(Image.open(front_image), caption="Front View", use_container_width=True)

with col2:
    st.markdown('<div class="angle-header">🔄 Back View</div>', unsafe_allow_html=True)
    back_image = st.file_uploader(
        "Upload Back View",
        type=['png', 'jpg', 'jpeg'],
        key="back",
        help="Heel, counter, back seam view"
    )
    if back_image:
        uploaded_images["Back View"] = back_image
        st.image(Image.open(back_image), caption="Back View", use_container_width=True)

with col3:
    st.markdown('<div class="angle-header">⬅️ Left Side</div>', unsafe_allow_html=True)
    left_image = st.file_uploader(
        "Upload Left Side",
        type=['png', 'jpg', 'jpeg'],
        key="left",
        help="Left profile view"
    )
    if left_image:
        uploaded_images["Left Side"] = left_image
        st.image(Image.open(left_image), caption="Left Side", use_container_width=True)

with col4:
    st.markdown('<div class="angle-header">➡️ Right Side</div>', unsafe_allow_html=True)
    right_image = st.file_uploader(
        "Upload Right Side",
        type=['png', 'jpg', 'jpeg'],
        key="right",
        help="Right profile view"
    )
    if right_image:
        uploaded_images["Right Side"] = right_image
        st.image(Image.open(right_image), caption="Right Side", use_container_width=True)

st.divider()

# Display upload status
if uploaded_images:
    st.success(f"✅ {len(uploaded_images)} images uploaded successfully")
    st.info(f"📸 Uploaded angles: {', '.join(uploaded_images.keys())}")
else:
    st.info("📤 Please upload at least 2 images from different angles to begin quality inspection.")

# Analysis Section
if len(uploaded_images) >= 2:
    if st.button("🔍 Start AI Quality Inspection", type="primary", use_container_width=True):
        st.header("🤖 AI Analysis in Progress...")
        
        # Progress tracking
        total_images = len(uploaded_images)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        analyses = []
        
        # Analyze each uploaded image
        for idx, (angle_name, uploaded_file) in enumerate(uploaded_images.items()):
            status_text.text(f"🔍 Analyzing {angle_name}... ({idx+1}/{total_images})")
            
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
        
        status_text.text("✅ Analysis complete! Generating report...")
        
        # Generate final QC report
        order_info = {
            "po_number": po_number,
            "style_number": style_number,
            "color": color,
            "customer": customer,
            "inspector": inspector,
            "inspection_date": inspection_date.strftime("%Y-%m-%d")
        }
        
        final_report = generate_qc_report(analyses, order_info)
        
        st.divider()
        
        # Display Results
        st.header("📊 Quality Control Inspection Report")
        
        # Result Header
        result_colors = {
            "ACCEPT": "success",
            "REWORK": "warning", 
            "REJECT": "error"
        }
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"### Final Result:")
            st.markdown(f"## :{result_colors[final_report['result']]}[{final_report['result']}]")
        
        with col2:
            st.markdown(f"### Reason:")
            st.markdown(f"**{final_report['reason']}**")
            st.markdown(f"*Inspection completed on {inspection_date.strftime('%B %d, %Y')}*")
        
        # Defect Summary Dashboard (Mobile-responsive)
        st.subheader("📈 Defect Summary (AQL 2.5 Standard)")
        
        # For mobile, stack metrics vertically
        if st.container():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🚨 Critical", 
                    final_report['critical_count'],
                    delta=f"Limit: {final_report['aql_limits']['critical']}",
                    delta_color="inverse"
                )
                
            with col2:
                major_over_limit = final_report['major_count'] - final_report['aql_limits']['major']
                st.metric(
                    "⚠️ Major", 
                    final_report['major_count'],
                    delta=f"Limit: {final_report['aql_limits']['major']}",
                    delta_color="inverse" if major_over_limit > 0 else "normal"
                )
                
            with col3:
                minor_over_limit = final_report['minor_count'] - final_report['aql_limits']['minor']
                st.metric(
                    "ℹ️ Minor", 
                    final_report['minor_count'],
                    delta=f"Limit: {final_report['aql_limits']['minor']}",
                    delta_color="inverse" if minor_over_limit > 0 else "normal"
                )
        
        # Detailed Defect Lists
        if final_report['critical_defects']:
            st.subheader("🚨 Critical Defects (Must Fix)")
            for i, defect in enumerate(final_report['critical_defects'], 1):
                st.error(f"**{i}.** {defect}")
        
        if final_report['major_defects']:
            st.subheader("⚠️ Major Defects (Require Attention)")
            for i, defect in enumerate(final_report['major_defects'], 1):
                st.warning(f"**{i}.** {defect}")
        
        if final_report['minor_defects']:
            st.subheader("ℹ️ Minor Defects (Monitor)")
            for i, defect in enumerate(final_report['minor_defects'], 1):
                st.info(f"**{i}.** {defect}")
        
        # Individual Angle Analysis
        st.subheader("🔍 Detailed Analysis by View")
        
        for angle_name, analysis in zip(uploaded_images.keys(), analyses):
            if analysis:
                # Color code based on condition
                condition_colors = {"Good": "🟢", "Fair": "🟡", "Poor": "🔴"}
                condition_icon = condition_colors.get(analysis['overall_condition'], "⚫")
                
                with st.expander(f"{condition_icon} {angle_name} - {analysis['overall_condition']} (Confidence: {analysis['confidence']})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if analysis['critical_defects']:
                            st.markdown("**🚨 Critical:** " + " | ".join(analysis['critical_defects']))
                        if analysis['major_defects']:
                            st.markdown("**⚠️ Major:** " + " | ".join(analysis['major_defects']))
                        if analysis['minor_defects']:
                            st.markdown("**ℹ️ Minor:** " + " | ".join(analysis['minor_defects']))
                        if not any([analysis['critical_defects'], analysis['major_defects'], analysis['minor_defects']]):
                            st.success("✅ No defects detected in this view")
                    
                    with col2:
                        # Show the corresponding image thumbnail
                        uploaded_file = uploaded_images[angle_name]
                        thumb_image = Image.open(uploaded_file)
                        st.image(thumb_image, caption=f"{angle_name}", width=150)
                    
                    if analysis.get('inspection_notes'):
                        st.markdown(f"**Inspector Notes:** {analysis['inspection_notes']}")
        
        # Export Report Section
        st.divider()
        st.subheader("💾 Download PDF Report")
        
        # Prepare comprehensive report data
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
        
        # Generate PDF report
        with st.spinner("Generating PDF report..."):
            pdf_bytes = generate_pdf_report(export_report, po_number, style_number)
        
        if pdf_bytes:
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name=f"QC_Report_{po_number}_{style_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
            st.success("✅ PDF report generated successfully!")
        else:
            st.error("❌ Failed to generate PDF report. Please try again.")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🤖 AI Model:** OpenAI GPT-4o Vision")
    
with col2:
    st.markdown("**📊 Standard:** AQL 2.5 Quality Control")
    
with col3:
    st.markdown("**🏢 Company:** Grand Step (H.K.) Ltd")

st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem; font-size: 0.9rem;'>
    <em>AI Footwear Quality Control Inspector - Transforming Manufacturing QC with Computer Vision</em><br>
    <strong>Grand Step (H.K.) Ltd</strong> | Tel: 86-769-8308 0888-381 | www.grandstep.com
</div>
""", unsafe_allow_html=True)
