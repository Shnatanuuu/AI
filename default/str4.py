# for sampling one                             
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
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
pdf_file = "sampling_inspection.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4, 
                       leftMargin=15*mm, rightMargin=15*mm,
                       topMargin=15*mm, bottomMargin=15*mm)

# Define data
data = [
    # Title row
    ['sampling inspection'],
    # Row 1
    ['Color\n颜色'],
    # Row 2
    ['quantity\n数量'],
    # Row 3
    ['箱号 CTN.NO'],
    # Row 4
    ['Total sampling number\n总抽检数']
]

# Calculate column width (single column)
page_width = A4[0] - 30*mm
col_widths = [page_width]

# Row heights
row_heights = [40, 50, 50, 50, 50]

# Create table
table = Table(data, colWidths=col_widths, rowHeights=row_heights)

# Define table style
style = TableStyle([
    # Title row - light blue background
    ('BACKGROUND', (0, 0), (0, 0), colors.Color(0.6, 0.8, 1)),
    ('FONTSIZE', (0, 0), (0, 0), 14),
    ('FONTNAME', (0, 0), (0, 0), chinese_font),
    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
    ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
    
    # Data rows - white background
    ('BACKGROUND', (0, 1), (0, 4), colors.white),
    ('FONTSIZE', (0, 1), (0, 4), 12),
    ('FONTNAME', (0, 1), (0, 4), chinese_font),
    ('ALIGN', (0, 1), (0, 4), 'LEFT'),
    ('VALIGN', (0, 1), (0, 4), 'TOP'),
    
    # Grid - black borders
    ('GRID', (0, 0), (0, 4), 1.5, colors.black),
    ('LINEWIDTH', (0, 0), (0, 4), 1.5),
    ('LINECOLOR', (0, 0), (0, 4), colors.black),
    
    # Padding
    ('LEFTPADDING', (0, 0), (0, 4), 8),
    ('RIGHTPADDING', (0, 0), (0, 4), 8),
    ('TOPPADDING', (0, 0), (0, 4), 8),
    ('BOTTOMPADDING', (0, 0), (0, 4), 8),
])

table.setStyle(style)

# Build PDF
elements = [table]
doc.build(elements)

print(f"PDF created successfully: {pdf_file}")