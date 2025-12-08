import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(page_title="Interactive Circle Annotator", layout="wide")

# Initialize session state
if 'circle_x' not in st.session_state:
    st.session_state.circle_x = 0.5
if 'circle_y' not in st.session_state:
    st.session_state.circle_y = 0.5
if 'circle_radius' not in st.session_state:
    st.session_state.circle_radius = 0.1
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'image_width' not in st.session_state:
    st.session_state.image_width = 0
if 'image_height' not in st.session_state:
    st.session_state.image_height = 0

def create_annotated_image(img, circle_x, circle_y, radius, show_handles=True):
    """Create image with circle annotation"""
    img_copy = img.copy()
    draw = ImageDraw.Draw(img_copy)
    
    width, height = img.size
    cx = int(circle_x * width)
    cy = int(circle_y * height)
    r = int(radius * min(width, height))
    
    # Draw red circle
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline='red', width=3)
    
    if show_handles:
        # Draw center dot
        dot_size = 5
        draw.ellipse([cx-dot_size, cy-dot_size, cx+dot_size, cy+dot_size], fill='red')
        
        # Draw resize handle (blue dot on right edge)
        handle_x = cx + r
        handle_y = cy
        handle_size = 8
        draw.ellipse([handle_x-handle_size, handle_y-handle_size, 
                     handle_x+handle_size, handle_y+handle_size], fill='blue')
    
    return img_copy

def image_to_base64(img):
    """Convert PIL image to base64 string"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def create_interactive_canvas(img, circle_x, circle_y, radius):
    """Create interactive HTML canvas with drag-and-drop circle"""
    annotated_img = create_annotated_image(img, circle_x, circle_y, radius)
    img_base64 = image_to_base64(annotated_img)
    
    width, height = img.size
    display_width = min(800, width)
    display_height = int(height * display_width / width)
    
    html_code = f"""
    <div style="border: 2px solid #ccc; display: inline-block;">
        <canvas id="canvas" width="{display_width}" height="{display_height}" 
                style="cursor: move; background-image: url(data:image/png;base64,{img_base64}); 
                       background-size: contain; background-repeat: no-repeat;"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        let isDragging = false;
        let isResizing = false;
        let dragMode = 'move';
        
        // Circle parameters (normalized 0-1)
        let circleX = {circle_x};
        let circleY = {circle_y};
        let circleRadius = {radius};
        
        const imgWidth = {width};
        const imgHeight = {height};
        const displayWidth = {display_width};
        const displayHeight = {display_height};
        
        // Load background image
        const img = new Image();
        img.src = 'data:image/png;base64,{img_base64}';
        
        function drawCircle() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, displayWidth, displayHeight);
            
            const cx = circleX * displayWidth;
            const cy = circleY * displayHeight;
            const r = circleRadius * Math.min(displayWidth, displayHeight);
            
            // Draw red circle
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, 2 * Math.PI);
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 3;
            ctx.stroke();
            
            // Draw center dot
            ctx.beginPath();
            ctx.arc(cx, cy, 5, 0, 2 * Math.PI);
            ctx.fillStyle = 'red';
            ctx.fill();
            
            // Draw resize handle
            const handleX = cx + r;
            const handleY = cy;
            ctx.beginPath();
            ctx.arc(handleX, handleY, 8, 0, 2 * Math.PI);
            ctx.fillStyle = 'blue';
            ctx.fill();
        }}
        
        function getMousePos(e) {{
            const rect = canvas.getBoundingClientRect();
            return {{
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            }};
        }}
        
        function isNearCenter(mx, my) {{
            const cx = circleX * displayWidth;
            const cy = circleY * displayHeight;
            const dist = Math.sqrt((mx - cx) ** 2 + (my - cy) ** 2);
            return dist < 15;
        }}
        
        function isNearHandle(mx, my) {{
            const cx = circleX * displayWidth;
            const cy = circleY * displayHeight;
            const r = circleRadius * Math.min(displayWidth, displayHeight);
            const handleX = cx + r;
            const handleY = cy;
            const dist = Math.sqrt((mx - handleX) ** 2 + (my - handleY) ** 2);
            return dist < 15;
        }}
        
        canvas.addEventListener('mousedown', (e) => {{
            const pos = getMousePos(e);
            
            if (isNearHandle(pos.x, pos.y)) {{
                isResizing = true;
                dragMode = 'resize';
                canvas.style.cursor = 'ew-resize';
            }} else if (isNearCenter(pos.x, pos.y)) {{
                isDragging = true;
                dragMode = 'move';
                canvas.style.cursor = 'grabbing';
            }}
        }});
        
        canvas.addEventListener('mousemove', (e) => {{
            const pos = getMousePos(e);
            
            if (isDragging) {{
                circleX = Math.max(0.1, Math.min(0.9, pos.x / displayWidth));
                circleY = Math.max(0.1, Math.min(0.9, pos.y / displayHeight));
                drawCircle();
                updateStreamlit();
            }} else if (isResizing) {{
                const cx = circleX * displayWidth;
                const cy = circleY * displayHeight;
                const dist = Math.sqrt((pos.x - cx) ** 2 + (pos.y - cy) ** 2);
                circleRadius = Math.max(0.02, Math.min(0.4, dist / Math.min(displayWidth, displayHeight)));
                drawCircle();
                updateStreamlit();
            }} else {{
                // Update cursor based on hover
                if (isNearHandle(pos.x, pos.y)) {{
                    canvas.style.cursor = 'ew-resize';
                }} else if (isNearCenter(pos.x, pos.y)) {{
                    canvas.style.cursor = 'grab';
                }} else {{
                    canvas.style.cursor = 'default';
                }}
            }}
        }});
        
        canvas.addEventListener('mouseup', () => {{
            isDragging = false;
            isResizing = false;
            canvas.style.cursor = 'move';
        }});
        
        canvas.addEventListener('mouseleave', () => {{
            isDragging = false;
            isResizing = false;
            canvas.style.cursor = 'move';
        }});
        
        function updateStreamlit() {{
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: {{
                    circle_x: circleX,
                    circle_y: circleY,
                    circle_radius: circleRadius
                }}
            }}, '*');
        }}
        
        img.onload = () => {{
            drawCircle();
        }};
    </script>
    """
    
    return html_code

def generate_pdf(img, circle_x, circle_y, radius):
    """Generate PDF with annotated image"""
    # Create final annotated image without handles
    final_img = create_annotated_image(img, circle_x, circle_y, radius, show_handles=False)
    
    # Create PDF
    buffer = io.BytesIO()
    width, height = img.size
    
    # Use image dimensions for PDF
    pdf_canvas = canvas.Canvas(buffer, pagesize=(width, height))
    
    # Convert PIL image to reportlab ImageReader
    img_buffer = io.BytesIO()
    final_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_reader = ImageReader(img_buffer)
    
    # Draw image on PDF
    pdf_canvas.drawImage(img_reader, 0, 0, width=width, height=height)
    pdf_canvas.save()
    
    buffer.seek(0)
    return buffer

# UI Layout
st.title("🎯 Interactive Circle Annotator")
st.markdown("Upload an image and **drag the circle** to position it, **drag the blue handle** to resize it!")

# File uploader
uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Load image
    img = Image.open(uploaded_file)
    st.session_state.uploaded_image = img
    st.session_state.image_width = img.width
    st.session_state.image_height = img.height
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Interactive Canvas")
        st.markdown("**Instructions:**")
        st.markdown("- 🔴 Drag the **red center dot** to move the circle")
        st.markdown("- 🔵 Drag the **blue handle** to resize the circle")
        
        # Create interactive canvas
        component_value = components.html(
            create_interactive_canvas(img, st.session_state.circle_x, 
                                     st.session_state.circle_y, 
                                     st.session_state.circle_radius),
            height=min(600, int(img.height * 800 / img.width)),
            scrolling=False
        )
        
        # Update session state from component
        if component_value is not None and isinstance(component_value, dict):
            if 'circle_x' in component_value:
                st.session_state.circle_x = component_value['circle_x']
            if 'circle_y' in component_value:
                st.session_state.circle_y = component_value['circle_y']
            if 'circle_radius' in component_value:
                st.session_state.circle_radius = component_value['circle_radius']
    
    with col2:
        st.subheader("Controls")
        
        # Display current values (read-only)
        st.markdown("**Current Position & Size:**")
        actual_x = int(st.session_state.circle_x * img.width)
        actual_y = int(st.session_state.circle_y * img.height)
        actual_r = int(st.session_state.circle_radius * min(img.width, img.height))
        
        st.info(f"""
        **X Position:** {actual_x} px  
        **Y Position:** {actual_y} px  
        **Radius:** {actual_r} px
        """)
        
        # Reset button
        if st.button("🔄 Reset to Center", use_container_width=True):
            st.session_state.circle_x = 0.5
            st.session_state.circle_y = 0.5
            st.session_state.circle_radius = 0.1
            st.rerun()
        
        st.markdown("---")
        
        # Quick adjustment buttons
        st.markdown("**Quick Adjustments:**")
        
        col_up, col_down = st.columns(2)
        with col_up:
            if st.button("⬆️ Move Up", use_container_width=True):
                st.session_state.circle_y = max(0.05, st.session_state.circle_y - 0.05)
                st.rerun()
        with col_down:
            if st.button("⬇️ Move Down", use_container_width=True):
                st.session_state.circle_y = min(0.95, st.session_state.circle_y + 0.05)
                st.rerun()
        
        col_left, col_right = st.columns(2)
        with col_left:
            if st.button("⬅️ Move Left", use_container_width=True):
                st.session_state.circle_x = max(0.05, st.session_state.circle_x - 0.05)
                st.rerun()
        with col_right:
            if st.button("➡️ Move Right", use_container_width=True):
                st.session_state.circle_x = min(0.95, st.session_state.circle_x + 0.05)
                st.rerun()
        
        col_smaller, col_bigger = st.columns(2)
        with col_smaller:
            if st.button("➖ Smaller", use_container_width=True):
                st.session_state.circle_radius = max(0.02, st.session_state.circle_radius - 0.02)
                st.rerun()
        with col_bigger:
            if st.button("➕ Bigger", use_container_width=True):
                st.session_state.circle_radius = min(0.4, st.session_state.circle_radius + 0.02)
                st.rerun()
        
        st.markdown("---")
        
        # Preview
        st.subheader("Preview")
        preview_img = create_annotated_image(img, st.session_state.circle_x, 
                                            st.session_state.circle_y, 
                                            st.session_state.circle_radius,
                                            show_handles=False)
        st.image(preview_img, use_container_width=True, caption="Final output preview")
        
        st.markdown("---")
        
        # PDF Generation
        st.subheader("Export")
        if st.button("📄 Generate PDF", type="primary", use_container_width=True):
            with st.spinner("Generating PDF..."):
                pdf_buffer = generate_pdf(img, st.session_state.circle_x, 
                                         st.session_state.circle_y, 
                                         st.session_state.circle_radius)
                
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_buffer,
                    file_name="annotated_image.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("✅ PDF ready for download!")

else:
    st.info("👆 Please upload an image to get started!")
    st.markdown("""
    ### How to use this tool:
    1. **Upload** an image using the file uploader above
    2. **Drag** the red center dot to position the circle
    3. **Drag** the blue handle on the circle's edge to resize it
    4. **Preview** your annotation in the sidebar
    5. **Generate PDF** to download your annotated image
    
    *No sliders, no manual inputs - just pure visual interaction!*
    """)