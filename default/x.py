import streamlit as st
import streamlit.components.v1 as components
import base64
import io
from PIL import Image
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader

# Page configuration
st.set_page_config(page_title="Circle Annotator", layout="wide", initial_sidebar_state="collapsed")

# Create the React component HTML with direct PDF generation
def create_react_app():
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Circle Annotator</title>
        <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
        <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
        <style>
            body { margin: 0; padding: 0; }
        </style>
    </head>
    <body>
        <div id="root"></div>
        
        <script type="text/babel">
            const { useState, useRef, useEffect } = React;
            const { jsPDF } = window.jspdf;
            
            function CircleAnnotator() {
              const [image, setImage] = useState(null);
              const [imageDataUrl, setImageDataUrl] = useState(null);
              const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
              const [circle, setCircle] = useState({ x: 0.5, y: 0.5, radius: 0.1 });
              const [dragging, setDragging] = useState(null);
              const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
              const [cursorStyle, setCursorStyle] = useState('default');
              const [generating, setGenerating] = useState(false);
              
              const canvasRef = useRef(null);
              const fileInputRef = useRef(null);
              const containerRef = useRef(null);

              useEffect(() => {
                drawCanvas();
              }, [image, circle, imageSize]);

              const handleImageUpload = (e) => {
                const file = e.target.files[0];
                if (file) {
                  const reader = new FileReader();
                  reader.onload = (event) => {
                    const img = new Image();
                    img.onload = () => {
                      setImageSize({ width: img.width, height: img.height });
                      setImage(img);
                      setImageDataUrl(event.target.result);
                      setCircle({ x: 0.5, y: 0.5, radius: 0.1 });
                    };
                    img.src = event.target.result;
                  };
                  reader.readAsDataURL(file);
                }
              };

              const drawCanvas = () => {
                const canvas = canvasRef.current;
                if (!canvas || !image) return;

                const ctx = canvas.getContext('2d');
                const container = containerRef.current;
                const maxWidth = container ? container.clientWidth - 40 : 800;
                const scale = Math.min(1, maxWidth / imageSize.width);
                const displayWidth = imageSize.width * scale;
                const displayHeight = imageSize.height * scale;

                canvas.width = displayWidth;
                canvas.height = displayHeight;

                ctx.clearRect(0, 0, displayWidth, displayHeight);
                ctx.drawImage(image, 0, 0, displayWidth, displayHeight);

                const cx = circle.x * displayWidth;
                const cy = circle.y * displayHeight;
                const r = circle.radius * Math.min(displayWidth, displayHeight);

                ctx.beginPath();
                ctx.arc(cx, cy, r, 0, 2 * Math.PI);
                ctx.strokeStyle = '#ef4444';
                ctx.lineWidth = 4;
                ctx.stroke();

                ctx.beginPath();
                ctx.arc(cx, cy, 12, 0, 2 * Math.PI);
                ctx.fillStyle = '#ef4444';
                ctx.fill();
                ctx.strokeStyle = 'white';
                ctx.lineWidth = 3;
                ctx.stroke();

                const handleX = cx + r;
                const handleY = cy;
                ctx.beginPath();
                ctx.arc(handleX, handleY, 12, 0, 2 * Math.PI);
                ctx.fillStyle = '#3b82f6';
                ctx.fill();
                ctx.strokeStyle = 'white';
                ctx.lineWidth = 3;
                ctx.stroke();
              };

              const getMousePos = (e) => {
                const canvas = canvasRef.current;
                if (!canvas) return { x: 0, y: 0 };
                
                const rect = canvas.getBoundingClientRect();
                return {
                  x: (e.clientX - rect.left) * (canvas.width / rect.width),
                  y: (e.clientY - rect.top) * (canvas.height / rect.height)
                };
              };

              const distance = (x1, y1, x2, y2) => {
                return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
              };

              const handleMouseDown = (e) => {
                if (!image) return;
                
                const pos = getMousePos(e);
                const canvas = canvasRef.current;
                const cx = circle.x * canvas.width;
                const cy = circle.y * canvas.height;
                const r = circle.radius * Math.min(canvas.width, canvas.height);

                if (distance(pos.x, pos.y, cx, cy) < 20) {
                  setDragging('center');
                  setDragStart({ x: pos.x - cx, y: pos.y - cy });
                  setCursorStyle('grabbing');
                  e.preventDefault();
                }
                else if (distance(pos.x, pos.y, cx + r, cy) < 20) {
                  setDragging('edge');
                  setDragStart({ x: cx, y: cy });
                  setCursorStyle('ew-resize');
                  e.preventDefault();
                }
              };

              const handleMouseMove = (e) => {
                const canvas = canvasRef.current;
                if (!canvas || !image) return;

                const pos = getMousePos(e);

                if (dragging === 'center') {
                  const newX = (pos.x - dragStart.x) / canvas.width;
                  const newY = (pos.y - dragStart.y) / canvas.height;
                  
                  setCircle(prev => ({
                    ...prev,
                    x: Math.max(0.05, Math.min(0.95, newX)),
                    y: Math.max(0.05, Math.min(0.95, newY))
                  }));
                } else if (dragging === 'edge') {
                  const cx = dragStart.x;
                  const cy = dragStart.y;
                  const dist = distance(pos.x, pos.y, cx, cy);
                  const newRadius = dist / Math.min(canvas.width, canvas.height);
                  
                  setCircle(prev => ({
                    ...prev,
                    radius: Math.max(0.03, Math.min(0.45, newRadius))
                  }));
                } else {
                  const cx = circle.x * canvas.width;
                  const cy = circle.y * canvas.height;
                  const r = circle.radius * Math.min(canvas.width, canvas.height);
                  
                  if (distance(pos.x, pos.y, cx, cy) < 20) {
                    setCursorStyle('grab');
                  } else if (distance(pos.x, pos.y, cx + r, cy) < 20) {
                    setCursorStyle('ew-resize');
                  } else {
                    setCursorStyle('crosshair');
                  }
                }
              };

              const handleMouseUp = () => {
                if (dragging) {
                  setDragging(null);
                  setCursorStyle('default');
                }
              };

              const handleReset = () => {
                setCircle({ x: 0.5, y: 0.5, radius: 0.1 });
              };

              const createAnnotatedImage = () => {
                // Create a canvas at full resolution without handles
                const tempCanvas = document.createElement('canvas');
                tempCanvas.width = imageSize.width;
                tempCanvas.height = imageSize.height;
                const ctx = tempCanvas.getContext('2d');

                // Draw image
                ctx.drawImage(image, 0, 0);

                // Draw circle
                const cx = circle.x * imageSize.width;
                const cy = circle.y * imageSize.height;
                const r = circle.radius * Math.min(imageSize.width, imageSize.height);

                ctx.beginPath();
                ctx.arc(cx, cy, r, 0, 2 * Math.PI);
                ctx.strokeStyle = '#ef4444';
                ctx.lineWidth = 8;
                ctx.stroke();

                return tempCanvas;
              };

              const handleDownloadPNG = () => {
                if (!image) return;

                const tempCanvas = createAnnotatedImage();
                tempCanvas.toBlob((blob) => {
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'annotated-image.png';
                  a.click();
                  URL.revokeObjectURL(url);
                });
              };

              const handleDownloadPDF = () => {
                if (!image) return;

                setGenerating(true);

                try {
                  // Create annotated canvas
                  const tempCanvas = createAnnotatedImage();
                  const imgData = tempCanvas.toDataURL('image/jpeg', 1.0);

                  // Create PDF with image dimensions
                  const pdf = new jsPDF({
                    orientation: imageSize.width > imageSize.height ? 'landscape' : 'portrait',
                    unit: 'px',
                    format: [imageSize.width, imageSize.height]
                  });

                  // Add image to PDF
                  pdf.addImage(imgData, 'JPEG', 0, 0, imageSize.width, imageSize.height);

                  // Save PDF
                  pdf.save('annotated-image.pdf');

                  setGenerating(false);
                } catch (error) {
                  console.error('PDF generation error:', error);
                  alert('Error generating PDF: ' + error.message);
                  setGenerating(false);
                }
              };

              const actualX = Math.round(circle.x * imageSize.width);
              const actualY = Math.round(circle.y * imageSize.height);
              const actualR = Math.round(circle.radius * Math.min(imageSize.width, imageSize.height));

              return (
                <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
                  <div className="max-w-7xl mx-auto">
                    <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
                      <div className="bg-gradient-to-r from-red-600 to-pink-600 p-6 text-white">
                        <h1 className="text-3xl font-bold mb-2">🎯 Drag & Drop Circle Annotator</h1>
                        <p className="text-red-50">Click and drag the handles to position and resize the circle</p>
                      </div>

                      <div className="p-6" ref={containerRef}>
                        {!image ? (
                          <div className="text-center py-20">
                            <input
                              ref={fileInputRef}
                              type="file"
                              accept="image/*"
                              onChange={handleImageUpload}
                              className="hidden"
                            />
                            <button
                              onClick={() => fileInputRef.current.click()}
                              className="inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl hover:from-red-700 hover:to-pink-700 transition-all text-xl font-bold shadow-2xl transform hover:scale-105"
                            >
                              📤 Upload Image
                            </button>
                            <p className="mt-6 text-gray-600 text-lg">Support: PNG, JPG, JPEG</p>
                          </div>
                        ) : (
                          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                            <div className="lg:col-span-3">
                              <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl p-6 border-2 border-slate-200">
                                <div className="mb-4 bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg">
                                  <div className="flex items-start gap-3">
                                    <div className="bg-blue-500 text-white rounded-full p-2">
                                      ✋
                                    </div>
                                    <div>
                                      <p className="font-bold text-blue-900 mb-1">Interactive Controls:</p>
                                      <p className="text-sm text-blue-800">🔴 <strong>Drag red dot</strong> to move circle</p>
                                      <p className="text-sm text-blue-800">🔵 <strong>Drag blue dot</strong> to resize circle</p>
                                    </div>
                                  </div>
                                </div>
                                
                                <div className="flex justify-center">
                                  <canvas
                                    ref={canvasRef}
                                    onMouseDown={handleMouseDown}
                                    onMouseMove={handleMouseMove}
                                    onMouseUp={handleMouseUp}
                                    onMouseLeave={handleMouseUp}
                                    className="border-4 border-slate-300 rounded-lg shadow-2xl max-w-full"
                                    style={{ 
                                      cursor: cursorStyle,
                                      touchAction: 'none'
                                    }}
                                  />
                                </div>
                                
                                {dragging && (
                                  <div className="mt-4 p-3 bg-yellow-50 border-l-4 border-yellow-500 rounded">
                                    <p className="text-yellow-800 font-semibold">
                                      {dragging === 'center' ? '🔴 Moving circle...' : '🔵 Resizing circle...'}
                                    </p>
                                  </div>
                                )}
                              </div>
                            </div>

                            <div className="space-y-4">
                              <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl p-5 border-2 border-slate-200">
                                <h3 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
                                  📏 Position & Size
                                </h3>
                                <div className="space-y-3 text-sm">
                                  <div className="flex justify-between items-center p-2 bg-white rounded">
                                    <span className="text-slate-600 font-medium">X Position:</span>
                                    <span className="font-mono font-bold text-lg">{actualX} px</span>
                                  </div>
                                  <div className="flex justify-between items-center p-2 bg-white rounded">
                                    <span className="text-slate-600 font-medium">Y Position:</span>
                                    <span className="font-mono font-bold text-lg">{actualY} px</span>
                                  </div>
                                  <div className="flex justify-between items-center p-2 bg-white rounded">
                                    <span className="text-slate-600 font-medium">Radius:</span>
                                    <span className="font-mono font-bold text-lg">{actualR} px</span>
                                  </div>
                                </div>
                              </div>

                              <div className="space-y-3">
                                <button
                                  onClick={handleReset}
                                  className="w-full flex items-center justify-center gap-2 px-4 py-4 bg-slate-600 text-white rounded-xl hover:bg-slate-700 transition-all font-bold shadow-lg hover:shadow-xl transform hover:scale-105"
                                >
                                  🔄 Reset to Center
                                </button>
                                
                                <button
                                  onClick={handleDownloadPDF}
                                  disabled={generating}
                                  className="w-full flex items-center justify-center gap-2 px-4 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all font-bold shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  {generating ? '⏳ Generating...' : '📄 Download PDF'}
                                </button>

                                <button
                                  onClick={handleDownloadPNG}
                                  className="w-full flex items-center justify-center gap-2 px-4 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all font-bold shadow-lg hover:shadow-xl transform hover:scale-105"
                                >
                                  ⬇️ Download PNG
                                </button>

                                <button
                                  onClick={() => {
                                    setImage(null);
                                    setImageDataUrl(null);
                                    setImageSize({ width: 0, height: 0 });
                                    if (fileInputRef.current) fileInputRef.current.value = '';
                                  }}
                                  className="w-full px-4 py-3 bg-red-50 text-red-700 rounded-xl hover:bg-red-100 transition-all font-bold border-2 border-red-200"
                                >
                                  📤 Upload New Image
                                </button>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            }
            
            ReactDOM.render(<CircleAnnotator />, document.getElementById('root'));
        </script>
    </body>
    </html>
    """
    return html_code

# Main Streamlit app
st.title("🎯 Circle Annotator with PDF & PNG Download")

st.markdown("""
This app uses an embedded React component with **jsPDF** for direct PDF generation in the browser!
Both PDF and PNG downloads work directly without server communication.
""")

# Display the React component
components.html(create_react_app(), height=900, scrolling=True)

st.markdown("---")
st.markdown("""
### ✨ Features:
- 🎨 **True drag-and-drop** using React and HTML5 Canvas
- 🔴 **Drag red dot** to move the circle anywhere on the image
- 🔵 **Drag blue dot** to resize the circle
- 📄 **Download PDF** - Direct PDF generation using jsPDF library
- 📥 **Download PNG** - Quick PNG download
- 🔄 **Reset button** to return to center position

### 🚀 How to use:
1. **Upload** an image
2. **Drag** the red and blue handles to position and resize
3. Click **"Download PDF"** to save as PDF (works just like PNG!)
4. Or click **"Download PNG"** for PNG format

### 💡 Technical Details:
- PDF generation happens **directly in your browser** using jsPDF
- No server communication needed
- High-quality output at original image resolution
- Both formats download immediately when clicked
""")