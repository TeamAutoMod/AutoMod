import logging
from logging.handlers import RotatingFileHandler

import contextlib
import datetime



class LogFilter(logging.Filter):
    def __init__(self):
        super().__init__(name="discord.state")
    
    def filter(self, r):
        if r.levelname == "WARNING" and "referencing an unknown" in r.msg:
            return False
        return True


@contextlib.contextmanager
def setup_logging():
    try:
        max_bytes = 32 * 1024 * 1012
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        logging.getLogger("discord.state").addFilter(LogFilter())

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = RotatingFileHandler(filename="automod.log", encoding="utf-8", mode="w", maxBytes=max_bytes, backupCount=5)
        fmt = "%d/%M/%Y %H:%M:%S"
        formatter = logging.Formatter("[{asctime}] [{levelname:<7}] {name}: {message}", fmt, style="{")
        handler.setFormatter(formatter)
        log.addHandler(handler)

        yield
    finally:
        handlers = log.handlers[:]
        for _handler in handlers:
            _handler.close()
            log.removeHandler(_handler)