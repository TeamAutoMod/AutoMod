import sentry_sdk
import json
import logging
import subprocess
from .bot import ShardedBotInstance



VERSION = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()


with open("backend/config.json", "r", encoding="utf8", errors="ignore") as config_file:
    config = json.load(config_file)


sentry_sdk.init(
    config["sentry_dsn"],
    traces_sample_rate=1.0
)


logging.basicConfig(level=logging.INFO, format="[{levelname:<7}] - {message}", style="{")