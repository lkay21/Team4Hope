import logging
import os
import sys

def get_logger(name: str = "team4hope") -> logging.Logger:
    """Configure and return a logger that respects env variables."""
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        logger.handlers.clear()

    log_level_env = int(os.getenv("LOG_LEVEL", "0"))
    log_file = os.getenv("LOG_FILE")
    
    if log_file and os.path.dirname(log_file):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    try:
        level = int(log_level_env)
    except ValueError:
        level = logging.WARNING

    if level <= 0:
        logger.setLevel(logging.CRITICAL + 1)
    elif level == 1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Console handler
    # if level > 0:
    #     ch = logging.StreamHandler()
    #     ch.setLevel(logger.level)
    #     ch.setFormatter(formatter)
    #     logger.addHandler(ch)

    # File handler
    if log_file and level > 0:
        fh = logging.FileHandler(log_file)
        fh.setLevel(logger.level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger
