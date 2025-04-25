import sys
import os
import json
from PIL import Image
import pytesseract
import numpy as np
from src.butterfly.visualization.ocr_visualizer import OCRVisualizer

try:
    import fitz  # PyMuPDF
except ImportError:
    print("[ERROR] PyMuPDF (fitz) is required. Install with: pip install pymupdf")
    sys.exit(1)

# Optional: Try to import pymongo for MongoDB saving
try:
    from pymongo import MongoClient
    HAS_MONGO = True
except ImportError:
    HAS_MONGO = False
    print("[Warning] pymongo not installed. OCR results will not be saved to MongoDB.")

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
            text_regions.append({
                "bbox": [x, y, x + w, y + h],
                "text": data['text'][i],
                "conf": int(data['conf'][i])
            })
    return text_regions

def main():
    if len(sys.argv) < 2:
        print("Usage: python ocr_visual.py <pdf_path>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        sys.exit(1)
    images = pdf_to_images(pdf_path)
    output_dir = "ocr_visualization_output"
    os.makedirs(output_dir, exist_ok=True)
    visualizer = OCRVisualizer()
    ocr_results = {
        "pdf_file": pdf_path,
        "pages": []
    }
    for i, img in enumerate(images):
        text_regions = extract_ocr_data(img)
        # Sort regions top-to-bottom, then left-to-right
        text_regions = sorted(text_regions, key=lambda r: (r['bbox'][1], r['bbox'][0]))
        page_text = ' '.join([region['text'] for region in text_regions])
        img_np = np.array(img)
        out_path = os.path.join(output_dir, f"page_{i+1}_ocr.png")
        visualizer.draw_ocr_results(img_np, [(tuple(region['bbox']), region['text']) for region in text_regions], output_path=out_path)
        print(f"[Saved visualization to {out_path}]")
        ocr_results["pages"].append({
            "page_number": i+1,
            "text": page_text,
            "regions": text_regions,
            "visualization_path": out_path
        })
    # Save structured output
    json_out = os.path.splitext(os.path.basename(pdf_path))[0] + "_ocr.json"
    json_path = os.path.join(output_dir, json_out)
    with open(json_path, "w") as f:
        json.dump(ocr_results, f, indent=2)
    print(f"[Saved structured OCR output to {json_path}]")

    # Save to MongoDB if pymongo is available
    if HAS_MONGO:
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["butterfly"]
            collection = db["ocr_results"]
            # Remove _id if present to avoid duplicate key error
            ocr_results.pop('_id', None)
            # Remove visualization_path from each page (optional, or keep if needed)
            # for page in ocr_results['pages']:
            #     page.pop('visualization_path', None)
            collection.insert_one(ocr_results)
            print(f"[Saved OCR output to MongoDB: butterfly.ocr_results]")
        except Exception as e:
            print(f"[Warning] Failed to save to MongoDB: {e}")

if __name__ == "__main__":
    main()
