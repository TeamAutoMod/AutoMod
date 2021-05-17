from ...Types import Embed



async def run(plugin, ctx):
    bot = plugin.bot
    e = Embed(title=plugin.translator.translate(ctx.guild, "about", bot=bot.user.name))
    e.set_thumbnail(url=bot.user.avatar_url)
    e.add_field(
        name="Status",
        value="```\n• Uptime: {} \n• Version: {} \n• Latency: {}ms \n• Timezone: UTC \n```"\
        .format(bot.get_uptime(), bot.version, round(bot.latency * 1000))
    )
    e.add_field(
        name="Stats",
        value="```\n• Guilds: {} \n• Users: {} ({} unique) \n• Commands Used: {} (Custom: {}) \n```"\
        .format(len(bot.guilds), sum([len(x.members) for x in bot.guilds]), len(bot.users), bot.used_commands, bot.used_custom_commands)
    )
    await ctx.send(embed=e)
