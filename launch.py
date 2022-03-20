import discord.http; discord.http.Route.BASE = "https://discordapp.com/api/v9"

import logging; log = logging.getLogger(__name__)

from backend import ShardedBotInstance



if __name__ == "__main__":
    ShardedBotInstance()