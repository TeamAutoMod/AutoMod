import discord

from ....utils.RegEx import Match
from ....utils.Constants import ZALGO_RE



async def check(plugin, message):
    found_zalgo = Match(message.content, ZALGO_RE, _return=True)

    if found_zalgo and "zalgo" in plugin.db.configs.get(message.guild.id, "automod"):
        plugin.bot.ignore_for_event.add("messages", message.id)
        try:
            await message.delete()
        except discord.NotFound:
            pass

        await plugin.action_validator.figure_it_out(
            message, 
            message.author,
            "zalgo",
            moderator=plugin.bot.user,
            moderator_id=plugin.bot.user.id,
            user=message.author,
            user_id=message.author.id,
            reason=f"Illegible message formatting (Zalgo chars) at position {found_zalgo.start()}"
        )