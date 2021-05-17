import discord

from ....utils.RegEx import getPattern, Match



async def check(plugin, message):
    content = message.content.replace("\\", "")
    CENSOR_RE = getPattern(plugin.db.configs.get(message.guild.id, "censored_words"), join=True)
    found_words = Match(content, CENSOR_RE, option="findall", _return=True)

    if found_words:
        plugin.bot.ignore_for_event.add("messages", message.id)
        try:
            await message.delete()
        except discord.NotFound:
            pass
        await plugin.action_validator.figure_it_out(
            message, 
            message.guild, 
            message.author,
            "word_censor",
            moderator=plugin.bot.user,
            moderator_id=plugin.bot.user.id,
            reason=f"NSFW language (Using slurs): {', '.join(found_words)} \n \n{content}",
            words=", ".join(found_words),
            content=content,
            _type="censor"
        )