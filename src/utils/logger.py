"""Logging configuration for the Literature Expert Agent."""

import sys
from pathlib import Path

from loguru import logger

from src.config.settings import settings


def setup_logger(log_file: str = "app.log") -> None:
    """Configure the logger with file and console output."""
    # Ensure logs directory exists
    settings.logs_path.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )

    # Add file handler
    log_path = settings.logs_path / log_file
    logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )

    logger.info(f"Logger initialized. Log file: {log_path}")


# Initialize logger on import
setup_logger()
