


async def setupAddSelfrole(plugin, ctx, name, role, roles):
    role_id = role.id
    name = name.lower()
    if role_id in [roles[x] for x in roles] or name in roles:
        return await ctx.send(plugin.translator.translate(ctx.guild, "already_selfrole", _emote="WARN"))

    if role.position >= ctx.guild.me.top_role.position:
        return await ctx.send(plugin.translator.translate(ctx.guild, "role_too_high", _emote="WARN"))

    if role == ctx.guild.default_role:
        return await ctx.send(plugin.translator.translate(ctx.guild, "default_role_forbidden", _emote="WARN"))

    roles[name] = str(role_id)
    plugin.db.configs.update(ctx.guild.id, "selfroles", roles)
    await ctx.send(plugin.translator.translate(ctx.guild, "selfrole_added", _emote="YES", role=role.name, name=name, prefix=plugin.bot.get_guild_prefix(ctx.guild)))