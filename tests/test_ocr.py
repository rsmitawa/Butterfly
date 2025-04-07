import os
import pytest
from butterfly.rag.pdf_extractor import PDFDataExtractor
from PIL import Image
import pytesseract

def test_text_extraction():
    """Test text extraction from both digital and scanned PDFs."""
    extractor = PDFDataExtractor()
    
    # Test directory
    test_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
    
    # Test each PDF in the directory
    for filename in os.listdir(test_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(test_dir, filename)
            print(f"\nTesting {filename}:")
            
            # Extract using regular method
            regular_data = extractor.extract_invoice_data(pdf_path)
            
            # Print extraction results
            print("Regular Extraction Results:")
            for page in regular_data['pages']:
                content = page['content'].strip()
                if content:
                    print(f"Page {page['page_number']} - First 100 chars: {content[:100]}")
                    print(f"Metadata: {page['metadata']}")
                else:
                    print(f"Page {page['page_number']} - No text extracted")
            
            # Basic validation
            assert regular_data['filename'] == filename
            assert len(regular_data['pages']) > 0
            assert any(page['content'].strip() for page in regular_data['pages']), "No text extracted from PDF"

if __name__ == '__main__':
    pytest.main([__file__])
