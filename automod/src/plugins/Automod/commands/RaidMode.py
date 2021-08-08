from ..sub.Raid import disableRaidMode, enableRaidMode



async def run(plugin, ctx, state, reason):
    state = state.lower()
    if state == "off":
        if ctx.guild.id not in plugin.raids:
            return await ctx.send(plugin.t(ctx.guild, "no_raid", _emote="NO"))
        else:
            await disableRaidMode(plugin, ctx.guild, ctx.author, reason)
            await ctx.send(plugin.t(ctx.guild, "disabled_raid", _emote="YES"))
    elif state == "on":
        if ctx.guild.id in plugin.raids:
            return await ctx.send(plugin.t(ctx.guild, "already_raid", _emote="NO"))
        else:
            await enableRaidMode(plugin, ctx.guild, ctx.author, reason)
            await ctx.send(plugin.t(ctx.guild, "enabled_raid", _emote="YES"))
    else:
        await ctx.send(plugin.t(ctx.guild, "invalid_raid_opt", _emote="WARN"))