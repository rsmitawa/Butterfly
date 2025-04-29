import os
import fitz
from pymongo import MongoClient
from typing import Dict, List
import json
from datetime import datetime

class PDFDataExtractor:
    def __init__(self, mongo_uri: str = "mongodb://mongodb:27017/", db_name: str = "pdf_rag"): 
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
            items = self.extract_line_items(lines)
            page_data = {
                "page_number": page_num + 1,
                "content": text,
                "extraction_method": "ocr" if len(page.get_text().strip()) < 50 else "regular",
                "metadata": {
                    "customer_name": self._extract_customer_name(lines),
                    "invoice_number": self._extract_invoice_number(lines),
                    "date": self._extract_date(lines),
                    "amount": self._extract_amount(lines),
                    "items": items
                }
            }
            invoice_data["pages"].append(page_data)
        
        return invoice_data

    def extract_line_items(self, lines: list) -> list:
        """Extract structured line items from invoice lines."""
        items = []
        in_items_section = False
        for i, line in enumerate(lines):
            # Heuristic: look for start of line items section
            if ("Item" in line and "Quantity" in line and "Rate" in line and "Amount" in line):
                in_items_section = True
                continue
            if in_items_section:
                # Stop at subtotal, total, or empty line
                if any(stop_word in line for stop_word in ["Subtotal", "Total", "Notes", "Terms", "Shipping", "Discount"]):
                    break
                parts = line.split()
                # Heuristic: look for lines with at least 3 columns (item, quantity, price)
                if len(parts) >= 3:
                    try:
                        # Try to parse quantity and price from the end
                        quantity = float(parts[-3]) if parts[-3].replace('.', '', 1).isdigit() else None
                        unit_price = float(parts[-2].replace('$', '')) if parts[-2].replace('.', '', 1).replace('$', '').isdigit() else None
                        amount = float(parts[-1].replace('$', '')) if parts[-1].replace('.', '', 1).replace('$', '').isdigit() else None
                        item_name = ' '.join(parts[:-3])
                        items.append({
                            "item": item_name,
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "amount": amount
                        })
                    except Exception:
                        continue
        return items

    def export_invoices_to_json(self, directory_path: str, output_file: str):
        """Extract and export all invoices in a directory to a JSON file (no MongoDB required)."""
        all_invoices = []
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(directory_path, filename)
                try:
                    invoice_data = self.extract_invoice_data(pdf_path)
                    all_invoices.append(invoice_data)
                except Exception as e:
                    print(f"Error extracting {filename}: {str(e)}")
        # Convert datetimes to string
        def convert(o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, dict):
                return {k: convert(v) for k, v in o.items()}
            if isinstance(o, list):
                return [convert(i) for i in o]
            return o
        with open(output_file, 'w') as f:
            json.dump([convert(inv) for inv in all_invoices], f, indent=2)

    
    def _extract_customer_name(self, lines: List[str]) -> str:
        """Extract customer name from invoice lines using heuristics and filename."""
        # Heuristic: Look for 'Bill To:' and take the next non-empty line
        for idx, line in enumerate(lines):
            if 'Bill To:' in line:
                # Look ahead for the next non-empty line
                for next_line in lines[idx+1:idx+3]:
                    candidate = next_line.strip()
                    if candidate and not candidate.lower().startswith(('ship to', 'date', 'same day', 'standard class')):
                        return candidate
        # Fallback to filename
        filename = getattr(self, 'current_filename', None)
        if filename:
            parts = filename.split('_')
            if len(parts) >= 2:
                return parts[1].replace('.pdf', '')
        return "Unknown"
    
    def _extract_invoice_number(self, lines: List[str]) -> str:
        """Extract invoice number from invoice lines using heuristics and filename."""
        import re
        # Look for lines like '# 36397' or 'Invoice # 36397'
        for line in lines:
            match = re.search(r'#\s*(\d+)', line)
            if match:
                return match.group(1)
        # Fallback to filename
        filename = getattr(self, 'current_filename', None)
        if filename:
            parts = filename.split('_')
            if len(parts) >= 3:
                num = parts[2].replace('.pdf', '')
                if num.isdigit():
                    return num
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
        """Extract the correct total amount from invoice lines using invoice-specific heuristics."""
        import re
        # 1. Look for a line with 'Total:' and a $ amount
        for line in lines:
            if 'Total:' in line:
                found = re.findall(r'\$([0-9]+\.[0-9]{2})', line)
                if found:
                    return float(found[0])
        # 2. Look for the last $ amount before 'Notes' or 'Thanks'
        for idx, line in enumerate(lines):
            if 'Notes' in line or 'Thanks' in line:
                for prev_line in reversed(lines[:idx]):
                    found = re.findall(r'\$([0-9]+\.[0-9]{2})', prev_line)
                    if found:
                        return float(found[0])
        # 3. Fallback: largest amount
        amounts = []
        for line in lines:
            found = re.findall(r'\$([0-9]+\.[0-9]{2})', line)
            for amt in found:
                try:
                    amounts.append(float(amt))
                except Exception:
                    continue
        if amounts:
            return max(amounts)
        return 0.0
    
    def process_directory(self, directory_path: str):
        """Process all PDFs in a directory and store in MongoDB."""
        print("DEBUG: Files in directory:", os.listdir(directory_path))
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                self.current_filename = filename
                pdf_path = os.path.join(directory_path, filename)
                try:
                    invoice_data = self.extract_invoice_data(pdf_path)
                    print(f"\n===== {filename} =====")
                    for page in invoice_data["pages"]:
                        print(f"Page {page['page_number']} ({page['extraction_method']}):\n{page['content']}\n{'-'*40}")
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
        print(f"Stored QA pair: {question}")
    
    def export_qa_pairs(self, output_file: str):
        """Export QA pairs to JSON, converting ObjectId and datetime fields to strings."""
        from bson import ObjectId
        from datetime import datetime
        def convert(o):
            if isinstance(o, ObjectId):
                return str(o)
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, dict):
                return {k: convert(v) for k, v in o.items()}
            if isinstance(o, list):
                return [convert(i) for i in o]
            return o
        qa_pairs = list(self.qa_pairs.find())
        qa_pairs = [convert(doc) for doc in qa_pairs]
        with open(output_file, 'w') as f:
            json.dump(qa_pairs, f, indent=2)

    
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
            # In a real scenario, you would get the answer from your PDFRAGSystem(embedding_model="nomic-embed-text")
            answer = "Sample answer"
            sources = ["invoice_Aaron_Hawkins_4820.pdf"]
            extractor.store_qa_pair(question, answer, sources)
        
        # Export QA pairs to JSON
        extractor.export_qa_pairs("data/qa_pairs.json")
        
    finally:
        extractor.close()

if __name__ == "__main__":
    # For local testing: extract and export all invoices to JSON (no MongoDB required)
    extractor = PDFDataExtractor()
    extractor.export_invoices_to_json("data/raw", "data/invoice_data.json")
    print("Exported structured invoice data to data/invoice_data.json")