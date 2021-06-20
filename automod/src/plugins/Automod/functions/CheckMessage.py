import discord

from ..functions.ShouldPerformAutomod import shouldPerformAutomod
from ..triggers import Attachments, Invites, Zalgo, Mentions, Caps, Everyone, Lines



async def checkMessage(plugin, message):
    if not await shouldPerformAutomod(plugin, message):
        return
    
    for opt in [Attachments, Invites, Everyone, Zalgo, Mentions, Lines, Caps]:
        await opt.check(plugin, message)