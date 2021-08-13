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
        ),
        inline=True
    )
    e.add_field(
        name="❯ Stats",
        value="• Guilds: {} \n• Users: {}"\
        .format(
            len(bot.guilds),
            len(bot.users)
        ),
        inline=True
    )
    e.add_field(
        name="❯ Commands",
        value="• Used: {} \n• Tags used: {}"\
        .format(
            bot.used_commands,
            bot.used_tags
        ),
        inline=True
    )
    e.add_field(
        name="❯ Support",
        value=f"[Join for help](https://discord.gg/S9BEBux)",
        inline=True
    )
    e.add_field(
        name="❯ GitHub",
        value=f"[{bot.version}](https://github.com/xezzz/AutoMod)",
        inline=True
    )
    e.add_field(
        name="❯ Invite",
        value="[Add to server](https://discord.com/oauth2/authorize?client_id=697487580522086431&scope=bot&permissions=403041534)",
        inline=True
    )

    await ctx.send(embed=e)
