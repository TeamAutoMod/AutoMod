# type: ignore

import discord
from discord.ext import commands

import re
from typing import Union

from . import IntegerConverter



class DiscordUser(commands.Converter):
    def __init__(
        self, 
        id_only: bool = False
    ) -> None:
        super().__init__()
        self.id_only = id_only


    async def convert(
        self, 
        ctx: discord.Interaction, 
        argument: str
    ) -> Union[
        discord.User, 
        Exception
    ]:
        user = None
        try:
            match = (re.compile(r"<@!?([0-9]+)>")).match(argument)
        except Exception:
            raise
        if match is not None:
            argument = match.group(1)
            
        if argument.isdigit():
            if int(argument) in ctx._client.fetched_user_cache:
                user = ctx._client.fetched_user_cache[int(argument)]
            else:
                try:
                    user = await ctx._client.fetch_user(
                        await IntegerConverter(min=20000000000000000, max=9223372036854775807).convert(ctx, argument))
                except (
                    ValueError, 
                    discord.HTTPException
                ):
                    pass

        if user is None or (self.id_only and str(user.id) != argument):
            raise commands.BadArgument(f"User {argument} not found")

        if not user.id in ctx._client.fetched_user_cache:
            ctx._client.fetched_user_cache.update({
                user.id: user
            })
        return user