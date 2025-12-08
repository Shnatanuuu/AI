from reportlab.lib import colors         # Problem from inspection rreport
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a Chinese font (you may need to adjust the font path)
try:
    pdfmetrics.registerFont(TTFont('Chinese', 'simsun.ttc'))
    chinese_font = 'Chinese'
except:
    print("Warning: Chinese font not found, using default font")
    chinese_font = 'Helvetica'

# Create PDF
pdf_file = "inspection_report.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=landscape(A4), 
                       leftMargin=10*mm, rightMargin=10*mm,
                       topMargin=10*mm, bottomMargin=10*mm)

# Define data - properly structured according to the image
data = [
    # Header row
    ['Problem 问题', 'CR', 'MAJOR', 'MINOR', '', 'CR', 'MAJOR', 'MINOR'],
    # Row 1
    ['Color Variation 色差', '', '', '', 'Clean 清洁度', '', '', ''],
    # Row 2
    ['Toe Lastingqianb 前帮', '', '', '', '包跟布起角', '', '', ''],
    # Row 3
    ['Waist 腰帮', '', '', '', '包边条皱', '', '', ''],
    # Row 4
    ['Lace 鞋带', '', '', '', 'Outsole 大底', '', '', ''],
    # Row 5
    ['Velcro 魔术贴', '', '', '', 'Adhesioin 胶着力', '', '', ''],
    # Row 6
    ['Buckle 鞋扣', '', '', '', '中底布欠胶开胶皱', '', '', ''],
    # Row 7
    ['Tonque 鞋舌', '', '', '', '帮脚打磨高', '', '', ''],
    # Row 8
    ['Back strap Length 后带长', '', '', '', 'Heel 鞋跟', '', '', ''],
    # Row 9
    ['Back strap attachment 后带固定', '', '', '', 'Toplift 大皮', '', '', ''],
    # Row 10
    ['Damage upper 鞋面受损', '', '', '', 'Bottom Gapping 底开胶', '', '', ''],
    # Row 11
    ['X-RAY 鞋面打皱', '', '', '', 'Stains 溢胶', '', '', ''],
    # Row 12
    ['线头 thread ends trims', '', '', '', '', '', '', ''],
    # Last row
    ['Inspection Results QTY: 不良数', '', '', '', '', '', '', '']
]

# Calculate column widths
page_width = landscape(A4)[0] - 20*mm
col_widths = [
    page_width * 0.25,  # Problem column (left side)
    page_width * 0.08,  # CR
    page_width * 0.08,  # MAJOR
    page_width * 0.08,  # MINOR
    page_width * 0.25,  # Problem column (right side)
    page_width * 0.08,  # CR
    page_width * 0.08,  # MAJOR
    page_width * 0.08   # MINOR
]

# Create table
table = Table(data, colWidths=col_widths, rowHeights=[25] + [22]*12 + [25])

# Define table style
style = TableStyle([
    # Header row styling - light blue background
    ('BACKGROUND', (0, 0), (0, 0), colors.Color(0.6, 0.8, 1)),
    ('BACKGROUND', (1, 0), (3, 0), colors.white),
    ('BACKGROUND', (4, 0), (4, 0), colors.white),
    ('BACKGROUND', (5, 0), (7, 0), colors.white),
    
    # All body rows - white background
    ('BACKGROUND', (0, 1), (7, 12), colors.white),
    
    # Last row styling
    ('BACKGROUND', (0, 13), (0, 13), colors.Color(1, 0.95, 0.6)),  # Yellow
    ('BACKGROUND', (1, 13), (3, 13), colors.Color(0.6, 0.7, 1)),   # Blue
    ('BACKGROUND', (4, 13), (4, 13), colors.white),
    ('BACKGROUND', (5, 13), (7, 13), colors.Color(0.5, 0.9, 0.5)), # Green
    
    # Grid - blue borders
    ('GRID', (0, 0), (7, 13), 1.5, colors.blue),
    ('LINEWIDTH', (0, 0), (7, 13), 1.5),
    ('LINECOLOR', (0, 0), (7, 13), colors.blue),
    
    # Font
    ('FONTNAME', (0, 0), (7, 13), chinese_font),
    ('FONTSIZE', (0, 0), (7, 13), 9),
    
    # Header row - slightly larger and bold
    ('FONTSIZE', (0, 0), (7, 0), 10),
    ('FONTNAME', (0, 0), (7, 0), chinese_font),
    
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

# Build PDF
elements = [table]
doc.build(elements)

print(f"PDF created successfully: {pdf_file}")