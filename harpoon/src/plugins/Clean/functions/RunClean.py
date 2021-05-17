


async def runClean(plugin, ctx, amount, check=None, before=None, after=None):
    if ctx.channel.id in plugin.cleaning:
        return await ctx.send(plugin.translator.translate(ctx.guild, "already_cleaning", _emote="WARN"))
    
    plugin.cleaning.append(ctx.channel.id)
    try:
        deleted = await ctx.channel.purge(limit=amount, check=check, before=before, after=after)
    except Exception as ex:
        await ctx.send(plugin.translator.translate(ctx.guild, "clean_error", _emote="WARN", exc=ex))
    else:
        if len(deleted) < 1:
            return await ctx.send(plugin.translator.translate(ctx.guild, "zero_cleaned", _emote="WARN"))
        else:
            await ctx.send(plugin.translator.translate(ctx.guild, "cleaned", _emote="YES", amount=len(deleted), plural="" if len(deleted) == 1 else "s"))
            await plugin.action_logger.log(
                ctx.guild, 
                "clean",
                moderator=ctx.author,
                moderator_id=ctx.author.id,
                count=len(deleted),
                plural="" if len(deleted) == 1 else "s",
                channel=ctx.channel.mention
            )
    finally:
        plugin.cleaning.remove(ctx.channel.id)