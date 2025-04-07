"""
Butterfly - A PDF processing and OCR toolkit.
"""

from .core.pdf_processor import PDFProcessor
from .visualization.ocr_visualizer import OCRVisualizer
from .utils.file_utils import ensure_directory, get_file_extension, list_files, get_output_path

__version__ = "0.1.0"
__all__ = [
    "PDFProcessor",
    "OCRVisualizer",
    "ensure_directory",
    "get_file_extension",
    "list_files",
    "get_output_path",
] 