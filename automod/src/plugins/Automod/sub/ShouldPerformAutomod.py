import discord

from ....utils import Permissions



async def shouldPerformAutomod(plugin, message):
    if message.guild is None:
        return False

    if not isinstance(message.author, discord.Member):
        return
        
    if Permissions.is_mod(message.author):
        return False

    if message.author.discriminator == "0000":
        return False

    if message.author.id == plugin.bot.user.id:
        return False

    if message.author.top_role.position >= message.guild.me.top_role.position:
        return

    if len(plugin.db.configs.get(message.guild.id, "automod")) < 1:
        return False
    
    if message.type != discord.MessageType.default:
        return False

    if len([x for x in message.author.roles if x.id in plugin.db.configs.get(message.guild.id, "ignored_roles")]) > 1:
        return False

    if message.channel.id in plugin.db.configs.get(message.guild.id, "ignored_channels"):
        return False
    
    return True