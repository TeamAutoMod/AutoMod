from ...Types import Embed



async def run(plugin, ctx):
    bot = plugin.bot
    e = Embed()
    e.set_thumbnail(url=plugin.bot.user.avatar_url)

    e.add_field(
        name="❯ Status",
        value="Uptime: {} \nVersion: {} \nLatency: {}ms \nTimezone: UTC"\
        .format(bot.get_uptime(), bot.version, round(bot.latency * 1000))
    )
    e.add_field(
        name="❯ Stats",
        value="Guilds: {} \nUsers: {} ({} unique) \nCommands used: {} (Tags: {})"\
        .format(len(bot.guilds), sum([len(x.members) for x in bot.guilds]), len(bot.users), bot.used_commands, bot.used_tags)
    )
    e.add_field(
        name="❯ Links",
        value="📌 [Support Server](https://discord.gg/S9BEBux) \n🛠 [GitHub](https://github.com/xezzz/AutoMod) \n🎉 [Bot Invite](https://discord.com/oauth2/authorize?client_id=697487580522086431&scope=bot&permissions=403041534)"
    )
    await ctx.send(embed=e)
