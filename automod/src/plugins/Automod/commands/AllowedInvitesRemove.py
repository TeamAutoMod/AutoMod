


async def run(plugin, ctx, guild_id):
    allowed = [x.strip().lower() for x in plugin.db.configs.get(ctx.guild.id, "whitelisted_invites")]

    if str(guild_id) not in allowed:
        return await ctx.send(plugin.i18next.t(ctx.guild, "not_whitelisted", _emote="NO", server=guild_id))

    allowed.remove(str(guild_id))
    plugin.db.configs.update(ctx.guild.id, "whitelisted_invites", allowed)
    
    await ctx.send(plugin.i18next.t(ctx.guild, "removed_invite", _emote="YES", server=guild_id))