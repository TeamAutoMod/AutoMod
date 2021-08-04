from ..sub.CleanMessages import cleanMessages



async def run(plugin, ctx, users, amount):
    if amount is None:
        amount = 50

    users = list(set(users))
    if len(users) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_member", _emote="NO"))
    
    if amount < 1:
        return await ctx.send(plugin.t(ctx.guild, "amount_too_small", _emote="NO"))

    if amount > 300:
        return await ctx.send(plugin.t(ctx.guild, "amount_too_big", _emote="NO"))

    await cleanMessages(
        plugin, 
        ctx, 
        "User", 
        amount, 
        lambda m: any(m.author.id == u.id for u in users)
    )