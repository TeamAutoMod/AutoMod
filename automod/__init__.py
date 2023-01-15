# type: ignore

import sentry_sdk
import json
import logging
import subprocess
from .bot import ShardedBotInstance



try:
    _V = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
except Exception:
    VERSION = "1.0.0"
else:
    VERSION = str(_V).replace("b'", "")[:7]


with open("automod/config.json", "r", encoding="utf8", errors="ignore") as config_file:
    config = json.load(config_file)


if config.get("sentry_dsn", "") != "":
    sentry_sdk.init(
        config["sentry_dsn"],
        traces_sample_rate=1.0
    )


class _Formatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__(
            fmt="\033[92m{loc:<8} |\033[0m [{asctime}] \033[92m {levelname:<4} \033[0m: {message}", datefmt="%H:%M:%S", style="{"
        )

    
    def format(self, record) -> str:
        fm_og = self._style._fmt
        record.levelname = record.levelname.lower()

        if record.levelno == logging.DEBUG:
            self._style._fmt = "\033[1;34m{loc:<10} |\033[0;0m [{asctime}] ⚙️ \033[1;34m {levelname:<4} \033[0;0m: {message}"

        elif record.levelno == logging.INFO:
            self._style._fmt = "\033[92m{loc:<10} |\033[0m [{asctime}] 🆗 \033[92m {levelname:<4} \033[0m: {message}"

        elif record.levelno == logging.WARN:
            self._style._fmt = "\033[1;33m{loc:<10} |\033[0;0m [{asctime}] ☣️ \033[1;33m warn \033[0;0m: {message}"

        elif record.levelno == logging.ERROR:
            self._style._fmt = "\033[1;31m{loc:<10} |\033[0;0m [{asctime}] 🔥 \033[1;31m fail \033[0;0m: {message}"

        elif record.levelno == logging.CRITICAL:
            self._style._fmt = "{message}" # This is just used for the ascii starting text

        res = logging.Formatter.format(self, record)
        self._style._fmt = fm_og

        return res
    

logging.getLogger("discord").propagate = False
for aiohttp_logger in [
    "access", "client", "internal", "server", "web", "websocket"
]: logging.getLogger(f"aiohttp.{aiohttp_logger}").propagate = False

sh = logging.StreamHandler()
sh.setFormatter(_Formatter())

logging.root.addHandler(sh)
logging.root.setLevel(logging.INFO)