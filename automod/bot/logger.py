import logging
import contextlib



class LogFilter(logging.Filter):
    def __init__(self):
        super().__init__(name="discord.state")

    def filter(self, r):
        if r.levelname == "WARNING" and "referencing an unknown" in r.msg:
            return False
        return True


@contextlib.contextmanager
def SetupLogging():
    try:
        logging.getLogger("discord").propagate = False
        #logging.getLogger("discord.http").propagate = False

        state = logging.getLogger("discord.state")
        state.propagate = False

        logging.basicConfig(level=logging.INFO, format="[{levelname:<7}] - {message}", style="{")
        
        yield 

        
    except Exception as ex:
        print("[Error] Error in logger: {}".format(ex))