import os
import sys

def run_command(cmd, cwd=None):
    print(f"\n[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)


def main():
    # Step 1: Check PDFs exist
    pdf_dir = os.path.join('data', 'raw')
    if not os.path.exists(pdf_dir) or not any(f.endswith('.pdf') for f in os.listdir(pdf_dir)):
        print(f"[ERROR] No PDFs found in {pdf_dir}. Please add PDF files to process.")
        sys.exit(1)
    print(f"[INFO] Found PDFs: {[f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]}")

    # Step 2: Extract and export invoices to JSON using the latest logic
    from src.butterfly.rag.pdf_extractor import PDFDataExtractor
    extractor = PDFDataExtractor()
    extractor.export_invoices_to_json(pdf_dir, os.path.join('data', 'invoice_data.json'))
    print("[INFO] Exported structured invoice data to data/invoice_data.json")


if __name__ == "__main__":
    main()
