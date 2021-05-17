import discord

from ....utils.RegEx import getPattern, Match


async def check(plugin, message):
    MENTION_RE = getPattern("<@[!&]?\\d+>")
    all_mentions = len(MENTION_RE.findall(message.content))
    if all_mentions >= plugin.db.configs.get(message.guild.id, "mention_threshold"):
        plugin.bot.ignore_for_event.add("messages", message.id)
        try:
            await message.delete()
        except discord.NotFound:
            pass
        await plugin.action_validator.figure_it_out(
            message, 
            message.guild, 
            message.author,
            "mention_spam",
            moderator=plugin.bot.user,
            moderator_id=plugin.bot.user.id,
            reason=f"Spamming mentions: {all_mentions}",
            all_mentions=all_mentions,
            _type="mention"
        )