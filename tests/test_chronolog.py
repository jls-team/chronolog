import pytest
import logging
import time


from chronolog import PrefixedLogger


# Helper to get a logger instance for testing
def get_test_logger(prefix, caplog):
    """Creates a logger instance for testing and sets the level to DEBUG."""
    logger = PrefixedLogger(logger_name="test_logger", prefix=prefix)
    # Set the level on the underlying logger to capture all messages
    logger.logger.setLevel(logging.DEBUG)
    return logger


def test_logger_initialization():
    """Test that the logger is initialized with the correct prefix."""
    logger = PrefixedLogger(logger_name="init_test", prefix="my-prefix")
    assert logger._prefix == "my-prefix"


def test_logger_initialization_no_prefix():
    """Test that the logger defaults to 'no-prefix' if none is provided."""
    logger = PrefixedLogger(logger_name="no_prefix_test")
    assert logger._prefix == "no-prefix"


def test_info_log_prefixing(caplog):
    """Test that info messages are correctly prefixed."""
    with caplog.at_level(logging.INFO):
        logger = get_test_logger("prefix-123", caplog)
        logger.info("This is a test message.")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "INFO"
    assert record.message == "[prefix-123] This is a test message."


def test_update_prefix(caplog):
    """Test that the prefix can be updated."""
    with caplog.at_level(logging.INFO):
        logger = get_test_logger("initial-prefix", caplog)
        logger.info("First message.")

        logger.update_prefix("new-prefix")
        logger.info("Second message.")

    assert len(caplog.records) == 2
    assert caplog.records[0].message == "[initial-prefix] First message."
    assert caplog.records[1].message == "[new-prefix] Second message."


def test_beacon_timer_logging(caplog, monkeypatch):
    """Test the log_start and log_end beacon functionality with timing."""
    start_time = 1000.0
    end_time = 1002.5

    # Mock time.time() to return predictable values
    # Add extra values in case time.time() is called more than expected
    time_calls = [start_time, end_time, end_time, end_time]
    monkeypatch.setattr(
        time, "time", lambda: time_calls.pop(0) if time_calls else end_time
    )

    with caplog.at_level(logging.INFO):
        logger = get_test_logger("beacon-test", caplog)
        logger.log_start("task-1", "Starting the task.")
        logger.log_end("task-1", "Finished the task.")

    assert len(caplog.records) == 2

    # Check start log
    start_record = caplog.records[0]
    assert start_record.levelname == "INFO"
    assert (
        start_record.message
        == "[beacon-test] (BEACON - [task-1] - START) Starting the task."
    )

    # Check end log
    end_record = caplog.records[1]
    assert end_record.levelname == "INFO"
    expected_end_msg = "[beacon-test] (BEACON - [task-1] - END (Elapsed time 2.50 s)) Finished the task. "
    assert end_record.message == expected_end_msg


def test_beacon_log_end_without_start(caplog):
    """Test that a warning is logged if log_end is called without log_start."""
    with caplog.at_level(
        logging.INFO
    ):  # Changed from WARNING to INFO to capture both logs
        logger = get_test_logger("warning-test", caplog)
        # We need to capture info logs too, as the beacon message itself is info level
        logger.logger.setLevel(logging.INFO)
        logger.log_end("dangling-task", "This task never started.")

    # Expect one warning record and one info record
    assert len(caplog.records) == 2

    warning_record = caplog.records[0]
    assert warning_record.levelname == "WARNING"
    assert (
        "log_end called for key 'dangling-task' without a corresponding log_start."
        in warning_record.message
    )

    info_record = caplog.records[1]
    assert info_record.levelname == "INFO"
    assert (
        "(BEACON - [dangling-task] - END (Elapsed time N/A s))" in info_record.message
    )
