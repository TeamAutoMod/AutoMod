import discord
from discord.ext import commands

import re

from . import IntegerConverter



class DiscordUser(commands.Converter):
    def __init__(self, id_only=False):
        super().__init__()
        self.id_only = id_only

    async def convert(self, ctx, argument):
        user = None
        match = (re.compile(r"<@!?([0-9]+)>")).match(argument)
        if match is not None:
            argument = match.group(1)
        try:
            user = await commands.UserConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                user = await ctx.bot.fetch_user(
                    await IntegerConverter(min=20000000000000000, max=9223372036854775807).convert(ctx, argument))
            except (ValueError, discord.HTTPException):
                pass

        if user is None or (self.id_only and str(user.id) != argument):
            raise commands.BadArgument("user_not_found")
        return user