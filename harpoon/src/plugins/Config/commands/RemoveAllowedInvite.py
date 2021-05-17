


async def run(plugin, ctx, server):
    if plugin.db.configs.get(ctx.guild.id, "automod") is False:
        return await ctx.send(plugin.t(ctx.guild, "automod_disabled", _emote="WARN"))

    allowed = plugin.db.configs.get(ctx.guild.id, "whitelisted_invites")

    if str(server) not in allowed:
        return await ctx.send(plugin.t(ctx.guild, "not_whitelisted", _emote="WARN"))

    allowed.remove(str(server))
    plugin.db.update(ctx.guild.id, "whitelisted_invites", allowed)
    
    await ctx.send(plugin.t(ctx.guild, "removed_invite", _emote="YES", server=server))