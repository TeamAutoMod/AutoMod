import discord

from ..sub.CleanMessages import cleanMessages



async def run(plugin, ctx, message):
    await cleanMessages(
        plugin, 
        ctx, 
        "Until", 
        500, 
        lambda m: True,
        after=discord.Object(message.id)
    )