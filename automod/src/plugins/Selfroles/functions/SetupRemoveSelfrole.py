


async def setupRemoveSelfrole(plugin, ctx, name, roles):
    name = name.lower()
    if name not in roles:
        return await ctx.send(plugin.translator.translate(ctx.guild, "not_selfrole", _emote="WARN"))

    del roles[name]
    plugin.db.configs.update(ctx.guild.id, "selfroles", roles)
    await ctx.send(plugin.translator.translate(ctx.guild, "selfrole_deleted", _emote="YES", name=name))