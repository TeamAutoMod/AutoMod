import discord
from discord.ext import commands

import logging; log = logging.getLogger()

from . import AutoModPlugin
from ..schemas import GuildConfig



class InternalPlugin(AutoModPlugin):
    """Plugin for all utility commands"""
    def __init__(self, bot):
        super().__init__(bot)


    @AutoModPlugin.listener()
    async def on_guild_join(self, guild: discord.Guild):
        log.info(f"Joined guild: {guild.name} ({guild.id})")

        try:
            await guild.chunk(cache=True)
        except Exception as ex:
            log.warn(f"Failed to chunk members for guild {guild.id} upon joining - {ex}")
        finally:
            if not self.db.configs.exists(guild.id):
                self.db.configs.insert(GuildConfig(guild, self.config.default_prefix))


    @AutoModPlugin.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        log.info(f"Removed from guild: {guild.name} ({guild.id})")

        if self.db.configs.exists(guild.id):
            self.db.configs.delete(guild.id)


def setup(bot): bot.register_plugin(InternalPlugin(bot))