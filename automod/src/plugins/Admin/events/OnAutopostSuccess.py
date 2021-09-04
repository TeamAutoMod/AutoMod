import logging



log = logging.getLogger(__name__)
async def run(plugin):
    log.info("Posted server count ({}) and shard count ({})".format(plugin.bot.topggpy.guild_count, plugin.bot.shard_count))