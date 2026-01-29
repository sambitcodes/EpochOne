"""
Logging configuration for shared use.
"""
import logging
import sys

def setup_logging(level: str = "INFO"):
    """Setup structured logging."""
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )