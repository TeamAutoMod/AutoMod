import discord

from ..functions.CheckMessage import checkMessage


async def run(plugin, message):
    if message.guild is None or not isinstance(message.guild, discord.Guild):
        return
    if len(plugin.db.configs.get(message.guild.id, "automod")) < 1:
        return

    await checkMessage(plugin, message)
