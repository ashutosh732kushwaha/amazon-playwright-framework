"""Centralized Loguru setup."""
from pathlib import Path
from loguru import logger

LOG_DIR = Path(__file__).resolve().parents[1] / "reports" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logger.remove()
logger.add(lambda message: print(message, end=""), format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
           colorize=False, level="INFO")
logger.add(LOG_DIR / "framework.log", rotation="10 MB", retention="10 days", compression="zip",
           enqueue=True, backtrace=False, diagnose=False)

__all__ = ["logger"]

