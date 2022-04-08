import discord
from discord.ext import commands

import emoji



class Emote(commands.Converter):
    async def convert(self, ctx, argument):
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