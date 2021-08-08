


async def run(plugin, ctx, warns):
    warns = warns.lower()
    if warns == "off":
        automod = plugin.db.configs.get(ctx.guild.id, "automod")
        if "invites" in automod:
            del automod["invites"]
        plugin.db.configs.update(ctx.guild.id, "automod", automod)

        await ctx.send(plugin.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="anti-invites"))
    else:
        try:
            warns = int(warns)
        except ValueError:
            await ctx.send(plugin.i18next.t(ctx.guild, "invalid_automod_feature_param", _emote="WARN", prefix=plugin.bot.get_guild_prefix(ctx.guild), command="invite <warns>", off_command="invite off"))
        else:
            if warns < 1:
                return await ctx.send(plugin.i18next.t(ctx.guild, "min_warns", _emote="NO"))

            if warns > 100:
                return await ctx.send(plugin.i18next.t(ctx.guild, "max_warns", _emote="NO"))

            automod = plugin.db.configs.get(ctx.guild.id, "automod")
            automod.update({
                "invites": {"warns": warns}
            })
            plugin.db.configs.update(ctx.guild.id, "automod", automod)

            await ctx.send(plugin.i18next.t(ctx.guild, "warns_set", _emote="YES", warns=warns, what="they send Discord invites"))