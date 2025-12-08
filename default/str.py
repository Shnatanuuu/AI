from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

def create_qc_inspection_report(filename="QC_Inspection_Report.pdf", image_path="shoe_image.jpg"):
    """
    Create a detailed QC Inspection Report matching the provided template
    """
    
    # Create PDF with landscape orientation
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4),
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=10*mm,
        bottomMargin=10*mm
    )
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.black,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=6,
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    # Title
    elements.append(Paragraph("QC Inspector 验货员", title_style))
    elements.append(Spacer(1, 3*mm))
    
    # ========== SECTION 1: Basic Information ==========
    basic_info_data = [
        [Paragraph('<b>Inspection Date</b><br/>日期', cell_style), 
         '10月24日', 
         Paragraph('<b>Factory</b><br/>工厂', cell_style), 
         'Eason',
         Paragraph('<b>Final Results</b><br/>验货结果', cell_style),
         '1st', '2nd', '3rd'],
        [Paragraph('<b>Customer</b><br/>客户', cell_style), 
         'PRIMARK', 
         Paragraph('<b>Brand</b><br/>商标', cell_style), 
         'GD',
         Paragraph('<b>Accept</b><br/>可接受', cell_style),
         '√', '', ''],
        [Paragraph('<b>PO</b><br/>订单号', cell_style), 
         '63828', 
         Paragraph('<b>Order Quantity</b><br/>订单数量', cell_style), 
         'PRIMARK',
         Paragraph('<b>Rework</b><br/>重新整理', cell_style),
         '', '', ''],
        [Paragraph('<b>Style No</b><br/>型体号', cell_style), 
         'F25-43640', 
         Paragraph('<b>Sales</b><br/>业务', cell_style), 
         '23520',
         Paragraph('<b>Reject</b><br/>不可接受', cell_style),
         '', '', ''],
        [Paragraph('<b>Color</b><br/>颜色', cell_style), 
         'KHAKI', 
         '', 
         'AMY',
         Paragraph('<b>Guarantee Ship</b><br/>保函出货', cell_style),
         '', '', ''],
        ['', '', 
         Paragraph('<b>Size Range</b><br/>订单配码', cell_style), 
         '2--9',
         Paragraph('<b>Hold</b><br/>待处理', cell_style),
         '', '', ''],
    ]
    
    basic_table = Table(basic_info_data, colWidths=[25*mm, 25*mm, 25*mm, 25*mm, 28*mm, 10*mm, 10*mm, 10*mm])
    basic_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('BACKGROUND', (4, 0), (4, -1), colors.lightgrey),
        ('BACKGROUND', (5, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('SPAN', (1, 2), (1, 3)),  # Order quantity spans 2 rows
        ('SPAN', (3, 4), (3, 5)),  # AMY spans 2 rows
    ]))
    
    elements.append(basic_table)
    elements.append(Spacer(1, 5*mm))
    
    # ========== SECTION 2: Lot Sizes ==========
    lot_data = [
        [Paragraph('<b>Lot Size</b><br/>客人订单批次', cell_style), 
         'N13309513', 'C13309514', 'B13309515', 'D13309516/G13309517'],
        [Paragraph('<b>批次数量</b>', cell_style), 
         '3336', '1176', '8016', '1824/2280'],
    ]
    
    lot_table = Table(lot_data, colWidths=[35*mm, 25*mm, 25*mm, 25*mm, 35*mm])
    lot_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
    ]))
    
    elements.append(lot_table)
    elements.append(Spacer(1, 2*mm))
    
    lot_data2 = [
        [Paragraph('<b>Lot Size</b><br/>客人订单批次', cell_style), 
         'S13309518', 'A13309519', 'F13309520', 'U19909521/Z13309527'],
        [Paragraph('<b>批次数量</b>', cell_style), 
         '4680', '1068', '660', '168/312'],
    ]
    
    lot_table2 = Table(lot_data2, colWidths=[35*mm, 25*mm, 25*mm, 25*mm, 35*mm])
    lot_table2.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
    ]))
    
    elements.append(lot_table2)
    elements.append(Spacer(1, 5*mm))
    
    # ========== SECTION 3: Inspection Standard ==========
    inspection_std_data = [
        [Paragraph('<b>Inspection Standard 2.5<br/>验货标准AQL2.5</b>', header_style), '', '', '', ''],
        [Paragraph('<b>BATCH SIZE</b><br/>订单数量', cell_style),
         Paragraph('<b>TO BE INSPECT</b><br/>检查数量', cell_style),
         Paragraph('<b>MAJOR AQL</b><br/>主要问题允许数量', cell_style),
         Paragraph('<b>CRITICAL AQL</b><br/>严重问题', cell_style),
         Paragraph('<b>MINOR AQL</b><br/>次要问题允许数量', cell_style)],
        ['0-300PRS', '100%', '1', '0', '5'],
        ['301-1200PRS', '80', '5', '0', '9'],
        ['1201-3200PRS', '125', '7', '0', '10'],
        ['3201-10000PRS', '200', '10', '0', '14'],
        ['10001-35000 above', '315', '14', '0', '21'],
    ]
    
    inspection_table = Table(inspection_std_data, colWidths=[45*mm, 30*mm, 35*mm, 30*mm, 35*mm])
    inspection_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('SPAN', (0, 0), (-1, 0)),
    ]))
    
    elements.append(inspection_table)
    elements.append(Spacer(1, 5*mm))
    
    # ========== SECTION 4: Inspection Results ==========
    results_header = [
        [Paragraph('<b>Inspection Results 验货结果</b>', header_style), '', '', '', '', '', '', ''],
        [Paragraph('<b>Total QTY: 总数</b>', cell_style), 
         '12',
         Paragraph('<b>Sampling inspection quantity</b><br/>抽检数量', cell_style),
         '',
         Paragraph('<b>Color</b><br/>颜色', cell_style),
         'KHAKI',
         Paragraph('<b>Quantity</b><br/>数量', cell_style),
         '315'],
    ]
    
    results_header_table = Table(results_header, colWidths=[35*mm, 20*mm, 40*mm, 20*mm, 20*mm, 20*mm, 20*mm, 20*mm])
    results_header_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (0, 1), colors.lightgrey),
        ('BACKGROUND', (2, 1), (2, 1), colors.lightgrey),
        ('BACKGROUND', (4, 1), (4, 1), colors.lightgrey),
        ('BACKGROUND', (6, 1), (6, 1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('SPAN', (0, 0), (-1, 0)),
        ('SPAN', (2, 1), (3, 1)),
    ]))
    
    elements.append(results_header_table)
    elements.append(Spacer(1, 2*mm))
    
    # Detailed inspection table
    inspection_details = [
        [Paragraph('<b>箱号 CTN.NO</b>', small_style),
         Paragraph('<b>Total sampling number</b><br/>总抽检数', small_style),
         Paragraph('<b>Problem 问题</b>', small_style), '', '', '', '', ''],
        ['', '', 'CR', 'MAJOR', 'MINOR', 'CR', 'MAJOR', 'MINOR'],
    ]
    
    # Add defect rows
    defects = [
        ('Color Variation 色差', '', '', '', '', '', ''),
        ('Waist 腰帮', '', '', '', '', '', ''),
        ('Lace 鞋带', '', '', '', '', '', ''),
        ('Velcro 魔术贴', '', '', '', '', '', ''),
        ('Buckle 鞋扣', '', '', '', '', '', ''),
        ('Tongue 鞋舌', '', '', '', '', '', ''),
        ('Back strap Length 后带长', '', '', '', '', '', ''),
        ('Back strap attachment 后带固定', '', '', '', '', '', ''),
        ('Damage upper 鞋面受损', '', '', '', '', '', ''),
        ('X-RAY 鞋面打皱', '', '', '', '', '', ''),
        ('Thread ends 线头', '', '', '', '3', '2', ''),
        ('Trims', '', '', '', '', '', ''),
        ('Vamp 鞋面', '', '2%', '', '', '', ''),
        ('Toe Lasting 前帮', '', '', '', '2', '1', ''),
        ('Stains 溢胶', '', '', '', '', '', ''),
        ('Bottom Gapping 底开胶', '', '', '', '', '', ''),
        ('Toplift 天皮', '', '', '', '', '', ''),
        ('Heel 鞋跟', '', '', '', '', '', ''),
        ('Clean 清洁度', '', '', '', '10', '', ''),
        ('Lining 内里', '3%', '', 'pass', '', '', ''),
        ('Sock Lining 鞋垫印刷 Printing', '', '', '', '', '', ''),
        ('Outsole 大底', '', '', '', '', '', ''),
        ('Adhesion 胶着力', '', '', '', '', '', ''),
        ('Sock Cushion 中底海棉/EVA', '', '', '', '', '', ''),
        ('Shank Attachment 钢心固定', '', '', '', '', '', ''),
        ('包中底接头', '', '', '', '4', '', ''),
        ('大底边溢胶', '', '', '', '7', '', ''),
        ('包中底褶皱', '', '', '', '4', '', ''),
        ('中皮开胶', '', '', '', '1', '', ''),
    ]
    
    for defect in defects:
        inspection_details.append([defect[0], defect[1], defect[2], defect[3], defect[4], defect[5], defect[6], ''])
    
    # Add totals
    inspection_details.append([
        Paragraph('<b>QTY: 不良数</b>', small_style),
        '无',
        '4', '3', '8', '', '14', '17'
    ])
    
    details_table = Table(inspection_details, 
                         colWidths=[45*mm, 20*mm, 12*mm, 12*mm, 12*mm, 12*mm, 12*mm, 12*mm])
    details_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('SPAN', (2, 0), (7, 0)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
    ]))
    
    elements.append(details_table)
    
    # Page Break
    elements.append(PageBreak())
    
    # ========== PAGE 2: Testing and Packaging ==========
    
    # General Information
    elements.append(Paragraph("<b>General Information 基本信息</b>", header_style))
    elements.append(Spacer(1, 3*mm))
    
    # Testing section
    test_data = [
        [Paragraph('<b>Test outcome</b><br/>测试结果', cell_style), 
         'Fail不及格', '', 
         'Yes', 'No',
         Paragraph('<b>Factory self-test</b><br/>工厂自测', cell_style),
         '√'],
        ['', 'pass', 'fail', 'pass', 'fail',
         Paragraph('<b>Third party testing</b><br/>第三方测试', cell_style),
         '√'],
        [Paragraph('<b>Carton Measurement</b><br/>箱规', cell_style),
         Paragraph('<b>Length</b><br/>长', cell_style), 
         Paragraph('<b>Width</b><br/>宽', cell_style),
         Paragraph('<b>Height</b><br/>高', cell_style),
         Paragraph('<b>No</b><br/>无', cell_style),
         Paragraph('<b>YES</b><br/>有', cell_style),
         Paragraph('<b>Name of third-party testing organization</b><br/>第三方测试机构名称', cell_style)],
        [Paragraph('<b>Customer Standard</b><br/>客户要求', cell_style),
         '', '', '', '', '√', 'TUV'],
        [Paragraph('<b>Factory Made</b><br/>实际数据', cell_style),
         '420', '360', '290', '', '', ''],
        [Paragraph('<b>QC Check</b><br/>QC检查数据', cell_style),
         '420', '360', '290', Paragraph('<b>No</b><br/>无', cell_style), 
         Paragraph('<b>YES</b><br/>有', cell_style), ''],
        [Paragraph('<b>Weight customer requirement</b><br/>重量要求', cell_style),
         Paragraph('<b>Correct</b><br/>正确', cell_style),
         Paragraph('<b>Wrong</b><br/>错误', cell_style),
         '', '', '√', ''],
        [Paragraph('<b>QC check result</b><br/>QC检查结果', cell_style),
         '不超15KG', '7.10kg', '', '√', '', ''],
    ]
    
    test_table = Table(test_data, colWidths=[38*mm, 25*mm, 25*mm, 25*mm, 20*mm, 20*mm, 40*mm])
    test_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (5, 0), (5, 1), colors.lightgrey),
        ('BACKGROUND', (6, 2), (6, 2), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('SPAN', (1, 0), (4, 0)),
        ('SPAN', (5, 0), (5, 1)),
        ('SPAN', (6, 2), (6, -1)),
    ]))
    
    elements.append(test_table)
    elements.append(Spacer(1, 5*mm))
    
    # Defect categories
    defect_cat_data = [
        [Paragraph('<b>MINOR 次要问题</b>', cell_style), 
         Paragraph('<b>MAJOR 主要问题</b>', cell_style),
         Paragraph('<b>CRITICAL 严重问题</b>', cell_style)],
    ]
    
    defect_cat_table = Table(defect_cat_data, colWidths=[60*mm, 60*mm, 60*mm])
    defect_cat_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(defect_cat_table)
    elements.append(Spacer(1, 5*mm))
    
    # Packaging and Label section
    elements.append(Paragraph("<b>Packaging And Label 包装及贴标</b>", header_style))
    elements.append(Spacer(1, 3*mm))
    
    packaging_data = [
        [Paragraph('<b>Mildew check</b><br/>防霉检查', cell_style),
         Paragraph('<b>Anti-mold tablet authenticity</b><br/>防霉片真伪', cell_style),
         '√'],
        [Paragraph('<b>AOS sample results</b><br/>AOS样结果', cell_style),
         Paragraph('<b>Moisture test result</b><br/>水分测试结果', cell_style),
         ''],
        [Paragraph('<b>Fitting</b><br/>试穿', cell_style),
         Paragraph('<b>Case Defects</b><br/>外箱缺陷', cell_style),
         ''],
        [Paragraph('<b>Physical test</b><br/>物理测试', cell_style),
         Paragraph('<b>Packing Defects</b><br/>包装缺陷', cell_style),
         ''],
        ['',
         Paragraph('<b>Size Assortment</b><br/>配码检查(10%)', cell_style),
         ''],
    ]
    
    packaging_table = Table(packaging_data, colWidths=[50*mm, 60*mm, 70*mm])
    packaging_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (1, 0), (1, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
    ]))
    
    elements.append(packaging_table)
    elements.append(Spacer(1, 5*mm))
    
    # Photos of Faults
    elements.append(Paragraph("<b>Photos of Faults 问题图片</b>", header_style))
    elements.append(Spacer(1, 3*mm))
    
    fault_desc = [
        '1.清洁度10prs',
        '2.线条3prs',
        '3.中底接头2prs',
        '4.天皮缝隙2prs',
        '1.大底边溢胶7prs',
        '2.包中底褶皱4prs',
        '3.中皮开胶1prs',
    ]
    
    for desc in fault_desc:
        elements.append(Paragraph(desc, cell_style))
    
    elements.append(Spacer(1, 5*mm))
    
    # Add fault images if available
    if os.path.exists(image_path):
        try:
            fault_images = []
            for i in range(4):
                img = Image(image_path, width=60*mm, height=45*mm)
                fault_images.append(img)
            
            # Create 2x2 grid
            img_table = Table([[fault_images[0], fault_images[1]], 
                              [fault_images[2], fault_images[3]]])
            img_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(img_table)
        except:
            elements.append(Paragraph("[Images would be inserted here]", cell_style))
    else:
        elements.append(Paragraph("[Images would be inserted here - provide shoe_image.jpg]", cell_style))
    
    # Page Break
    elements.append(PageBreak())
    
    # ========== PAGE 3: Bulk Photos ==========
    elements.append(Paragraph("<b>Photos of Bulk 大货图片</b>", title_style))
    elements.append(Spacer(1, 5*mm))
    
    photo_labels = [
        'Production Pairs(Front) 大货鞋从鞋头正面拍',
        'Production Pairs(Side) 大货鞋侧面和样鞋拍',
        'Production Pairs(Back) 大货鞋从后跟拍',
        'Production Pair with sample(Front) 大货鞋正面和样鞋拍',
        'Production Pair with sample(Side) 大货侧面拍',
        'Production Pair with sample(Back) 大货后跟和样鞋拍',
    ]
    
    if os.path.exists(image_path):
        try:
            for i in range(0, len(photo_labels), 2):
                elements.append(Paragraph(f"<b>{photo_labels[i]}</b>", cell_style))
                if i+1 < len(photo_labels):
                    elements.append(Paragraph(f"<b>{photo_labels[i+1]}</b>", cell_style))
                
                imgs = []
                img1 = Image(image_path, width=85*mm, height=65*mm)
                imgs.append(img1)
                if i+1 < len(photo_labels):
                    img2 = Image(image_path, width=85*mm, height=65*mm)
                    imgs.append(img2)
                
                img_row = Table([imgs])
                img_row.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ]))
                elements.append(img_row)
                elements.append(Spacer(1, 3*mm))
        except:
            elements.append(Paragraph("[Bulk photos would be inserted here]", cell_style))
    else:
        elements.append(Paragraph("[Bulk photos would be inserted here - provide shoe_image.jpg]", cell_style))
    
    # Page Break
    elements.append(PageBreak())
    
    # ========== PAGE 4: Packaging Photos ==========
    elements.append(Paragraph("<b>Photos of Packaging 包装图片</b>", title_style))
    elements.append(Spacer(1, 5*mm))
    
    packaging_labels = [
        'BOX/Polybag/Mark 鞋盒/胶袋/唛头',
        'Pictogram/printing/ticket/hanger/logo 材质标/印刷/吊牌/挂钩/商标',
    ]
    
    for label in packaging_labels:
        elements.append(Paragraph(f"<b>{label}</b>", cell_style))
        elements.append(Spacer(1, 2*mm))
        
        if os.path.exists(image_path):
            try:
                img = Image(image_path, width=120*mm, height=90*mm)
                elements.append(img)
            except:
                elements.append(Paragraph("[Packaging image would be here]", cell_style))
        else:
            elements.append(Paragraph("[Packaging image would be here]", cell_style))
        
        elements.append(Spacer(1, 5*mm))
    
    elements.append(Paragraph("<b>Bulk Photos 其他正常图片</b>", header_style))
    elements.append(Spacer(1, 3*mm))
    
    if os.path.exists(image_path):
        try:
            img = Image(image_path, width=120*mm, height=90*mm)
            elements.append(img)
        except:
            elements.append(Paragraph("[Bulk normal photos would be here]", cell_style))
    else:
        elements.append(Paragraph("[Bulk normal photos would be here]", cell_style))
    
    # Build PDF
    doc.build(elements)
    print(f"QC Inspection Report created successfully: {filename}")
    print(f"Note: Place your shoe image as '{image_path}' in the same directory for images to appear")

if __name__ == "__main__":
    # Create the report
    # Make sure you have a file called 'shoe_image.jpg' in the same directory
    create_qc_inspection_report()
    print("\nReport generation complete!")
    print("If images don't appear, ensure 'shoe_image.jpg' exists in the same folder.")