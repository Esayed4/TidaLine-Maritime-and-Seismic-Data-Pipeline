import logging
import os


class Logger:

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

        if not self.logger.handlers:
            self._configure()

    def _configure(self):

        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        self.logger.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def info(self, message, *args):
        self.logger.info(message, *args)

    def debug(self, message, *args):
        self.logger.debug(message, *args)

    def warning(self, message, *args):
        self.logger.warning(message, *args)

    def error(self, message, *args):
        self.logger.error(message, *args)

    def exception(self, message, *args):
        self.logger.exception(message, *args)