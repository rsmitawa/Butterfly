import os
from src.pdf_processor import pdf_to_jpeg

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
        for img in image_paths:
            print(f"  - {img}")
    else:
        print("Failed to convert PDF to JPEG.")

print("\nManual inspection: Please open the generated JPEGs and compare them to the original PDFs to verify OCR image quality.")
