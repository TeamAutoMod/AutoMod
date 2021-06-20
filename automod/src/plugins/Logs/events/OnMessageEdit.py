import discord

import asyncio

from ...Types import Embed



async def run(plugin, before, after):
    if after.guild is None:
        return
    if plugin.db.configs.get(after.guild.id, "message_logging") is False \
    or not isinstance(after.channel, discord.TextChannel) \
    or after.author.id == plugin.bot.user.id \
    or str(after.channel.id) == plugin.db.configs.get(after.guild.id, "server_log") \
    or str(after.channel.id) == plugin.db.configs.get(after.guild.id, "voice_log") \
    or str(after.channel.id) == plugin.db.configs.get(after.guild.id, "mod_log") \
    or str(after.channel.id) == plugin.db.configs.get(after.guild.id, "message_log") \
    or after.type != discord.MessageType.default:
        return
    
    if before.content != after.content and len(after.content) > 0:

        e = Embed(
            color=0xFFFF00, 
            timestamp=after.created_at
        )
        e.set_author(
            name=f"{after.author} ({after.author.id})",
            icon_url=after.author.avatar_url_as()
        )
        e.add_field(
            name="❯ Before",
            value=before.content
        )
        e.add_field(
            name="❯ After",
            value=after.content
        )
        e.set_footer(text=f"#{after.channel.name}")
        await plugin.action_logger.log(
            after.guild, 
            "message_edited", 
            _embed=e
        )