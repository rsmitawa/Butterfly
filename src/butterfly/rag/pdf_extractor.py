import os
import fitz
from pymongo import MongoClient
from typing import Dict, List
import json
from datetime import datetime

class PDFDataExtractor:
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017/", db_name: str = "pdf_rag"):
        """Initialize the PDF data extractor with MongoDB connection."""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.invoices = self.db.invoices
        self.qa_pairs = self.db.qa_pairs
        self.current_filename = None
    
    def extract_invoice_data(self, pdf_path: str) -> Dict:
        """Extract structured data from an invoice PDF using both regular extraction and OCR if needed."""
        import cv2
        import numpy as np
        import pytesseract
        from PIL import Image
        
        doc = fitz.open(pdf_path)
        invoice_data = {
            "filename": os.path.basename(pdf_path),
            "extraction_date": datetime.now(),
            "pages": []
        }
        
        for page_num, page in enumerate(doc):
            # Try regular text extraction first
            text = page.get_text()
            
            # If regular extraction yields little or no text, try OCR
            if len(text.strip()) < 50:  # Threshold for minimum text length
                # Get page as image
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # 300 DPI
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Convert to cv2 format for preprocessing
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                # Preprocess image
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                
                # Apply OCR
                text = pytesseract.image_to_string(thresh)
                print(f"Used OCR for page {page_num + 1} of {os.path.basename(pdf_path)}")
            
            # Process extracted text
            lines = text.split('\n')
            page_data = {
                "page_number": page_num + 1,
                "content": text,
                "extraction_method": "ocr" if len(page.get_text().strip()) < 50 else "regular",
                "metadata": {
                    "customer_name": self._extract_customer_name(lines),
                    "invoice_number": self._extract_invoice_number(lines),
                    "date": self._extract_date(lines),
                    "amount": self._extract_amount(lines)
                }
            }
            invoice_data["pages"].append(page_data)
        
        return invoice_data
    
    def _extract_customer_name(self, lines: List[str]) -> str:
        """Extract customer name from invoice lines."""
        # Try different patterns for customer name
        patterns = ["Customer:", "Name:", "Client:"]
        for line in lines:
            for pattern in patterns:
                if pattern in line:
                    return line.split(pattern)[1].strip()
        
        # If no pattern found, try to extract from filename
        filename = self.current_filename
        if filename:
            parts = filename.split('_')
            if len(parts) >= 2:
                return parts[1].replace('.pdf', '')
        return "Unknown"
    
    def _extract_invoice_number(self, lines: List[str]) -> str:
        """Extract invoice number from invoice lines."""
        patterns = ["Invoice #", "Invoice:", "Invoice Number:", "INV-"]
        for line in lines:
            for pattern in patterns:
                if pattern in line:
                    return line.split(pattern)[1].strip()
        
        # If no pattern found, try to extract from filename
        filename = self.current_filename
        if filename:
            parts = filename.split('_')
            if len(parts) >= 3:
                return parts[2].replace('.pdf', '')
        return "Unknown"
    
    def _extract_date(self, lines: List[str]) -> str:
        """Extract date from invoice lines."""
        patterns = ["Date:", "Invoice Date:", "Issued:", "Created:"]
        for line in lines:
            for pattern in patterns:
                if pattern in line:
                    date_str = line.split(pattern)[1].strip()
                    try:
                        # Try to parse and standardize the date format
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        return date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        return date_str
        return "Unknown"
    
    def _extract_amount(self, lines: List[str]) -> float:
        """Extract total amount from invoice lines."""
        patterns = ["Total:", "Amount:", "Invoice Total:", "Balance Due:"]
        for line in lines:
            for pattern in patterns:
                if pattern in line:
                    amount_str = line.split(pattern)[1].strip()
                    # Remove currency symbols and commas
                    amount_str = amount_str.replace('$', '').replace(',', '')
                    try:
                        return float(amount_str)
                    except ValueError:
                        continue
        return 0.0
    
    def process_directory(self, directory_path: str):
        """Process all PDFs in a directory and store in MongoDB."""
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                self.current_filename = filename
                pdf_path = os.path.join(directory_path, filename)
                try:
                    invoice_data = self.extract_invoice_data(pdf_path)
                    self.invoices.insert_one(invoice_data)
                    print(f"Processed {filename}")
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                finally:
                    self.current_filename = None
    
    def store_qa_pair(self, question: str, answer: str, sources: List[str]):
        """Store a question-answer pair with its sources."""
        qa_data = {
            "question": question,
            "answer": answer,
            "sources": sources,
            "timestamp": datetime.now()
        }
        self.qa_pairs.insert_one(qa_data)
    
    def export_qa_pairs(self, output_file: str):
        """Export all QA pairs to a JSON file."""
        qa_pairs = list(self.qa_pairs.find({}, {"_id": 0}))
        with open(output_file, 'w') as f:
            json.dump(qa_pairs, f, indent=2, default=str)
    
    def close(self):
        """Close MongoDB connection."""
        self.client.close()

def main():
    # Initialize the extractor
    extractor = PDFDataExtractor()
    
    try:
        # Process PDFs in the data/raw directory
        extractor.process_directory("data/raw")
        
        # Example QA pairs (you can add more)
        test_questions = [
            "Find all invoices for Aaron Hawkins",
            "What's the total amount across all invoices?",
            "Compare the invoice amounts between Aaron Hawkins and Aaron Bergman"
        ]
        
        # Store test QA pairs
        for question in test_questions:
            # In a real scenario, you would get the answer from your RAG system
            answer = "Sample answer"
            sources = ["invoice_Aaron_Hawkins_4820.pdf"]
            extractor.store_qa_pair(question, answer, sources)
        
        # Export QA pairs to JSON
        extractor.export_qa_pairs("data/qa_pairs.json")
        
    finally:
        extractor.close()

if __name__ == "__main__":
    main() 