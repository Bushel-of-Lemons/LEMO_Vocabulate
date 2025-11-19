"""
LEMO Vocabulate - Dictionary-based text analysis tool
"""

from .core import run_vocabulate_analysis
import os
from pathlib import Path

def get_data_path(filename):
    """
    Get the full path to a data file included with the package.
    
    Parameters:
    -----------
    filename : str
        Name of the data file (e.g., 'AEV_Dict.csv', 'stopwords.txt')
    
    Returns:
    --------
    str : Full path to the data file
    """
    package_dir = Path(__file__).parent
    data_path = package_dir / 'data' / filename
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {filename}")
    
    return str(data_path)

__version__ = "0.1.0"
__all__ = ['run_vocabulate_analysis', 'get_data_path']