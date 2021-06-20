


async def run(plugin, ctx):
    confirm = await ctx.prompt("This will setup the basic automod config. If you've already setup a few settings, those will be overwritten", timeout=15)
    if not confirm:
        return await ctx.send(plugin.t(ctx.guild, "aborting"))

    msg = await ctx.send(plugin.t(ctx.guild, "start_automod", _emote="YES"))

    punishments = plugin.db.configs.get(ctx.guild.id, "punishments")
    if not "5" in punishments:
        punishments.update({
            "5": "kick"
        })
    
    automod = {
        "invites": {"warns": 1},
        "everyone": {"warns": 1},

        "mention": {"threshold": 10},
        "lines": {"threshold": 15},

        "raid": {"status": False, "threshold": ""},

        "caps": {"warns": 1},
        "files": {"warns": 1},
        "zalgo": {"warns": 1},
        "censor": {"warns": 1},
        "spam": {"status": True, "warns": 3}
    }

    plugin.db.configs.update(ctx.guild.id, "punishments", punishments)
    plugin.db.configs.update(ctx.guild.id, "automod", automod)

    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    await msg.edit(content=plugin.t(ctx.guild, "automod_done", _emote="YES", prefix=prefix))
    