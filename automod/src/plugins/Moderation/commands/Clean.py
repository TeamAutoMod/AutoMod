from ..sub.CleanMessages import cleanMessages



async def run(plugin, ctx, amount):
    if amount is None:
        amount = 10
    
    if amount < 1:
        return await ctx.send(plugin.i18next.t(ctx.guild, "amount_too_small", _emote="NO"))

    if amount > 300:
        return await ctx.send(plugin.i18next.t(ctx.guild, "amount_too_big", _emote="NO"))

    await cleanMessages(
        plugin, 
        ctx, 
        "All", 
        amount, 
        lambda m: True, 
        check_amount=amount
    )