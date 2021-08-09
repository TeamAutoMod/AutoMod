


async def run(plugin, role):
    plugin.bot.cache.roles[role.guild.id] = role.guild.roles