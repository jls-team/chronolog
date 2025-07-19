# chronolog

[![PyPI](https://img.shields.io/pypi/v/chronolog.svg)](https://pypi.org/project/chronolog/)
[![Tests](https://github.com/jls-team/chronolog/actions/workflows/test.yml/badge.svg)](https://github.com/jls-team/chronolog/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/jls-team/chronolog?include_prereleases&label=changelog)](https://github.com/jls-team/chronolog/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/jls-team/chronolog/blob/main/LICENSE)

Logger with elpased time calculation.

## Installation

Install this library using `pip`:
```bash
pip install chronolog
```

Alternatively, you can install the latest version directly from GitHub:

```bash
git clone https://github.com/jls-team/chronolog.git
cd chronolog
pip install -e .
```
## Usage

The `chronolog` library provides a `PrefixedLogger` instance that automatically adds a configurable prefix to all log messages. It also includes special "beacon" logging for timing operations.

To get a logger instance, use the `get_prefixed_logger` function:

```python
from chronolog import get_prefixed_logger
import time

# Get a logger with a default prefix
log = get_prefixed_logger("my_app", prefix="APP")
log.info("Application started.")

# Log with debug level
log.debug("Debug message here.")

# Update the prefix dynamically
log.update_prefix("PROCESS_A")
log.info("Processing data...")

# Use beacon logging for timing operations
log.log_start("data_processing", "Starting heavy data processing.")
# Simulate some work
time.sleep(0.1)
log.log_end("data_processing", "Heavy data processing completed.")

log.update_prefix("PROCESS_B")
log.warning("Something might be wrong here.")
log.error("An error occurred!")

# Example of logging an exception
try:
    1 / 0
except ZeroDivisionError:
    log.exception("Division by zero attempt caught!")
```

### File Logging Configuration

By default, `chronolog` writes logs to a file named `logs.txt` (100MB max, 5 backups) and to the console. You can customize or disable the file logging via `get_prefixed_logger` parameters:

**1. Disabling File Logging**

To disable the `RotatingFileHandler` completely, set `log_file_path` to `None`:

```python
from chronolog import get_prefixed_logger

# Get a logger that only logs to the console (and Google Cloud if enabled)
log_no_file = get_prefixed_logger("no_file_app", prefix="NO_FILE", log_file_path=None)
log_no_file.info("This message will not be written to a local log file.")
```

**2. Customizing File Logging Properties**

You can specify a custom log file path, maximum file size, and the number of backup files to keep:

```python
from chronolog import get_prefixed_logger
import os

# Define custom log file settings
custom_log_path = os.path.join(os.getcwd(), "my_custom_app.log")
custom_max_bytes = 5 * 1024 * 1024  # 5 MB
custom_backup_count = 2 # Keep 2 backup files

log_custom_file = get_prefixed_logger(
    "custom_file_app",
    prefix="CUSTOM_FILE",
    log_file_path=custom_log_path,
    log_file_max_bytes=custom_max_bytes,
    log_file_backup_count=custom_backup_count,
)
log_custom_file.info("This log goes to a custom-configured file.")
```

## Configuration

### Google Cloud Logging

If you install the package with the `[google]` extra, logs will also be sent to Google Cloud Logging in addition to the local file.

```bash
pip install "chronolog[google]"
```

To initialize Google Cloud Logging explicitly (e.g., if you want to control the client name or prevent default initialization):

```python
from chronolog import get_prefixed_logger

# This will attempt to set up Google Cloud Logging if 'google-cloud-logging' is installed.
log = get_prefixed_logger(
    "my_app",
    prefix="CLOUD_ENABLED",
    enable_gcloud_logging=True, # Set to True to enable GCloud logging
    cloud_logger_name="my-gcp-logger-instance" # Optional: customize GCloud logger name
)
log.info("This message will go to Google Cloud Logging.")
```

If `enable_gcloud_logging` is set to `False` (default for `get_prefixed_logger`), Google Cloud Logging will not be initialized, even if the library is installed. This is useful for development or environments where cloud logging is not desired.

### File Logging Parameters

The `chronolog` library uses a `RotatingFileHandler` for local file logging. You can configure its behavior using the following parameters in the `setup_logging` or `get_prefixed_logger` functions:

*   `log_file_path` (str, optional): The path to the log file.
    *   If `None`, file logging is completely disabled.
    *   Defaults to `logs.txt` if not provided.
*   `log_file_max_bytes` (int, optional): The maximum size of the log file in bytes before it is rotated. Defaults to `100 * 1024 * 1024` (100 MB).
*   `log_file_backup_count` (int, optional): The number of backup log files to keep. Defaults to `5`.

### Log Level

By default, the logger is set to `INFO` level. You can change the level of the root logger (which `chronolog` configures) directly using Python's `logging` module.

```python
import logging
from chronolog import get_prefixed_logger

# Set the root logger level to DEBUG
logging.getLogger().setLevel(logging.DEBUG)

log = get_prefixed_logger("debug_app", prefix="DEBUG")
log.debug("This debug message will now be visible.")
log.info("This info message is also visible.")
```

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:
```bash
cd chronolog
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
python -m pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
