import discord



async def check(plugin, message):
    content = message.content.replace("\\", "")
    up_percentage = sum(map(str.isupper, list(filter(str.isalpha, content)))) / len(list(filter(str.isalpha, content)))

    if len(content) > 10 and up_percentage > 0.75:
        plugin.bot.ignore_for_event.add("messages", message.id)
        up_percentage = round(up_percentage * 100, 2)
        try:
            await message.delete()
        except discord.NotFound:
            pass
        await plugin.action_validator.figure_it_out(
            message, 
            message.guild, 
            message.author,
            "caps_censor",
            moderator=plugin.bot.user,
            moderator_id=plugin.bot.user.id,
            reason=f"Excessive caps usage: {up_percentage}% \n \n{content}",
            up_percentage=up_percentage,
            content=content,
            _type="caps"
        )