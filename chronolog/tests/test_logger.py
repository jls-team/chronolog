import unittest
import logging
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Import the module under test
# Assuming the test is run from the project root or chronolog directory,
# ensuring chronolog/chronolog is discoverable on sys.path.
from chronolog import logger
from logging.handlers import RotatingFileHandler


class TestLogger(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for log files for each test run
        self.temp_log_dir = tempfile.mkdtemp()

        # Reset the module-level flag before each test
        # This ensures setup_logging can be called fully for each test's fresh state.
        logger._logging_configured = False

        # Get all loggers and remove their handlers to ensure a clean slate.
        # This is critical to prevent handlers from accumulating across tests
        # or affecting subsequent tests with previous configurations.
        for log_name in logging.Logger.manager.loggerDict:
            l = logging.getLogger(log_name)
            if isinstance(
                l, logging.Logger
            ):  # Ensure it's a Logger instance, not a PlaceHolder
                for h in l.handlers[:]:
                    l.removeHandler(h)
                    h.close()  # Close handler to release file locks if any

        # Explicitly clear handlers for the root logger and the 'chronolog' logger
        # as they are often the primary targets of `basicConfig` or `getLogger("chronolog")`
        root_logger = logging.getLogger()
        for h in root_logger.handlers[:]:
            root_logger.removeHandler(h)
            h.close()

        chronolog_logger = logging.getLogger("chronolog")
        for h in chronolog_logger.handlers[:]:
            chronolog_logger.removeHandler(h)
            h.close()

        # Reset logging level to default if it was changed by a previous test
        root_logger.setLevel(logging.WARNING)  # A common default level

    def tearDown(self):
        # Clean up the temporary directory after each test
        shutil.rmtree(self.temp_log_dir)

        # Reset the module-level flag again (good practice for idempotency)
        logger._logging_configured = False

        # Clean up handlers again, just to be safe, echoing setUp's cleanup
        for log_name in logging.Logger.manager.loggerDict:
            l = logging.getLogger(log_name)
            if isinstance(l, logging.Logger):
                for h in l.handlers[:]:
                    l.removeHandler(h)
                    h.close()
        root_logger = logging.getLogger()
        for h in root_logger.handlers[:]:
            root_logger.removeHandler(h)
            h.close()

        chronolog_logger = logging.getLogger("chronolog")
        for h in chronolog_logger.handlers[:]:
            chronolog_logger.removeHandler(h)
            h.close()

    def _get_file_handler(self, logger_instance=None):
        """Helper to find RotatingFileHandler from the root logger's handlers.
        `setup_logging` uses `logging.basicConfig` which configures the root logger.
        """
        # Always check the root logger for handlers added by basicConfig
        target_logger = logging.getLogger()

        for handler in target_logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                return handler
        return None

    def test_setup_logging_with_default_file_handler(self):
        # Define a log file path within the temporary directory
        log_file = os.path.join(self.temp_log_dir, "default_logs.txt")

        # Call setup_logging with default file handler parameters
        # Explicitly disable GCloud logging to avoid warnings in test output
        logger.setup_logging(
            logger_name="test_default_logger",
            log_file_path=log_file,
            enable_gcloud_logging=False,
        )

        # Retrieve the file handler from the root logger and verify its properties
        file_handler = self._get_file_handler()
        self.assertIsNotNone(file_handler, "RotatingFileHandler should be present")
        self.assertIsInstance(file_handler, RotatingFileHandler)
        self.assertEqual(file_handler.baseFilename, os.path.abspath(log_file))
        self.assertEqual(file_handler.maxBytes, 100 * 1024 * 1024)  # Default 100MB
        self.assertEqual(file_handler.backupCount, 5)  # Default 5

        # Verify that a StreamHandler is also present (default behavior)
        stream_handler_found = any(
            isinstance(h, logging.StreamHandler) for h in logging.getLogger().handlers
        )
        self.assertTrue(stream_handler_found, "StreamHandler should be present")

    def test_setup_logging_with_custom_file_handler_params(self):
        # Define custom parameters for the file handler
        custom_path = os.path.join(self.temp_log_dir, "custom_log.txt")
        custom_max_bytes = 5 * 1024 * 1024  # 5MB
        custom_backup_count = 3

        # Call setup_logging with custom parameters
        logger.setup_logging(
            logger_name="test_custom_logger",
            log_file_path=custom_path,
            log_file_max_bytes=custom_max_bytes,
            log_file_backup_count=custom_backup_count,
            enable_gcloud_logging=False,
        )

        # Retrieve the file handler and verify its custom properties
        file_handler = self._get_file_handler()
        self.assertIsNotNone(
            file_handler, "RotatingFileHandler should be present with custom params"
        )
        self.assertIsInstance(file_handler, RotatingFileHandler)
        self.assertEqual(file_handler.baseFilename, os.path.abspath(custom_path))
        self.assertEqual(file_handler.maxBytes, custom_max_bytes)
        self.assertEqual(file_handler.backupCount, custom_backup_count)

    def test_setup_logging_disables_file_handler_if_path_is_none(self):
        # Call setup_logging with log_file_path set to None to disable file logging
        logger.setup_logging(
            logger_name="test_no_file_logger",
            log_file_path=None,
            enable_gcloud_logging=False,
        )

        # Verify that no RotatingFileHandler is present
        file_handler = self._get_file_handler()
        self.assertIsNone(
            file_handler, "RotatingFileHandler should NOT be present when path is None"
        )

        # Ensure that the StreamHandler is still present (default behavior)
        stream_handler_found = any(
            isinstance(h, logging.StreamHandler) for h in logging.getLogger().handlers
        )
        self.assertTrue(stream_handler_found, "StreamHandler should still be present")

    @patch("chronolog.logger.setup_logging")
    def test_get_prefixed_logger_passes_file_params(self, mock_setup_logging):
        # Test that get_prefixed_logger correctly passes file logging parameters to setup_logging
        logger_name = "my_app"
        prefix = "TEST"
        cloud_logger_name = "my_cloud_app"
        enable_gcloud_logging = (
            True  # Test passing True, even if GCloud might not be installed
        )
        log_file_path = os.path.join(self.temp_log_dir, "app_log.txt")
        log_file_max_bytes = 20 * 1024 * 1024
        log_file_backup_count = 2

        prefixed_logger_instance = logger.get_prefixed_logger(
            logger_name=logger_name,
            prefix=prefix,
            cloud_logger_name=cloud_logger_name,
            enable_gcloud_logging=enable_gcloud_logging,
            log_file_path=log_file_path,
            log_file_max_bytes=log_file_max_bytes,
            log_file_backup_count=log_file_backup_count,
        )

        # Verify that setup_logging was called exactly once with the expected arguments
        mock_setup_logging.assert_called_once_with(
            logger_name,
            cloud_logger_name,
            enable_gcloud_logging=enable_gcloud_logging,
            log_file_path=log_file_path,
            log_file_max_bytes=log_file_max_bytes,
            log_file_backup_count=log_file_backup_count,
        )

        # Also check the returned PrefixedLogger instance
        self.assertIsInstance(prefixed_logger_instance, logger.PrefixedLogger)
        self.assertEqual(prefixed_logger_instance._prefix, prefix)
        self.assertEqual(prefixed_logger_instance.logger.name, logger_name)

    @patch("chronolog.logger.setup_logging")
    def test_get_prefixed_logger_disables_file_logging(self, mock_setup_logging):
        # Test that get_prefixed_logger correctly passes log_file_path=None to disable file logging
        logger_name = "another_app"
        prefix = "NO_FILE"

        prefixed_logger_instance = logger.get_prefixed_logger(
            logger_name=logger_name,
            prefix=prefix,
            log_file_path=None,  # Explicitly disable file logging
        )

        # Verify that setup_logging was called with log_file_path=None and default values for other params
        mock_setup_logging.assert_called_once_with(
            logger_name,
            None,  # Default value for cloud_logger_name
            enable_gcloud_logging=False,  # Default value for enable_gcloud_logging
            log_file_path=None,
            log_file_max_bytes=100
            * 1024
            * 1024,  # Default value for max_bytes if not provided
            log_file_backup_count=5,  # Default value for backup_count if not provided
        )

        # Also check the returned PrefixedLogger instance
        self.assertIsInstance(prefixed_logger_instance, logger.PrefixedLogger)
        self.assertEqual(prefixed_logger_instance._prefix, prefix)
        self.assertEqual(prefixed_logger_instance.logger.name, logger_name)

    def test_setup_logging_prevents_reconfiguration(self):
        # This test verifies that the _logging_configured flag works as intended,
        # preventing setup_logging from re-configuring if it's already been run.

        log_file_1 = os.path.join(self.temp_log_dir, "first_run.txt")
        log_file_2 = os.path.join(self.temp_log_dir, "second_run.txt")

        # First call: This should configure logging for the first time.
        logger.setup_logging(
            logger_name="first_config_logger",
            log_file_path=log_file_1,
            enable_gcloud_logging=False,
        )
        self.assertTrue(
            logger._logging_configured,
            "logger._logging_configured should be True after first setup",
        )

        # Get the file handler created by the first call and its properties
        file_handler_first_call = self._get_file_handler()
        self.assertIsNotNone(file_handler_first_call)
        self.assertEqual(
            file_handler_first_call.baseFilename, os.path.abspath(log_file_1)
        )
        initial_handlers_count = len(logging.getLogger().handlers)

        # Second call with different parameters: This call should be ignored by the _logging_configured flag.
        logger.setup_logging(
            logger_name="second_config_logger",  # Different logger name
            log_file_path=log_file_2,  # Different log file path
            log_file_max_bytes=10 * 1024,  # Different max bytes
            enable_gcloud_logging=False,
        )

        # The _logging_configured flag should still be True
        self.assertTrue(
            logger._logging_configured, "logger._logging_configured should remain True"
        )

        # The number of handlers on the root logger should NOT have increased
        self.assertEqual(
            len(logging.getLogger().handlers),
            initial_handlers_count,
            "Handlers count should remain the same, indicating no reconfiguration",
        )

        # The file handler's baseFilename should still be from the *first* configuration,
        # confirming that the second setup call was skipped and did not alter the existing configuration.
        file_handler_after_second_call = self._get_file_handler()
        self.assertIsNotNone(file_handler_after_second_call)
        self.assertEqual(
            file_handler_after_second_call.baseFilename,
            os.path.abspath(log_file_1),
            "File handler path should remain from the first configuration",
        )


if __name__ == "__main__":
    unittest.main()
