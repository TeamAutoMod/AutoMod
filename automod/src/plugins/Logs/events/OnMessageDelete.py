import discord

import asyncio
import datetime

from ...Types import Embed



async def run(plugin, message):
    if message.guild is None:
        return
    # Wait 1s before we continue
    # This is so we don't log actions
    # From e.g. message censorships
    await asyncio.sleep(0.5)
    if plugin.ignore_for_event.has("messages", message.id):
        return plugin.ignore_for_event.remove("messages", message.id)

    
    if plugin.db.configs.get(message.guild.id, "message_logging") is False \
    or not isinstance(message.channel, discord.TextChannel) \
    or message.author.id == plugin.bot.user.id \
    or str(message.channel.id) == plugin.db.configs.get(message.guild.id, "server_log") \
    or str(message.channel.id) == plugin.db.configs.get(message.guild.id, "voice_log") \
    or str(message.channel.id) == plugin.db.configs.get(message.guild.id, "mod_log") \
    or str(message.channel.id) == plugin.db.configs.get(message.guild.id, "message_log") \
    or message.type != discord.MessageType.default:
        return

    content = " ".join([x.url for x in message.attachments]) + message.content
    e = Embed(
        color=0xFF0000, 
        timestamp=datetime.datetime.utcnow()
    )
    e.set_author(
        name=f"{message.author} ({message.author.id})",
        icon_url=message.author.avatar_url_as()
    )
    e.add_field(
        name="Content",
        value=content
    )
    e.set_footer(
        text=f"#{message.channel.name}"
    )
    await plugin.action_logger.log(
        message.guild, 
        "message_deleted", 
        _embed=e
    )