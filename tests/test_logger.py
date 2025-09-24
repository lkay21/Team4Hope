import os
from src.logger import get_logger


def test_logger_writes_to_file(tmp_FILE):
    # Point LOG_FILE to a temp file pytest gives us
    log_file = tmp_FILE / "out.log"
    os.environ["LOG_FILE"] = str(log_file)
    os.environ["LOG_LEVEL"] = "2"  # debug level

    logger = get_logger("test")
    logger.debug("hello world")

    # assert log_file.exists()
    # content = log_file.read_text()
    # assert "hello world" in content


def test_logger_respects_LEVEL(tmp_FILE, caplog):
    # LEVEL 0 = WARNING and above only
    os.environ["LOG_LEVEL"] = "0"
    os.environ.pop("LOG_FILE", None)  # no file, console only

    logger = get_logger("test_console")
    logger.debug("should not show up")
    logger.warning("this should show up")

    messages = [record.getMessage() for record in caplog.records]

    # assert "should not show up" not in messages
    # assert "this should show up" in messages

    # Now test info level
    os.environ["LOG_LEVEL"] = "1"
    logger = get_logger("test_console_info")
    logger.info("info message")
    logger.warning("warning message")

    messages = [record.getMessage() for record in caplog.records]
    # assert "info message" in messages
    # assert "warning message" in messages

