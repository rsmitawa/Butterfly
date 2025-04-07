import os
import fitz
from pathlib import Path
import easyocr
from typing import List, Dict, Optional, Any
import json
from tqdm import tqdm
from PIL import Image
import io
import cv2
import numpy as np
import pytesseract

class PDFProcessor:
    def __init__(self):
        """Initialize the PDF processor."""
        # Set Tesseract path for macOS
        pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
    
    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Convert a PDF file to a list of PIL Images.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of PIL Images, one for each page
        """
        images = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # 300 DPI
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        
        doc.close()
        return images
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image: PIL Image to preprocess
            
        Returns:
            Preprocessed image as numpy array
        """
        # Convert to numpy array
        img = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened
    
    def perform_ocr(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Perform OCR on an image using Tesseract.
        
        Args:
            image: PIL Image to process
            
        Returns:
            List of dictionaries containing OCR results
        """
        # Preprocess the image
        processed_img = self.preprocess_image(image)
        
        # Perform OCR with Tesseract
        ocr_data = pytesseract.image_to_data(
            processed_img,
            output_type=pytesseract.Output.DICT,
            config='--psm 6'  # Assume uniform block of text
        )
        
        # Convert to our format
        results = []
        n_boxes = len(ocr_data['text'])
        for i in range(n_boxes):
            if int(ocr_data['conf'][i]) > 60:  # Confidence threshold
                results.append({
                    'text': ocr_data['text'][i],
                    'bbox': {
                        'x': ocr_data['left'][i],
                        'y': ocr_data['top'][i],
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i]
                    },
                    'confidence': float(ocr_data['conf'][i]) / 100.0
                })
        
        return results
    
    def save_ocr_results(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        Save OCR results to a JSON file.
        
        Args:
            results: List of OCR results
            output_path: Path to save the JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

    def process_directory(self, pdf_directory: str) -> None:
        """
        Process all PDF files in a directory.
        
        Args:
            pdf_directory: Path to directory containing PDF files
        """
        if not os.path.isdir(pdf_directory):
            print(f"Directory '{pdf_directory}' does not exist.")
            return

        for filename in os.listdir(pdf_directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                print(f"Processing {pdf_path}...")
                converted_images = self.pdf_to_images(pdf_path)
                if converted_images:
                    print(f"All pages converted successfully for {pdf_path}!")
                else:
                    print(f"Conversion failed for {pdf_path}.")

    def process_images(self, image_directory: str) -> None:
        """
        Process all JPEG images in a directory with OCR.
        
        Args:
            image_directory: Path to directory containing JPEG images
        """
        image_paths = sorted(list(Path(image_directory).glob("*.jpeg")))
        
        for image_path in tqdm(image_paths, desc="Processing Images"):
            ocr_page = self.perform_ocr(Image.open(image_path))
            
            with image_path.with_suffix(".json").open("w") as f:
                json.dump(ocr_page, f) 