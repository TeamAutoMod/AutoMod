import time



async def run(plugin, ctx):
    bot = plugin.bot
    
    t1 = time.perf_counter()
    msg = await ctx.send(f"{plugin.emotes.get('PINGING')} Pinging...")
    t2 = time.perf_counter()

    await msg.edit(
        content="Client Latency: ``{}ms`` \nREST API Ping: ``{}ms`` \nShard Latency: ``{}ms``"\
        .format(round(bot.latency * 1000, 2), round((t2 - t1) * 1000, 2), bot.get_shard_ping(ctx.guild))
    )