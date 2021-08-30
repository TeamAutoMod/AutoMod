from ...Types import Embed



async def run(plugin, ctx, warns):
    warns = warns.lower()
    if warns == "off":
        automod = plugin.db.configs.get(ctx.guild.id, "automod")
        if "zalgo" in automod:
            del automod["zalgo"]
        plugin.db.configs.update(ctx.guild.id, "automod", automod)
        
        await ctx.send(plugin.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="anti-zalgo"))
    else:
        try:
            warns = int(warns)
        except ValueError:
            e = Embed(
                title="Invalid paramater",
                description=plugin.i18next.t(ctx.guild, "invalid_automod_feature_param", prefix=plugin.bot.get_guild_prefix(ctx.guild), command="zalgo <warns>", off_command="zalgo off")
            )
            await ctx.send(embed=e)
        else:
            if warns < 1:
                return await ctx.send(plugin.i18next.t(ctx.guild, "min_warns", _emote="NO"))

            if warns > 100:
                return await ctx.send(plugin.i18next.t(ctx.guild, "max_warns", _emote="NO"))

            automod = plugin.db.configs.get(ctx.guild.id, "automod")
            automod.update({
                "zalgo": {"warns": warns}
            })
            plugin.db.configs.update(ctx.guild.id, "automod", automod)

            await ctx.send(plugin.i18next.t(ctx.guild, "warns_set", _emote="YES", warns=warns, what="there message contains zalgo letters."))