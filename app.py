import streamlit as st
import openai
import base64
from PIL import Image
import io
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import pdfkit
import webbrowser
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Load environment variables
load_dotenv()

# Set up the page
st.set_page_config(
    page_title="AI Shoe QC Inspector",
    page_icon="👟",
    layout="wide"
)

st.title("🔍 AI Footwear Quality Control Inspector")
st.markdown("*Powered by OpenAI GPT-4 Vision API*")

# Function to encode image
def encode_image(image):
    """Convert PIL image to base64 string for OpenAI API"""
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

# Professional QC Analysis function
def analyze_shoe_image(client, image, angle_name, style_number="", color="", po_number=""):
    """
    Analyze shoe image using OpenAI GPT-4 Vision API with professional QC expertise
    """
    base64_image = encode_image(image)
    
    # COMPREHENSIVE PROFESSIONAL QC INSPECTOR PROMPT
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

ANGLE-SPECIFIC INSPECTION FOCUS:

**FRONT VIEW INSPECTION:**
- Toe cap symmetry and shape consistency
- Lace eyelet alignment and spacing
- Tongue centering and positioning
- Color matching between panels
- Overall toe box shape and lasting quality
- Front stitching line straightness
- Logo placement and quality

**BACK VIEW INSPECTION:**
- Heel counter shape and symmetry
- Back seam alignment and straightness
- Heel tab positioning and attachment
- Ankle collar height consistency
- Back logo/branding placement
- Counter stitching quality
- Heel to sole attachment integrity

**LEFT/RIGHT SIDE INSPECTION:**
- Profile shape consistency and symmetry
- Sole to upper bonding quality
- Waist definition and shaping
- Arch support visibility and positioning
- Side panel alignment and stitching
- Heel pitch and alignment
- Overall silhouette conformity

**TOP VIEW INSPECTION:**
- Tongue positioning and symmetry
- Lace eyelet spacing and alignment
- Upper panel symmetry (left vs right)
- Color consistency across all visible areas
- Stitching line parallelism
- Logo and branding alignment

**SOLE VIEW INSPECTION:**
- Outsole pattern completeness and clarity
- Heel attachment and alignment
- Forefoot flex groove positioning
- Tread depth consistency
- Midsole compression and uniformity
- Any embedded foreign objects
- Sole marking and size confirmation

INSPECTION METHODOLOGY:
1. **Systematic Visual Scan:** Examine the shoe systematically from one end to the other
2. **Lighting Assessment:** Consider if image lighting affects defect visibility
3. **Symmetry Check:** Compare left vs right sides for consistency
4. **Scale Assessment:** Evaluate defect size relative to shoe size
5. **Functionality Impact:** Consider if defect affects shoe performance or durability
6. **Customer Perception:** Would an average consumer notice and be concerned?

QUALITY ASSESSMENT CRITERIA:
- **Good:** No visible defects or only very minor cosmetic issues
- **Fair:** Minor defects present but within acceptable limits
- **Poor:** Major defects present or excessive minor defects

CONFIDENCE LEVEL GUIDELINES:
- **High:** Clear, well-lit image with obvious defects or clearly clean areas
- **Medium:** Adequate image quality with some uncertainty due to angle/lighting
- **Low:** Poor image quality, shadows, or unclear areas affecting assessment

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
            model="gpt-4o",  # Using GPT-4 with vision capabilities
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
            max_tokens=800,  # Increased for detailed responses
            temperature=0.1  # Low temperature for consistent, factual analysis
        )
        
        # Parse the JSON response
        result_text = response.choices[0].message.content
        
        # Find JSON in the response
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = result_text[start_idx:end_idx]
            return json.loads(json_str)
        else:
            # Fallback if JSON parsing fails
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
    """
    Generate final QC report based on all angle analyses and AQL 2.5 standards
    """
    # Combine all defects from all angles
    all_critical = []
    all_major = []
    all_minor = []
    
    for analysis in analyses:
        if analysis:
            all_critical.extend(analysis.get('critical_defects', []))
            all_major.extend(analysis.get('major_defects', []))
            all_minor.extend(analysis.get('minor_defects', []))
    
    # Remove duplicates while preserving order
    all_critical = list(dict.fromkeys(all_critical))
    all_major = list(dict.fromkeys(all_major))
    all_minor = list(dict.fromkeys(all_minor))
    
    # Count defects
    critical_count = len(all_critical)
    major_count = len(all_major)
    minor_count = len(all_minor)
    
    # Apply AQL 2.5 standards (based on sample size of 200 pieces)
    # These are the actual limits from your inspection report
    aql_limits = {
        "critical": 0,  # Zero tolerance for critical defects
        "major": 10,    # Maximum 10 major defects allowed
        "minor": 14     # Maximum 14 minor defects allowed
    }
    
    # Determine final result
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

# Function to categorize defects into QC table categories
def categorize_defects_for_table(all_defects):
    """
    Categorize defects into the QC table categories based on keywords
    """
    categories = {
        "Color Variation (色差)": [],
        "Clean (清潔度)": [],
        "Toe Lasting": [],
        "Lining (內里)": [],
        "Waist (腰幫)": [],
        "Sock Lining Printing (鞋墊印刷)": [],
        "Lace (鞋帶)": [],
        "Outsole (大底)": [],
        "Velcro (魔術貼)": [],
        "Adhesion (膠著力)": [],
        "Buckle (鞋扣)": [],
        "Sock Cushion (中底海棉/EVA)": [],
        "Tongue (鞋舌)": [],
        "Shank Attachment (鐵心固定)": [],
        "Backstrap Length (後帶長)": [],
        "Heel (鞋跟)": [],
        "Backstrap Attachment (後帶固定)": [],
        "Toplift (天皮)": [],
        "Damage Upper (鞋面受損)": [],
        "Bottom Gapping (貼合底片裂口)": [],
        "X-RAY (鞋面打皺)": [],
        "Stains (溢膠)": []
    }
    
    # Keywords mapping for categorization
    keyword_mapping = {
        "Color Variation (色差)": ["color", "chromatic", "variation", "shade", "bleeding"],
        "Clean (清潔度)": ["clean", "dirt", "dust", "cleanliness"],
        "Toe Lasting": ["toe", "lasting", "toe cap", "toe box"],
        "Lining (內里)": ["lining", "inner", "interior"],
        "Waist (腰幫)": ["waist", "smooth"],
        "Sock Lining Printing (鞋墊印刷)": ["sock liner", "insole", "printing"],
        "Lace (鞋帶)": ["lace", "eyelet"],
        "Outsole (大底)": ["outsole", "sole", "bottom"],
        "Velcro (魔術貼)": ["velcro"],
        "Adhesion (膠著力)": ["adhesion", "glue", "bonding", "debond"],
        "Buckle (鞋扣)": ["buckle"],
        "Sock Cushion (中底海棉/EVA)": ["midsole", "eva", "cushion"],
        "Tongue (鞋舌)": ["tongue"],
        "Shank Attachment (鐵心固定)": ["shank"],
        "Backstrap Length (後帶長)": ["backstrap", "strap length"],
        "Heel (鞋跟)": ["heel"],
        "Backstrap Attachment (後帶固定)": ["backstrap attachment"],
        "Toplift (天皮)": ["toplift"],
        "Damage Upper (鞋面受損)": ["upper", "damage", "tear", "hole"],
        "Bottom Gapping (貼合底片裂口)": ["gap", "separation"],
        "X-RAY (鞋面打皺)": ["wrinkle", "crease"],
        "Stains (溢膠)": ["stain", "overflow", "excess"]
    }
    
    # Categorize defects
    for defect in all_defects:
        defect_lower = defect.lower()
        categorized = False
        
        for category, keywords in keyword_mapping.items():
            if any(keyword in defect_lower for keyword in keywords):
                categories[category].append(defect)
                categorized = True
                break
        
        # If not categorized, add to most relevant category or create an "Other" category
        if not categorized:
            if "other" not in categories:
                categories["Other"] = []
            categories["Other"].append(defect)
    
    return categories

# Enhanced HTML Report Generation with Company Header and QC Table
def generate_html_report(export_report, po_number, style_number):
    """Generate a professional HTML report with styling, company header, and QC table"""
    
    inspection_data = export_report['inspection_summary']
    defect_data = export_report['defect_summary']
    defects = export_report['defect_details']
    
    # Combine all defects for categorization
    all_defects = defects['critical_defects'] + defects['major_defects'] + defects['minor_defects']
    
    # Categorize defects for QC table
    categorized_defects = categorize_defects_for_table(all_defects)
    
    # Determine result color
    result_colors = {
        "ACCEPT": "#28a745",  # Green
        "REWORK": "#ffc107",  # Yellow
        "REJECT": "#dc3545"   # Red
    }
    
    result_color = result_colors.get(inspection_data['final_result'], "#6c757d")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QC Inspection Report - {style_number}</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                color: #333;
            }}
            
            .report-container {{
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .company-header {{
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                padding: 25px;
                text-align: center;
                border-bottom: 3px solid #ffd700;
            }}
            
            .company-header h1 {{
                margin: 0 0 10px 0;
                font-size: 1.8rem;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            
            .company-header h2 {{
                margin: 0 0 15px 0;
                font-size: 1.4rem;
                color: #ffd700;
                font-weight: normal;
            }}
            
            .company-contact {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                font-size: 0.9rem;
                opacity: 0.9;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                text-align: center;
                position: relative;
            }}
            
            .header::before {{
                content: '🔍';
                font-size: 2.5rem;
                position: absolute;
                top: 10px;
                left: 25px;
                opacity: 0.3;
            }}
            
            .header h1 {{
                margin: 0;
                font-size: 1.8rem;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            
            .content {{
                padding: 30px;
            }}
            
            .result-banner {{
                background: {result_color};
                color: white;
                padding: 20px;
                margin: -30px -30px 30px -30px;
                text-align: center;
                font-size: 1.4rem;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 25px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 5px solid #667eea;
            }}
            
            .info-item {{
                display: flex;
                align-items: center;
            }}
            
            .info-label {{
                font-weight: bold;
                color: #495057;
                margin-right: 10px;
                min-width: 80px;
            }}
            
            .info-value {{
                color: #212529;
                font-family: 'Courier New', monospace;
                background: white;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #dee2e6;
            }}
            
            .qc-table-container {{
                margin: 25px 0;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            
            .qc-table-title {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                text-align: center;
                font-size: 1.2rem;
                font-weight: bold;
            }}
            
            .qc-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9rem;
            }}
            
            .qc-table th {{
                background: #f8f9fa;
                padding: 12px 8px;
                text-align: center;
                border: 1px solid #dee2e6;
                font-weight: bold;
                color: #495057;
            }}
            
            .qc-table td {{
                padding: 8px;
                border: 1px solid #dee2e6;
                text-align: center;
                vertical-align: middle;
            }}
            
            .qc-table .problem-cell {{
                text-align: left;
                font-weight: 500;
                min-width: 180px;
            }}
            
            .defect-mark {{
                width: 20px;
                height: 20px;
                border-radius: 50%;
                display: inline-block;
                margin: 2px;
            }}
            
            .critical-mark {{
                background: #dc3545;
            }}
            
            .major-mark {{
                background: #ffc107;
            }}
            
            .minor-mark {{
                background: #17a2b8;
            }}
            
            .metrics-container {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin: 25px 0;
            }}
            
            .metric-card {{
                text-align: center;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                position: relative;
                overflow: hidden;
            }}
            
            .metric-card.critical {{
                background: linear-gradient(135deg, #ff6b6b, #ee5a52);
                color: white;
            }}
            
            .metric-card.major {{
                background: linear-gradient(135deg, #feca57, #ff9ff3);
                color: white;
            }}
            
            .metric-card.minor {{
                background: linear-gradient(135deg, #48dbfb, #0abde3);
                color: white;
            }}
            
            .metric-number {{
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            
            .metric-label {{
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 1px;
                opacity: 0.9;
            }}
            
            .metric-limit {{
                font-size: 0.8rem;
                opacity: 0.8;
                margin-top: 5px;
            }}
            
            .defects-section {{
                margin-top: 25px;
            }}
            
            .section-title {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #495057;
                margin: 20px 0 10px 0;
                padding: 10px 0;
                border-bottom: 2px solid #e9ecef;
                display: flex;
                align-items: center;
            }}
            
            .defect-list {{
                background: #fff;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            
            .defect-item {{
                padding: 10px;
                margin: 6px 0;
                border-radius: 6px;
                border-left: 4px solid;
                display: flex;
                align-items: flex-start;
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
                margin-right: 10px;
                min-width: 25px;
            }}
            
            .no-defects {{
                text-align: center;
                padding: 15px;
                color: #28a745;
                font-style: italic;
                background: #f8fff8;
                border: 1px dashed #28a745;
                border-radius: 6px;
            }}
            
            .footer {{
                background: #f8f9fa;
                padding: 20px 30px;
                text-align: center;
                color: #6c757d;
                border-top: 1px solid #e9ecef;
            }}
            
            .footer .logo {{
                font-size: 1.1rem;
                font-weight: bold;
                color: #495057;
            }}
            
            .generated-info {{
                font-size: 0.9rem;
                margin-top: 10px;
            }}
            
            .reason-box {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                text-align: center;
                font-weight: 500;
            }}
            
            @media print {{
                body {{ background: white; }}
                .report-container {{ box-shadow: none; }}
            }}
            
            .icon {{
                font-size: 1.2rem;
                margin-right: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <!-- Company Header -->
            <div class="company-header">
                <h1>Grand Step (H.K.) Ltd</h1>
                <h2>ONLINE INSPECTION REPORT</h2>
                <div class="company-contact">
                    <div>📞 Tel: 86-769-8308 0888-381</div>
                    <div>📠 Fax: 86-769-8308 0999</div>
                    <div>📧 Email: production7@grandstep.com</div>
                    <div>📧 Email: production@grandstep.com</div>
                    <div>🌐 Web: www.grandstep.com</div>
                </div>
            </div>
            
            <!-- Report Header -->
            <div class="header">
                <h1>Quality Control Inspection Report</h1>
            </div>
            
            <div class="content">
                <div class="result-banner">
                    🎯 Final Result: {inspection_data['final_result']}
                </div>
                
                <div class="reason-box">
                    <strong>📋 Decision Rationale:</strong> {export_report['decision_rationale']}
                </div>
                
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">📦 PO Number:</span>
                        <span class="info-value">{inspection_data['po_number']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">👟 Style:</span>
                        <span class="info-value">{inspection_data['style_number']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">🎨 Color:</span>
                        <span class="info-value">{inspection_data['color']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">🏢 Customer:</span>
                        <span class="info-value">{inspection_data['customer']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">👨‍🔬 Inspector:</span>
                        <span class="info-value">{inspection_data['inspector']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">📅 Date:</span>
                        <span class="info-value">{inspection_data['inspection_date']}</span>
                    </div>
                </div>
                
                <!-- QC Problem Table -->
                <div class="qc-table-container">
                    <div class="qc-table-title">
                        🔍 Quality Control Problem Analysis
                    </div>
                    <table class="qc-table">
                        <thead>
                            <tr>
                                <th>Problem 问题</th>
                                <th>CR</th>
                                <th>MINOR</th>
                                <th>CR</th>
                                <th>MAJOR</th>
                                <th>MINOR</th>
                            </tr>
                        </thead>
                        <tbody>"""

    # Generate QC table rows
    qc_table_items = [
        ("Color Variation (色差)", "Clean (清潔度)"),
        ("Toe Lasting", "Lining (內里)"),
        ("Waist (腰幫)", "Sock Lining Printing (鞋墊印刷)"),
        ("Lace (鞋帶)", "Outsole (大底)"),
        ("Velcro (魔術貼)", "Adhesion (膠著力)"),
        ("Buckle (鞋扣)", "Sock Cushion (中底海棉/EVA)"),
        ("Tongue (鞋舌)", "Shank Attachment (鐵心固定)"),
        ("Backstrap Length (後帶長)", "Heel (鞋跟)"),
        ("Backstrap Attachment (後帶固定)", "Toplift (天皮)"),
        ("Damage Upper (鞋面受損)", "Bottom Gapping (貼合底片裂口)"),
        ("X-RAY (鞋面打皺)", "Stains (溢膠)")
    ]
    
    for left_item, right_item in qc_table_items:
        # Check if defects exist for each category
        left_critical = any(defect in defects['critical_defects'] for defect in categorized_defects.get(left_item, []))
        left_major = any(defect in defects['major_defects'] for defect in categorized_defects.get(left_item, []))
        left_minor = any(defect in defects['minor_defects'] for defect in categorized_defects.get(left_item, []))
        
        right_critical = any(defect in defects['critical_defects'] for defect in categorized_defects.get(right_item, []))
        right_major = any(defect in defects['major_defects'] for defect in categorized_defects.get(right_item, []))
        right_minor = any(defect in defects['minor_defects'] for defect in categorized_defects.get(right_item, []))
        
        html_content += f"""
                            <tr>
                                <td class="problem-cell">{left_item}</td>
                                <td>{'<span class="defect-mark critical-mark"></span>' if left_critical else ''}</td>
                                <td>{'<span class="defect-mark minor-mark"></span>' if left_minor else ''}</td>
                                <td>{'<span class="defect-mark critical-mark"></span>' if right_critical else ''}</td>
                                <td>{'<span class="defect-mark major-mark"></span>' if right_major else ''}</td>
                                <td>{'<span class="defect-mark minor-mark"></span>' if right_minor else ''}</td>
                            </tr>
                            <tr>
                                <td class="problem-cell">{right_item}</td>
                                <td>{'<span class="defect-mark critical-mark"></span>' if right_critical else ''}</td>
                                <td>{'<span class="defect-mark minor-mark"></span>' if right_minor else ''}</td>
                                <td colspan="3" style="background: #f8f9fa;"></td>
                            </tr>"""
    
    html_content += """
                        </tbody>
                    </table>
                </div>
                
                <div class="section-title">
                    <span class="icon">📊</span>
                    Defect Summary (AQL 2.5 Standard)
                </div>
                
                <div class="metrics-container">
                    <div class="metric-card critical">
                        <div class="metric-number">{defect_data['critical_count']}</div>
                        <div class="metric-label">🚨 Critical Defects</div>
                        <div class="metric-limit">Limit: {defect_data['aql_limits']['critical']}</div>
                    </div>
                    <div class="metric-card major">
                        <div class="metric-number">{defect_data['major_count']}</div>
                        <div class="metric-label">⚠️ Major Defects</div>
                        <div class="metric-limit">Limit: {defect_data['aql_limits']['major']}</div>
                    </div>
                    <div class="metric-card minor">
                        <div class="metric-number">{defect_data['minor_count']}</div>
                        <div class="metric-label">ℹ️ Minor Defects</div>
                        <div class="metric-limit">Limit: {defect_data['aql_limits']['minor']}</div>
                    </div>
                </div>
                
                <div class="defects-section">"""

    # Critical Defects Section
    html_content += """
                    <div class="section-title">
                        <span class="icon">🚨</span>
                        Critical Defects
                    </div>
                    <div class="defect-list">"""
    
    if defects['critical_defects']:
        for i, defect in enumerate(defects['critical_defects'], 1):
            html_content += f"""
                        <div class="defect-item critical">
                            <span class="defect-number">{i}.</span>
                            <span>{defect}</span>
                        </div>"""
    else:
        html_content += '<div class="no-defects">✅ No critical defects found</div>'
    
    html_content += "</div>"
    
    # Major Defects Section
    html_content += """
                    <div class="section-title">
                        <span class="icon">⚠️</span>
                        Major Defects
                    </div>
                    <div class="defect-list">"""
    
    if defects['major_defects']:
        for i, defect in enumerate(defects['major_defects'], 1):
            html_content += f"""
                        <div class="defect-item major">
                            <span class="defect-number">{i}.</span>
                            <span>{defect}</span>
                        </div>"""
    else:
        html_content += '<div class="no-defects">✅ No major defects found</div>'
    
    html_content += "</div>"
    
    # Minor Defects Section
    html_content += """
                    <div class="section-title">
                        <span class="icon">ℹ️</span>
                        Minor Defects
                    </div>
                    <div class="defect-list">"""
    
    if defects['minor_defects']:
        for i, defect in enumerate(defects['minor_defects'], 1):
            html_content += f"""
                        <div class="defect-item minor">
                            <span class="defect-number">{i}.</span>
                            <span>{defect}</span>
                        </div>"""
    else:
        html_content += '<div class="no-defects">✅ No minor defects found</div>'
    
    html_content += f"""
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div class="logo">🤖 AI Footwear Quality Control Inspector</div>
                <div class="generated-info">
                    Report generated on {inspection_data['inspection_date']} using OpenAI GPT-4 Vision API<br>
                    Powered by advanced computer vision and professional QC expertise
                </div>
            </div>
        </div>
    </body>
    </html>"""
    
    return html_content

# Function to convert HTML to JPG using Selenium
def html_to_jpg(html_content, style_number):
    """Convert HTML content to JPG image using Selenium"""
    try:
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_file_path = temp_file.name

        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1200,1600")  # Adjust size as needed
        chrome_options.add_argument("--disable-gpu")

        # Initialize the Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            # Load the HTML file
            driver.get(f"file://{temp_file_path}")
            
            # Wait for the page to load completely
            time.sleep(3)
            
            # Get page dimensions and set window size accordingly
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(1200, total_height)
            
            # Take screenshot
            screenshot = driver.get_screenshot_as_png()
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(screenshot))
            
            # Convert to RGB if necessary
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            return image

        finally:
            driver.quit()
            # Clean up temporary file
            os.unlink(temp_file_path)

    except Exception as e:
        st.error(f"Error converting HTML to JPG: {str(e)}")
        return None