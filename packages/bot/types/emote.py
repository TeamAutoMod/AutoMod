import discord
from discord.ext import commands

import emoji
import re
from typing import Union



class Emote(commands.Converter):
    async def convert(
        self, 
        ctx: discord.Interaction, 
        argument: Union[
            str, 
            None
        ]
    ) -> Union[
        str, 
        discord.Emoji, 
        Exception
    ]:
        try:
            server_emote = await ServerEmote().convert(ctx, argument)
        except commands.BadArgument:
            found = emoji.get_emoji_regexp().search(argument)
            if found:
                return argument
            else:
                raise commands.BadArgument(f"Emote {argument} not found")
        else:
            return server_emote


class ServerEmote(commands.Converter):
    async def convert(
        self, 
        ctx: discord.Interaction,
        argument: str
    ) -> Union[
        discord.Emoji, 
        Exception
    ]:
        match = re.match(r'<a?:[a-zA-Z0-9\_]{1,32}:([0-9]{15,20})>$', argument)
        result = None
        bot = ctx._client
        guild = ctx.guild

        if match is None:
            if guild:
                result = discord.utils.get(guild.emojis, name=argument)

            if result is None:
                result = discord.utils.get(bot.emojis, name=argument)
        else:
            emoji_id = int(match.group(1))

            result = bot.get_emoji(emoji_id)

        if result is None:
            raise commands.EmojiNotFound(argument)

        return result