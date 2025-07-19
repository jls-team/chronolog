# chronolog

[![PyPI](https://img.shields.io/pypi/v/chronolog.svg)](https://pypi.org/project/chronolog/)
[![Tests](https://github.com/jls-team/chronolog/actions/workflows/test.yml/badge.svg)](https://github.com/jls-team/chronolog/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/jls-team/chronolog?include_prereleases&label=changelog)](https://github.com/jls-team/chronolog/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/jls-team/chronolog/blob/main/LICENSE)

A Python logger with elapsed time calculation, dynamic prefixes, and optional Google Cloud integration.

## Installation

Install the library using `pip`.

**From PyPI:**
```bash
pip install chronolog
```

**With Google Cloud Logging support:**
```bash
pip install "chronolog[google]"
```

**For latest releases:**
```bash
pip install git+https://github.com/jls-team/chronolog.git
```

**For development:**
```bash
git clone https://github.com/jls-team/chronolog.git
cd chronolog
pip install -e '.[test]'
```

## Usage

The `chronolog` library provides a `PrefixedLogger` that automatically adds a configurable prefix to all log messages. It also includes special "beacon" logging for timing operations.

### Basic Logging

To get a logger instance, use the `get_prefixed_logger` function.

```python
from chronolog import get_prefixed_logger

# Get a logger with a prefix
log = get_prefixed_logger("my_app", prefix="APP")
log.info("Application started.")

# The prefix can be updated dynamically
log.update_prefix("PROCESS_A")
log.info("Processing data...")
log.warning("Something might be wrong here.")

# Example of logging an exception
try:
    1 / 0
except ZeroDivisionError:
    log.exception("Division by zero attempt caught!")

```
Will produce result like this:
```
2025-07-19 15:53:14,339 - INFO - [APP] Application started.
2025-07-19 15:53:14,339 - INFO - [PROCESS_A] Processing data...
2025-07-19 15:53:14,339 - INFO - [PROCESS_A] (BEACON - [data_processing] - START) Starting heavy data processing.
2025-07-19 15:53:14,444 - INFO - [PROCESS_A] (BEACON - [data_processing] - END (Elapsed time 0.11 s)) Heavy data processing completed.
2025-07-19 15:53:14,444 - WARNING - [PROCESS_B] Something might be wrong here.
2025-07-19 15:53:14,444 - ERROR - [PROCESS_B] An error occurred!
2025-07-19 15:53:14,445 - ERROR - [PROCESS_B] Division by zero attempt caught!
Traceback (most recent call last):
  File "/Users/Liudas.Sodonis/Dev/tests/ch/main.py", line 27, in <module>
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
```

### Beacon Logging for Timing

Use `log_start` and `log_end` to automatically log the elapsed time of an operation with `BEACON` prefix. This can be used for monitoring and performance analysis, since `BEACON` logs are designed to be easily parsed and aggregated.

```python
import time
from chronolog import get_prefixed_logger

log = get_prefixed_logger("timed_app", prefix="TIMER")

# Use a unique key to mark the start and end of an operation
log.log_start("data_processing", "Starting heavy data processing.")

# Simulate some work
time.sleep(0.1)

log.log_end("data_processing", "Heavy data processing completed.")
```
would result in a log message like:
```log
2025-02-19 16:17:41,419 - INFO - [TIMER] (BEACON - [data_processing] - START) Starting heavy data processing.
2025-02-19 16:17:41,524 - INFO - [TIMER] (BEACON - [data_processing] - END (Elapsed time 0.11 s)) Heavy data processing completed.
```
This will produce a log message that includes the total time spent between the `log_start` and `log_end` calls for the `data_processing` key.

## Configuration

### Log Level

Set the desired log level using Python's standard `logging` module. The default level is `INFO`.

```python
import logging
from chronolog import get_prefixed_logger

# Set the root logger level to DEBUG
logging.getLogger().setLevel(logging.DEBUG)

log = get_prefixed_logger("debug_app", prefix="DEBUG")
log.debug("This debug message will now be visible.")
```

### File Logging

By default, `chronolog` writes to a rotating file named `logs.txt` (100MB max, 5 backups). You can customize or disable this feature.

**1. Customizing the Log File**

Provide custom settings for the path, max size, and backup count.

```python
from chronolog import get_prefixed_logger

log_custom_file = get_prefixed_logger(
    name="custom_file_app",
    prefix="CUSTOM_FILE",
    log_file_path="my_custom_app.log",
    log_file_max_bytes=5 * 1024 * 1024,  # 5 MB
    log_file_backup_count=2,
)
log_custom_file.info("This log goes to a custom-configured file.")
```

**2. Disabling File Logging**

To log only to the console (and Google Cloud, if enabled), set `log_file_path` to `None`.

```python
from chronolog import get_prefixed_logger

log_no_file = get_prefixed_logger("console_app", prefix="NO_FILE", log_file_path=None)
log_no_file.info("This message will not be written to a local file.")
```

### Google Cloud Logging

If you installed the library with the `[google]` extra, you can enable logging to Google Cloud.

```python
from chronolog import get_prefixed_logger

# Set enable_gcloud_logging to True
log = get_prefixed_logger(
    name="my_gcp_app",
    prefix="CLOUD_APP",
    enable_gcloud_logging=True,
    cloud_logger_name="my-gcp-logger-instance" # Optional: custom GCloud logger name
)
log.info("This message will be sent to Google Cloud Logging.")
```
If `enable_gcloud_logging` is `False` (the default), no logs will be sent to Google Cloud, even if the dependency is installed.

## Development

To contribute to this library, set up a development environment.

**1. Set up the virtual environment:**
```bash
# Assumes you have already cloned the repository
cd chronolog
python -m venv venv
source venv/bin/activate
```

**2. Install dependencies:**
```bash
pip install -e '.[test]'
```

**3. Run tests:**
```bash
python -m pytest
```
