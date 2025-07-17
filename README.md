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

Usage instructions go here.

## Configuration

### Google Cloud Logging

If you install the package with the `[google]` extra, logs will also be sent to Google Cloud Logging in addition to the local file.

```bash
pip install "chronolog[google]"
```

### Log File Path

You can configure the path for the log file by setting the `LOGGING_FILE_PATH` environment variable. If this variable is not set, it defaults to `logs.txt` in the current working directory.

Example:
```bash
export LOGGING_FILE_PATH="/var/log/my_app.log"
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
