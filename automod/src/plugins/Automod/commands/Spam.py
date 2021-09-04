


async def run(plugin, ctx, warns):
    warns = warns.lower()
    automod = plugin.db.configs.get(ctx.guild.id, "automod")
    if warns == "off":
        automod.update({
            "spam": {"status": False, "warns": 0}
        })
        plugin.db.configs.update(ctx.guild.id, "automod", automod)

        return await ctx.send(plugin.i18next.t(ctx.guild, "spam_off", _emote="YES"))

    elif warns.isnumeric():
        warns = int(warns)
        if warns < 1:
            return await ctx.send(plugin.i18next.t(ctx.guild, "min_warns", _emote="NO"))

        if warns > 100:
            return await ctx.send(plugin.i18next.t(ctx.guild, "max_warns", _emote="NO"))

        automod.update({
            "spam": {"status": True, "warns": warns}
        })
        plugin.db.configs.update(ctx.guild.id, "automod", automod)

        await ctx.send(plugin.i18next.t(ctx.guild, "warns_set", _emote="YES", warns=warns, what="they spam more than 10 messages within the last 10 seconds"))

    else:
        prefix = plugin.bot.get_guild_prefix(ctx.guild)
        return await ctx.send(plugin.i18next.t(ctx.guild, "spam_help_2", _emote="BULB", prefix=prefix))