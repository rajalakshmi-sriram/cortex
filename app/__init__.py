"""
Cortex Application Package
Brain Research Methodology Platform
"""

__version__ = "1.0.0"
__author__ = "Raja Lakshmi Sriram"
__description__ = "A comprehensive platform for validating and guiding neuroscience research"

from app.logger import logger

logger.info(f"Cortex v{__version__} loaded")
