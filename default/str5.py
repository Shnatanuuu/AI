from reportlab.lib import colors            # photos of fault
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
pdf_file = "photos_of_faults.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4, 
                       leftMargin=5*mm, rightMargin=5*mm,
                       topMargin=5*mm, bottomMargin=5*mm)

# Define data
data = [
    # Title row
    ['Photos of Faults 问题图片', ''],
    # MINOR section header
    ['MINOR 次要问题', ''],
    # MINOR items - 2 columns with photo spaces
    ['1  清洁度   dirty', '2  皱 wrinkle'],
    ['', ''],  # Photo space row 1
    ['', ''],  # Photo space row 2
    ['', ''],  # Photo space row 3
    ['3  歪 off center', '4  后跟高低 heel high mismated'],
    ['', ''],  # Photo space row 4
    ['', ''],  # Photo space row 5
    ['', ''],  # Photo space row 6
    # MAJOR section header
    ['MAJOR 主要问题', ''],
    # MAJOR items - 2 columns with photo spaces
    ['1   包边皱 wraping wrinkle', '3    开胶 Gapping'],
    ['', ''],  # Photo space row 7
    ['', ''],  # Photo space row 8
    ['', ''],  # Photo space row 9
    ['', ''],  # Photo space row 10
    ['', ''],  # Photo space row 11
    ['3   溢胶 glue over', '4  帮舟打磨高   rough damage shoe'],
    ['', ''],  # Photo space row 12
    ['', ''],  # Photo space row 13
    ['', ''],  # Photo space row 14
    ['', ''],  # Photo space row 15
    # CRITICAL section header
    ['CRITICAL 严重问题', ''],
    # CRITICAL items
    ['1', '2'],
    ['', ''],  # Photo space row 16
    ['', ''],  # Photo space row 17
    ['3', '4'],
    ['', ''],  # Photo space row 18
    ['', ''],  # Photo space row 19s
]

# Calculate column widths - 2 equal columns
page_width = A4[0] - 10*mm
col_widths = [page_width * 0.5, page_width * 0.5]

# Row heights
row_heights = [
    25,  # Title
    20,  # MINOR header
    20,  # Item 1-2
    60, 60, 60,  # Photo spaces
    20,  # Item 3-4
    60, 60, 60,  # Photo spaces
    20,  # MAJOR header
    20,  # Item 1-3
    50, 50, 50, 50, 50,  # Photo spaces
    20,  # Item 3-4
    50, 50, 50, 50,  # Photo spaces
    20,  # CRITICAL header
    20,  # Item 1-2
    60, 60,  # Photo spaces
    20,  # Item 3-4
    60, 60  # Photo spaces
]

# Create table
table = Table(data, colWidths=col_widths, rowHeights=row_heights)

# Define table style
style = TableStyle([
    # Title row - yellow background
    ('BACKGROUND', (0, 0), (1, 0), colors.Color(1, 0.84, 0.4)),
    ('SPAN', (0, 0), (1, 0)),
    ('FONTSIZE', (0, 0), (1, 0), 14),
    ('FONTNAME', (0, 0), (1, 0), chinese_font),
    ('ALIGN', (0, 0), (1, 0), 'CENTER'),
    ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
    
    # MINOR header - light gray
    ('BACKGROUND', (0, 1), (1, 1), colors.Color(0.9, 0.9, 0.9)),
    ('SPAN', (0, 1), (1, 1)),
    ('FONTSIZE', (0, 1), (1, 1), 11),
    ('FONTNAME', (0, 1), (1, 1), chinese_font),
    ('ALIGN', (0, 1), (1, 1), 'LEFT'),
    ('VALIGN', (0, 1), (1, 1), 'MIDDLE'),
    
    # MAJOR header - orange
    ('BACKGROUND', (0, 10), (1, 10), colors.Color(1, 0.7, 0.5)),
    ('SPAN', (0, 10), (1, 10)),
    ('FONTSIZE', (0, 10), (1, 10), 11),
    ('FONTNAME', (0, 10), (1, 10), chinese_font),
    ('ALIGN', (0, 10), (1, 10), 'LEFT'),
    ('VALIGN', (0, 10), (1, 10), 'MIDDLE'),
    
    # CRITICAL header - red
    ('BACKGROUND', (0, 21), (1, 21), colors.Color(0.9, 0.2, 0.2)),
    ('SPAN', (0, 21), (1, 21)),
    ('FONTSIZE', (0, 21), (1, 21), 11),
    ('FONTNAME', (0, 21), (1, 21), chinese_font),
    ('TEXTCOLOR', (0, 21), (1, 21), colors.white),
    ('ALIGN', (0, 21), (1, 21), 'LEFT'),
    ('VALIGN', (0, 21), (1, 21), 'MIDDLE'),
    
    # All other cells - white background
    ('BACKGROUND', (0, 2), (1, 9), colors.white),
    ('BACKGROUND', (0, 11), (1, 20), colors.white),
    ('BACKGROUND', (0, 22), (1, 27), colors.white),
    
    # Font for data cells
    ('FONTSIZE', (0, 2), (1, 27), 10),
    ('FONTNAME', (0, 2), (1, 27), chinese_font),
    ('ALIGN', (0, 2), (1, 27), 'LEFT'),
    ('VALIGN', (0, 2), (1, 27), 'TOP'),
    
    # Grid - black borders
    ('GRID', (0, 0), (1, 27), 1.5, colors.black),
    ('LINEWIDTH', (0, 0), (1, 27), 1.5),
    ('LINECOLOR', (0, 0), (1, 27), colors.black),
    
    # Padding
    ('LEFTPADDING', (0, 0), (1, 27), 5),
    ('RIGHTPADDING', (0, 0), (1, 27), 5),
    ('TOPPADDING', (0, 0), (1, 27), 3),
    ('BOTTOMPADDING', (0, 0), (1, 27), 3),
])

table.setStyle(style)

# Build PDF
elements = [table]
doc.build(elements)

print(f"PDF created successfully: {pdf_file}")
