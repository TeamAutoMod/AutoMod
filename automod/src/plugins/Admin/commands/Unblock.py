import discord



async def run(plugin, ctx, guild_id):
    # Ensure this is an int
    guild_id = int(guild_id) 
    blocked_guilds = plugin.bot.config["blocked_guilds"]
    if guild_id not in blocked_guilds:
        return await ctx.send(plugin.t(ctx.guild, "not_blocked", _emote="WARN"))

    g = discord.utils.get(plugin.bot.guilds, id=guild_id)
    if g is not None:
        await g.leave()
    
    plugin.bot.modify_config.unblock_guild(guild_id)
    await ctx.send(plugin.t(ctx.guild, "unblocked_guild", _emote="YES", guild_id=guild_id))