import discord



async def check(plugin, message):
    content = message.content.replace("\\", "")

    if "@everyone" in content.lower() or "@here" in content.lower() and "everyone" in plugin.db.configs.get(message.guild.id, "automod"):
        plugin.bot.ignore_for_event.add("messages", message.id)
        try:
            await message.delete()
        except discord.NotFound:
            pass
        
        await plugin.action_validator.figure_it_out(
            message, 
            message.author,
            "everyone",
            moderator=plugin.bot.user,
            moderator_id=plugin.bot.user.id,
            reason=discord.utils.escape_mentions("Attempted @everyone/here")
        )
