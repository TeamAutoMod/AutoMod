import json
import logging
import discord
import sentry_sdk
import sys
import os

from logging.handlers import TimedRotatingFileHandler
from aiohttp import ClientOSError, ServerDisconnectedError
from discord import ConnectionClosed

from i18n import Translator
from Utils import Utils
from Database import Connector, DBUtils

log = logging.getLogger(__name__)

LOGGER = logging.getLogger("automod")
DISCORD_LOGGER = logging.getLogger("discord")
BOT_LOG = None
BOT = None

db = Connector.Database()


async def init(actual_bot):
    global BOT
    global BOT_LOG
    BOT_LOG = await actual_bot.fetch_channel(int(Utils.from_config("GLOBAL_LOG_CHANNEL")))
    BOT = actual_bot


def before_send(event, hint):
    if event['level'] == "error" and 'logger' in event.keys() and event['logger'] == 'automod':
        return None  # we send errors manually, in a much cleaner way
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        for t in [ConnectionClosed, ClientOSError, ServerDisconnectedError]:
            if isinstance(exc_value, t):
                return
    return event


def init_sentry():
    dsn = Utils.from_config("SENTRY_DSN")
    sentry_sdk.init(dsn, before_send=before_send)


async def bot_log(bot, text=None, embed=None):
    log_channel: discord.TextChannel = await bot.fetch_channel(int(Utils.from_config("GLOBAL_LOG_CHANNEL")))
    await log_channel.send(content=text, embed=embed)


async def guild_log(bot, text=None, embed=None):
    log_channel: discord.TextChannel = await bot.fetch_channel(int(Utils.from_config("GUILD_LOG_CHANNEL")))
    await log_channel.send(content=text, embed=embed)


async def log_to_guild(guild_id, log_type, text):
    # check if we can even log to this guild
    log_id = DBUtils.get(db.configs, "guildId", f"{guild_id}", f"{log_type}")
    if log_id == None or log_id == "":
        return

    # check if the channel is still valid
    log_channel = await BOT.fetch_channel(int(log_id))
    if log_channel is None:
        return

    await log_channel.send(text)



async def bot_log(msg=None, embed=None):
    global BOT_LOG
    if BOT_LOG is not None:
        await BOT_LOG.send(content=msg, embed=embed)
    else:
        log.error(f"[Booting Up] Bot log channel hasn't been fetched yet!")