import discord

from ..functions.ParseFilter import parseFilter
from ...Automod.functions.ShouldPerformAutomod import shouldPerformAutomod



async def run(plugin, message):
    if not await shouldPerformAutomod(plugin, message):
        return

    filters = plugin.db.configs.get(message.guild.id, "filters")
    if len(filters) < 1:
        return

    content = message.content.replace("\\", "")
    for name in filters:
        f = filters[name]
        parsed = parseFilter(f["words"])
        found = parsed.findall(content)
        if found:
            plugin.bot.ignore_for_event.add("messages", message.id)
            try:
                await message.delete()
            except discord.NotFound:
                pass

            await plugin.action_validator.add_warns(
                message, 
                message.author,
                int(f["warns"]),
                moderator=plugin.bot.user,
                moderator_id=plugin.bot.user.id,
                user=message.author,
                user_id=message.author.id,
                reason=f"Triggered filter '{name}' with '{', '.join(found)}'"
            )