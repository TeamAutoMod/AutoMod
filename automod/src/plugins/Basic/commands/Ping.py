


async def run(plugin, ctx):
    bot = plugin.bot
    msg = await ctx.send(f"{plugin.emotes.get('PINGING')} Pinging...")

    await msg.edit(
        content="{} Pong! ``{}ms``"\
        .format(plugin.emotes.get("PONG"), round(bot.latency * 1000, 2))
    )