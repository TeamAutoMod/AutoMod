import discord

import asyncio



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
    or str(message.channel.id) == plugin.db.configs.get(message.guild.id, "member_log_channel") \
    or str(message.channel.id) == plugin.db.configs.get(message.guild.id, "voice_log_channel") \
    or str(message.channel.id) == plugin.db.configs.get(message.guild.id, "action_log_channel") \
    or str(message.channel.id) == plugin.db.configs.get(message.guild.id, "message_log_channel") \
    or message.type != discord.MessageType.default:
        return

    await plugin.action_logger.log(
        message.guild, 
        "message_deleted", 
        user=message.author,
        user_id=message.author.id,
        channel=message.channel.mention,
        content=message.content if len(message.content) < 1500 else f"{message.content[:1500]}..."
    )