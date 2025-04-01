"""
Utility functions for the Butterfly project.
"""

import os
from typing import List

def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory (str): Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_pdf_files(directory: str) -> List[str]:
    """
    Get all PDF files in a directory.
    
    Args:
        directory (str): Path to the directory
        
    Returns:
        List[str]: List of PDF file paths
    """
    return [os.path.join(directory, f) for f in os.listdir(directory) 
            if f.lower().endswith('.pdf')] 