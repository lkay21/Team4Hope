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
    # Accept LOG_FILE_PATH (preferred), then LOG_FILE, then default
    default_path = Path.cwd() / "log_files" / "app.log"

    # Helper to emit exactly one line to **stderr only**
    def _warn(msg: str) -> None:
        try:
            sys.stderr.write(msg + "\n")
        except Exception:
            pass  # never crash on logging warning paths

    # Preferred env
    raw = os.environ.get("LOG_FILE_PATH")
    if raw is not None:  # var is present, even if empty
        raw_s = raw.strip()
        if not raw_s:
            _warn("Invalid LOG_FILE_PATH; using default ./log_files/app.log")
            return default_path
        candidate = Path(raw_s).expanduser()
        try:
            candidate = candidate.resolve()
        except Exception:
            candidate = Path(raw_s).expanduser()
        if _usable(candidate):
            return candidate
        _warn("Invalid LOG_FILE_PATH; using default ./log_files/app.log")
        return default_path

    # Legacy env
    raw_legacy = os.environ.get("LOG_FILE")
    if raw_legacy is not None:
        raw_s = raw_legacy.strip()
        if not raw_s:
            _warn("Invalid LOG_FILE; using default ./log_files/app.log")
            return default_path
        candidate = Path(raw_s).expanduser()
        try:
            candidate = candidate.resolve()
        except Exception:
            candidate = Path(raw_s).expanduser()
        if _usable(candidate):
            return candidate
        _warn("Invalid LOG_FILE; using default ./log_files/app.log")
        return default_path

    # Default path (make it if possible; no warning)
    if _usable(default_path):
        return default_path
    # Last-ditch fallback in cwd (no warning)
    return Path.cwd() / "app.log"

def get_logger(name: str = "team4hope") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    # LOG_LEVEL semantics: 0 = WARNING+, 1 = INFO+, >=2 = DEBUG
    log_level_env = os.getenv("LOG_LEVEL", "0")
    try:
        level_int = int(log_level_env)
    except ValueError:
        level_int = 0

    if level_int <= 0:
        effective_level = logging.WARNING
    elif level_int == 1:
        effective_level = logging.INFO
    else:
        effective_level = logging.DEBUG

    logger.setLevel(effective_level)
    logger.propagate = True  # <- ensure records reach root for caplog

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler (created if path usable)
    log_path = _pick_log_path()
    if log_path:
        try:
            fh = logging.FileHandler(str(log_path))
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception:
            pass  # never crash on log file issues

    return logger
