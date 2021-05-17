from ..functions.MassbanUsers import massbanUsers



async def run(plugin, ctx, targets, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")

    if len(targets) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_ban_then", _emote="THINK"))

    if len(targets) > 50:
        return await ctx.send(plugin.t(ctx.guild, "max_ban", _emote="WARN"))

    await massbanUsers(plugin, ctx, targets, reason)