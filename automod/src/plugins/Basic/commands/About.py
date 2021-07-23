from ...Types import Embed



async def run(plugin, ctx):
    bot = plugin.bot
    e = Embed()
    e.set_thumbnail(url=plugin.bot.user.avatar_url)

    e.add_field(
        name="❯ Uptime",
        value="{}"\
        .format(
            bot.get_uptime()
        )
    )
    e.add_field(
        name="❯ Stats",
        value="• Guilds: {} \n• Users: {} ({} unique) \n• Channels: {}"\
        .format(
            len(bot.guilds), 
            sum([len(x.members) for x in bot.guilds]), 
            len(bot.users), 
            sum([len(x.channels) for x in bot.guilds])
        )
    )
    e.add_field(
        name="❯ Commands",
        value="• Commands used: {} \n• Tags used: {}"\
        .format(
            bot.used_commands,
            bot.used_tags
        )
    )
    e.add_field(
        name="❯ Links",
        value="[Support Server](https://discord.gg/S9BEBux) \n[GitHub](https://github.com/TeamAutoMod/AutoMod) \n[Bot Invite](https://discord.com/oauth2/authorize?client_id=697487580522086431&scope=bot&permissions=403041534)"
    )

    await ctx.send(embed=e)
