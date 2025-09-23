# src/logger.py
import logging
import os
import sys
from pathlib import Path

def _usable(p: Path) -> bool:
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a"):
            pass
        return True
    except Exception:
        return False

def _pick_log_path() -> Path:
    """
    Priority for tests + autograder:
      1) LOG_FILE        (unit tests set this)
      2) LOG_FILE_PATH   (autograder uses this)
      3) ./log_files/app.log
    """
    env_legacy  = os.getenv("LOG_FILE", "").strip()
    env_primary = os.getenv("LOG_FILE_PATH", "").strip()
    default_path = Path.cwd() / "log_files" / "app.log"

    # Prefer LOG_FILE (unit tests)
    if env_legacy:
        p = Path(env_legacy).expanduser()
        try:
            p = p.resolve()
        except Exception:
            p = Path(env_legacy).expanduser()
        if _usable(p):
            return p

    # Next, LOG_FILE_PATH (autograder)
    if env_primary:
        p = Path(env_primary).expanduser()
        try:
            p = p.resolve()
        except Exception:
            p = Path(env_primary).expanduser()
        if _usable(p):
            return p
        # Warn but continue (expected by autograder)
        print("Invalid LOG_FILE_PATH; using default ./log_files/app.log", file=sys.stderr)

    # Default
    if _usable(default_path):
        return default_path
    return Path.cwd() / "app.log"

def get_logger(name: str = "team4hope") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    # Map LOG_LEVEL: 0=WARNING, 1=INFO, 2+=DEBUG
    raw = os.getenv("LOG_LEVEL", "0")
    try:
        n = int(raw)
    except ValueError:
        n = 0

    if n <= 0:
        level = logging.WARNING
    elif n == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logger.setLevel(level)
    logger.propagate = True  # avoid duplicate prints via root

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Console handler (always attach; level gate is on the logger)
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler (if we can open a path)
    log_path = _pick_log_path()
    try:
        fh = logging.FileHandler(str(log_path))
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:
        # If even fallback fails, just skip file logging—don’t crash
        print("WARNING: Could not open log file; logging to console only.", file=sys.stderr)

    return logger
