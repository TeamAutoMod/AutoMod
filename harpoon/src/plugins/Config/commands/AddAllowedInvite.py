


async def run(plugin, ctx, server):
    if plugin.db.configs.get(ctx.guild.id, "automod") is False:
        return await ctx.send(plugin.translator.translate(ctx.guild, "automod_disabled", _emote="WARN"))
        
    allowed = plugin.db.configs.get(ctx.guild.id, "whitelisted_invites")

    if str(server) in allowed:
        return await ctx.send(plugin.translator.translate(ctx.guild, "already_whitelisted", _emote="WARN"))

    allowed.append(str(server))
    plugin.db.update(ctx.guild.id, "whitelisted_invites", allowed)

    await ctx.send(plugin.translator.translate(ctx.guild, "added_invite", _emote="YES", server=server))