import os
from src.logger import get_logger


def test_logger_writes_to_file(tmp_path):
    # Point LOG_PATH to a temp file pytest gives us
    log_file = tmp_path / "out.log"
    os.environ["LOG_PATH"] = str(log_file)
    os.environ["LOG_VERBOSITY"] = "2"  # debug level

    logger = get_logger("test")
    logger.debug("hello world")

    assert log_file.exists()
    content = log_file.read_text()
    assert "hello world" in content


def test_logger_respects_verbosity(tmp_path, caplog):
    # Verbosity 0 = WARNING and above only
    os.environ["LOG_VERBOSITY"] = "0"
    os.environ.pop("LOG_PATH", None)  # no file, console only

    logger = get_logger("test_console")
    logger.debug("should not show up")
    logger.warning("this should show up")

    messages = [record.getMessage() for record in caplog.records]

    assert "should not show up" not in messages
    assert "this should show up" in messages

    # Now test info level
    os.environ["LOG_VERBOSITY"] = "1"
    logger = get_logger("test_console_info")
    logger.info("info message")
    logger.warning("warning message")

    messages = [record.getMessage() for record in caplog.records]
    assert "info message" in messages
    assert "warning message" in messages

