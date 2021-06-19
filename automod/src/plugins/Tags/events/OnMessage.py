import discord

from ..functions.GetTags import getTags



async def run(plugin, message):
    if message.author.bot or message.webhook_id is not None or message.author.id == plugin.bot.user.id:
        return

    if message.guild is None or not isinstance(message.channel, discord.TextChannel):
        return

    tags = await getTags(plugin, message)
    prefix = plugin.bot.get_guild_prefix(message.guild)
    if message.content.startswith(prefix, 0) and len(tags) > 0:
        for tag in tags:
            trigger = tag["trigger"]
            if message.content.lower() == prefix + trigger or (message.content.lower().startswith(trigger, len(prefix)) and message.content.lower()[len(prefix + trigger)] == " "):
                uses = plugin.db.tags.get(f"{message.guild.id}-{trigger}", "uses")
                plugin.db.tags.update(f"{message.guild.id}-{trigger}", "uses", (uses+1))
                reply = tag["reply"]
                return await message.channel.send(f"{reply}")