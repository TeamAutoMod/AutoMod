import discord

from ..sub.ShouldPerformAutomod import shouldPerformAutomod
from ..triggers import Attachments, Invites, Lines, Mentions, Everyone



async def checkMessage(plugin, message): 
    automod = plugin.db.configs.get(f"{message.guild.id}", "automod")
    if "files" in automod:  
        await Attachments.check(plugin, message)
    if "invites" in automod:
        await Invites.check(plugin, message)
    if "mention" in automod:
        await Mentions.check(plugin, message)
    if "lines" in automod:
        await Lines.check(plugin, message)
    if "everyone" in automod:
        await Everyone.check(plugin, message)