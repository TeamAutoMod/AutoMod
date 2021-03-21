import json
import logging



log = logging.getLogger(__name__)


EMOTES = None

async def init_emotes():
    with open("./src/emotes.json", "r", encoding="utf8", errors="ignore") as f:
        global EMOTES
        EMOTES = json.load(f)
    log.info("[Emotes] Loaded the emotes")

    
def get(emote):
    try:
        return EMOTES[emote]
    except KeyError:
        log.warn(f"[Emotes] I couldn't find an emoji with the key {emote}")
        return ""


async def reload_emotes():
    log.info("[Emotes] Reloading the emotes")
    await init_emotes()
    log.info("[Emotes] Reloaded the emotes!")
