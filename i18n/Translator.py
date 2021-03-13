import json
import logging

from Database import Connector, DBUtils



log = logging.getLogger(__name__)


db = Connector.Database()
LANGS = dict()
LANG_CACHE = dict()



async def init_translator(langs):
    log.info("[Translator] Initiating translator")
    global LANGS
    for l in langs:
        with open(f"./i18n/{l}.json", "r", encoding="utf8", errors="ignore") as f:
            LANGS[l] = json.load(f)
            log.info(f"[Translator] Loaded strings for language {l}")
    log.info("[Translator] Initiated translator")
    



def translate(guild, key, **kwargs):
    if not guild.id in LANG_CACHE:
        lang = DBUtils.get(
            db.configs,
            "guildId",
            guild.id,
            "lang"
        )
        LANG_CACHE[guild.id] = lang # cache the language for the guild, so we don't have to fetch it from the DB every time
    else:
        lang = LANG_CACHE[guild.id]
    try:
        string = LANGS[lang][key]
    except KeyError:
        string = LANGS["en_US"][key]
    finally:
        return str(string).format(**kwargs)
