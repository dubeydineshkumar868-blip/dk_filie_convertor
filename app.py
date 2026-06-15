import streamlit as st
import os
from PIL import Image
import fitz  # PyMuPDF
from pdf2docx import Converter
from docx import Document
from docx.shared import Inches
import pdfplumber
import pandas as pd
import io
import tempfile

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
    /* Main header style */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
    }
    /* Card style for sections */
    .card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin-bottom: 1rem;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102,126,234,0.4);
    }
    /* Success message */
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
    }
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        margin-top: 3rem;
    }
    /* Slider styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
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

# Sidebar for navigation with icons
st.sidebar.title("📋 Tools")
conversion_type = st.sidebar.selectbox(
    "Select what you want to do:",
    [
        "🖼️ Image to PDF",
        "🖼️ Image to Word",
        "📄 PDF to Image", 
        "📝 PDF to Word", 
        "📊 PDF to Excel",
        "📎 Merge PDFs",
        "🔽 Compress Image",
        "🔽 Compress PDF"
    ]
)

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

def image_to_word(uploaded_files):
    """
    Converts a list of images into a single Word document.
    """
    doc = Document()
    for uploaded_file in uploaded_files:
        # Save image to a temporary file because docx needs a file path or stream
        img = Image.open(uploaded_file)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format=img.format if img.format else 'PNG')
        img_buffer.seek(0)
        
        doc.add_picture(img_buffer, width=Inches(6)) # Adjust width as needed
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

def compress_pdf(uploaded_pdf, quality='medium'):
    """
    Compresses a PDF file using PyMuPDF.
    """
    pdf_bytes = uploaded_pdf.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # Define compression levels
    garbage = 4
    deflate = True
    if quality == 'low':
        garbage = 3
    elif quality == 'high':
        garbage = 2
        deflate = False
    
    compressed_buffer = io.BytesIO()
    doc.save(compressed_buffer, garbage=garbage, deflate=deflate)
    compressed_buffer.seek(0)
    
    return compressed_buffer

# Helper function to get file size in human-readable format
def get_file_size(file_obj):
    file_obj.seek(0, 2)  # Seek to end
    size = file_obj.tell()
    file_obj.seek(0)  # Reset to start
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

# Main logic based on selection
if conversion_type == "🖼️ Image to PDF":
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
                    for i, img_data in enumerate(images):
                        st.image(img_data, caption=f"Page {i+1}")
                        st.download_button(
                            label=f"📥 Download Page {i+1} (PNG)",
                            data=img_data,
                            file_name=f"page_{i+1}.png",
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
    st.markdown("Reduce image file size with adjustable quality.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "webp", "bmp"])
    
    if uploaded_image:
        original_size = get_file_size(uploaded_image)
        st.info(f"📏 Original Size: {original_size}")
        
        quality = st.slider("Compression Quality (1-100)", min_value=1, max_value=100, value=85, 
                           help="Lower values = smaller file size but more compression artifacts")
        
        if st.button("Compress Image"):
            with st.spinner("Compressing image..."):
                compressed_data = compress_image(uploaded_image, quality)
                compressed_size = get_file_size(compressed_data)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.image(uploaded_image, caption="Original Image")
                with col2:
                    st.image(compressed_data, caption="Compressed Image")
                
                st.success(f"🎉 Compression Successful!")
                st.info(f"📏 Compressed Size: {compressed_size}")
                
                st.download_button(
                    label="📥 Download Compressed Image",
                    data=compressed_data,
                    file_name=f"compressed_{uploaded_image.name}",
                    mime="image/jpeg"
                )

elif conversion_type == "🔽 Compress PDF":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Compress PDF")
    st.markdown("Reduce PDF file size with adjustable compression levels.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    uploaded_pdf = st.file_uploader("Upload PDF File", type=["pdf"])
    
    if uploaded_pdf:
        original_size = get_file_size(uploaded_pdf)
        st.info(f"📏 Original Size: {original_size}")
        
        quality = st.select_slider("Compression Level", options=["high", "medium", "low"], value="medium",
                                  help="High = Less compression, Low = More compression")
        
        if st.button("Compress PDF"):
            with st.spinner("Compressing PDF..."):
                compressed_data = compress_pdf(uploaded_pdf, quality)
                compressed_size = get_file_size(compressed_data)
                
                st.success(f"🎉 Compression Successful!")
                st.info(f"📏 Compressed Size: {compressed_size}")
                
                st.download_button(
                    label="📥 Download Compressed PDF",
                    data=compressed_data,
                    file_name=f"compressed_{uploaded_pdf.name}",
                    mime="application/pdf"
                )

# Footer
st.markdown("""
<div class="footer">
    <p>Created with ❤️ for learners. DK File Converter © 2024</p>
</div>
""", unsafe_allow_html=True)
