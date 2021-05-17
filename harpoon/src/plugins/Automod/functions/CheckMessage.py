import discord

from ....utils import Permissions
from ..triggers import Attachments, Invites, Words, Zalgo, Mentions, Caps



async def checkMessage(plugin, message):
    if Permissions.is_mod(message.author) or message.author.discriminator == "0000" or message.author.id == plugin.bot.user.id:
        return
    
    if message.type != discord.MessageType.default:
        return
    
    for opt in [Attachments, Invites, Words, Zalgo, Mentions, Caps]:
        await opt.check(plugin, message)