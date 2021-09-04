import discord

from ..sub.Utils import get_stars_for_message, delete_or_edit



async def run(plugin, payload: discord.RawReactionActionEvent):
    if str(payload.emoji) != "⭐":
        return

    if payload.guild_id == None:
        return
    guild = plugin.bot.get_guild(payload.guild_id)
    if guild is None:
        return

    config = plugin.db.configs.get(f"{payload.guild_id}", "starboard")
    if config["enabled"] == False or config["channel"] == "":
        return

    if payload.channel_id in config["ignored_channels"]:
        return

    starbord_channel = await plugin.bot.utils.getChannel(guild, int(config["channel"]))
    if starbord_channel == None:
        return

    current_channel = await plugin.bot.utils.getChannel(guild, payload.channel_id)
    if current_channel == None:
        return

    message = await current_channel.fetch_message(payload.message_id)
    if message == None or str(message.author.id) == str(payload.user_id) or message.author.bot == True:
        return

    if not plugin.db.stars.exists(f"{message.id}"):
        return

    await delete_or_edit(plugin, message, starbord_channel)