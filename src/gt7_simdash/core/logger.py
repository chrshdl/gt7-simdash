import logging


class Logger:
    def __init__(self, name: str):
        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(LogFormatter())
        self.logger.addHandler(sh)

    def get(self) -> logging.Logger:
        return self.logger


class LogFormatter(logging.Formatter):
    grey: str = "\x1b[38;20m"
    yellow: str = "\x1b[33;20m"
    red: str = "\x1b[91;20m"
    reset: str = "\x1b[0m"
    format_text: str = (
        "%(asctime)s  | %(levelname)s | %(message)s  (%(filename)s:%(lineno)d)"
    )

    FORMATS: dict[int, str] = {
        logging.DEBUG: grey + format_text + reset,
        logging.INFO: grey + format_text + reset,
        logging.WARNING: yellow + format_text + reset,
        logging.ERROR: red + format_text + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
