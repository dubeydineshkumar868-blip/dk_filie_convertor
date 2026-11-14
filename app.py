import os
import sys
import zipfile
import uuid
import json
import secrets
# Set UTF-8 encoding environment variables to fix UnicodeEncodeError
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'
# Set EasyOCR environment variable first to avoid home directory access
os.environ['EASYOCR_MODULE_PATH'] = os.path.join(os.getcwd(), '.easyocr_models')
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import fitz  # PyMuPDF
from pdf2docx import Converter
from docx import Document
from docx.shared import Inches
import pdfplumber
import pandas as pd
import io
import tempfile
import easyocr
import numpy as np
import cv2

# Set page configuration with custom theme
st.set_page_config(
    page_title="DK File Converter", 
    page_icon="🔄", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for attractive frontend
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    }
    
    /* Main header style */
    .main-header {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 50%, #f59e0b 100%);
        padding: 3rem 2rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 20px 60px rgba(139, 92, 246, 0.4);
        animation: pulse 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 20px 60px rgba(139, 92, 246, 0.4); }
        50% { box-shadow: 0 20px 80px rgba(236, 72, 153, 0.5); }
    }
    
    .main-header h1 {
        color: white;
        margin: 0 0 0.5rem 0;
        font-size: 2.8rem;
        font-weight: 900;
        text-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.95;
        margin: 0;
        font-weight: 500;
    }
    
    /* Card style for sections */
    .card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 20px;
        border-left: 6px solid #8b5cf6;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(139, 92, 246, 0.3);
    }
    
    .card h3 {
        color: #ffffff;
        font-weight: 800;
        font-size: 1.7rem;
        margin-bottom: 1rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .card p {
        color: #ffffff;
        font-size: 1.15rem;
        line-height: 1.6;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(139, 92, 246, 0.2);
    }
    
    [data-testid="stSidebar"] h1 {
        color: #8b5cf6;
        font-weight: 800;
    }
    
    [data-testid="stSidebar"] label {
        color: #ffffff;
        font-weight: 700;
        font-size: 1rem;
    }

    /* Sidebar selectbox and dropdown styling */
    [data-testid="stSidebar"] [data-baseweb="select"] span {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] div {
        color: #ffffff !important;
    }

    /* Selectbox dropdown options */
    [data-testid="stSidebar"] [role="listbox"],
    [data-testid="stSidebar"] [role="listbox"] div,
    [data-testid="stSidebar"] [role="option"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        background-color: #1e293b !important;
    }
    
    [data-testid="stSidebar"] [role="option"]:hover {
        background-color: rgba(139, 92, 246, 0.5) !important;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        border-radius: 50px;
        border: none;
        padding: 0.8rem 3rem;
        font-weight: 800;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(236, 72, 153, 0.5);
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* Success message */
    .stSuccess {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        color: #a7f3d0;
        border-radius: 15px;
        border: 1px solid #10b981;
        box-shadow: 0 5px 20px rgba(16, 185, 129, 0.2);
    }
    
    /* Warning message */
    .stWarning {
        background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
        color: #fed7aa;
        border-radius: 15px;
        border: 1px solid #f59e0b;
        box-shadow: 0 5px 20px rgba(245, 158, 11, 0.2);
    }
    
    /* Info message */
    .stInfo {
        background: linear-gradient(135deg, #3730a3 0%, #4f46e5 100%);
        color: #c7d2fe;
        border-radius: 15px;
        border: 1px solid #6366f1;
        box-shadow: 0 5px 20px rgba(99, 102, 241, 0.2);
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: rgba(139, 92, 246, 0.15);
        border: 2px dashed #a78bfa;
        border-radius: 15px;
        padding: 2rem;
    }
    
    [data-testid="stFileUploader"] div {
        color: #ffffff;
    }
    
    /* All text elements */
    .stMarkdown, .stText {
        color: #ffffff;
    }
    
    /* All labels */
    label {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%);
    }
    
    /* Selectbox text */
    [data-baseweb="select"] span {
        color: #ffffff !important;
    }
    
    [data-baseweb="select"] div {
        color: #ffffff !important;
    }
    
    /* All other text */
    div, p, span {
        color: #e2e8f0;
    }
    
    /* Ensure headings are white */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        color: #64748b;
        margin-top: 3rem;
        border-top: 1px solid rgba(139, 92, 246, 0.2);
    }
    
    .footer p {
        margin: 0;
        font-size: 1rem;
    }
    
    /* Input and text styling */
    .stSelectbox label, .stSelectbox p {
        color: #ffffff;
    }
    
    /* Selectbox dropdown menu / popover / dialog */
    [data-baseweb="popover"],
    [data-baseweb="modal"],
    [role="dialog"],
    [role="listbox"] {
        background: #1e293b !important;
    }
    
    [data-baseweb="popover"] *:not(button):not(input):not(textarea),
    [data-baseweb="modal"] *:not(button):not(input):not(textarea),
    [role="dialog"] *:not(button):not(input):not(textarea),
    [role="listbox"] *:not(button):not(input):not(textarea) {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    [role="option"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        background-color: #1e293b !important;
    }
    
    /* Ensure dropdown list is fully dark */
    [data-testid="stSidebar"] [role="listbox"],
    [role="listbox"] {
        background-color: #0f172a !important;
    }
    
    /* Selectbox button and container */
    [data-baseweb="select"] {
        background-color: rgba(139, 92, 246, 0.15) !important;
        border: 1px solid #a78bfa !important;
        border-radius: 8px !important;
    }
    
    [data-baseweb="select"] button {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #a78bfa !important;
    }
    
    /* Slider styling */
    .stSlider label {
        color: #ffffff !important;
    }
    
    .stSlider > div > div {
        color: #ffffff !important;
    }
    
    /* All widgets background fix */
    [data-testid="stWidgetLabel"] {
        color: #ffffff !important;
    }
    
    [data-testid="stForm"] {
        background-color: transparent !important;
    }
    
    /* File uploader text and dialog */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stFileUploader"] {
        background-color: rgba(139, 92, 246, 0.15) !important;
        border: 2px dashed #a78bfa !important;
    }
    
    /* File uploader drop area */
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(139, 92, 246, 0.1) !important;
    }
    
    /* File uploader dialog (browse files) */
    /* This targets native file dialog but since we can't style native, style surrounding elements */
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        color: white !important;
    }
    
    /* Uploaded file items */
    [data-testid="stFileUploaderFile"] {
        background-color: rgba(139, 92, 246, 0.2) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    .stMetric {
        background: rgba(139, 92, 246, 0.15);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }
    
    .stMetric label {
        color: #a78bfa;
        font-weight: 700;
    }
    
    .stMetric > div > div:nth-child(2) {
        color: #10b981;
        font-size: 2rem;
        font-weight: 900;
    }

    /* Alert boxes (st.info / success / warning / error): dark background so the
       white text stays readable in both light and dark browser themes */
    [data-testid="stAlertContainer"] {
        background: rgba(99, 102, 241, 0.22) !important;
        border: 1px solid #6366f1 !important;
        border-radius: 12px !important;
    }
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {
        background: rgba(16, 185, 129, 0.2) !important; border-color: #10b981 !important;
    }
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {
        background: rgba(245, 158, 11, 0.2) !important; border-color: #f59e0b !important;
    }
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {
        background: rgba(239, 68, 68, 0.2) !important; border-color: #ef4444 !important;
    }
    [data-testid="stAlertContainer"] p,
    [data-testid="stAlertContainer"] span,
    [data-testid="stAlertContainer"] div {
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

# App Header - Attractive version
st.markdown("""
<div class="main-header">
    <h1>🔄 DK File Converter</h1>
    <p style="margin-top: 0.5rem; font-size: 1.1rem;">Your all-in-one file conversion & compression toolkit</p>
</div>
""", unsafe_allow_html=True)

P2P_TOOL = "🤝 Direct File Transfer (Free)"
CLOUD_TOOL = "📤 Large File Transfer (Cloud)"

def r2_is_configured():
    """Checks whether Cloudflare R2 credentials exist in Streamlit secrets."""
    try:
        cfg = st.secrets["r2"]
        return all(k in cfg for k in ("account_id", "access_key_id", "secret_access_key", "bucket"))
    except Exception:
        return False

# Sidebar for navigation with icons
st.sidebar.title("📋 Tools")
tool_options = [P2P_TOOL]
if r2_is_configured():  # cloud transfer only shows up once R2 keys are added in Secrets
    tool_options.append(CLOUD_TOOL)
tool_options += [
        "🖼️ Image to PDF",
        "🖼️ Image to Word",
        "🔁 WebP Converter",
        "📝 Image to Editable Text (OCR)",
        "📄 PDF to Image", 
        "📝 PDF to Word", 
        "📊 PDF to Excel",
        "📎 Merge PDFs",
        "🔽 Compress Image",
        "🔽 Compress PDF",
        "🧹 Remove Watermark from Images"
    ]

# Direct Transfer is the first option, so a shared ?receive=CODE link lands on it directly
conversion_type = st.sidebar.selectbox("Select what you want to do:", tool_options)

# Helper functions for conversion
def image_to_pdf(uploaded_files):
    """
    Converts a list of images into a single PDF file.
    """
    images = []
    for uploaded_file in uploaded_files:
        img = Image.open(uploaded_file)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        images.append(img)
    
    if images:
        pdf_buffer = io.BytesIO()
        images[0].save(pdf_buffer, format="PDF", save_all=True, append_images=images[1:])
        pdf_buffer.seek(0)
        return pdf_buffer
    return None

def image_to_word(uploaded_files, lang_list=['en', 'hi']):
    """
    Converts a list of images into a single Word document by extracting text via OCR.
    """
    import contextlib
    
    # Set custom model directory
    model_dir = os.path.join(os.getcwd(), '.easyocr_models')
    user_network_dir = os.path.join(model_dir, 'user_network')
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(user_network_dir, exist_ok=True)
    
    # Initialize OCR reader
    with open(os.devnull, 'w') as f_null, contextlib.redirect_stdout(f_null), contextlib.redirect_stderr(f_null):
        reader = easyocr.Reader(lang_list, gpu=False, model_storage_directory=model_dir, user_network_directory=user_network_dir, verbose=False)
    
    doc = Document()
    for idx, uploaded_file in enumerate(uploaded_files):
        # Add image to doc first
        img = Image.open(uploaded_file)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format=img.format if img.format else 'PNG')
        img_buffer.seek(0)
        doc.add_picture(img_buffer, width=Inches(6))
        
        # Extract text from image and add to doc
        img_buffer_for_ocr = io.BytesIO()
        img.save(img_buffer_for_ocr, format=img.format if img.format else 'PNG')
        img_buffer_for_ocr.seek(0)
        results = reader.readtext(img_buffer_for_ocr.getvalue(), detail=0)
        extracted_text = '\n'.join(results)
        
        if extracted_text:
            doc.add_paragraph(f"\n--- Page {idx+1} Extracted Text ---")
            doc.add_paragraph(extracted_text)
        
        if idx != len(uploaded_files) -1:
            doc.add_page_break()
    
    word_buffer = io.BytesIO()
    doc.save(word_buffer)
    word_buffer.seek(0)
    return word_buffer.getvalue()

def pdf_to_images(uploaded_pdf):
    """
    Converts each page of a PDF into a separate image.
    Returns a list of image buffers.
    """
    pdf_bytes = uploaded_pdf.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    image_buffers = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        image_buffers.append(img_data)
    
    doc.close()
    return image_buffers

def create_zip_from_images(image_buffers, base_name="pdf_pages"):
    """
    Creates a ZIP file from a list of image bytes.
    Returns the ZIP buffer.
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for idx, img_data in enumerate(image_buffers):
            zf.writestr(f"{base_name}_page_{idx+1}.png", img_data)
    
    zip_buffer.seek(0)
    return zip_buffer

def create_zip_from_files(file_list):
    """
    Creates a ZIP file from a list of (file_name, file_bytes) tuples.
    Generic helper for bundling any compressed files.
    Returns the ZIP buffer.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_name, file_bytes in file_list:
            zf.writestr(file_name, file_bytes)
    zip_buffer.seek(0)
    return zip_buffer

def pdf_to_word(uploaded_pdf):
    """
    Converts a PDF file to a Word document (.docx).
    """
    # Create a temporary file to store the PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(uploaded_pdf.read())
        temp_pdf_path = temp_pdf.name
    
    # Create a temporary path for the Word file
    temp_word_path = temp_pdf_path.replace(".pdf", ".docx")
    
    try:
        # Perform conversion
        cv = Converter(temp_pdf_path)
        cv.convert(temp_word_path)
        cv.close()
        
        # Read the converted Word file
        with open(temp_word_path, "rb") as f:
            word_data = f.read()
            
        return word_data
    finally:
        # Clean up temporary files
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        if os.path.exists(temp_word_path):
            os.remove(temp_word_path)

def pdf_to_excel(uploaded_pdf):
    """
    Extracts tables from a PDF file and saves them into an Excel file.
    Each table is saved in a different sheet.
    """
    pdf_bytes = uploaded_pdf.read()
    excel_buffer = io.BytesIO()
    
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                # Convert table to DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)
        
        if all_tables:
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                for i, df in enumerate(all_tables):
                    df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
            excel_buffer.seek(0)
            return excel_buffer
    return None

def merge_pdfs(uploaded_pdfs):
    """
    Merges multiple PDF files into a single PDF.
    """
    merger = fitz.open()
    
    for uploaded_pdf in uploaded_pdfs:
        pdf_bytes = uploaded_pdf.read()
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            merger.insert_pdf(doc)
    
    merged_buffer = io.BytesIO()
    merger.save(merged_buffer)
    merger.close()
    merged_buffer.seek(0)
    return merged_buffer

def compress_image(uploaded_image, quality=85):
    """
    Compresses an image file with adjustable quality.
    """
    img = Image.open(uploaded_image)
    
    # Convert to RGB if it's RGBA or has palette
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    compressed_buffer = io.BytesIO()
    img.save(compressed_buffer, format='JPEG', quality=quality, optimize=True)
    compressed_buffer.seek(0)
    
    return compressed_buffer

def convert_image_format(image_bytes, target="WEBP", quality=85, lossless=False):
    """
    Converts image bytes to another format (WEBP, JPEG or PNG).
    - Transparency is kept for WEBP/PNG; for JPEG it is placed on a white background.
    - Animated images (GIF / animated WebP) stay animated when converting to WEBP.
    Returns the converted image bytes.
    """
    img = Image.open(io.BytesIO(image_bytes))
    out = io.BytesIO()

    if target == "WEBP":
        if getattr(img, "is_animated", False):
            img.save(out, format="WEBP", save_all=True, quality=quality, lossless=lossless)
        else:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA" if "transparency" in img.info or img.mode in ("LA", "P") else "RGB")
            img.save(out, format="WEBP", quality=quality, lossless=lossless, method=6)

    elif target == "JPEG":
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.save(out, format="JPEG", quality=quality, optimize=True)

    else:  # PNG
        if img.mode not in ("RGB", "RGBA", "L", "LA", "P"):
            img = img.convert("RGBA")
        img.save(out, format="PNG", optimize=True)

    return out.getvalue()

def compress_pdf(uploaded_pdf, quality='medium'):
    """
    Compresses a PDF file with maximum compression by reducing image quality and size.
    """
    pdf_bytes = uploaded_pdf.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # Set quality and scale level
    settings = {
        'high': {'quality': 80, 'scale': 1.0},
        'medium': {'quality': 50, 'scale': 0.75},
        'low': {'quality': 25, 'scale': 0.5}
    }
    config = settings[quality]
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get all images on the page
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            
            try:
                # Extract the image
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                original_size = len(image_bytes)
                
                # Open with Pillow
                img_pil = Image.open(io.BytesIO(image_bytes))
                
                # Convert to RGB if needed
                if img_pil.mode in ('RGBA', 'P'):
                    img_pil = img_pil.convert('RGB')
                
                # Resize image if needed
                if config['scale'] < 1.0:
                    new_width = int(img_pil.width * config['scale'])
                    new_height = int(img_pil.height * config['scale'])
                    # Use compatible resampling method
                    try:
                        img_pil = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    except AttributeError:
                        img_pil = img_pil.resize((new_width, new_height), Image.LANCZOS)
                
                # Compress the image
                img_buffer = io.BytesIO()
                img_pil.save(img_buffer, format='JPEG', quality=config['quality'], optimize=True)
                compressed_img_bytes = img_buffer.getvalue()
                
                # Only replace if we actually reduced the size
                if len(compressed_img_bytes) < original_size:
                    page.replace_image(xref, stream=compressed_img_bytes)
            except:
                continue  # Skip if there's an error with this image
    
    # Save the compressed PDF
    compressed_buffer = io.BytesIO()
    doc.save(compressed_buffer, deflate=True, garbage=4, clean=True)
    compressed_buffer.seek(0)
    doc.close()
    
    return compressed_buffer

def image_to_editable_text(uploaded_image, lang_list=['en', 'hi']):
    """
    Extracts editable text from an image using OCR (Optical Character Recognition).
    Supports multiple languages (default: English + Hindi).
    """
    import contextlib
    
    # Set custom model directory inside project to avoid permission issues
    model_dir = os.path.join(os.getcwd(), '.easyocr_models')
    user_network_dir = os.path.join(model_dir, 'user_network')
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(user_network_dir, exist_ok=True)
    
    # Redirect stdout/stderr to null to completely suppress EasyOCR output (prevents Unicode errors)
    with open(os.devnull, 'w') as f_null, contextlib.redirect_stdout(f_null), contextlib.redirect_stderr(f_null):
        # Initialize EasyOCR reader with custom model and user network directories, no verbose output
        reader = easyocr.Reader(lang_list, gpu=False, model_storage_directory=model_dir, user_network_directory=user_network_dir, verbose=False)
    
    # Read the image
    img = Image.open(uploaded_image)
    
    # Convert image to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format=img.format if img.format else 'PNG')
    img_buffer.seek(0)
    
    # Perform OCR
    results = reader.readtext(img_buffer.getvalue(), detail=0)
    
    # Join the results into a single string
    extracted_text = '\n'.join(results)
    
    return extracted_text

def detect_watermark_mask(img_bgr, tolerance=30, dilate_size=3):
    """
    Automatically detects light-colored/semi-transparent watermarks.
    Returns a single-channel mask (uint8) where watermark pixels > 0.
    Uses L channel from LAB + threshold + morphological dilation.
    """
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l_channel = lab[:, :, 0]
    _, bright_mask = cv2.threshold(l_channel, 255 - tolerance, 255, cv2.THRESH_BINARY)
    white_mask = cv2.inRange(img_bgr, (255 - tolerance, 255 - tolerance, 255 - tolerance), (255, 255, 255))
    combined = cv2.bitwise_or(bright_mask, white_mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (dilate_size, dilate_size))
    dilated = cv2.dilate(combined, kernel, iterations=2)
    return dilated

def remove_watermark(image_buffer, tolerance=30, inpaint_radius=5, method='auto'):
    """
    Remove watermark from an image (given as file-like / BytesIO / bytes).
    Returns cleaned image bytes (PNG).
    method:
      - 'auto'   => auto-detect watermark mask & inpaint
      - 'manual' => caller provides mask separately; here equivalent to auto
    """
    try:
        if hasattr(image_buffer, 'read'):
            raw = image_buffer.read()
        elif isinstance(image_buffer, (bytes, bytearray)):
            raw = bytes(image_buffer)
        else:
            raw = image_buffer
        arr = np.frombuffer(raw, np.uint8)
        img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return None
    except Exception:
        return None

    mask = detect_watermark_mask(img_bgr, tolerance=tolerance, dilate_size=3)

    if cv2.countNonZero(mask) == 0:
        clean_bgr = img_bgr
    else:
        try:
            clean_bgr = cv2.inpaint(img_bgr, mask, inpaint_radius, cv2.INPAINT_TELEA)
        except Exception:
            clean_bgr = img_bgr

    ok, encoded = cv2.imencode('.png', clean_bgr)
    if not ok:
        return None
    return encoded.tobytes()

# Helper function to get file size in human-readable format
def get_file_size(file_obj):
    file_obj.seek(0, 2)  # Seek to end
    size = file_obj.tell()
    file_obj.seek(0)  # Reset to start
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

# ---------------------------------------------------------------------------
# Large File Transfer (WeTransfer style) - files go browser -> Cloudflare R2
# directly, so Streamlit's upload limit and RAM are never touched.
# ---------------------------------------------------------------------------
TRANSFER_MAX_FILES = 10          # files per transfer
TRANSFER_UPLOAD_WINDOW = 6 * 3600  # upload URL valid for 6 hours

def get_r2_client():
    """Creates an S3-compatible client pointing at Cloudflare R2."""
    import boto3
    from botocore.config import Config
    cfg = st.secrets["r2"]
    client = boto3.client(
        "s3",
        endpoint_url=f"https://{cfg['account_id']}.r2.cloudflarestorage.com",
        aws_access_key_id=cfg["access_key_id"],
        aws_secret_access_key=cfg["secret_access_key"],
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )
    return client, cfg["bucket"]

def make_transfer_slots(transfer_id, expiry_days, n=TRANSFER_MAX_FILES):
    """
    Generates n pairs of presigned URLs:
      put -> browser uploads the file straight to R2
      get -> shareable download link (valid for expiry_days, max 7)
    """
    client, bucket = get_r2_client()
    slots = []
    for i in range(n):
        key = f"transfers/{transfer_id}/file_{i + 1}"
        put_url = client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=TRANSFER_UPLOAD_WINDOW,
        )
        get_url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expiry_days * 24 * 3600,
        )
        slots.append({"put": put_url, "get": get_url})
    return slots

TRANSFER_HTML = """
<style>
  body { margin:0; font-family: system-ui, -apple-system, Segoe UI, sans-serif; color:#fff; background:transparent; }
  .drop { border:2px dashed #a78bfa; border-radius:16px; padding:30px 16px; text-align:center;
          background:rgba(139,92,246,.12); cursor:pointer; transition:background .2s; }
  .drop.over { background:rgba(236,72,153,.2); }
  .drop b { font-size:17px; }
  .btn { background:linear-gradient(135deg,#8b5cf6,#ec4899); color:#fff; border:none; border-radius:50px;
         padding:12px 28px; font-weight:800; font-size:15px; cursor:pointer; margin-top:14px; letter-spacing:.5px; }
  .btn:disabled { opacity:.45; cursor:not-allowed; }
  .item { background:#1e293b; border-radius:12px; padding:12px 14px; margin-top:10px; border-left:4px solid #8b5cf6; }
  .bar { height:8px; background:#334155; border-radius:8px; overflow:hidden; margin-top:8px; }
  .fill { height:100%; width:0; background:linear-gradient(90deg,#8b5cf6,#ec4899); transition:width .2s; }
  .small { font-size:13px; color:#cbd5e1; margin-top:4px; }
  .ok { color:#6ee7b7; } .err { color:#fca5a5; }
  a { color:#f9a8d4; word-break:break-all; }
  textarea { width:100%; box-sizing:border-box; background:#0f172a; color:#fff; border:1px solid #a78bfa;
             border-radius:8px; padding:8px; margin-top:10px; font-size:12px; }
  h3 { margin:18px 0 4px; }
</style>

<div id="drop" class="drop">
  📂 <b>Click karke files chuno</b> ya yahan drag &amp; drop karo<br>
  <span class="small">Ek baar mein __MAXFILES__ files tak &bull; har file 5 GB tak</span>
  <input id="inp" type="file" multiple style="display:none">
</div>
<div id="list"></div>
<button id="go" class="btn" disabled>🚀 Upload &amp; Get Links</button>
<div id="done"></div>

<script>
const SLOTS = __SLOTS__;
const MAX_BYTES = 5 * 1024 * 1024 * 1024;
let files = [];
let busy = false;
const drop = document.getElementById('drop');
const inp  = document.getElementById('inp');
const list = document.getElementById('list');
const go   = document.getElementById('go');
const done = document.getElementById('done');

function fmt(b) { const u=['B','KB','MB','GB']; let i=0; while (b>=1024 && i<3) { b/=1024; i++; } return b.toFixed(i ? 2 : 0) + ' ' + u[i]; }
function esc(s) { return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

drop.onclick = () => { if (!busy) inp.click(); };
drop.ondragover = e => { e.preventDefault(); if (!busy) drop.classList.add('over'); };
drop.ondragleave = () => drop.classList.remove('over');
drop.ondrop = e => { e.preventDefault(); drop.classList.remove('over'); if (!busy) addFiles(e.dataTransfer.files); };
inp.onchange = () => { addFiles(inp.files); inp.value = ''; };

function addFiles(fl) {
  for (const f of fl) {
    if (files.length >= SLOTS.length) { alert('Ek transfer mein max ' + SLOTS.length + ' files. Baaki ke liye "New Transfer" karo.'); break; }
    if (f.size > MAX_BYTES) { alert(f.name + ' 5 GB se badi hai. Ise chhote parts mein zip karke bhejo.'); continue; }
    files.push(f);
  }
  render();
}

function render() {
  list.innerHTML = files.map((f, i) =>
    `<div class="item"><b>${esc(f.name)}</b> <span class="small">(${fmt(f.size)})</span>
       <div class="bar"><div class="fill" id="fill${i}"></div></div>
       <div class="small" id="st${i}">Ready</div></div>`).join('');
  const total = files.reduce((s, f) => s + f.size, 0);
  go.disabled = !files.length || busy;
  go.textContent = files.length ? `🚀 Upload ${files.length} file(s) • ${fmt(total)}` : '🚀 Upload & Get Links';
}

function contentDisposition(name) {
  const ascii = name.replace(/[^\\x20-\\x7E]/g, '_').replace(/["\\\\]/g, '');
  return `attachment; filename="${ascii}"; filename*=UTF-8''${encodeURIComponent(name)}`;
}

function uploadOne(f, i) {
  return new Promise(resolve => {
    const fill = document.getElementById('fill' + i);
    const st = document.getElementById('st' + i);
    const x = new XMLHttpRequest();
    x.open('PUT', SLOTS[i].put);
    x.setRequestHeader('Content-Type', f.type || 'application/octet-stream');
    x.setRequestHeader('Content-Disposition', contentDisposition(f.name));
    const t0 = Date.now();
    x.upload.onprogress = e => {
      if (!e.lengthComputable) return;
      const p = e.loaded / e.total * 100;
      const secs = Math.max((Date.now() - t0) / 1000, 0.5);
      const speed = e.loaded / secs;
      const left = speed > 0 ? Math.round((e.total - e.loaded) / speed) : 0;
      fill.style.width = p + '%';
      st.textContent = `${p.toFixed(1)}% • ${fmt(e.loaded)} / ${fmt(e.total)} • ${fmt(speed)}/s • ~${left}s left`;
    };
    x.onload = () => {
      if (x.status >= 200 && x.status < 300) {
        fill.style.width = '100%';
        st.innerHTML = '<span class="ok">✅ Uploaded</span>';
        resolve({ ok: true, name: f.name, size: f.size, url: SLOTS[i].get });
      } else {
        st.innerHTML = `<span class="err">❌ Upload failed (HTTP ${x.status}). R2 keys/bucket check karo.</span>`;
        resolve({ ok: false });
      }
    };
    x.onerror = () => {
      st.innerHTML = '<span class="err">❌ Network ya CORS error. R2 bucket ki CORS setting check karo.</span>';
      resolve({ ok: false });
    };
    x.send(f);
  });
}

go.onclick = async () => {
  busy = true; go.disabled = true; drop.style.opacity = .5;
  window.onbeforeunload = () => 'Upload chal raha hai!';
  const results = [];
  for (let i = 0; i < files.length; i++) {
    const r = await uploadOne(files[i], i);
    if (r.ok) results.push(r);
  }
  window.onbeforeunload = null;
  go.textContent = '✔ Done';
  showLinks(results);
};

function showLinks(results) {
  if (!results.length) return;
  let html = '<h3>✅ Aapke share links taiyaar hain</h3>';
  results.forEach(r => {
    html += `<div class="item"><b>${esc(r.name)}</b> <span class="small">(${fmt(r.size)})</span><br>
             <a href="${esc(r.url)}" target="_blank">⬇️ Download link kholo</a></div>`;
  });
  const all = results.map(r => r.name + '\\n' + r.url).join('\\n\\n');
  html += `<textarea id="all" rows="6" readonly>${esc(all)}</textarea>
           <button class="btn" id="cp">📋 Copy All Links</button>`;
  done.innerHTML = html;
  document.getElementById('cp').onclick = () => {
    const t = document.getElementById('all');
    t.select();
    try { navigator.clipboard.writeText(t.value); } catch (e) {}
    try { document.execCommand('copy'); } catch (e) {}
    document.getElementById('cp').textContent = '✅ Copied!';
  };
}
</script>
"""

def build_transfer_html(slots):
    return (TRANSFER_HTML
            .replace("__SLOTS__", json.dumps(slots))
            .replace("__MAXFILES__", str(len(slots))))

# ---------------------------------------------------------------------------
# Direct File Transfer (P2P, AnyDesk style) - the file goes straight from the
# sender's browser to the receiver's browser over WebRTC. Nothing is stored on
# any server, so there is no size limit and no cost. Both people must keep the
# page open during the transfer. The free PeerJS cloud server is used only to
# introduce the two browsers to each other.
# ---------------------------------------------------------------------------
PEERJS_SRC = "https://unpkg.com/peerjs@1.5.5/dist/peerjs.min.js"
P2P_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O/1/I confusion
P2P_STUN_SERVERS = [
    {"urls": "stun:stun.l.google.com:19302"},
    {"urls": "stun:stun1.l.google.com:19302"},
    {"urls": "stun:stun.cloudflare.com:3478"},
]

def new_p2p_code():
    return "".join(secrets.choice(P2P_CODE_ALPHABET) for _ in range(6))

def clean_p2p_code(raw):
    return "".join(ch for ch in str(raw).upper() if ch in P2P_CODE_ALPHABET)[:6]

def p2p_ice_servers():
    """STUN servers, plus an optional TURN server from Secrets for strict networks."""
    servers = list(P2P_STUN_SERVERS)
    try:
        t = st.secrets["turn"]
        servers.append({"urls": t["urls"], "username": t["username"], "credential": t["credential"]})
    except Exception:
        pass
    return servers

def build_p2p_html(mode, code, peer_opts=None, peerjs_src=PEERJS_SRC):
    opts = peer_opts if peer_opts is not None else {"debug": 1, "config": {"iceServers": p2p_ice_servers()}}
    return (P2P_HTML
            .replace("__PEERJS_SRC__", peerjs_src)
            .replace("__MODE__", json.dumps(mode))
            .replace("__CODE__", json.dumps(code))
            .replace("__PEER_OPTS__", json.dumps(opts)))

P2P_HTML = r"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&display=swap');
  :root { --ink:#0f172a; --panel:#161f35; --panel2:#1d2844; --line:#2b3758; --violet:#8b5cf6; --pink:#ec4899;
          --mint:#34d399; --amber:#fbbf24; --red:#f87171; --text:#f1f5f9; --muted:#9aa8c1; }
  * { box-sizing:border-box; }
  body { margin:0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; font-size:14px;
         color:var(--text); background:transparent; line-height:1.45; }
  .panel { background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:16px 18px; margin-bottom:12px; }

  /* device-to-device connection strip */
  .linkrow { display:flex; align-items:center; gap:12px; }
  .dev { display:flex; align-items:center; gap:10px; min-width:0; }
  .dev.right { flex-direction:row-reverse; text-align:right; }
  .dev .ic { width:44px; height:44px; border-radius:13px; display:grid; place-items:center; font-size:21px; flex:none;
             background:var(--panel2); border:1px solid var(--line); }
  .dev.me .ic { background:linear-gradient(135deg,var(--violet),var(--pink)); border-color:transparent; }
  .dev b { display:block; font-family:Sora, system-ui, sans-serif; font-size:14px; font-weight:700; }
  .dev span { display:block; font-size:12px; color:var(--muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .wire { flex:1; min-width:36px; height:4px; border-radius:4px; background:var(--line); position:relative; overflow:hidden; }
  .wire::after { content:""; position:absolute; top:0; bottom:0; left:-40px; right:0; opacity:0;
                 background:repeating-linear-gradient(90deg, rgba(255,255,255,.45) 0 8px, transparent 8px 40px); }
  [data-state=ready] .wire { background:repeating-linear-gradient(90deg, var(--amber) 0 6px, transparent 6px 12px); }
  [data-state=connected] .wire { background:var(--mint); }
  [data-state=busy] .wire { background:linear-gradient(90deg,var(--violet),var(--pink)); }
  [data-state=busy] .wire::after { opacity:1; animation:flow .9s linear infinite; }
  [data-state=error] .wire { background:var(--red); }
  @keyframes flow { from { transform:translateX(0); } to { transform:translateX(40px); } }
  .state { margin-top:12px; display:flex; gap:9px; align-items:flex-start; font-size:13px; }
  .dot { width:8px; height:8px; border-radius:50%; margin-top:5px; flex:none; background:var(--muted); animation:pulse 1.6s ease-in-out infinite; }
  [data-state=ready] .dot { background:var(--amber); }
  [data-state=connected] .dot, [data-state=busy] .dot { background:var(--mint); animation:none; }
  [data-state=error] .dot { background:var(--red); animation:none; }
  @keyframes pulse { 50% { opacity:.25; } }

  /* pairing code */
  .codewrap { display:flex; align-items:flex-end; justify-content:space-between; gap:14px; flex-wrap:wrap; }
  .hint { font-size:12px; color:var(--muted); margin-bottom:8px; }
  .tiles { display:flex; gap:7px; }
  .tile { width:44px; height:56px; border-radius:12px; display:grid; place-items:center; background:var(--ink);
          border:1px solid var(--line); box-shadow: inset 0 -3px 0 var(--violet);
          font-family:Sora, system-ui, sans-serif; font-weight:800; font-size:26px; }
  .actions { display:flex; gap:8px; flex-wrap:wrap; }
  .chip { border:1px solid var(--line); background:var(--panel2); color:var(--text); border-radius:999px; padding:8px 14px;
          font:600 13px system-ui, sans-serif; cursor:pointer; text-decoration:none; display:inline-flex; align-items:center; gap:6px; }
  .chip:hover { border-color:var(--violet); }
  .chip.wa { background:#15803d; border-color:#15803d; color:#fff; }
  .chip.wa:hover { background:#16a34a; }

  /* drop zone */
  .drop { border:2px dashed #46557e; border-radius:18px; padding:24px 16px 20px; text-align:center;
          background:rgba(139,92,246,.06); transition:border-color .15s, background .15s; }
  .drop.over { border-color:var(--pink); background:rgba(236,72,153,.1); }
  .drop.off { opacity:.45; }
  .drop .icon { font-size:34px; line-height:1; }
  .drop .big { font-family:Sora, system-ui, sans-serif; font-size:17px; font-weight:700; margin:8px 0 2px; }
  .drop .sub { font-size:12px; color:var(--muted); }
  .pick { display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin:14px 0 12px; }

  .btn { background:linear-gradient(135deg,var(--violet),var(--pink)); color:#fff; border:none; border-radius:999px;
         padding:10px 20px; font:700 14px system-ui, sans-serif; cursor:pointer; }
  .btn.ghost { background:var(--panel2); border:1px solid var(--line); }
  .btn.ghost:hover { border-color:var(--violet); }
  .btn.big { width:100%; padding:14px 20px; font-size:16px; margin-top:12px; box-shadow:0 10px 30px rgba(139,92,246,.35); }
  .btn:disabled { opacity:.45; cursor:not-allowed; box-shadow:none; }
  :focus-visible { outline:2px solid var(--pink); outline-offset:2px; }

  /* file list */
  .rows { background:var(--panel); border:1px solid var(--line); border-radius:18px; overflow:hidden; margin-top:12px; }
  .rows:empty { display:none; }
  .row { display:flex; gap:12px; align-items:center; padding:12px 14px; border-top:1px solid var(--line); }
  .row:first-child { border-top:none; }
  .ft { width:40px; height:40px; border-radius:11px; display:grid; place-items:center; font-size:19px; flex:none; }
  .rbody { flex:1; min-width:0; }
  .name { font-weight:650; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .meta { font-size:12px; color:var(--muted); }
  .bar { height:6px; background:var(--ink); border-radius:6px; overflow:hidden; margin:7px 0 4px; }
  .fill { height:100%; width:0; background:linear-gradient(90deg,var(--violet),var(--pink)); border-radius:6px; transition:width .25s; }
  .fill.done { background:var(--mint); }
  .small { font-size:12px; color:var(--muted); }
  .x { background:none; border:none; color:var(--muted); font-size:15px; cursor:pointer; padding:6px 8px; border-radius:8px; flex:none; }
  .x:hover { color:var(--red); background:var(--panel2); }

  .total { display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; font-size:13px; color:var(--muted); margin-top:10px; padding:0 4px; }
  .total:empty { display:none; }
  .total b { color:var(--text); }
  .msg { margin-top:10px; font-size:13px; padding:0 4px; }
  .ok { color:var(--mint); } .err { color:var(--red); } .wait { color:var(--amber); }
  a.save { display:inline-block; margin-top:2px; color:#f9a8d4; font-weight:700; text-decoration:none; }
  a.save:hover { text-decoration:underline; }

  @media (max-width:520px) {
    .tile { width:38px; height:48px; font-size:22px; }
    .dev span { display:none; }
    .codewrap { align-items:flex-start; }
  }
  @media (prefers-reduced-motion: reduce) { *, *::after { animation:none !important; transition:none !important; } }
</style>
<div id="app"></div>
<script src="__PEERJS_SRC__"></script>
<script>
  // backup CDN if the first one is blocked or down
  if (typeof Peer === 'undefined')
    document.write('<script src="https://cdn.jsdelivr.net/npm/peerjs@1.5.5/dist/peerjs.min.js"><\/script>');
</script>
<script>
const MODE = __MODE__, CODE = __CODE__, OPTS = __PEER_OPTS__;
const PREFIX = 'dkft-';
const READ_BLOCK = 1024 * 1024;          // read file 1 MB at a time
const HIGH_WATER = 8 * 1024 * 1024;      // pause sending above 8 MB in buffer
const LOW_WATER = 1024 * 1024;           // resume below 1 MB
const FLUSH_BYTES = 16 * 1024 * 1024;    // receiver: pack chunks into a Blob every 16 MB
const LIST_SLICE = 300;                  // groups per "list" message
const ZIP64_LIMIT = (typeof window.__ZIP64_LIMIT__ === 'number') ? window.__ZIP64_LIMIT__ : 0xFFFFFFFF;
const app = document.getElementById('app');
const $ = id => document.getElementById(id);

function fmt(b) { const u=['B','KB','MB','GB','TB']; let i=0; while (b>=1024 && i<4) { b/=1024; i++; } return b.toFixed(i ? 2 : 0) + ' ' + u[i]; }
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function eta(s) { s = Math.max(0, Math.round(s)); return s >= 3600 ? Math.floor(s/3600)+'h '+Math.floor(s%3600/60)+'m' : s >= 60 ? Math.floor(s/60)+'m '+(s%60)+'s' : s+'s'; }
function pct(done, total) { return total ? Math.min(100, done / total * 100) : 100; }
function setStatus(id, html, cls) { const el = $(id); if (el) el.innerHTML = cls ? `<span class="${cls}">${html}</span>` : html; }
function progressText(done, total, t0) {
  const secs = Math.max((Date.now() - t0) / 1000, 0.5), speed = done / secs;
  const left = speed > 0 ? (total - done) / speed : 0;
  return `${pct(done, total).toFixed(1)}% • ${fmt(done)} / ${fmt(total)} • ${fmt(speed)}/s • ~${eta(left)} baaki`;
}
let wakeLock = null;
async function keepAwake(on) {
  try {
    if (on && !wakeLock && navigator.wakeLock) wakeLock = await navigator.wakeLock.request('screen');
    if (!on && wakeLock) { await wakeLock.release(); wakeLock = null; }
  } catch (e) {}
}
function copyText(text, btn, label) {
  try { navigator.clipboard.writeText(text); } catch (e) {}
  const t = document.createElement('textarea'); t.value = text; document.body.appendChild(t); t.select();
  try { document.execCommand('copy'); } catch (e) {}
  t.remove(); btn.textContent = '✅ Copied!'; setTimeout(() => btn.textContent = label, 2000);
}
function shareUrl() {
  for (const w of [window.top, window.parent]) {
    try {
      const u = new URL(w.location.href);
      if (!u.protocol.startsWith('http')) continue;
      u.search = ''; u.hash = ''; u.pathname = u.pathname.replace(/\/~\/\+\/?$/, '/');
      u.searchParams.set('receive', CODE);
      return u.toString();
    } catch (e) {}
  }
  return '';
}
function peerErrorText(err) {
  const t = err && err.type;
  if (t === 'unavailable-id') return 'Ye code abhi busy hai. Neeche "New Code" dabao.';
  if (t === 'peer-unavailable') return 'Is code par koi sender nahi mila. Code check karo aur sender ka page khula ho.';
  if (t === 'network' || t === 'server-error' || t === 'socket-error' || t === 'socket-closed')
    return 'Connection server tak nahi pahunch paaye. Internet check karke page refresh karo.';
  if (t === 'browser-incompatible') return 'Ye browser support nahi karta. Chrome ya Edge use karo.';
  return 'Error: ' + esc((err && (err.message || err.type)) || err);
}
function watchIce(conn, onFail) {
  const pc = conn.peerConnection;
  if (!pc) return;
  pc.addEventListener('iceconnectionstatechange', () => { if (pc.iceConnectionState === 'failed') onFail(); });
}
const ICE_FAIL_TEXT = 'Dono devices aapas mein connect nahi ho paaye (network strict hai). ' +
  'Dono ek hi WiFi par try karo, ya mobile hotspot badal kar dekho.';

/* ---------------- UI helpers ---------------- */
function tilesHtml(code) { return [...code].map(c => `<div class="tile">${esc(c)}</div>`).join(''); }
const FILE_KINDS = [
  [/\.(jpe?g|png|gif|webp|bmp|tiff?|heic|svg)$/i, '🖼️', '#1e3a5f'],
  [/\.(mp4|mkv|mov|avi|webm|m4v|3gp)$/i, '🎬', '#4a1d3f'],
  [/\.(mp3|wav|m4a|aac|flac|ogg|opus)$/i, '🎵', '#1f4a3a'],
  [/\.pdf$/i, '📕', '#4c1d24'],
  [/\.(zip|rar|7z|tar|gz|bz2|xz)$/i, '🗜️', '#4a3a16'],
  [/\.(docx?|txt|rtf|odt|md)$/i, '📝', '#1e3350'],
  [/\.(xlsx?|csv|ods)$/i, '📊', '#1a4030'],
  [/\.(pptx?|odp|key)$/i, '📽️', '#4a2a16'],
  [/\.(apk|exe|msi|dmg|iso)$/i, '📦', '#2f2a52'],
];
function fileIcon(name, kind) {
  if (kind === 'folder') return `<div class="ft" style="background:#3b2f6b">📁</div>`;
  for (const [re, ic, bg] of FILE_KINDS) if (re.test(name)) return `<div class="ft" style="background:${bg}">${ic}</div>`;
  return `<div class="ft" style="background:#2b3758">📄</div>`;
}
// state: wait | ready | connected | busy | error
function setConn(state, sub) {
  const el = $('conn'); if (!el) return;
  el.dataset.state = state;
  if (sub !== undefined) $('themsub').textContent = sub;
  $('themic').textContent = (state === 'connected' || state === 'busy') ? '📱' : state === 'error' ? '⚠️' : '⌛';
}
function totalLine(count, size, done, t0) {
  if (!count) return '';
  const left = `<span><b>${count}</b> file(s) • <b>${fmt(size)}</b></span>`;
  if (done == null) return left;
  return left + `<span>Kul: ${progressText(done, size, t0)}</span>`;
}

/* ---------------- CRC32 + ZIP (store, no compression, ZIP64 when needed) ---------------- */
const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1); t[n] = c >>> 0; }
  return t;
})();
function crc32(crc, buf) {
  const u = new Uint8Array(buf); let c = (crc ^ 0xFFFFFFFF) >>> 0;
  for (let i = 0; i < u.length; i++) c = CRC_TABLE[(c ^ u[i]) & 0xFF] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}
class ZipBuilder {
  constructor() {
    this.parts = []; this.central = []; this.offset = 0; this.count = 0;
    const d = new Date();
    this.time = (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1);
    this.date = ((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
  }
  add(path, size, crc, dataParts) {
    const name = new TextEncoder().encode(path);
    const big = size >= ZIP64_LIMIT, extraLen = big ? 20 : 0;
    const h = new DataView(new ArrayBuffer(30 + name.length + extraLen));
    h.setUint32(0, 0x04034b50, true); h.setUint16(4, big ? 45 : 20, true); h.setUint16(6, 0x0800, true);
    h.setUint16(8, 0, true); h.setUint16(10, this.time, true); h.setUint16(12, this.date, true);
    h.setUint32(14, crc, true);
    h.setUint32(18, big ? 0xFFFFFFFF : size, true); h.setUint32(22, big ? 0xFFFFFFFF : size, true);
    h.setUint16(26, name.length, true); h.setUint16(28, extraLen, true);
    new Uint8Array(h.buffer).set(name, 30);
    if (big) {
      const o = 30 + name.length;
      h.setUint16(o, 1, true); h.setUint16(o + 2, 16, true);
      h.setBigUint64(o + 4, BigInt(size), true); h.setBigUint64(o + 12, BigInt(size), true);
    }
    this.central.push({ name, size, crc, big, localOffset: this.offset });
    this.parts.push(h.buffer, ...dataParts);
    this.offset += h.byteLength + size;
    this.count++;
  }
  finish() {
    const cdStart = this.offset, cd = []; let cdSize = 0;
    for (const e of this.central) {
      const offBig = e.localOffset >= ZIP64_LIMIT, z = e.big || offBig;
      const fields = []; if (e.big) fields.push(e.size, e.size); if (offBig) fields.push(e.localOffset);
      const extraLen = fields.length ? 4 + 8 * fields.length : 0;
      const v = new DataView(new ArrayBuffer(46 + e.name.length + extraLen));
      // "made by" = Unix (3) so unzip tools never apply DOS codepage conversion to UTF-8 names
      v.setUint32(0, 0x02014b50, true); v.setUint16(4, (3 << 8) | (z ? 45 : 20), true); v.setUint16(6, z ? 45 : 20, true);
      v.setUint16(8, 0x0800, true); v.setUint16(10, 0, true); v.setUint16(12, this.time, true); v.setUint16(14, this.date, true);
      v.setUint32(16, e.crc, true);
      v.setUint32(20, e.big ? 0xFFFFFFFF : e.size, true); v.setUint32(24, e.big ? 0xFFFFFFFF : e.size, true);
      v.setUint16(28, e.name.length, true); v.setUint16(30, extraLen, true);
      v.setUint32(38, (0o100644 << 16) >>> 0, true);   // regular file, rw-r--r--
      v.setUint32(42, offBig ? 0xFFFFFFFF : e.localOffset, true);
      new Uint8Array(v.buffer).set(e.name, 46);
      if (extraLen) {
        let o = 46 + e.name.length;
        v.setUint16(o, 1, true); v.setUint16(o + 2, 8 * fields.length, true); o += 4;
        for (const f of fields) { v.setBigUint64(o, BigInt(f), true); o += 8; }
      }
      cd.push(v.buffer); cdSize += v.byteLength;
    }
    const tail = [];
    const z64 = this.count >= 0xFFFF || cdSize >= ZIP64_LIMIT || cdStart >= ZIP64_LIMIT;
    if (z64) {
      const r = new DataView(new ArrayBuffer(76));
      r.setUint32(0, 0x06064b50, true); r.setBigUint64(4, BigInt(44), true); r.setUint16(12, 45, true); r.setUint16(14, 45, true);
      r.setBigUint64(24, BigInt(this.count), true); r.setBigUint64(32, BigInt(this.count), true);
      r.setBigUint64(40, BigInt(cdSize), true); r.setBigUint64(48, BigInt(cdStart), true);
      r.setUint32(56, 0x07064b50, true); r.setBigUint64(64, BigInt(cdStart + cdSize), true); r.setUint32(72, 1, true);
      tail.push(r.buffer);
    }
    const end = new DataView(new ArrayBuffer(22));
    end.setUint32(0, 0x06054b50, true);
    end.setUint16(8, z64 ? 0xFFFF : this.count, true); end.setUint16(10, z64 ? 0xFFFF : this.count, true);
    end.setUint32(12, z64 ? 0xFFFFFFFF : cdSize, true); end.setUint32(16, z64 ? 0xFFFFFFFF : cdStart, true);
    tail.push(end.buffer);
    return new Blob([...this.parts, ...cd, ...tail], { type: 'application/zip' });
  }
}

/* ============================ SENDER ============================ */
async function entriesFromDrop(dt) {
  // grab entries synchronously - DataTransfer items expire after the first await
  const roots = [...(dt.items || [])].map(i => i.webkitGetAsEntry && i.webkitGetAsEntry()).filter(Boolean);
  if (!roots.length) return [...dt.files].map(f => ({ file: f, path: f.name }));
  const out = [];
  async function walk(entry) {
    if (entry.isFile) {
      const f = await new Promise((res, rej) => entry.file(res, rej));
      out.push({ file: f, path: entry.fullPath.replace(/^\/+/, '') });
    } else if (entry.isDirectory) {
      const reader = entry.createReader(); let batch;
      do {
        batch = await new Promise((res, rej) => reader.readEntries(res, rej));
        for (const child of batch) await walk(child);
      } while (batch.length);
    }
  }
  for (const r of roots) await walk(r);
  return out;
}

function initSender() {
  app.innerHTML = `
    <div class="panel" id="conn" data-state="wait">
      <div class="linkrow">
        <div class="dev me"><div class="ic">💻</div><div><b>Aap</b><span>Bhej rahe ho</span></div></div>
        <div class="wire"></div>
        <div class="dev right"><div class="ic" id="themic">⌛</div><div><b>Receiver</b><span id="themsub">Abhi juda nahi</span></div></div>
      </div>
      <div class="state"><span class="dot"></span><span id="pstatus">Ready ho raha hai…</span></div>
    </div>
    <div class="panel">
      <div class="codewrap">
        <div><div class="hint">Receiver ko ye code do</div><div class="tiles">${tilesHtml(CODE)}</div></div>
        <div class="actions">
          <button class="chip" id="cpc">📋 Code copy</button>
          <button class="chip" id="cpl" style="display:none">🔗 Link copy</button>
          <a class="chip wa" id="wa" target="_blank" rel="noopener" style="display:none">💬 WhatsApp par bhejo</a>
        </div>
      </div>
    </div>
    <div id="drop" class="drop">
      <div class="icon">📦</div>
      <div class="big">Files ya poora folder yahan chhodo</div>
      <div class="sub">Ya neeche se chuno. Koi size limit nahi, kuch bhi server par save nahi hota.</div>
      <div class="pick">
        <button id="pf" class="btn">📄 Files chuno</button>
        <button id="pd" class="btn ghost">📁 Folder chuno</button>
      </div>
      <div class="sub">Folder receiver ko ZIP file mein milega</div>
    </div>
    <input id="inp" type="file" multiple style="display:none">
    <input id="dinp" type="file" webkitdirectory directory multiple style="display:none">
    <div id="list" class="rows"></div>
    <div id="total" class="total"></div>
    <div id="status" class="msg"></div>`;

  $('cpc').onclick = () => copyText(CODE, $('cpc'), '📋 Code copy');
  const url = shareUrl();
  if (url) {
    $('cpl').style.display = ''; $('cpl').onclick = () => copyText(url, $('cpl'), '🔗 Link copy');
    $('wa').style.display = '';
    $('wa').href = 'https://wa.me/?text=' + encodeURIComponent(`Ye file(s) lene ke liye link kholo:\n${url}\n\nCode: ${CODE}`);
  }

  let groups = [], conn = null, dc = null, sending = false, batchDone = false;
  const drop = $('drop'), inp = $('inp'), dinp = $('dinp');
  $('pf').onclick = () => { if (!sending) inp.click(); };
  $('pd').onclick = () => { if (!sending) dinp.click(); };
  drop.ondragover = e => { e.preventDefault(); if (!sending) drop.classList.add('over'); };
  drop.ondragleave = () => drop.classList.remove('over');
  drop.ondrop = async e => {
    e.preventDefault(); drop.classList.remove('over');
    if (sending) return;
    setStatus('status', 'Files/folder padh rahe hain…', 'wait');
    try { addEntries(await entriesFromDrop(e.dataTransfer)); }
    catch (x) { setStatus('status', 'Ye folder padh nahi paaye. "📁 Folder chuno" button se try karo.', 'err'); }
  };
  inp.onchange = () => { addEntries([...inp.files].map(f => ({ file: f, path: f.name }))); inp.value = ''; };
  dinp.onchange = () => { addEntries([...dinp.files].map(f => ({ file: f, path: f.webkitRelativePath || f.name }))); dinp.value = ''; };

  function totals() {
    return { count: groups.reduce((s, g) => s + g.files.length, 0), size: groups.reduce((s, g) => s + g.size, 0) };
  }

  function addEntries(list) {
    if (!list.length) { setStatus('status', ''); return; }
    if (batchDone) { groups = []; batchDone = false; }  // new batch: don't resend old files
    for (const en of list) {
      const slash = en.path.indexOf('/');
      if (slash > 0) {
        const top = en.path.slice(0, slash);
        let g = groups.find(x => x.kind === 'folder' && x.name === top);
        if (!g) { g = { kind: 'folder', name: top, files: [], size: 0 }; groups.push(g); }
        g.files.push(en); g.size += en.file.size;
      } else {
        groups.push({ kind: 'file', name: en.path, files: [en], size: en.file.size });
      }
    }
    setStatus('status', conn ? 'Receiver juda hua hai. Wo "Start Download" dabayega toh transfer shuru hoga.' : 'Ab code ya link receiver ko bhejo.');
    render(); sendList();
  }
  window.removeGroup = i => { if (sending) return; groups.splice(i, 1); render(); sendList(); };

  function render() {
    $('list').innerHTML = groups.map((g, i) => `
      <div class="row">
        ${fileIcon(g.name, g.kind)}
        <div class="rbody">
          <div class="name" title="${esc(g.name)}">${esc(g.name)}</div>
          <div class="bar"><div class="fill ${batchDone ? 'done' : ''}" id="sf${i}" ${batchDone ? 'style="width:100%"' : ''}></div></div>
          <div class="small" id="ss${i}">${g.kind === 'folder' ? g.files.length + ' files • ' : ''}${fmt(g.size)}${batchDone ? ' • <span class="ok">Bhej diya</span>' : ''}</div>
        </div>
        ${sending || batchDone ? '' : `<button class="x" title="Hatao" aria-label="Hatao ${esc(g.name)}" onclick="removeGroup(${i})">✕</button>`}
      </div>`).join('');
    const t = totals();
    $('total').innerHTML = totalLine(t.count, t.size);
    drop.classList.toggle('off', sending);
    $('pf').disabled = $('pd').disabled = sending;
  }

  function sendList() {
    if (!(dc && dc.readyState === 'open') || sending) return;
    const summary = groups.map(g => ({ kind: g.kind, name: g.name, count: g.files.length, size: g.size }));
    if (!summary.length) { dc.send(JSON.stringify({ t: 'list', groups: [], first: true, more: false })); return; }
    for (let s = 0; s < summary.length; s += LIST_SLICE)
      dc.send(JSON.stringify({ t: 'list', groups: summary.slice(s, s + LIST_SLICE), first: s === 0, more: s + LIST_SLICE < summary.length }));
  }

  function drain() {
    if (dc.bufferedAmount < HIGH_WATER) return Promise.resolve();
    return new Promise((res, rej) => {
      const ok = () => { cleanup(); res(); }, bad = () => { cleanup(); rej(new Error('closed')); };
      const cleanup = () => { dc.removeEventListener('bufferedamountlow', ok); dc.removeEventListener('close', bad); };
      dc.addEventListener('bufferedamountlow', ok); dc.addEventListener('close', bad);
    });
  }

  async function sendAll() {
    if (sending || !groups.length) return;
    sending = true; render(); keepAwake(true);
    setConn('busy', 'File le raha hai');
    setStatus('pstatus', 'Transfer chal raha hai. Ye tab band mat karna.');
    setStatus('status', '');
    const pc = conn.peerConnection;
    const maxMsg = (pc && pc.sctp && pc.sctp.maxMessageSize) || 65536;
    const CH = Math.max(16384, Math.min(65536, maxMsg));
    const all = totals(), tAll = Date.now(); let allSent = 0;
    try {
      for (let gi = 0; gi < groups.length; gi++) {
        const g = groups[gi], t0 = Date.now(); let gsent = 0, lastUi = 0;
        for (let fi = 0; fi < g.files.length; fi++) {
          const { file: f, path } = g.files[fi];
          dc.send(JSON.stringify({ t: 'file', g: gi, path, size: f.size, type: f.type }));
          for (let off = 0; off < f.size; off += READ_BLOCK) {
            const buf = await f.slice(off, off + READ_BLOCK).arrayBuffer();
            for (let p = 0; p < buf.byteLength; p += CH) {
              await drain();
              if (dc.readyState !== 'open') throw new Error('closed');
              dc.send(buf.slice(p, p + CH));
            }
            gsent += buf.byteLength; allSent += buf.byteLength;
            if (Date.now() - lastUi > 250) {
              lastUi = Date.now();
              $('sf' + gi).style.width = pct(gsent, g.size) + '%';
              setStatus('ss' + gi, (g.kind === 'folder' ? `File ${fi + 1}/${g.files.length} • ` : '') + progressText(gsent, g.size, t0));
              $('total').innerHTML = totalLine(all.count, all.size, allSent, tAll);
            }
          }
          if (dc.readyState !== 'open') throw new Error('closed');
          dc.send(JSON.stringify({ t: 'end' }));
        }
        dc.send(JSON.stringify({ t: 'gend', g: gi }));
        $('sf' + gi).style.width = '100%'; $('sf' + gi).classList.add('done');
        setStatus('ss' + gi, (g.kind === 'folder' ? g.files.length + ' files • ' : '') + fmt(g.size) + ' • <span class="ok">Bhej diya</span>');
      }
      dc.send(JSON.stringify({ t: 'done' }));
      batchDone = true;
      setConn('connected', 'Sab mil gaya');
      setStatus('pstatus', 'Transfer poora ho gaya.');
      setStatus('status', '🎉 Sab kuch bhej diya! Aur bhejna ho toh nayi files ya folder chuno.', 'ok');
    } catch (e) {
      setConn('error', 'Beech mein toot gaya');
      setStatus('pstatus', 'Receiver disconnect ho gaya.');
      setStatus('status', 'Transfer beech mein ruk gaya. Receiver link dobara khol kar "Start Download" dabaye.', 'err');
    }
    sending = false; keepAwake(false); render();
  }

  if (typeof Peer === 'undefined') {
    setConn('error'); setStatus('pstatus', 'Transfer system load nahi hua. Internet check karke page refresh karo.', 'err'); return;
  }
  const peer = new Peer(PREFIX + CODE.toLowerCase(), OPTS);
  peer.on('open', () => { if (!conn) { setConn('ready', 'Code ka intezaar'); setStatus('pstatus', 'Ready! Receiver ko code ya link bhejo aur ye page khula rakho.'); } });
  peer.on('error', err => { if (err.type !== 'peer-unavailable') { setConn('error'); setStatus('pstatus', peerErrorText(err), 'err'); } });
  peer.on('disconnected', () => { setTimeout(() => { if (!peer.destroyed && peer.disconnected) peer.reconnect(); }, 2000); });
  peer.on('connection', c => {
    if (conn && conn.open) {
      c.on('open', () => { try { c.dataChannel.send(JSON.stringify({ t: 'busy' })); } catch (e) {} setTimeout(() => c.close(), 1000); });
      return;
    }
    conn = c;
    c.on('open', () => {
      dc = c.dataChannel;
      dc.binaryType = 'arraybuffer';
      dc.bufferedAmountLowThreshold = LOW_WATER;
      dc.addEventListener('message', e => {
        if (typeof e.data !== 'string') return;
        let m; try { m = JSON.parse(e.data); } catch (x) { return; }
        if (m.t === 'start') sendAll();
      });
      setConn('connected', 'Jud gaya');
      setStatus('pstatus', groups.length ? 'Receiver jud gaya. Wo "Start Download" dabayega toh transfer shuru hoga.' : 'Receiver jud gaya. Ab files ya folder chuno.');
      render(); sendList();
    });
    c.on('close', () => {
      if (conn !== c) return;
      conn = null; dc = null;
      if (!sending) { setConn('ready', 'Disconnect ho gaya'); setStatus('pstatus', 'Receiver chala gaya. Wo link dobara khol sakta hai.'); }
      render();
    });
    watchIce(c, () => { if (conn === c) { setConn('error', 'Connect nahi ho paaya'); setStatus('pstatus', ICE_FAIL_TEXT, 'err'); } });
  });
}

/* ============================ RECEIVER ============================ */
function initReceiver() {
  app.innerHTML = `
    <div class="panel" id="conn" data-state="wait">
      <div class="linkrow">
        <div class="dev"><div class="ic" id="themic">⌛</div><div><b>Sender</b><span id="themsub">Dhoondh rahe hain…</span></div></div>
        <div class="wire"></div>
        <div class="dev me right"><div class="ic">💻</div><div><b>Aap</b><span>Code ${esc(CODE)}</span></div></div>
      </div>
      <div class="state"><span class="dot"></span><span id="rstatus">Sender se connect ho rahe hain…</span></div>
    </div>
    <div id="list" class="rows"></div>
    <div id="total" class="total"></div>
    <button id="start" class="btn big" style="display:none">⬇️ Start Download</button>
    <div id="status" class="msg"></div>`;

  let offered = [], incoming = [], cur = null, gstate = {}, zips = {}, finished = false, started = false;
  let allGot = 0, tAll = 0;

  function totals() {
    return { count: offered.reduce((s, g) => s + g.count, 0), size: offered.reduce((s, g) => s + g.size, 0) };
  }

  function renderList() {
    $('list').innerHTML = offered.map((g, i) => `
      <div class="row">
        ${fileIcon(g.name, g.kind)}
        <div class="rbody">
          <div class="name" title="${esc(g.name)}">${esc(g.name)}${g.kind === 'folder' ? '<span class="small"> → ' + esc(g.name) + '.zip</span>' : ''}</div>
          <div class="bar"><div class="fill" id="rf${i}"></div></div>
          <div class="small" id="rs${i}">${g.kind === 'folder' ? g.count + ' files • ' : ''}${fmt(g.size)}</div>
        </div>
      </div>`).join('');
    const t = totals();
    $('total').innerHTML = totalLine(t.count, t.size);
    updateButton();
  }

  function updateButton() {
    const t = totals();
    const btn = $('start');
    btn.style.display = offered.length && !finished ? '' : 'none';
    btn.disabled = started || finished;
    btn.textContent = finished ? '✅ Download ho gaya'
      : started ? '⏳ Download ho raha hai…'
      : `⬇️ Start Download (${fmt(t.size)})`;
  }

  function saveBlob(g, blob, name) {
    const url = URL.createObjectURL(blob);
    const fill = $('rf' + g); fill.style.width = '100%'; fill.classList.add('done');
    const o = offered[g];
    setStatus('rs' + g, `${o && o.kind === 'folder' ? o.count + ' files • ' : ''}${fmt(blob.size)} • <span class="ok">Aa gaya</span><br>` +
      `<a class="save" id="sv${g}" href="${url}" download="${esc(name)}">💾 Save ${esc(name)}</a>`);
    try { $('sv' + g).click(); } catch (e) {}
  }

  function finishFile() {
    if (cur.pending.length) cur.parts.push(new Blob(cur.pending));
    const g = offered[cur.g];
    if (g && g.kind === 'folder') {
      (zips[cur.g] = zips[cur.g] || new ZipBuilder()).add(cur.path, cur.got, cur.crc, cur.parts);
    } else {
      saveBlob(cur.g, new Blob(cur.parts, { type: cur.type || 'application/octet-stream' }), cur.path.split('/').pop());
    }
    cur = null;
  }

  function finishGroup(gi) {
    const g = offered[gi];
    if (!g || g.kind !== 'folder') return;
    setStatus('rs' + gi, 'ZIP bana rahe hain…', 'wait');
    const zip = zips[gi] || new ZipBuilder();
    delete zips[gi];
    saveBlob(gi, zip.finish(), g.name + '.zip');
  }

  if (typeof Peer === 'undefined') {
    setConn('error'); setStatus('rstatus', 'Transfer system load nahi hua. Internet check karke page refresh karo.', 'err'); return;
  }
  const peer = new Peer(OPTS);
  let opened = false;
  peer.on('error', err => { if (!finished) { setConn('error', 'Nahi mila'); setStatus('rstatus', peerErrorText(err), 'err'); } });
  peer.on('disconnected', () => { setTimeout(() => { if (!peer.destroyed && peer.disconnected && !opened) peer.reconnect(); }, 2000); });
  peer.on('open', () => {
    setConn('ready', 'Dhoondh rahe hain…');
    const conn = peer.connect(PREFIX + CODE.toLowerCase(), { reliable: true, serialization: 'raw' });
    const timer = setTimeout(() => {
      if (!opened) { setConn('error', 'Nahi mila'); setStatus('rstatus', 'Sender se connect nahi ho paaye. Code sahi hai? Sender ka page khula hai? ' + ICE_FAIL_TEXT, 'err'); }
    }, 30000);
    watchIce(conn, () => { if (!finished) { setConn('error', 'Connect nahi ho paaya'); setStatus('rstatus', ICE_FAIL_TEXT, 'err'); } });

    conn.on('open', () => {
      opened = true; clearTimeout(timer);
      const dc = conn.dataChannel;
      dc.binaryType = 'arraybuffer';
      setConn('connected', 'Jud gaya');
      setStatus('rstatus', 'Sender se jud gaye. Files ki list aa rahi hai…');

      $('start').onclick = () => {
        if (started || !offered.length) return;
        started = true; gstate = {}; zips = {}; allGot = 0; tAll = Date.now();
        updateButton(); keepAwake(true);
        dc.send(JSON.stringify({ t: 'start' }));
        setConn('busy', 'Bhej raha hai');
        setStatus('rstatus', 'Files aa rahi hain. Ye tab band mat karna.');
        setStatus('status', '');
      };

      let lastUi = 0;
      dc.addEventListener('message', e => {
        const d = e.data;
        if (typeof d === 'string') {
          let m; try { m = JSON.parse(d); } catch (x) { return; }
          if (m.t === 'list') {
            if (m.first) incoming = [];
            incoming.push(...m.groups);
            if (m.more) return;
            offered = incoming; started = false; finished = false; renderList();
            setConn('connected', 'Jud gaya');
            setStatus('rstatus', offered.length ? 'Files taiyaar hain. "Start Download" dabao.' : 'Sender files chun raha hai…');
          }
          else if (m.t === 'file') {
            const gs = gstate[m.g] = gstate[m.g] || { got: 0, n: 0, t0: Date.now() };
            gs.n++;
            cur = { g: m.g, path: m.path, size: m.size, type: m.type, got: 0, crc: 0, parts: [], pending: [], pendingBytes: 0,
                    zip: !!(offered[m.g] && offered[m.g].kind === 'folder') };
          }
          else if (m.t === 'end') { if (cur) finishFile(); }
          else if (m.t === 'gend') { finishGroup(m.g); }
          else if (m.t === 'done') {
            finished = true; started = false; keepAwake(false); updateButton();
            const t = totals(); $('total').innerHTML = totalLine(t.count, t.size);
            setConn('connected', 'Sab bhej diya');
            setStatus('rstatus', 'Transfer poora ho gaya.');
            setStatus('status', '🎉 Sab kuch aa gaya! Download apne aap shuru na hua ho toh "Save" link dabao.', 'ok');
          }
          else if (m.t === 'busy') { setConn('error', 'Busy hai'); setStatus('rstatus', 'Sender abhi kisi aur ko file bhej raha hai. Thodi der baad try karo.', 'err'); }
          return;
        }
        if (!cur) return;
        if (cur.zip) cur.crc = crc32(cur.crc, d);
        cur.pending.push(d); cur.pendingBytes += d.byteLength; cur.got += d.byteLength; allGot += d.byteLength;
        if (cur.pendingBytes >= FLUSH_BYTES) { cur.parts.push(new Blob(cur.pending)); cur.pending = []; cur.pendingBytes = 0; }
        const gs = gstate[cur.g]; gs.got += d.byteLength;
        if (Date.now() - lastUi > 250) {
          lastUi = Date.now();
          const g = offered[cur.g] || { size: cur.size, count: 1, kind: 'file' };
          $('rf' + cur.g).style.width = pct(gs.got, g.size) + '%';
          setStatus('rs' + cur.g, (g.kind === 'folder' ? `File ${gs.n}/${g.count} • ` : '') + progressText(gs.got, g.size, gs.t0));
          const t = totals(); $('total').innerHTML = totalLine(t.count, t.size, allGot, tAll);
        }
      });
    });
    conn.on('close', () => {
      if (!finished) { keepAwake(false); setConn('error', 'Chala gaya'); setStatus('rstatus', 'Sender disconnect ho gaya. Sender ka page khula ho toh ye page refresh karo.', 'err'); }
    });
  });
}

if (MODE === 'send') initSender(); else initReceiver();
</script>
"""

# Main logic based on selection
if conversion_type == P2P_TOOL:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Direct File Transfer")
    st.markdown("AnyDesk ki tarah: files ya poora folder seedha aapke device se saamne wale ke device par jaata hai. "
                "**Koi size limit nahi, koi account nahi, bilkul free.** Bas transfer ke waqt dono ka page khula hona chahiye.")
    st.markdown("</div>", unsafe_allow_html=True)

    incoming = clean_p2p_code(st.query_params.get("receive", ""))
    p2p_mode = st.radio(
        "Aap kya karna chahte ho?",
        ["📤 File Bhejna", "📥 File Lena"],
        index=1 if incoming else 0,
        horizontal=True,
    )

    if p2p_mode == "📤 File Bhejna":
        if "p2p_code" not in st.session_state:
            st.session_state.p2p_code = new_p2p_code()
        st.info("Kaise bhejein: (1) Files ya folder chuno, (2) code ya link receiver ko bhejo, (3) receiver 'Start' dabayega "
                "aur file seedha uske paas pahunch jaayegi. Transfer poora hone tak ye page khula rakho aur upar ka option mat badlo.",
                icon="💡")
        components.html(build_p2p_html("send", st.session_state.p2p_code), height=820, scrolling=True)
        if st.button("🔄 New Code"):
            st.session_state.p2p_code = new_p2p_code()
            st.rerun()
    else:
        code = clean_p2p_code(st.text_input("Sender ka 6 akshar ka code daalo", value=incoming, max_chars=8,
                                            placeholder="e.g. K7P2QX"))
        if len(code) == 6:
            st.info("Sender ka page khula hona chahiye. Connect hone par files ki list dikhegi, phir 'Start Download' dabao. "
                    "Transfer poora hone tak ye page khula rakho.")
            components.html(build_p2p_html("receive", code), height=660, scrolling=True)
        elif code:
            st.warning("Code poore 6 akshar ka hona chahiye.")

    with st.expander("ℹ️ Kaam kaise karta hai / problem aaye toh"):
        st.markdown(
            "- File kisi server par **save nahi hoti**. Seedha ek browser se doosre browser mein jaati hai (WebRTC, encrypted).\n"
            "- **Folder** bhejoge toh receiver ko woh ek **ZIP file** mein milega, andar saare sub-folder waise hi rahenge. "
            "ZIP par right-click → Extract karke folder wapas mil jaayega.\n"
            "- Folder chunna laptop/desktop browser par chalta hai. Mobile par 'Files chuno' use karo.\n"
            "- Badi files (kai GB) ke liye **Chrome ya Edge, laptop/desktop par** sabse achha chalta hai.\n"
            "- Speed dono taraf ke internet par depend karti hai. Ek hi WiFi par ho toh bahut tez chalti hai.\n"
            "- Connect na ho toh: dono page refresh karo, naya code banao, ya network badal kar dekho "
            "(kuch office/college WiFi aur kuch mobile networks direct connection rok dete hain).\n"
            "- Beech mein connection toote toh transfer dobara Start karna padega."
        )

elif conversion_type == CLOUD_TOOL:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Large File Transfer")
    st.markdown("WeTransfer ki tarah badi files bhejo. Files seedha secure cloud storage par upload hoti hain "
                "aur aapko ek download link milta hai jo kisi ko bhi bhej sakte ho.")
    st.markdown("</div>", unsafe_allow_html=True)

    if not r2_is_configured():
        st.warning("⚠️ File Transfer abhi setup nahi hua hai. App ke **Secrets** mein Cloudflare R2 ki details daalni hongi.")
        with st.expander("Setup kaise karein?"):
            st.code(
                '[r2]\n'
                'account_id = "YOUR_CLOUDFLARE_ACCOUNT_ID"\n'
                'access_key_id = "YOUR_R2_ACCESS_KEY_ID"\n'
                'secret_access_key = "YOUR_R2_SECRET_ACCESS_KEY"\n'
                'bucket = "dk-transfers"',
                language="toml",
            )
            st.markdown("Streamlit Cloud par: **App → Settings → Secrets** mein ye paste karo. "
                        "Local chalane ke liye `.streamlit/secrets.toml` file banao.")
    else:
        expiry_days = st.selectbox(
            "⏳ Download link kitne din tak chale?",
            [1, 3, 7],
            index=2,
            format_func=lambda d: f"{d} din",
        )

        if "transfer_id" not in st.session_state:
            st.session_state.transfer_id = uuid.uuid4().hex

        # Keep the same URLs across reruns so an in-progress upload is not reset
        slots_key = f"{st.session_state.transfer_id}_{expiry_days}"
        if st.session_state.get("transfer_slots_key") != slots_key:
            try:
                st.session_state.transfer_slots = make_transfer_slots(st.session_state.transfer_id, expiry_days)
                st.session_state.transfer_slots_key = slots_key
            except Exception as e:
                st.session_state.pop("transfer_slots", None)
                st.session_state.pop("transfer_slots_key", None)
                st.error(f"❌ Storage se connect nahi ho paaya: {e}")

        if st.session_state.get("transfer_slots"):
            st.info("💡 Upload ke dauran is tab ko band mat karna aur sidebar mein tool mat badalna. "
                    "Link milne ke baad aap use WhatsApp, email kahin bhi bhej sakte ho.")
            components.html(build_transfer_html(st.session_state.transfer_slots), height=720, scrolling=True)

            if st.button("🔄 New Transfer"):
                for k in ("transfer_id", "transfer_slots", "transfer_slots_key"):
                    st.session_state.pop(k, None)
                st.rerun()

elif conversion_type == "🖼️ Image to PDF":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Convert Images to PDF")
    st.markdown("Combine multiple images into a single professional PDF file.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    uploaded_images = st.file_uploader("Upload Images (jpg, png, webp, etc.)", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"], accept_multiple_files=True)
    
    if uploaded_images:
        st.info(f"✅ {len(uploaded_images)} image(s) selected.")
        if st.button("Convert to PDF"):
            with st.spinner("Converting images to PDF..."):
                pdf_data = image_to_pdf(uploaded_images)
                if pdf_data:
                    st.success("🎉 Conversion Successful!")
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_data,
                        file_name="converted_images.pdf",
                        mime="application/pdf"
                    )

elif conversion_type == "🖼️ Image to Word":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Convert Images to Word")
    st.markdown("Insert images into a well-formatted Word document.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    uploaded_images = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"], accept_multiple_files=True)
    
    if uploaded_images:
        st.info(f"✅ {len(uploaded_images)} image(s) selected.")
        if st.button("Convert to Word"):
            with st.spinner("Creating Word document..."):
                word_data = image_to_word(uploaded_images)
                if word_data:
                    st.success("🎉 Conversion Successful!")
                    st.download_button(
                        label="📥 Download Word Document",
                        data=word_data,
                        file_name="converted_images.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

elif conversion_type == "🔁 WebP Converter":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("WebP Converter")
    st.markdown("Images ko WebP mein badlo (chhoti size, same quality), ya WebP ko JPG / PNG / PDF mein badlo.")
    st.markdown("</div>", unsafe_allow_html=True)

    webp_mode = st.radio(
        "Kya karna hai?",
        ["🖼️ Images → WebP", "🔁 WebP → JPG / PNG / PDF"],
        horizontal=True
    )

    if webp_mode == "🖼️ Images → WebP":
        uploaded_images = st.file_uploader(
            "Upload Images (jpg, png, gif, bmp, tiff)",
            type=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
            accept_multiple_files=True,
            key="to_webp_uploader"
        )
        target_format = "WEBP"
        out_ext, out_mime = "webp", "image/webp"
    else:
        uploaded_images = st.file_uploader(
            "Upload WebP Images",
            type=["webp"],
            accept_multiple_files=True,
            key="from_webp_uploader"
        )
        target_choice = st.selectbox("Kis format mein chahiye?", ["JPG", "PNG", "PDF (sab images ek PDF mein)"])
        target_format = {"JPG": "JPEG", "PNG": "PNG"}.get(target_choice, "PDF")
        out_ext, out_mime = {"JPEG": ("jpg", "image/jpeg"), "PNG": ("png", "image/png")}.get(target_format, ("pdf", "application/pdf"))

    if uploaded_images:
        st.info(f"✅ {len(uploaded_images)} image(s) selected.")

        lossless = False
        quality = 85
        if target_format == "WEBP":
            lossless = st.checkbox("Lossless (bilkul original quality, size thodi badi)", value=False)
        if target_format in ("WEBP", "JPEG") and not lossless:
            quality = st.slider("Quality (1-100)", min_value=1, max_value=100, value=85,
                                help="Kam value = chhoti file, par quality thodi kam")

        if st.button("Convert Now"):
            if target_format == "PDF":
                with st.spinner("WebP images ko PDF mein badal rahe hain..."):
                    pdf_data = image_to_pdf(uploaded_images)
                if pdf_data:
                    st.success("🎉 PDF taiyaar hai!")
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_data,
                        file_name="converted_webp_images.pdf",
                        mime="application/pdf",
                        key="dl_webp_pdf"
                    )
            else:
                results = []
                total_in, total_out = 0, 0
                with st.spinner(f"Converting {len(uploaded_images)} image(s)..."):
                    for f in uploaded_images:
                        raw = f.getvalue()
                        try:
                            converted = convert_image_format(raw, target=target_format, quality=quality, lossless=lossless)
                        except Exception as e:
                            st.warning(f"⚠️ {f.name} convert nahi ho paayi: {e}")
                            continue
                        new_name = f"{f.name.rsplit('.', 1)[0]}.{out_ext}"
                        results.append((new_name, raw, converted))
                        total_in += len(raw)
                        total_out += len(converted)

                if results:
                    st.success(f"🎉 {len(results)} image(s) converted!")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Original Size", f"{total_in / 1024:.1f} KB")
                    c2.metric("New Size", f"{total_out / 1024:.1f} KB")
                    change = ((total_in - total_out) / total_in * 100) if total_in else 0
                    c3.metric("Size Change", f"{'-' if change >= 0 else '+'}{abs(change):.1f}%")

                    st.markdown("### 📦 Converted Files")
                    for new_name, raw, converted in results:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(io.BytesIO(raw), caption=f"Original — {len(raw) / 1024:.1f} KB", use_container_width=True)
                        with col2:
                            st.image(io.BytesIO(converted), caption=f"{new_name} — {len(converted) / 1024:.1f} KB", use_container_width=True)
                        st.download_button(
                            label=f"📥 Download {new_name}",
                            data=converted,
                            file_name=new_name,
                            mime=out_mime,
                            key=f"dl_webp_{new_name}"
                        )
                        st.markdown("---")

                    if len(results) > 1:
                        zip_buf = create_zip_from_files([(n, c) for n, _r, c in results])
                        st.download_button(
                            label="🗂️ Download All as ZIP",
                            data=zip_buf.getvalue(),
                            file_name=f"converted_{out_ext}_images.zip",
                            mime="application/zip",
                            key="dl_webp_zip"
                        )

elif conversion_type == "📝 Image to Editable Text (OCR)":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Image to Editable Text (OCR)")
    st.markdown("Extract editable text from images using Optical Character Recognition (supports English + Hindi).")
    st.markdown("</div>", unsafe_allow_html=True)
    
    uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image")
        if st.button("Extract Text"):
            with st.spinner("Extracting text from image... (This may take a moment)"):
                extracted_text = image_to_editable_text(uploaded_image)
                if extracted_text:
                    st.success("🎉 Text Extracted Successfully!")
                    st.text_area("Extracted Text:", value=extracted_text, height=300)
                    st.download_button(
                        label="📥 Download as Text File",
                        data=extracted_text,
                        file_name="extracted_text.txt",
                        mime="text/plain"
                    )
                else:
                    st.warning("⚠️ No text found in the image.")

elif conversion_type == "📄 PDF to Image":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Convert PDF to Images")
    st.markdown("Extract each page of your PDF as high-quality PNG images.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    uploaded_pdf = st.file_uploader("Upload PDF File", type=["pdf"])
    
    if uploaded_pdf:
        if st.button("Convert to Images"):
            with st.spinner("Extracting pages as images..."):
                images = pdf_to_images(uploaded_pdf)
                if images:
                    st.success(f"🎉 Converted {len(images)} pages!")
                    
                    # Create ZIP buffer
                    zip_buffer = create_zip_from_images(images, base_name=os.path.splitext(uploaded_pdf.name)[0])
                    
                    st.download_button(
                        label="📥 Download All Pages as ZIP",
                        data=zip_buffer,
                        file_name=f"{os.path.splitext(uploaded_pdf.name)[0]}_images.zip",
                        mime="application/zip"
                    )
                    
                    for i, img_data in enumerate(images):
                        st.image(img_data, caption=f"Page {i+1}")
                        st.download_button(
                            label=f"📥 Download Page {i+1} (PNG)",
                            data=img_data,
                            file_name=f"{os.path.splitext(uploaded_pdf.name)[0]}_page_{i+1}.png",
                            mime="image/png"
                        )

elif conversion_type == "📝 PDF to Word":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Convert PDF to Word")
    st.markdown("Turn your PDF files into editable Word documents.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    uploaded_pdf = st.file_uploader("Upload PDF File", type=["pdf"])
    
    if uploaded_pdf:
        if st.button("Convert to Word"):
            with st.spinner("Converting PDF to Word... This may take a moment."):
                word_data = pdf_to_word(uploaded_pdf)
                if word_data:
                    st.success("🎉 Conversion Successful!")
                    st.download_button(
                        label="📥 Download Word Document",
                        data=word_data,
                        file_name="converted_document.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

elif conversion_type == "📊 PDF to Excel":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Convert PDF to Excel")
    st.markdown("Extract tables from your PDF into an Excel spreadsheet.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    uploaded_pdf = st.file_uploader("Upload PDF File", type=["pdf"])
    
    if uploaded_pdf:
        if st.button("Convert to Excel"):
            with st.spinner("Extracting tables and converting..."):
                excel_data = pdf_to_excel(uploaded_pdf)
                if excel_data:
                    st.success("🎉 Conversion Successful!")
                    st.download_button(
                        label="📥 Download Excel File",
                        data=excel_data,
                        file_name="converted_tables.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("⚠️ No tables found in the PDF.")

elif conversion_type == "📎 Merge PDFs":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Merge Multiple PDFs")
    st.markdown("Combine multiple PDF files into a single, organized document.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    uploaded_pdfs = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_pdfs:
        st.info(f"✅ {len(uploaded_pdfs)} PDF(s) selected.")
        st.markdown("Reorder files by dragging them in the upload box.")
        if st.button("Merge PDFs"):
            with st.spinner("Merging PDF files..."):
                merged_pdf = merge_pdfs(uploaded_pdfs)
                if merged_pdf:
                    st.success("🎉 PDFs Merged Successfully!")
                    st.download_button(
                        label="📥 Download Merged PDF",
                        data=merged_pdf,
                        file_name="merged_document.pdf",
                        mime="application/pdf"
                    )

elif conversion_type == "🔽 Compress Image":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Compress Image")
    st.markdown("Reduce multiple image file sizes at once with adjustable quality.")
    st.markdown("</div>", unsafe_allow_html=True)

    uploaded_images = st.file_uploader("Upload Images (single or multiple)", type=["jpg", "jpeg", "png", "webp", "bmp"], accept_multiple_files=True)

    if uploaded_images:
        st.info(f"✅ {len(uploaded_images)} image(s) selected.")

        for idx, img_file in enumerate(uploaded_images):
            img_file.seek(0)
            orig_size = get_file_size(img_file)
            with st.expander(f"🖼️ {img_file.name} — Original: {orig_size}", expanded=(idx == 0)):
                st.image(img_file, caption=f"Original: {img_file.name}")

        quality = st.slider("Compression Quality (1-100)", min_value=1, max_value=100, value=85,
                            help="Lower values = smaller file size but more compression artifacts")

        if st.button("Compress All Images"):
            compressed_results = []
            total_original = 0
            total_compressed = 0

            with st.spinner(f"Compressing {len(uploaded_images)} image(s)..."):
                for img_file in uploaded_images:
                    img_raw = img_file.getvalue()
                    total_original += len(img_raw)

                    compressed_buf = compress_image(io.BytesIO(img_raw), quality)
                    comp_raw = compressed_buf.getvalue()
                    total_compressed += len(comp_raw)

                    compressed_name = f"compressed_{img_file.name.rsplit('.', 1)[0]}.jpg"
                    compressed_results.append((compressed_name, comp_raw))

            st.success(f"🎉 Compression Successful for {len(compressed_results)} image(s)!")

            if total_original > 0:
                overall_reduction = ((total_original - total_compressed) / total_original) * 100
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Original", f"{total_original / 1024:.2f} KB")
                c2.metric("Total Compressed", f"{total_compressed / 1024:.2f} KB")
                c3.metric("Overall Reduction", f"{overall_reduction:.1f}%")

            st.markdown("### 📦 Compressed Files")
            for (f_name, f_bytes), src_img in zip(compressed_results, uploaded_images):
                col1, col2 = st.columns(2)
                with col1:
                    st.image(io.BytesIO(src_img.getvalue()), caption="Original", use_container_width=True)
                with col2:
                    st.image(io.BytesIO(f_bytes), caption="Compressed", use_container_width=True)

                st.info(f"📄 {f_name} — {len(f_bytes) / 1024:.2f} KB")
                st.download_button(
                    label=f"📥 Download {f_name}",
                    data=f_bytes,
                    file_name=f_name,
                    mime="image/jpeg",
                    key=f"dl_img_{f_name}"
                )
                st.markdown("---")

            if len(compressed_results) > 0:
                zip_buf = create_zip_from_files(compressed_results)
                st.download_button(
                    label="🗂️ Download All Compressed Images as ZIP",
                    data=zip_buf.getvalue(),
                    file_name="compressed_images.zip",
                    mime="application/zip",
                    key="dl_img_zip"
                )

elif conversion_type == "🔽 Compress PDF":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Compress PDFs (Maximum Reduction!)")
    st.markdown("Compress multiple PDFs at once by reducing image quality inside them. Low level = smallest files!")
    st.markdown("</div>", unsafe_allow_html=True)

    uploaded_pdfs = st.file_uploader("Upload PDF Files (single or multiple)", type=["pdf"], accept_multiple_files=True)

    if uploaded_pdfs:
        st.info(f"✅ {len(uploaded_pdfs)} PDF(s) selected.")

        for idx, pdf_file in enumerate(uploaded_pdfs):
            pdf_file.seek(0)
            orig_size = get_file_size(pdf_file)
            st.markdown(f"- 📄 **{pdf_file.name}** — Original: **{orig_size}**")

        quality = st.select_slider("Compression Level", options=["high", "medium", "low"], value="low",
                                   help="Low = Maximum compression (smallest file size)")

        if st.button("Compress All PDFs"):
            compressed_results = []
            total_original = 0
            total_compressed = 0
            total_reduction_positive = 0

            with st.spinner(f"Compressing {len(uploaded_pdfs)} PDF(s)... This may take a moment for large files."):
                for pdf_file in uploaded_pdfs:
                    pdf_raw = pdf_file.getvalue()
                    orig_bytes = len(pdf_raw)
                    total_original += orig_bytes

                    compressed_buf = compress_pdf(io.BytesIO(pdf_raw), quality)
                    compressed_raw = compressed_buf.getvalue()
                    comp_bytes = len(compressed_raw)
                    total_compressed += comp_bytes

                    if comp_bytes < orig_bytes:
                        total_reduction_positive += 1

                    compressed_name = f"compressed_{pdf_file.name}"
                    compressed_results.append((compressed_name, compressed_buf.getvalue(), orig_bytes, comp_bytes))

            st.success(f"🎉 Compression Finished for {len(compressed_results)} PDF(s)!")

            if total_original > 0:
                overall_reduction = ((total_original - total_compressed) / total_original) * 100
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Original", f"{total_original / (1024 * 1024):.2f} MB")
                c2.metric("Total Compressed", f"{total_compressed / (1024 * 1024):.2f} MB")
                c3.metric("Overall Reduction", f"{overall_reduction:.1f}%")

            st.markdown("### 📦 Individual Results")
            for f_name, f_bytes, orig_b, comp_b in compressed_results:
                red_percent = ((orig_b - comp_b) / orig_b) * 100 if orig_b > 0 else 0
                colA, colB, colC = st.columns(3)
                colA.info(f"📄 {f_name}")
                colB.info(f"Size: {orig_b / 1024:.1f} KB → {comp_b / 1024:.1f} KB")
                if red_percent > 0:
                    colC.success(f"Reduced by {red_percent:.1f}%")
                else:
                    colC.warning("Already optimized")

                st.download_button(
                    label=f"📥 Download {f_name}",
                    data=f_bytes,
                    file_name=f_name,
                    mime="application/pdf",
                    key=f"dl_pdf_{f_name}"
                )
                st.markdown("---")

            if len(compressed_results) > 0:
                zip_pairs = [(name, data) for name, data, _, _ in compressed_results]
                zip_buf = create_zip_from_files(zip_pairs)
                st.download_button(
                    label="🗂️ Download All Compressed PDFs as ZIP",
                    data=zip_buf.getvalue(),
                    file_name="compressed_pdfs.zip",
                    mime="application/zip",
                    key="dl_pdf_zip"
                )

elif conversion_type == "🧹 Remove Watermark from Images":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Remove Watermark from Images")
    st.markdown("Automatically remove light / white / semi-transparent watermarks from one or multiple images using AI-free inpainting.")
    st.markdown("</div>", unsafe_allow_html=True)

    uploaded_imgs = st.file_uploader(
        "Upload Images (single or multiple)",
        type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
        accept_multiple_files=True
    )

    if uploaded_imgs:
        st.info(f"✅ {len(uploaded_imgs)} image(s) selected.")

        tolerance = st.slider(
            "Watermark Detection Sensitivity",
            min_value=5, max_value=80, value=30,
            help="Higher value = more aggressive detection (removes larger range of bright pixels). Lower = conservative."
        )
        inpaint_radius = st.slider(
            "Inpaint Radius (smoothness)",
            min_value=1, max_value=15, value=5,
            help="Larger radius = smoother blending around detected watermark."
        )

        for idx, f in enumerate(uploaded_imgs):
            raw = f.getvalue()
            size_kb = len(raw) / 1024
            size_str = f"{size_kb:.2f} KB" if size_kb < 1024 else f"{size_kb / 1024:.2f} MB"
            with st.expander(f"🖼️ {f.name} — {size_str}", expanded=(idx == 0)):
                st.image(io.BytesIO(raw), caption=f"Original: {f.name}", use_container_width=True)

        if st.button("Remove Watermark from All"):
            results = []
            with st.spinner(f"Processing {len(uploaded_imgs)} image(s)..."):
                for f in uploaded_imgs:
                    raw = f.getvalue()
                    cleaned = remove_watermark(
                        io.BytesIO(raw),
                        tolerance=tolerance,
                        inpaint_radius=inpaint_radius
                    )
                    base = f.name.rsplit(".", 1)[0]
                    out_name = f"no_watermark_{base}.png"
                    results.append((out_name, raw, cleaned))

            success_count = sum(1 for _, _, c in results if c is not None)
            if success_count == 0:
                st.error("❌ Could not process any image. Please try a different format.")
            else:
                st.success(f"🎉 Processed {success_count}/{len(results)} image(s).")

                st.markdown("### 📦 Results")
                for f_name, orig_bytes, clean_bytes in results:
                    if clean_bytes is None:
                        st.warning(f"⚠️ Skipped {f_name} — unsupported format or read error.")
                        continue
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(io.BytesIO(orig_bytes), caption="Original", use_container_width=True)
                    with col2:
                        st.image(io.BytesIO(clean_bytes), caption="Watermark Removed", use_container_width=True)
                    st.info(f"📄 {f_name} — Output: {len(clean_bytes) / 1024:.2f} KB")
                    st.download_button(
                        label=f"📥 Download {f_name}",
                        data=clean_bytes,
                        file_name=f_name,
                        mime="image/png",
                        key=f"dl_wm_{f_name}"
                    )
                    st.markdown("---")

                ok_results = [(n, c) for n, _o, c in results if c is not None]
                if ok_results:
                    zip_b = create_zip_from_files(ok_results)
                    st.download_button(
                        label="🗂️ Download All as ZIP",
                        data=zip_b.getvalue(),
                        file_name="no_watermark_images.zip",
                        mime="application/zip",
                        key="dl_wm_zip"
                    )

# Footer
st.markdown("""
<div class="footer">
    <p>Created with ❤️ for learners. DK File Converter © 2024</p>
</div>
""", unsafe_allow_html=True)
