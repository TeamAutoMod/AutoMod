import discord

import time
import traceback

from ...Types import Embed



async def run(plugin, ctx):
    bot = plugin.bot
    
    t1 = time.perf_counter()
    msg = await ctx.send(f"{plugin.emotes.get('PINGING')} Pinging...")
    t2 = time.perf_counter()

    e = Embed(
        title=f"{plugin.emotes.get('PONG')} Pong!",
        description="```\n• Client Latency: {}ms \n• REST API Ping: {}ms \n• Shard Latency: {}ms \n```"\
        .format(round(bot.latency * 1000, 2), round((t2 - t1) * 1000), bot.get_shard_ping(ctx.guild))
    )
    await msg.edit(content=None, embed=e)