import pytest
from pathlib import Path
from butterfly.visualization.ocr_visualizer import OCRVisualizer

def test_ocr_visualizer_initialization():
    visualizer = OCRVisualizer()
    assert visualizer.font_size == 22
    assert visualizer.font is not None

def test_ocr_visualizer_custom_font_size():
    visualizer = OCRVisualizer(font_size=30)
    assert visualizer.font_size == 30
    assert visualizer.font is not None 