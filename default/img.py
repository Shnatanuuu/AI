import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from datetime import datetime
from streamlit.components.v1 import html

st.set_page_config(layout="wide", page_title="Drag & Drop Defect Marker")
st.title("🎯 Interactive Defect Marker (Click & Drag)")

# Constants
TARGET_SIZE_INCHES = 1  # 1x1 inches
DPI = 150  # Dots per inch for display
TARGET_SIZE_PIXELS = TARGET_SIZE_INCHES * DPI  # 150x150 pixels

# Initialize session state
if 'image' not in st.session_state:
    st.session_state.image = None
if 'resized_image' not in st.session_state:
    st.session_state.resized_image = None
if 'defect_circle' not in st.session_state:
    st.session_state.defect_circle = (TARGET_SIZE_PIXELS//2, TARGET_SIZE_PIXELS//2, 30)
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = None

# Function to resize image using OpenCV
def resize_to_1x1_inch(image):
    """Resize image to 1x1 inch at specified DPI"""
    # Convert PIL to OpenCV format
    if isinstance(image, Image.Image):
        image_cv = np.array(image)
        if len(image_cv.shape) == 2:  # Grayscale
            image_cv = cv2.cvtColor(image_cv, cv2.COLOR_GRAY2RGB)
        elif image_cv.shape[2] == 4:  # RGBA
            image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGBA2RGB)
    else:
        image_cv = image
    
    # Resize while maintaining aspect ratio
    h, w = image_cv.shape[:2]
    scale = min(TARGET_SIZE_PIXELS/w, TARGET_SIZE_PIXELS/h)
    new_w, new_h = int(w * scale), int(h * scale)
    
    resized = cv2.resize(image_cv, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Create white canvas
    canvas_img = np.ones((TARGET_SIZE_PIXELS, TARGET_SIZE_PIXELS, 3), dtype=np.uint8) * 255
    
    # Center the image on canvas
    x_offset = (TARGET_SIZE_PIXELS - new_w) // 2
    y_offset = (TARGET_SIZE_PIXELS - new_h) // 2
    canvas_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return canvas_img

# File upload
uploaded = st.file_uploader("📁 Upload Image", type=["png", "jpg", "jpeg"])

if uploaded:
    if st.session_state.image is None:
        # Load image
        image = Image.open(uploaded)
        
        # Resize to 1x1 inch using OpenCV
        resized_cv = resize_to_1x1_inch(image)
        
        # Convert back to PIL for display
        resized_pil = Image.fromarray(resized_cv)
        
        # Convert to base64 for HTML
        buffered = io.BytesIO()
        resized_pil.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        st.session_state.image = image
        st.session_state.resized_image = resized_pil
        st.session_state.base64_image = img_str
        st.session_state.defect_circle = (TARGET_SIZE_PIXELS//2, TARGET_SIZE_PIXELS//2, 30)
        st.rerun()

# Custom CSS for better styling
st.markdown("""
<style>
.interactive-container {
    width: 300px;
    margin: 20px auto;
    text-align: center;
}
.canvas-container {
    position: relative;
    width: 150px;
    height: 150px;
    margin: 0 auto;
    border: 3px solid #4a5568;
    border-radius: 8px;
    overflow: hidden;
    cursor: move;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.interactive-canvas {
    width: 100%;
    height: 100%;
    display: block;
}
.drag-handle {
    position: absolute;
    width: 16px;
    height: 16px;
    background-color: #dc2626;
    border: 2px solid white;
    border-radius: 50%;
    right: -8px;
    bottom: -8px;
    cursor: nwse-resize;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    z-index: 10;
}
.drag-handle:hover {
    background-color: #ef4444;
    transform: scale(1.2);
}
.circle-outline {
    position: absolute;
    border: 3px solid #dc2626;
    border-radius: 50%;
    box-sizing: border-box;
    transform: translate(-50%, -50%);
    pointer-events: none;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.8) inset;
}
.circle-center {
    position: absolute;
    width: 8px;
    height: 8px;
    background-color: #dc2626;
    border: 2px solid white;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
.info-box {
    background: #f8fafc;
    padding: 12px;
    border-radius: 8px;
    margin-top: 15px;
    border-left: 4px solid #3b82f6;
    font-size: 14px;
}
.measurement-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}
.measurement-label {
    font-size: 12px;
    opacity: 0.9;
}
.measurement-value {
    font-size: 18px;
    font-weight: bold;
}
.stButton button {
    transition: all 0.3s ease;
}
.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

if st.session_state.resized_image:
    img = st.session_state.resized_image
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("### 🎯 Interactive Canvas (1×1 inch)")
        
        # Get current circle position
        x, y, r = st.session_state.defect_circle
        
        # Create interactive HTML/JavaScript component
        html_code = f"""
        <div class="interactive-container">
            <div class="info-box">
                <strong>🎮 How to Use:</strong><br>
                1. <strong>Click & drag the circle</strong> to move it<br>
                2. <strong>Drag the red handle</strong> to resize<br>
                3. Changes update automatically
            </div>
            
            <div id="canvasWrapper" class="canvas-container">
                <img id="baseImage" src="data:image/png;base64,{st.session_state.base64_image}" 
                     class="interactive-canvas" draggable="false">
                
                <div id="circleOutline" class="circle-outline"
                     style="left: {x}px; top: {y}px; width: {2*r}px; height: {2*r}px;">
                </div>
                
                <div id="circleCenter" class="circle-center"
                     style="left: {x}px; top: {y}px;">
                </div>
                
                <div id="resizeHandle" class="drag-handle"
                     style="left: {x + r}px; top: {y + r}px;">
                </div>
            </div>
            
            <div class="measurement-box">
                <div style="display: flex; justify-content: space-around; text-align: center;">
                    <div>
                        <div class="measurement-label">X Position</div>
                        <div class="measurement-value" id="posX">{x}</div>
                        <div style="font-size: 10px;">{x/DPI:.2f} in</div>
                    </div>
                    <div>
                        <div class="measurement-label">Y Position</div>
                        <div class="measurement-value" id="posY">{y}</div>
                        <div style="font-size: 10px;">{y/DPI:.2f} in</div>
                    </div>
                    <div>
                        <div class="measurement-label">Radius</div>
                        <div class="measurement-value" id="radius">{r}</div>
                        <div style="font-size: 10px;">{r/DPI:.2f} in</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <button onclick="centerCircle()" style="
                    background: #3b82f6;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 5px;
                    font-weight: bold;
                ">🎯 Center Circle</button>
                
                <button onclick="sendToPython()" style="
                    background: #10b981;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 5px;
                    font-weight: bold;
                ">💾 Save Position</button>
            </div>
        </div>
        
        <script>
        let circle = {{
            x: {x},
            y: {y},
            r: {r},
            dragging: false,
            resizing: false,
            startX: 0,
            startY: 0
        }};
        
        const container = document.getElementById('canvasWrapper');
        const circleOutline = document.getElementById('circleOutline');
        const circleCenter = document.getElementById('circleCenter');
        const resizeHandle = document.getElementById('resizeHandle');
        const posX = document.getElementById('posX');
        const posY = document.getElementById('posY');
        const radius = document.getElementById('radius');
        
        function updateVisuals() {{
            // Update circle visuals
            circleOutline.style.left = circle.x + 'px';
            circleOutline.style.top = circle.y + 'px';
            circleOutline.style.width = (circle.r * 2) + 'px';
            circleOutline.style.height = (circle.r * 2) + 'px';
            
            // Update center dot
            circleCenter.style.left = circle.x + 'px';
            circleCenter.style.top = circle.y + 'px';
            
            // Update resize handle
            resizeHandle.style.left = (circle.x + circle.r) + 'px';
            resizeHandle.style.top = (circle.y + circle.r) + 'px';
            
            // Update measurements
            posX.textContent = Math.round(circle.x);
            posY.textContent = Math.round(circle.y);
            radius.textContent = Math.round(circle.r);
            
            // Update inch measurements
            posX.nextElementSibling.textContent = (circle.x / {DPI}).toFixed(2) + ' in';
            posY.nextElementSibling.textContent = (circle.y / {DPI}).toFixed(2) + ' in';
            radius.nextElementSibling.textContent = (circle.r / {DPI}).toFixed(2) + ' in';
        }}
        
        function getMousePos(e) {{
            const rect = container.getBoundingClientRect();
            return {{
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            }};
        }}
        
        function startDrag(e) {{
            e.preventDefault();
            const pos = getMousePos(e);
            
            // Check if clicking on resize handle
            const handleRect = resizeHandle.getBoundingClientRect();
            if (e.clientX >= handleRect.left && e.clientX <= handleRect.right &&
                e.clientY >= handleRect.top && e.clientY <= handleRect.bottom) {{
                circle.resizing = true;
            }} else {{
                circle.dragging = true;
            }}
            
            circle.startX = pos.x - circle.x;
            circle.startY = pos.y - circle.y;
        }}
        
        function doDrag(e) {{
            if (!circle.dragging && !circle.resizing) return;
            
            const pos = getMousePos(e);
            
            if (circle.dragging) {{
                // Move the circle
                let newX = pos.x - circle.startX;
                let newY = pos.y - circle.startY;
                
                // Constrain to canvas bounds
                newX = Math.max(circle.r, Math.min({TARGET_SIZE_PIXELS} - circle.r, newX));
                newY = Math.max(circle.r, Math.min({TARGET_SIZE_PIXELS} - circle.r, newY));
                
                circle.x = newX;
                circle.y = newY;
            }}
            
            if (circle.resizing) {{
                // Resize the circle
                const dx = pos.x - circle.x;
                const dy = pos.y - circle.y;
                let newR = Math.sqrt(dx * dx + dy * dy);
                
                // Constrain radius
                newR = Math.max(10, Math.min({TARGET_SIZE_PIXELS//2}, newR));
                
                // Constrain position if needed
                circle.x = Math.max(newR, Math.min({TARGET_SIZE_PIXELS} - newR, circle.x));
                circle.y = Math.max(newR, Math.min({TARGET_SIZE_PIXELS} - newR, circle.y));
                
                circle.r = newR;
            }}
            
            updateVisuals();
        }}
        
        function stopDrag() {{
            circle.dragging = false;
            circle.resizing = false;
            sendToPython();
        }}
        
        function centerCircle() {{
            circle.x = {TARGET_SIZE_PIXELS//2};
            circle.y = {TARGET_SIZE_PIXELS//2};
            circle.r = 30;
            updateVisuals();
            sendToPython();
        }}
        
        function sendToPython() {{
            // Send data to Streamlit
            const data = {{
                x: Math.round(circle.x),
                y: Math.round(circle.y),
                r: Math.round(circle.r)
            }};
            
            // Use Streamlit's setComponentValue if available
            if (window.parent.streamlit && window.parent.streamlit.setComponentValue) {{
                window.parent.streamlit.setComponentValue(data);
            }}
            
            // Alternative: dispatch event
            document.body.dispatchEvent(new CustomEvent('CIRCLE_UPDATE', {{
                detail: data
            }}));
            
            console.log('Circle data sent:', data);
        }}
        
        // Event listeners
        container.addEventListener('mousedown', startDrag);
        document.addEventListener('mousemove', doDrag);
        document.addEventListener('mouseup', stopDrag);
        
        // Touch events for mobile
        container.addEventListener('touchstart', function(e) {{
            e.preventDefault();
            startDrag(e.touches[0]);
        }}, {{passive: false}});
        
        document.addEventListener('touchmove', function(e) {{
            if (!circle.dragging && !circle.resizing) return;
            e.preventDefault();
            doDrag(e.touches[0]);
        }}, {{passive: false}});
        
        document.addEventListener('touchend', stopDrag);
        
        // Initialize
        updateVisuals();
        </script>
        """
        
        # Display the interactive component
        html(html_code, height=450)
        
        # JavaScript to handle communication
        js_comm = """
        <script>
        // Listen for circle updates
        document.addEventListener('CIRCLE_UPDATE', function(e) {
            console.log('Received circle update:', e.detail);
            
            // Create a hidden form to send data to Streamlit
            const form = document.createElement('form');
            form.method = 'POST';
            
            for (const key in e.detail) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = key;
                input.value = e.detail[key];
                form.appendChild(input);
            }
            
            document.body.appendChild(form);
            
            // In a real Streamlit component, you would use:
            // Streamlit.setComponentValue(e.detail);
        });
        </script>
        """
        
        html(js_comm)
        
        # Manual update section (fallback)
        st.markdown("---")
        st.markdown("**🔄 Manual Update (if needed):**")
        
        # Create a form for manual update
        with st.form("manual_update"):
            man_col1, man_col2 = st.columns(2)
            with man_col1:
                new_x = st.number_input("X Position", 0, TARGET_SIZE_PIXELS, x)
                new_y = st.number_input("Y Position", 0, TARGET_SIZE_PIXELS, y)
            with man_col2:
                new_r = st.number_input("Radius", 10, TARGET_SIZE_PIXELS//2, r)
            
            if st.form_submit_button("Update Circle Manually"):
                st.session_state.defect_circle = (new_x, new_y, new_r)
                st.success("Circle updated!")
                st.rerun()
    
    with col2:
        st.markdown("### 📋 Preview & Report Generation")
        
        # Create preview with OpenCV for better quality
        preview_cv = np.array(img)
        
        # Draw circle using OpenCV (smoother than PIL)
        x, y, r = st.session_state.defect_circle
        
        # Draw main circle
        cv2.circle(preview_cv, (int(x), int(y)), int(r), (220, 50, 50), 3)
        
        # Draw center point
        cv2.circle(preview_cv, (int(x), int(y)), 6, (220, 50, 50), -1)
        cv2.circle(preview_cv, (int(x), int(y)), 6, (255, 255, 255), 2)
        
        # Draw crosshair
        cv2.line(preview_cv, (int(x)-10, int(y)), (int(x)+10, int(y)), (220, 50, 50), 2)
        cv2.line(preview_cv, (int(x), int(y)-10), (int(x), int(y)+10), (220, 50, 50), 2)
        
        # Draw measurement lines
        cv2.line(preview_cv, (int(x), int(y)-int(r)), (int(x), int(y)+int(r)), 
                (220, 50, 50), 1, cv2.LINE_AA)
        cv2.line(preview_cv, (int(x)-int(r), int(y)), (int(x)+int(r), int(y)), 
                (220, 50, 50), 1, cv2.LINE_AA)
        
        # Add text with measurements
        cv2.putText(preview_cv, f"Radius: {r}px", (10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(preview_cv, f"Radius: {r}px", (10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Convert back to PIL for display
        preview_pil = Image.fromarray(preview_cv)
        
        # Display preview
        st.image(preview_pil, caption="Preview with defect marker", width=250)
        
        # Measurement display
        st.markdown("### 📏 Measurements")
        
        # Calculate inch measurements
        inches_x = x / DPI
        inches_y = y / DPI
        inches_r = r / DPI
        inches_diameter = 2 * inches_r
        
        # Display in a nice format
        col_meas1, col_meas2 = st.columns(2)
        with col_meas1:
            st.metric("X Position", f"{x} px", f"{inches_x:.2f} in")
            st.metric("Y Position", f"{y} px", f"{inches_y:.2f} in")
        with col_meas2:
            st.metric("Radius", f"{r} px", f"{inches_r:.2f} in")
            st.metric("Diameter", f"{2*r} px", f"{inches_diameter:.2f} in")
        
        st.markdown("---")
        
        # Report form
        st.markdown("### 📄 Report Details")
        
        defect_type = st.selectbox("Defect Type", ["Crack", "Corrosion", "Dent", "Spalling", "Other"])
        severity = st.select_slider("Severity Level", ["Low", "Medium", "High", "Critical"])
        location = st.text_input("Location", placeholder="e.g., Column A-3, Beam 5")
        inspector = st.text_input("Inspector Name", placeholder="Your name")
        notes = st.text_area("Additional Notes", placeholder="Observations, measurements, recommendations...", 
                           height=100)
        
        st.markdown("---")
        
        # Generate PDF
        if st.button("📄 GENERATE PDF REPORT", type="primary", use_container_width=True):
            if not location or not inspector:
                st.error("❌ Please fill in Location and Inspector fields!")
            else:
                with st.spinner("Generating PDF report..."):
                    # Create PDF
                    pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(pdf_buffer, pagesize=A4)
                    
                    # Title
                    c.setFont("Helvetica-Bold", 24)
                    c.drawString(50, 780, "DEFECT INSPECTION REPORT")
                    
                    # Scale information
                    c.setFont("Helvetica", 10)
                    c.drawString(50, 760, f"Image Scale: 1 inch = {DPI} pixels | Image Size: 1×1 inch")
                    
                    # Defect details
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(50, 730, "DEFECT INFORMATION")
                    c.setFont("Helvetica", 11)
                    
                    y_pos = 710
                    details = [
                        f"Type: {defect_type}",
                        f"Severity: {severity}",
                        "",
                        "IMAGE MEASUREMENTS:",
                        f"  • Position: ({x}, {y}) pixels",
                        f"  • Position: ({inches_x:.2f}, {inches_y:.2f}) inches",
                        f"  • Radius: {r} pixels ({inches_r:.2f} inches)",
                        f"  • Diameter: {2*r} pixels ({inches_diameter:.2f} inches)",
                        "",
                        "INSPECTION DETAILS:",
                        f"  • Location: {location}",
                        f"  • Inspector: {inspector}",
                        f"  • Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    ]
                    
                    for detail in details:
                        if detail.startswith("  •"):
                            c.setFont("Helvetica", 10)
                            c.drawString(70, y_pos, detail)
                            y_pos -= 15
                        elif detail.startswith("IMAGE") or detail.startswith("INSPECTION"):
                            c.setFont("Helvetica-Bold", 11)
                            c.drawString(50, y_pos, detail)
                            y_pos -= 20
                        elif detail == "":
                            y_pos -= 10
                        else:
                            c.setFont("Helvetica", 11)
                            c.drawString(50, y_pos, detail)
                            y_pos -= 20
                    
                    y_pos -= 10
                    
                    if notes:
                        c.setFont("Helvetica-Bold", 11)
                        c.drawString(50, y_pos, "ADDITIONAL NOTES:")
                        y_pos -= 15
                        c.setFont("Helvetica", 10)
                        # Wrap long notes
                        words = notes.split()
                        lines = []
                        current_line = ""
                        for word in words:
                            if len(current_line + " " + word) <= 80:
                                current_line += " " + word
                            else:
                                lines.append(current_line.strip())
                                current_line = word
                        if current_line:
                            lines.append(current_line.strip())
                        
                        for line in lines:
                            c.drawString(70, y_pos, line)
                            y_pos -= 15
                    
                    # Add the image to PDF
                    c.setFont("Helvetica-Bold", 14)
                    y_pos = max(200, y_pos)
                    c.drawString(50, y_pos, "DEFECT IMAGE (1×1 inch scale)")
                    
                    # Convert preview image for PDF
                    img_buffer = io.BytesIO()
                    preview_pil.save(img_buffer, format="PNG", dpi=(DPI, DPI))
                    img_buffer.seek(0)
                    
                    # Draw image at 2x size for visibility
                    pdf_image_size = 1 * 72 * 2  # 2 inches at PDF standard 72 DPI
                    c.drawImage(ImageReader(img_buffer), 50, 50, 
                               width=pdf_image_size, height=pdf_image_size)
                    
                    # Add scale reference
                    c.setFont("Helvetica", 9)
                    c.drawString(50, 40, "Scale: 1 inch = 150 pixels | Red circle indicates defect location")
                    
                    c.showPage()
                    c.save()
                    pdf_buffer.seek(0)
                    
                    st.success("✅ PDF Generated Successfully!")
                    st.balloons()
                    
                    # Download button
                    st.download_button(
                        "📥 Download PDF Report",
                        pdf_buffer,
                        f"defect_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        "application/pdf",
                        use_container_width=True,
                        type="primary"
                    )

else:
    # Welcome screen
    st.info("👆 **Upload an image to begin**")
    
    # Demo instructions
    st.markdown("""
    ## 🎯 **Interactive Defect Marker**
    
    ### **Features:**
    
    **🎮 Intuitive Controls:**
    - **Click & drag** the circle to move it
    - **Drag the red handle** to resize
    - No sliders needed - pure mouse/touch interaction
    
    **📐 Accurate Measurements:**
    - Automatic 1×1 inch canvas (150×150 pixels)
    - Real-time pixel to inch conversion
    - Precise positioning
    
    **📄 Professional Reports:**
    - Generate PDF with all measurements
    - Include defect details and notes
    - High-quality output
    
    ### **How to Use:**
    1. **Upload** your inspection image
    2. **Drag** the red circle to mark the defect
    3. **Resize** using the red handle
    4. **Fill** in defect details
    5. **Generate** PDF report
    
    ### **Technical Specifications:**
    - Canvas: **1 inch × 1 inch**
    - Resolution: **150 DPI** (150 pixels per inch)
    - Output: **Vector PDF** with embedded image
    - Support: **Desktop & Mobile** touch enabled
    """)

# Note about interactive component
st.markdown("---")
st.markdown("*💡 **Tip**: For best experience, click and drag the circle directly on the interactive canvas*")