import discord

import asyncio



async def run(plugin, before, after):
    if after.guild is None:
        return
    if plugin.db.configs.get(after.guild.id, "message_logging") is False \
    or not isinstance(after.channel, discord.TextChannel) \
    or after.author.id == plugin.bot.user.id \
    or str(after.channel.id) == plugin.db.configs.get(after.guild.id, "member_log_channel") \
    or str(after.channel.id) == plugin.db.configs.get(after.guild.id, "voice_log_channel") \
    or str(after.channel.id) == plugin.db.configs.get(after.guild.id, "action_log_channel") \
    or str(after.channel.id) == plugin.db.configs.get(after.guild.id, "message_log_channel") \
    or after.type != discord.MessageType.default:
        return
    if before.content != after.content:
        await plugin.action_logger.log(
            after.guild, 
            "message_edited", 
            user=after.author,
            user_id=after.author.id,
            channel=after.channel.mention,
            before=before.content if len(before.content) < 900 else f"{before.content[:900]}...",
            after=after.content if len(after.content) < 900 else f"{after.content[:900]}..."
        )