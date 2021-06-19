


async def run(plugin, ctx, amount):
    if amount is None:
        amount = 10
    
    if amount < 1:
        return await ctx.send(plugin.t(ctx.guild, "amount_too_small", _emote="WARN"))

    if amount > 300:
        return await ctx.send(plugin.t(ctx.guild, "amount_too_big", _emote="WARN"))

    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(plugin.t(ctx.guild, "messages_deleted", _emote="YES", count=len(deleted), plural="" if len(deleted) == 1 else "s"))
    await plugin.action_logger.log(
        ctx.guild,
        "clean",
        moderator=ctx.message.author,
        moderator_id=ctx.message.author.id,
        count=len(deleted),
        plural="" if len(deleted) == 1 else "s",
        channel=ctx.message.channel.mention
    )