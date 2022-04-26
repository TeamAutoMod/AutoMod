<<<<<<< HEAD
import json
import logging; log = logging.getLogger()

from typing import Union



class Emotes(object):
    def __init__(self, bot) -> None:
        self.bot = bot
        with open(f"data/emotes.json", "r", encoding="utf8", errors="ignore") as f:
            self.emotes = json.load(f)
            if bot.config.dev:
                self.emotes.update({
                    "YES": "✅",
                    "NO": "❌"
                })


    def get(self, key: str) -> Union[str, None]:
        try:
            return self.emotes[key]
        except KeyError:
            log.warn("⚠️ Failed to obtain an emoji with key {}".format(key))


    def reload(self) -> None:
=======
import json
import logging; log = logging.getLogger()

from typing import Union



class Emotes(object):
    def __init__(self, bot) -> None:
        self.bot = bot
        with open(f"data/emotes.json", "r", encoding="utf8", errors="ignore") as f:
            self.emotes = json.load(f)
            if bot.config.dev:
                self.emotes.update({
                    "YES": "✅",
                    "NO": "❌"
                })


    def get(self, key: str) -> Union[str, None]:
        try:
            return self.emotes[key]
        except KeyError:
            log.warn("⚠️ Failed to obtain an emoji with key {}".format(key))


    def reload(self) -> None:
>>>>>>> 049ddcde2a090ba7492f82b75ee62cc010bbc290
        self.__init__(self.bot)