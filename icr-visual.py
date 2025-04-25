import sys
import os
from PIL import Image
import pytesseract
from src.butterfly.visualization.ocr_visualizer import OCRVisualizer
try:
    import fitz  # PyMuPDF
except ImportError:
    print("[ERROR] PyMuPDF (fitz) is required. Install with: pip install pymupdf")
    sys.exit(1)

def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def extract_ocr_data(img):
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    text_regions = []
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 0 and data['text'][i].strip():
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            text_regions.append(((x, y, x + w, y + h), data['text'][i]))
    return text_regions

def main():
    if len(sys.argv) < 2:
        print("Usage: python icr-visual.py <pdf_path>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        sys.exit(1)
    images = pdf_to_images(pdf_path)
    output_dir = "ocr_visualization_output"
    os.makedirs(output_dir, exist_ok=True)
    visualizer = OCRVisualizer()
    for i, img in enumerate(images):
        text_regions = extract_ocr_data(img)
        print(f"\n--- Page {i+1} OCR Text ---")
        print(' '.join([t[1] for t in text_regions]))
        out_path = os.path.join(output_dir, f"page_{i+1}_ocr.png")
        import numpy as np
        img_np = np.array(img)
        visualizer.draw_ocr_results(img_np, text_regions, output_path=out_path)
        print(f"[Saved visualization to {out_path}]")

if __name__ == "__main__":
    main()
