import discord

from ..functions.CleanMessages import cleanMessages



async def run(plugin, ctx, start, end):
    await cleanMessages(
        plugin, 
        ctx, 
        "Between", 
        500, 
        lambda m: True,
        before=discord.Object(end.id),
        after=discord.Object(start.id)
    )