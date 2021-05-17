from ..functions.AddSelfroles import addSelfroles



async def run(plugin, ctx, role):
    roles = plugin.db.configs.get(ctx.guild.id, "selfroles")
    if len(roles) < 1:
        return await ctx.send(plugin.translator.translate(ctx.guild, "no_selfroles", _emote="WARN"))
    
    await addSelfroles(plugin, ctx, roles, role)
