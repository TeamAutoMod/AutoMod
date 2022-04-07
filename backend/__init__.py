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


with open("backend/config.json", "r", encoding="utf8", errors="ignore") as config_file:
    config = json.load(config_file)


sentry_sdk.init(
    config["sentry_dsn"],
    traces_sample_rate=1.0
)


logging.getLogger("discord").propagate = False
logging.basicConfig(
    level=logging.INFO, 
    format="[{asctime}] {levelname:<7}: {message}",
    datefmt="%H:%M:%S",
    style="{"
)