import discord

from ..sub.ShouldPerformAutomod import shouldPerformAutomod
from ..triggers import Attachments, Invites, Zalgo, Mentions, Caps, Everyone, Lines



async def checkMessage(plugin, message):
    if not await shouldPerformAutomod(plugin, message):
        return
    
    automod = plugin.db.configs.get(f"{message.guild.id}", "automod")
    if "files" in automod:
        await Attachments.check(plugin, message)
    if "invites" in automod:
        await Invites.check(plugin, message)
    if "everyone" in automod:
        await Everyone.check(plugin, message)
    if "zalgo" in automod:
        await Zalgo.check(plugin, message)
    if "mention" in automod:
        await Mentions.check(plugin, message)
    if "lines" in automod:
        await Lines.check(plugin, message)
    if "caps" in automod:
        await Caps.check(plugin, message)

    # for opt in [Attachments, Invites, Everyone, Zalgo, Mentions, Lines, Caps]:
    #     await opt.check(plugin, message)