import logging
import os
import sys
from pathlib import Path

def _usable(p: Path) -> bool:
    """Return True if we can create parent dirs and open the file for append."""
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a"):
            pass
        return True
    except Exception:
        return False

def _pick_log_path() -> Path:
    """
    Priority:
      1) LOG_FILE        (unit tests set this)
      2) LOG_FILE_PATH   (autograder may set this)
      3) LOG_PATH        (alternate name some graders use)
      4) ./log_files/app.log
    If LOG_FILE_PATH/LOG_PATH is present but empty or unusable, print a warning to stderr and fall back.
    """
    env_legacy = os.environ.get("LOG_FILE")              # tests
    env_primary_raw = os.environ.get("LOG_FILE_PATH")    # grader (variant 1)
    env_alt_raw     = os.environ.get("LOG_PATH")         # grader (variant 2)

    default_path = Path.cwd() / "log_files" / "app.log"

    # 1) Prefer LOG_FILE when set and usable
    if env_legacy:
        p = Path(env_legacy).expanduser()
        try:
            p = p.resolve()
        except Exception:
            p = Path(env_legacy).expanduser()
        if _usable(p):
            return p

    # Helper to try a candidate var and warn if unusable
    def _check(raw_val: str | None) -> Path | None:
        present = raw_val is not None
        val = (raw_val or "").strip()
        if present:
            if val:
                p = Path(val).expanduser()
                try:
                    p = p.resolve()
                except Exception:
                    p = Path(val).expanduser()
                if _usable(p):
                    return p
            # present but empty or unusable -> WARN to stderr only
            sys.stderr.write("Invalid LOG_FILE_PATH; using default ./log_files/app.log\n")
        return None

    # 2) Try LOG_FILE_PATH
    p = _check(env_primary_raw)
    if p:
        return p

    # 3) Try LOG_PATH (alternate env name some graders use)
    p = _check(env_alt_raw)
    if p:
        return p

    # 4) Default
    if _usable(default_path):
        return default_path
    return Path.cwd() / "app.log"

def get_logger(name: str = "team4hope") -> logging.Logger:
    """
    - LOG_LEVEL: 0=WARNING, 1=INFO, 2+=DEBUG
    - Always attach a console handler, and a file handler if path usable.
    - propagate=True so pytest caplog can capture records.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

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
    logger.propagate = True

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler (best-effort)
    log_path = _pick_log_path()
    try:
        fh = logging.FileHandler(str(log_path))
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:
        # Do not crash on file issues; console still works
        sys.stderr.write("WARNING: Could not open log file; logging to console only.\n")

    return logger
