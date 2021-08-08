


async def run(plugin, ctx, lines):
    lines = lines.lower()
    if lines == "off":
        automod = plugin.db.configs.get(ctx.guild.id, "automod")
        if "lines" in automod:
            del automod["lines"]
        plugin.db.configs.update(ctx.guild.id, "automod", automod)

        await ctx.send(plugin.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="max-lines"))
    else:
        try:
            lines = int(lines)
        except ValueError:
            await ctx.send(plugin.i18next.t(ctx.guild, "invalid_automod_feature_param", _emote="WARN", prefix=plugin.bot.get_guild_prefix(ctx.guild), command="lines <lines>", off_command="lines off"))
        else:
            if lines < 6:
                return await ctx.send(plugin.i18next.t(ctx.guild, "min_lines", _emote="NO"))

            if lines > 150:
                return await ctx.send(plugin.i18next.t(ctx.guild, "max_lines", _emote="NO"))

            automod = plugin.db.configs.get(ctx.guild.id, "automod")
            automod.update({
                "lines": {"threshold": lines}
            })
            plugin.db.configs.update(ctx.guild.id, "automod", automod)

            await ctx.send(plugin.i18next.t(ctx.guild, "lines_set", _emote="YES", lines=lines, what="they attempt to mention @everyone/here"))