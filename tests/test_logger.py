from infrapilot.logger import setup_logger


def test_logger_initialization():
    logger = setup_logger()

    assert logger.name == "infrapilot"
    assert logger.level == 20


def test_logger_has_handlers():
    logger = setup_logger()

    assert len(logger.handlers) >= 2


def test_logger_writes_message():
    logger = setup_logger()

    logger.info("InfraPilot test log message")

    assert logger.hasHandlers()
