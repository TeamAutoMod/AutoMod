import logging



log = logging.getLogger(__name__)


async def run(plugin, guild):
    log.info(f"Joined guild: {guild.name} ({guild.id})")
    if guild is None:
        return
    try:
        await guild.chunk(cache=True)
    except Exception:
        log.warn(f"Failed to chunk guild {guild.name} ({guild.id})")
        pass
    finally:
        plugin.cache.build_for_guild(guild)
        if not plugin.db.configs.exists(guild.id):
            plugin.db.configs.insert(plugin.schemas.GuildConfig(guild))