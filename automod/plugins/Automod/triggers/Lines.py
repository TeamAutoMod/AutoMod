import discord



async def check(plugin, message):
    content = message.content.replace("\\", "")
    new_lines = len(content.split('\n'))
    if "lines" not in plugin.db.configs.get(message.guild.id, "automod"):
        pass
    elif new_lines >= int(plugin.db.configs.get(message.guild.id, "automod")["lines"]["threshold"]):
        plugin.bot.ignore_for_event.add("messages", message.id)
        try:
            await message.delete()
        except discord.NotFound:
            pass

        await plugin.action_validator.figure_it_out(
            message, 
            message.author,
            "lines",
            moderator=plugin.bot.user,
            moderator_id=plugin.bot.user.id,
            user=message.author,
            user_id=message.author.id,
            reason=f"Message contained {new_lines} newlines"
        )
