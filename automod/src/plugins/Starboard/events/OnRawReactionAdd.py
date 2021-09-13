import discord

from ..sub.Utils import build_embed, get_stars_for_message, edit_or_send



async def run(plugin, payload: discord.RawReactionActionEvent):
    if str(payload.emoji) != "⭐":
        return

    if payload.guild_id == None:
        return
    guild = plugin.bot.get_guild(payload.guild_id)
    if guild is None:
        return

    if str(payload.user_id) == str(plugin.bot.user.id):
        return

    config = plugin.db.configs.get(f"{payload.guild_id}", "starboard")
    if config["enabled"] == False or config["channel"] == "":
        return

    if payload.channel_id in config["ignored_channels"]:
        return

    starboard_channel = await plugin.bot.utils.getChannel(guild, int(config["channel"]))
    if starboard_channel == None:
        return

    current_channel = await plugin.bot.utils.getChannel(guild, payload.channel_id)
    if current_channel == None:
        return

    if str(starboard_channel.id) == str(current_channel.id):
        return

    message = await current_channel.fetch_message(payload.message_id)
    if message == None or str(message.author.id) == str(payload.user_id) or message.author.bot == True:
        return

    stars, new = get_stars_for_message(plugin, message)
    embed, content = build_embed(message, stars)

    await edit_or_send(plugin, new, message, starboard_channel, content, embed)