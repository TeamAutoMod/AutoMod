from ..functions.RemoveSelfroles import removeSelfroles



async def run(plugin, ctx, role):
    roles = plugin.db.configs.get(ctx.guild.id, "selfroles")
    if len(roles) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_selfroles", _emote="WARN"))
    
    await removeSelfroles(plugin, ctx, roles, role)