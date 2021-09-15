import time



async def run(plugin, ctx):
    t1 = time.perf_counter()
    msg = await ctx.send(f"{plugin.emotes.get('PINGING')} Pinging...")
    t2 = time.perf_counter()

    rest = round((t2 - t1) * 1000)
    latency = round(plugin.bot.latency * 1000)
    await msg.edit(
        content="{} Rest API: ``{}ms`` | Latency: ``{}ms``"\
        .format(plugin.emotes.get("PONG"), rest, latency)
    )