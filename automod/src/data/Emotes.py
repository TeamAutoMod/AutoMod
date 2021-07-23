import json
import logging
import pathlib



log = logging.getLogger(__name__)

class Emotes:
    def __init__(self, bot):
        self.bot = bot
        with open(f"{pathlib.Path(__file__).parent}/emotes.json", "r", encoding="utf8", errors="ignore") as f:
            self.emotes = json.load(f)
            if bot.config.dev:
                self.emotes.update({
                    "YES": "👌",
                    "NO": "❌"
                })


    def get(self, key):
        try:
            return self.emotes[key]
        except KeyError:
            log.warn("Failed to obtain an emoji with key {}".format(key))


    def reload(self):
        with open(f"{pathlib.Path(__file__).parent}/emotes.json", "r", encoding="utf8", errors="ignore") as f:
            self.emotes = json.load(f)
            if self.bot.config.dev:
                self.emotes.update({
                    "YES": "👌",
                    "NO": "❌"
                })