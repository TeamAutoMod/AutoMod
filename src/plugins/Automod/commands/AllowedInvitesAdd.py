


async def run(plugin, ctx, guild_id):
    allowed = [x.strip().lower() for x in plugin.db.configs.get(ctx.guild.id, "whitelisted_invites")]

    if str(guild_id) in allowed:
        return await ctx.send(plugin.t(ctx.guild, "already_whitelisted", _emote="WARN", server=guild_id))

    allowed.append(str(guild_id))
    plugin.db.configs.update(ctx.guild.id, "whitelisted_invites", allowed)

    await ctx.send(plugin.t(ctx.guild, "added_invite", _emote="YES", server=guild_id))