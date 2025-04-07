import os
from pathlib import Path
from typing import List, Optional

def ensure_directory(directory: str) -> None:
    """
    Ensure that a directory exists, create it if it doesn't.
    
    Args:
        directory: Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The file extension (including the dot)
    """
    return os.path.splitext(file_path)[1].lower()

def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
    """
    List files in a directory, optionally filtered by extension.
    
    Args:
        directory: Path to the directory
        extension: Optional file extension to filter by
        
    Returns:
        List of file paths
    """
    if not os.path.isdir(directory):
        return []
        
    files = []
    for filename in os.listdir(directory):
        if extension is None or get_file_extension(filename) == extension:
            files.append(os.path.join(directory, filename))
    return sorted(files)

def get_output_path(input_path: str, suffix: str) -> str:
    """
    Generate an output path by adding a suffix to the input path.
    
    Args:
        input_path: Path to the input file
        suffix: Suffix to add to the filename
        
    Returns:
        The new output path
    """
    path = Path(input_path)
    return str(path.with_name(f"{path.stem}{suffix}{path.suffix}")) 