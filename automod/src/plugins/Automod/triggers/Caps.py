import discord



async def check(plugin, message):
    content = message.content.replace("\\", "")
    if len(content) < 1 or content is None or "caps" not in plugin.db.configs.get(message.guild.id, "automod"):
        return
    try:
        up_percentage = sum(map(str.isupper, list(filter(str.isalpha, content)))) / len(list(filter(str.isalpha, content)))
    except ZeroDivisionError:
        return

    if len(content) > 10 and up_percentage > 0.75:
        plugin.bot.ignore_for_event.add("messages", message.id)
        up_percentage = round(up_percentage * 100, 2)
        try:
            await message.delete()
        except discord.NotFound:
            pass

        await plugin.action_validator.figure_it_out(
            message, 
            message.author,
            "caps",
            moderator=plugin.bot.user,
            moderator_id=plugin.bot.user.id,
            user=message.author,
            user_id=message.author.id,
            reason=f"Excessive caps usage: {up_percentage}% in {len(content)} chars"
        )