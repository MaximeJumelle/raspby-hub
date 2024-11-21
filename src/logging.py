import logging
import logging.handlers

from logging import Formatter
from . import conf

logger = logging.getLogger(__name__)

LOG_FORMAT = "[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s"
LOG_FORMAT_COLOR = "%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s"


class StreamFormatter(Formatter):
    string_format = LOG_FORMAT_COLOR

    FORMATS_COLORS = {
        logging.DEBUG: "\x1b[34;20m",
        logging.INFO: "\x1b[34;20m",
        logging.WARNING: "\x1b[33;20m",
        logging.ERROR: "\x1b[31;20m",
        logging.CRITICAL: "\x1b[31;1m",
    }

    def format(self, record):
        log_fmt = self.string_format.replace(
            "%(color)s", self.FORMATS_COLORS.get(record.levelno, "\x1b[0m")
        ).replace("%(end_color)s", "\x1b[0m")
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def initialize_logger(
    enable_stream_logging: bool = True, enable_file_logging: bool = True
):
    logger.handlers.clear()
    logger.setLevel(conf["log.level"])
    # We don't want Tornado to log a second time
    logger.propagate = False

    if enable_stream_logging:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(conf["log.level"])
        stream_handler.setFormatter(StreamFormatter())
        logger.addHandler(stream_handler)

    if enable_file_logging:
        file_handler = logging.handlers.RotatingFileHandler(
            conf["log.file_path"],
            maxBytes=50 * 1024 * 1024,
            backupCount=10,
        )
        file_handler.setLevel(conf["log.level"])
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)
