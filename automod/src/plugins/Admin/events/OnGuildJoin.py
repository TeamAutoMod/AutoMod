


async def run(plugin, guild):
    if guild is None:
        return
    try:
        await guild.chunk(cache=True)
    except Exception:
        pass
    finally:
        plugin.cache.build_for_guild(guild)
        if not plugin.db.configs.exists(guild.id):
            plugin.db.configs.insert(plugin.schemas.GuildConfig(guild))