"""
Logging configuration for Cortex app
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

def setup_logger(name, log_file=None):
    """
    Setup logger with file and console handlers
    
    Args:
        name (str): Logger name
        log_file (str): Path to log file (optional)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    logger.addHandler(console_handler)
    
    return logger


# Create app logger
logger = setup_logger(
    'cortex',
    log_file='/Users/rajalakshmisriram/cortex/logs/cortex.log'
)
