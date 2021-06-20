


async def run(plugin, ctx, mentions):
    if mentions < 4:
        return await ctx.send(plugin.t(ctx.guild, "min_mentions", _emote="WARN"))

    if mentions > 100:
        return await ctx.send(plugin.t(ctx.guild, "max_mentions", _emote="WARN"))

    automod = plugin.db.configs.get(ctx.guild.id, "automod")
    automod.update({
        "mentions": {"threshold": mentions}
    })

    await ctx.send(plugin.t(ctx.guild, "mentions_set", _emote="YES", mentions=mentions))