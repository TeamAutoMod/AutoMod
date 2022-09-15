# type: ignore

import discord
from discord.ext import commands

import sys
import inspect
import logging; log = logging.getLogger(__name__)

from packages.bot import ShardedBotInstance



if __name__ == "__main__":
    if not inspect.iscoroutinefunction(commands.Bot.load_extension):
        print("You're discord.py version is too old. Install a newer one using the following command: \npip install git+https://github.com/Rapptz/discord.py"); sys.exit(1)
    else:
        ShardedBotInstance()