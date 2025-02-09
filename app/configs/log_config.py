import os
from loguru import logger

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Set up logging configuration
def setup_logger():
    logger.remove()  # Remove default logger
    logger.add(
        "app/logs/app_{time:YYYY-MM-DD}.log", 
        level=LOG_LEVEL, 
        rotation="1 day",  # Rotate log daily
        retention="7 days",  # Keep logs for 7 days
        compression="zip",  # Compress old logs
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra}"
    )
    logger.add(
        "app/logs/app_error_{time:YYYY-MM-DD}.log", 
        level="ERROR", 
        rotation="1 day", 
        retention="7 days", 
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra}"
    )

setup_logger()