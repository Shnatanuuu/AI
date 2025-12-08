from reportlab.lib import colors  # inspection table
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a Chinese font
try:
    pdfmetrics.registerFont(TTFont('Chinese', 'simsun.ttc'))
    chinese_font = 'Chinese'
except:
    print("Warning: Chinese font not found, using default font")
    chinese_font = 'Helvetica'

# Create PDF
pdf_file = "inspection_standard_aql25.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=landscape(A4), 
                       leftMargin=10*mm, rightMargin=10*mm,
                       topMargin=10*mm, bottomMargin=10*mm)

# Define data
data = [
    # Title row
    ['Inspection Standard 2.5      验货标准AQL2.5', '', '', '', ''],
    # Header row
    ['BATCH SIZE订单数量', 'TO INSPECT检查数量', 'CRITICAL AQL\n严重问题', 'MAJOR AQL\n主要问题允许数量', 'MINOR QAL\n次要问题允许数量'],
    # Data rows
    ['0-300PRS', '100%', '0', '1', '5'],
    ['301-1200PRS', '80', '0', '5', '9'],
    ['1201-3200PRS', '125', '0', '7', '10'],
    ['3201-10000PRS', '200', '0', '10', '14'],
    ['10001-35000 above', '315', '0', '14', '21'],
    # Last row
    ['Inspection Results Total QTY:', '', '', '', '']
]

# Calculate column widths
page_width = landscape(A4)[0] - 20*mm
col_widths = [
    page_width * 0.20,  # BATCH SIZE
    page_width * 0.20,  # TO INSPECT
    page_width * 0.20,  # CRITICAL AQL
    page_width * 0.20,  # MAJOR AQL
    page_width * 0.20   # MINOR QAL
]

# Row heights
row_heights = [35, 30] + [25]*5 + [35]

# Create table
table = Table(data, colWidths=col_widths, rowHeights=row_heights)

# Define table style
style = TableStyle([
    # Title row - yellow background
    ('BACKGROUND', (0, 0), (4, 0), colors.yellow),
    ('SPAN', (0, 0), (4, 0)),  # Merge all columns for title
    ('ALIGN', (0, 0), (4, 0), 'LEFT'),
    ('FONTSIZE', (0, 0), (4, 0), 16),
    ('FONTNAME', (0, 0), (4, 0), chinese_font),
    ('VALIGN', (0, 0), (4, 0), 'MIDDLE'),
    
    # Header row - light gray background
    ('BACKGROUND', (0, 1), (4, 1), colors.Color(0.85, 0.85, 0.85)),
    ('FONTSIZE', (0, 1), (4, 1), 10),
    ('FONTNAME', (0, 1), (4, 1), chinese_font),
    ('ALIGN', (0, 1), (4, 1), 'CENTER'),
    ('VALIGN', (0, 1), (4, 1), 'MIDDLE'),
    
    # Data rows - white background
    ('BACKGROUND', (0, 2), (4, 6), colors.white),
    ('FONTSIZE', (0, 2), (4, 6), 11),
    ('FONTNAME', (0, 2), (4, 6), chinese_font),
    ('ALIGN', (0, 2), (0, 6), 'LEFT'),
    ('ALIGN', (1, 2), (4, 6), 'CENTER'),
    ('VALIGN', (0, 2), (4, 6), 'MIDDLE'),
    
    # Last row - yellow background
    ('BACKGROUND', (0, 7), (4, 7), colors.yellow),
    ('SPAN', (0, 7), (4, 7)),  # Merge all columns
    ('FONTSIZE', (0, 7), (4, 7), 10),
    ('FONTNAME', (0, 7), (4, 7), chinese_font),
    ('ALIGN', (0, 7), (4, 7), 'LEFT'),
    ('VALIGN', (0, 7), (4, 7), 'MIDDLE'),
    
    # Grid - black borders
    ('GRID', (0, 0), (4, 7), 1.5, colors.black),
    ('LINEWIDTH', (0, 0), (4, 7), 1.5),
    ('LINECOLOR', (0, 0), (4, 7), colors.black),
    
    # Padding
    ('LEFTPADDING', (0, 0), (4, 7), 5),
    ('RIGHTPADDING', (0, 0), (4, 7), 5),
    ('TOPPADDING', (0, 0), (4, 7), 4),
    ('BOTTOMPADDING', (0, 0), (4, 7), 4),
])

table.setStyle(style)

# Build PDF
elements = [table]
doc.build(elements)

print(f"PDF created successfully: {pdf_file}")