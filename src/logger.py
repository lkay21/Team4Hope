import logging
import os


def get_logger(name: str = "team4hope") -> logging.Logger:
    """Configure and return a logger that respects env variables."""
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured
        return logger

    verbosity = int(os.getenv("LOG_VERBOSITY", "0"))
    log_path = os.getenv("LOG_PATH")

    level = logging.WARNING  # default
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler if LOG_PATH is set
    if log_path:
        fh = logging.FileHandler(log_path)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
