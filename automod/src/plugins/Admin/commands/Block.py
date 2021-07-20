


async def run(plugin, ctx, guild_id):
    # Ensure this is an int
    guild_id = int(guild_id) 
    blocked_guilds = plugin.bot.config.blocked_guilds
    if guild_id in blocked_guilds:
        return await ctx.send(plugin.t(ctx.guild, "already_blocked", _emote="WARN"))
    
    plugin.bot.modify_config.block_guild(guild_id)
    await ctx.send(plugin.t(ctx.guild, "blocked_guild", _emote="YES", guild_id=guild_id))