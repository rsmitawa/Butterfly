"""
PDF processing functions for converting PDFs to JPEG images.
"""

import os
import fitz  # PyMuPDF

def pdf_to_jpeg(pdf_path):
    """
    Convert a PDF file to JPEG images.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        list: List of paths to generated JPEG images, or None if there's an error
    """
    try:
        doc = fitz.open(pdf_path)  # Open document
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return None  # Skip processing if there's an error opening the PDF

    resolution_dpi = 300  # Higher DPI gives better quality
    zoom = resolution_dpi / 72  # Default PDF resolution is 72 DPI
    matrix = fitz.Matrix(zoom, zoom)  # Scaling matrix

    # Extract base name
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    # Set output directory for OCR images
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'ocr_images')
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    output_images = []  # List to store paths of generated images

    try:
        for page_num in range(len(doc)):
            page = doc[page_num]  # Get page
            pix = page.get_pixmap(matrix=matrix)  # Render page to image
            
            # Output file path (page_1, page_2, etc. if multi-page)
            output_file_path = os.path.join(output_dir, f"{base_name}_page_{page_num + 1}.jpeg")
            
            pix.save(output_file_path)  # Save image
            output_images.append(output_file_path)  # Store file path
            print(f"Converted PDF Page {page_num + 1} to JPEG: {output_file_path}")

    except fitz.fitz.MuPDFError as e:
        print(f"MuPDF error while processing {pdf_path}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while converting PDF to JPEG: {e}")
        return None
        
    return output_images 