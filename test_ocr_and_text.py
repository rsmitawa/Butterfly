import os
from src.pdf_processor import pdf_to_jpeg
import pytesseract
from PIL import Image

# Directory containing sample PDFs
data_dir = os.path.join(os.path.dirname(__file__), 'data', 'raw')

# List all PDF files in the directory
pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]

for pdf_file in pdf_files:
    pdf_path = os.path.join(data_dir, pdf_file)
    print(f"\nProcessing: {pdf_path}")
    image_paths = pdf_to_jpeg(pdf_path)
    if image_paths:
        print(f"Generated {len(image_paths)} JPEG(s):")
        for img_path in image_paths:
            print(f"  - {img_path}")
            # OCR step
            try:
                img = Image.open(img_path)
                text = pytesseract.image_to_string(img)
                print(f"--- OCR Text from {os.path.basename(img_path)} ---\n{text}\n---------------------")
            except Exception as e:
                print(f"OCR failed for {img_path}: {e}")
    else:
        print("Failed to convert PDF to JPEG.")

print("\nManual inspection: Please check the extracted text above and compare to the original PDF for OCR accuracy.")
