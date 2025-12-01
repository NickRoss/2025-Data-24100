"""Custom Logger for use in this project

Contains the setup for the custom logger
"""

import logging


def setup_logging():
    """Set up logging and return the custom logger"""
    logger = logging.getLogger("flask_app")
    if not logger.handlers:  # Prevent duplicate handlers
        logger.setLevel(logging.INFO)  # set level to track, can be overwritten
        handler = logging.StreamHandler()
        log_format = "%(asctime)s | %(levelname)s | %(message)s"
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


custom_logger = setup_logging()
