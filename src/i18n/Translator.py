import json
import logging
import pathlib

from Database import Connector, DBUtils
from Utils import Emotes



log = logging.getLogger(__name__)


db = Connector.Database()
LANGS = dict()
LANG_CACHE = dict()



async def init_translator(langs):
    log.info("Initiating translator")
    global LANGS
    for l in langs:
        with open(f"src/i18n/{l}.json", "r", encoding="utf8", errors="ignore") as f:
            LANGS[l] = json.load(f)
            log.info(f"Loaded strings for language {l}")
    log.info("Initiated translator")





def translate(guild, key, _emote=None, **kwargs):
    if not guild.id in LANG_CACHE:
        try:
            lang = DBUtils.get(
                db.configs,
                "guildId",
                guild.id,
                "lang"
            )
        except KeyError:
            DBUtils.update(
                db.configs,
                "guildId",
                guild.id,
                "lang",
                "en_US"
            )
            lang = "en_US"
        LANG_CACHE[guild.id] = lang # cache the language for the guild, so we don't have to fetch it from the DB every time
    else:
        lang = LANG_CACHE[guild.id]
    global string
    try:
        string = LANGS[lang][key]
    except KeyError:
        string = LANGS["en_US"][key]
    finally:
        if "{emote}" in string:
            return str(string).format(emote=str(Emotes.get(_emote)), **kwargs)
        else:
            return str(string).format(**kwargs)




class Translator:
    def __init__(self, bot, langs):
        self.bot = bot
        self._langs = dict()
        self._lang_cache = dict()
        for l in langs:
            with open(f"src/i18n/{l}.json", "r", encoding="utf8", errors="ignore") as f:
                self._langs[l] = json.load(f)
                log.info(f"Loaded strings for language {l}")
    
    
    def translate(self, guild, key, _emote=None, **kwargs):
        if not guild.id in LANG_CACHE:
            try:
                lang = self.bot.db.configs.get(f"{guild.id}", "lang")
            except KeyError:
                self.bot.db.configs.update(f"{guild.id}", "lang", "en_US")
                lang = "en_US"
            self._lang_cache[guild.id] = lang
        else:
            lang = self._lang_cache[guild.id]
        global string
        try:
            string = self._langs[lang][key]
        except KeyError:
            string = self._langs["en_US"][key]
        finally:
            if "{emote}" in string:
                return str(string).format(emote=str(Emotes.get(_emote)), **kwargs)
            else:
                return str(string).format(**kwargs)