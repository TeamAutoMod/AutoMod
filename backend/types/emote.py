import discord
from discord.ext import commands

import emoji
from typing import Union



class Emote(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: Union[str, None]) -> Union[str, discord.Emoji, Exception]:
        try:
            server_emote = await commands.EmojiConverter().convert(ctx, argument)
        except commands.BadArgument:
            found = emoji.get_emoji_regexp().search(argument)
            if found:
                return argument
            else:
                raise commands.BadArgument(f"Emote {argument} not found")
        else:
            return server_emote