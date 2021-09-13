


async def run(plugin, guild):
    if guild is None:
        return
    plugin.cache.destroy(guild_id=guild.id)
    if plugin.db.configs.exists(guild.id):
        plugin.db.configs.delete(guild.id)