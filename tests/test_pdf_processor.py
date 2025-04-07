import pytest
from pathlib import Path
from butterfly.core.pdf_processor import PDFProcessor

def test_pdf_processor_initialization():
    processor = PDFProcessor()
    assert processor.resolution_dpi == 300
    assert processor.zoom == 300/72
    assert processor.reader is not None

def test_pdf_processor_custom_dpi():
    processor = PDFProcessor(resolution_dpi=600)
    assert processor.resolution_dpi == 600
    assert processor.zoom == 600/72
    assert processor.reader is not None 