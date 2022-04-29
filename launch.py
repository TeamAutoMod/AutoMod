import discord.http; discord.http.Route.BASE = "https://discordapp.com/api/v9"
import discord
from discord.ext import commands

import sys
import inspect
import logging; log = logging.getLogger(__name__)

from backend import ShardedBotInstance



if __name__ == "__main__":
    if discord.__version__ != "2.0.0a":
        print("You're discord.py version is too old. Install a newer one using the following command: \npip install git+https://github.com/Rapptz/discord.py"); sys.exit(1)
    else:
        if not inspect.iscoroutinefunction(commands.Bot.load_extension):
            print("You're discord.py version is too old. Install a newer one using the following command: \npip install git+https://github.com/Rapptz/discord.py"); sys.exit(1)
        else:
            ShardedBotInstance()