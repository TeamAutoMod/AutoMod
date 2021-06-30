from ..functions.CleanMessages import cleanMessages



async def run(plugin, ctx, amount):
    if amount is None:
        amount = 50
    
    if amount < 1:
        return await ctx.send(plugin.t(ctx.guild, "amount_too_small", _emote="NO"))

    if amount > 300:
        return await ctx.send(plugin.t(ctx.guild, "amount_too_big", _emote="NO"))

    await cleanMessages(
        plugin, 
        ctx, 
        "Bots", 
        amount, 
        lambda m: m.author.bot
    )