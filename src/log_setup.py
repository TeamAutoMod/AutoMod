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
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARN)
        logging.getLogger("discord.state").addFilter(LogFilter())

        logging.basicConfig(level=logging.INFO, format="[{levelname:<7}] - {message}", style="{")
        
        yield
    except Exception as ex:
        print("[Fatal] Error in logger: {}".format(ex))