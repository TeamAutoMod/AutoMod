


async def run(plugin, ctx, lines):
    if lines < 6:
        return await ctx.send(plugin.t(ctx.guild, "min_lines", _emote="WARN"))

    if lines > 150:
        return await ctx.send(plugin.t(ctx.guild, "max_lines", _emote="WARN"))

    automod = plugin.db.configs.get(ctx.guild.id, "automod")
    automod.update({
        "lines": {"threshold": lines}
    })

    await ctx.send(plugin.t(ctx.guild, "lines_set", _emote="YES", lines=lines, what="they attempt to mention @everyone/here"))