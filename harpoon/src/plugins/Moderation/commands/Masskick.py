from ..functions.MasskickUsers import masskickUsers



async def run(plugin, ctx, targets, reason):
    if reason is None:
        reason = plugin.translator.translate(ctx.guild, "no_reason")

    if len(targets) < 1:
        return await ctx.send(plugin.translator.translate(ctx.guild, "no_kick_then", _emote="THINK"))

    if len(targets) > 50:
        return await ctx.send(plugin.translator.translate(ctx.guild, "max_kick", _emote="WARN"))

    await masskickUsers(plugin, ctx, targets, reason)