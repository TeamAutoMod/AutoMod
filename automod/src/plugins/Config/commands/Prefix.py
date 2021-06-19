


async def run(plugin, ctx, prefix):
    current = plugin.bot.get_guild_prefix(ctx.guild)
    if prefix is None:
        return await ctx.send(plugin.t(ctx.guild, "current_prefix", prefix=current))

    if prefix == current:
        return await ctx.send(plugin.t(ctx.guild, "already_is_prefix", _emote="WARN"))
    
    if len(prefix) > 10:
        return await ctx.send(plugin.t(ctx.guild, "prefix_too_long", _emote="WARN"))

    plugin.db.configs.update(ctx.guild.id, "prefix", prefix)
    await ctx.send(plugin.t(ctx.guild, "prefix_updated", _emote="YES", prefix=prefix))