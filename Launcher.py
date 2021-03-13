import discord.http
discord.http.Route.BASE = "https://discordapp.com/api/v6" # v6 > v7

from Bot.AutoMod import AutoMod
from discord import Intents
from Database import Connector, DBUtils

from Utils import Logging

import logging
from logging.handlers import RotatingFileHandler

import contextlib
import datetime
import asyncio
import traceback

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


db = Connector.Database()


def prefix_callable(bot, message):
    bot_id = bot.user.id
    prefixes = [f"<@!{bot_id}> ", f"<@{bot_id}> "]
    if message.guild is None:
        prefixes.append("+")
    elif bot.READY:
        try:
            prefix = DBUtils.get(db.configs, "guildId", f"{message.guild.id}", "prefix")
            if prefix is not None:
                prefixes.append(prefix)
            else:
                prefixes.append("+")
        except Exception:
            prefixes.append("+")
    return prefixes


class LogFilter(logging.Filter):
    def __init__(self):
        super().__init__(name="discord.state")
    
    def filter(self, r):
        if r.levelname == "WARNING" and "referencing an unknown" in r.msg:
            return False
        return True


@contextlib.contextmanager
def init_logger():
    try:
        max_bytes = 32 * 1024 * 1012
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        logging.getLogger("discord.state").addFilter(LogFilter())

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = RotatingFileHandler(filename="automod.log", encoding="utf-8", mode="w", maxBytes=max_bytes, backupCount=5)
        fmt = "%d/%M/%Y %H:%M:%S"
        formatter = logging.Formatter("[{asctime}] [{levelname:<7}] {name}: {message}", fmt, style="{")
        handler.setFormatter(formatter)
        log.addHandler(handler)

        yield
    finally:
        handlers = log.handlers[:]
        for _handler in handlers:
            _handler.close()
            log.removeHandler(_handler)



if __name__ == "__main__":
    with init_logger():
        automod = AutoMod(**{
            "command_prefix": prefix_callable,
            "case_insensitive": True,
            "max_messages": 1000,
            "intents": Intents(
                guilds=True,
                members=True,
                bans=True,
                emojis=True,
                messages=True,
                reactions=True
            ),
            "chunk_guilds_at_startup": False,
            "description": "Discord moderation/utility bot!"
        })
        automod.remove_command("help")
        automod.run()
