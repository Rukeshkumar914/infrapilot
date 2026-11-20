
import logging
from logging.handlers import RotatingFileHandler

from infrapilot.logger import setup_logger


def test_logger_initialization():
    logger = setup_logger()

    assert logger.name == "infrapilot"
    assert logger.level == logging.INFO


def test_logger_has_handlers():
    logger = setup_logger()

    assert len(logger.handlers) >= 2


def test_logger_writes_message():
    logger = setup_logger()

    test_message = "InfraPilot test log message"
    logger.info(test_message)

    file_handlers = [
        handler
        for handler in logger.handlers
        if isinstance(handler, RotatingFileHandler)
    ]

    assert len(file_handlers) == 1

    file_handlers[0].flush()

    with open(
        file_handlers[0].baseFilename,
        "r",
        encoding="utf-8",
    ) as file:
        content = file.read()

    assert test_message in content


def test_logger_uses_rotating_file_handler():
    logger = setup_logger()

    file_handlers = [
        handler
        for handler in logger.handlers
        if isinstance(handler, RotatingFileHandler)
    ]

    assert len(file_handlers) == 1
    assert file_handlers[0].maxBytes == 5 * 1024 * 1024
    assert file_handlers[0].backupCount == 5
