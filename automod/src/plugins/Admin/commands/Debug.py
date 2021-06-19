import psutil

from ...Types import Embed
from ..functions.ParseShardInfo import parseShardInfo



async def run(plugin, ctx):
    e = Embed()
    e.add_field(
        name="❯ AutoMod Statistics",
        value="• Last startup: ``{}`` \n• RAM usage: ``{}%`` \n• CPU usage: ``{}%``"\
            .format(
                plugin.bot.get_uptime(), 
                round(psutil.virtual_memory().percent, 2),
                round(psutil.cpu_percent())
            )
    )
    shards = [parseShardInfo(plugin, x) for x in plugin.bot.shards.values()]
    e.add_field(
        name="❯ {} ({})".format(plugin.bot.user.name, plugin.bot.user.id),
        value="• Guilds: ``{}`` \n• Latency: ``{}ms`` \n• Total shards: ``{}`` \n• Shard Connectivity: \n```diff\n{}\n```"\
        .format(
            len(plugin.bot.guilds),
            round(plugin.bot.latency * 1000, 2), 
            len(plugin.bot.shards),
            "\n".join(shards)
        )
    )

    await ctx.send(embed=e)
