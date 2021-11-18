import unicodedata
import logging; log = logging.getLogger(__name__)



def toStr(char):
    digit = f"{ord(char):x}".upper()
    name = unicodedata.name(char, "Name not found")
    return f"{char} - {digit:>04} | {name.upper()}"


def parseShardInfo(plugin, shard):
    guilds = len(list(filter(lambda x: x.shard_id == shard.id, plugin.bot.guilds)))
    if not shard.is_closed():
        text = "+ {}: CONNECTED ~ {} guilds".format(shard.id, guilds)
    else:
        text = "- {}: DISCONNECTED ~ {} guilds".format(shard.id, guilds)
    return text